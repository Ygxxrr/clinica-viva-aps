"""Ponto de entrada Flask, rotas HTTP, autenticação e composição das telas."""
from clock_local import now_local, today_local
import csv
import io
import os
import secrets
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort, Response
from sqlalchemy import select, func, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from models import *
from catalog import CATALOGS
from services import *

load_dotenv()
app=Flask(__name__,static_folder='public',static_url_path='')
database=os.environ.get('DATABASE_URL','sqlite:///clinica.db')
if database.startswith(('postgres://','postgresql://')):
    database=database.replace(database.split('://')[0]+'://','postgresql+psycopg://',1)
if os.environ.get('VERCEL') and database.startswith('sqlite'):
    raise RuntimeError('Configure DATABASE_URL com PostgreSQL antes do deploy na Vercel.')
secret=os.environ.get('SECRET_KEY')
if os.environ.get('VERCEL') and not secret: raise RuntimeError('Configure SECRET_KEY na Vercel.')
app.config.update(SECRET_KEY=secret or 'local-development-only-change-before-deploy',SQLALCHEMY_DATABASE_URI=database,
 SQLALCHEMY_TRACK_MODIFICATIONS=False,SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping':True},
 SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=bool(os.environ.get('VERCEL')),
 PERMANENT_SESSION_LIFETIME=timedelta(hours=4),MAX_CONTENT_LENGTH=1024*1024)
db.init_app(app)
with app.app_context():
    try: upgrade_schema()
    except Exception: app.logger.exception('Falha ao atualizar a estrutura do banco.')
DEMO_MODE=os.environ.get('DEMO_MODE','true').lower()=='true'

@event.listens_for(Engine,'connect')
def enable_sqlite_constraints(connection,record):
    if type(connection).__module__=='sqlite3': connection.execute('PRAGMA foreign_keys=ON')

def roles(*allowed):
    def decorate(view):
        @wraps(view)
        def wrapped(*args,**kwargs):
            if g.user is None: return redirect(url_for('login'))
            if g.user.role not in allowed and g.user.role!='admin': abort(403)
            return view(*args,**kwargs)
        return wrapped
    return decorate

@app.before_request
def authenticate():
    g.user=db.session.get(User,session['user_id']) if session.get('user_id') else None
    if 'csrf' not in session: session['csrf']=secrets.token_urlsafe(32)
    if request.method=='POST' and not secrets.compare_digest(str(request.form.get('csrf','')),session['csrf']): abort(400,description='Sessão do formulário expirada. Atualize a página e tente novamente.')
    if request.endpoint not in ('login','static','health') and g.user is None: return redirect(url_for('login'))

@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='same-origin'
    if request.endpoint!='static': response.headers['Cache-Control']='no-store'
    return response

@app.context_processor
def context():
    return dict(catalogs=CATALOGS,today=today_local(),now=now_local(),demo_mode=DEMO_MODE,
      can_clinical=g.user is not None and g.user.role in ('admin','medico'),
      can_reception=g.user is not None and g.user.role in ('admin','recepcao'),
      can_finance=g.user is not None and g.user.role in ('admin','financeiro'),label=label,format_cpf=format_cpf)

def label(obj):
    if obj is None:return '—'
    if isinstance(obj,(list,tuple)): return ', '.join(label(x) for x in obj) or '—'
    if isinstance(obj,datetime): return obj.strftime('%d/%m/%Y %H:%M')
    if isinstance(obj,date): return obj.strftime('%d/%m/%Y')
    if isinstance(obj,Decimal): return brl(obj)
    return getattr(obj,'name',str(obj))

@app.template_filter('brl')
def brl(value): return 'R$ '+f'{Decimal(value or 0):,.2f}'.replace(',','X').replace('.',',').replace('X','.')

@app.template_filter('datebr')
def datebr(value): return label(value)

@app.template_filter('cell')
def cell(obj,key): return label(getattr(obj,key,None))

def audit(action): db.session.add(AuditLog(user_id=g.user.id,action=action))

def commit(action):
    audit(action)
    db.session.commit()
    flash('Operação realizada com sucesso.','success')

@app.errorhandler(BusinessError)
def business_error(error):
    db.session.rollback()
    return render_template('error.html',title='Confira as informações',message=str(error),code=422),422

@app.errorhandler(IntegrityError)
def integrity_error(error):
    db.session.rollback()
    app.logger.info('Restrição de integridade: %s',type(error).__name__)
    return render_template('error.html',title='Registro não permitido',message='Existe um registro duplicado ou um vínculo obrigatório inválido. Confira CPF, CNPJ, nome e vínculos antes de salvar.',code=409),409

@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(400)
def http_error(error):
    return render_template('error.html',title='Acesso não permitido' if error.code==403 else 'Não foi possível abrir esta página',message=error.description,code=error.code),error.code

@app.get('/health')
def health():
    db.session.execute(select(1))
    return {'status':'ok','application':'Clínica Silva','database':'connected'}

@app.route('/login',methods=['GET','POST'])
def login():
    if g.user is not None:
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        user=db.session.scalar(select(User).where(User.email==request.form.get('email','').strip().lower()))
        if user and user.verify_password(request.form.get('password','')):
            session.clear(); session['user_id']=user.id; session['csrf']=secrets.token_urlsafe(32);session.permanent=True
            return redirect(url_for('dashboard'))
        flash('E-mail ou senha inválidos.','error')
    return render_template('login.html',title='Entrar')

@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def clinical_scope(query):
    if g.user.role=='medico': query=query.where(Appointment.doctor_id==g.user.professional_id)
    return query

def allowed_consultation(obj):
    if g.user.role=='medico' and obj.appointment.doctor_id!=g.user.professional_id: abort(403)
    return obj

@app.get('/')
def dashboard():
    selected_day=parse_date(request.args['day']) if request.args.get('day') else today_local()
    appointments=db.session.scalars(clinical_scope(select(Appointment)).where(func.date(Appointment.starts_at)==selected_day).order_by(Appointment.starts_at)).all()
    selected_appointment=next((a for a in appointments if str(a.id)==request.args.get('appointment_id')),None)
    if selected_appointment is None:
        selected_appointment=next((a for a in appointments if a.status in ('Agendado','Confirmado')),appointments[0] if appointments else None)
    monday=selected_day-timedelta(days=selected_day.weekday())
    week_days=[monday+timedelta(days=i) for i in range(7)]
    charges=db.session.scalars(select(Charge).order_by(Charge.id)).all() if g.user.role in ('admin','financeiro') else []
    month=today_local().replace(day=1)
    received=db.session.scalar(select(func.coalesce(func.sum(Payment.amount),0)).where(Payment.status=='Pago',Payment.paid_at>=month)) if g.user.role in ('admin','financeiro') else None
    consultations=db.session.scalars(clinical_scope(select(Consultation).join(Appointment))).all() if g.user.role in ('admin','medico') else []
    pending_exams=sum(1 for c in consultations for e in c.exam_requests if e.status in ('Solicitado','Agendado'))
    return render_template('dashboard.html',title='Visão geral',appointments=appointments,patient_count=db.session.scalar(select(func.count(Patient.id)).where(Patient.archived_at.is_(None))),
      received=received,balance=sum((x.balance for x in charges),Decimal('0')),pending_exams=pending_exams,
      appointments_count=len(appointments),consultation_count=len(consultations),selected_day=selected_day,
      selected_appointment=selected_appointment,week_days=week_days,recent_charges=charges[-5:][::-1])

@app.get('/cadastros/<slug>')
def catalog_list(slug):
    meta=CATALOGS.get(slug)
    if not meta: abort(404)
    if g.user.role=='financeiro' and slug not in ('convenios','unidades','especialidades','profissionais'): abort(403)
    if g.user.role=='recepcao' and slug in ('alergias','medicamentos','exames','procedimentos'): abort(403)
    query=select(meta['model']).order_by(meta['model'].id.desc())
    show_archived=slug=='pacientes' and request.args.get('arquivados')=='1'
    if slug=='pacientes': query=query.where(Patient.archived_at.isnot(None) if show_archived else Patient.archived_at.is_(None))
    rows=db.session.scalars(query).all()
    q=request.args.get('q','').strip().lower()
    if q: rows=[r for r in rows if q in ' '.join(label(getattr(r,k,None)) for k,_ in meta['columns']).lower()]
    return render_template('catalog.html',title=meta['title'],meta=meta,slug=slug,rows=rows,can_edit=g.user.role in meta['roles'],show_archived=show_archived)

@app.route('/cadastros/<slug>/novo',methods=['GET','POST'])
@app.route('/cadastros/<slug>/<int:row_id>/editar',methods=['GET','POST'])
def catalog_form(slug,row_id=None):
    meta=CATALOGS.get(slug)
    if not meta: abort(404)
    if g.user.role not in meta['roles']: abort(403)
    obj=db.get_or_404(meta['model'],row_id) if row_id else None
    if request.method=='POST':
        obj=save_catalog(meta,request.form,obj)
        db.session.flush()
        commit(f'{"Atualizou" if row_id else "Criou"} {slug} #{obj.id}')
        return redirect(url_for('catalog_list',slug=slug))
    options={f['key']:db.session.scalars(select(f['model']).order_by(f['model'].name if hasattr(f['model'],'name') else f['model'].id)).all() for f in meta['fields'] if f['model']}
    for key,rows in options.items():
        options[key]=[r for r in rows if not getattr(r,'archived_at',None) or (obj is not None and getattr(obj,key,None)==r.id)]
    return render_template('form.html',title=f'{"Editar" if obj else "Novo cadastro de"} {meta["singular"]}',meta=meta,obj=obj,options=options,slug=slug)

@app.get('/pacientes/<int:patient_id>')
@roles('admin','medico','recepcao')
def patient_detail(patient_id):
    patient=db.get_or_404(Patient,patient_id)
    consultations=[]
    if g.user.role in ('admin','medico'):
        consultations=db.session.scalars(select(Consultation).join(Appointment).where(Appointment.patient_id==patient.id).order_by(Consultation.attended_at.desc())).all()
    return render_template('patient.html',title=patient.name,patient=patient,consultations=consultations)

@app.post('/pacientes/<int:patient_id>/excluir')
@roles('admin','recepcao')
def patient_delete(patient_id):
    patient=db.get_or_404(Patient,patient_id)
    name=patient.name
    result=remove_patient(patient)
    audit(f'{"Arquivou" if result=="arquivado" else "Excluiu"} paciente #{patient_id}')
    db.session.commit()
    flash(f'Cadastro de {name} arquivado. O histórico de consultas e o financeiro foram preservados.' if result=='arquivado' else f'Cadastro de {name} excluído.','success')
    return redirect(url_for('catalog_list',slug='pacientes'))

@app.post('/pacientes/<int:patient_id>/restaurar')
@roles('admin','recepcao')
def patient_restore(patient_id):
    patient=db.get_or_404(Patient,patient_id)
    patient.archived_at=None
    audit(f'Restaurou paciente #{patient_id}')
    db.session.commit()
    flash(f'Cadastro de {patient.name} restaurado.','success')
    return redirect(url_for('catalog_list',slug='pacientes'))

@app.post('/pacientes/<int:patient_id>/prontuario')
@roles('admin','medico')
def record_update(patient_id):
    patient=db.get_or_404(Patient,patient_id)
    if not patient.record: patient.record=MedicalRecord()
    patient.record.notes=request.form.get('notes','').strip()
    patient.allergies=allergies_from_text(request.form.get('allergies',''))
    commit(f'Atualizou prontuário do paciente #{patient.id}')
    return redirect(url_for('patient_detail',patient_id=patient.id))

@app.get('/agenda')
@roles('admin','recepcao','medico')
def agenda():
    query=clinical_scope(select(Appointment)).order_by(Appointment.starts_at.desc())
    if request.args.get('day'): query=query.where(func.date(Appointment.starts_at)==parse_date(request.args['day']))
    if request.args.get('status'): query=query.where(Appointment.status==request.args['status'])
    appointments=db.session.scalars(query).all()
    q=request.args.get('q','').lower().strip()
    if q: appointments=[a for a in appointments if q in (a.patient.name+' '+a.doctor.name).lower()]
    return render_template('agenda.html',title='Agenda de consultas',appointments=appointments)

@app.route('/agenda/novo',methods=['GET','POST'])
@roles('admin','recepcao')
def appointment_new():
    if request.method=='POST':
        obj=schedule(request.form);db.session.flush();commit(f'Agendou atendimento #{obj.id}')
        return redirect(url_for('agenda'))
    return render_template('appointment_form.html',title='Novo agendamento',patients=db.session.scalars(select(Patient).where(Patient.archived_at.is_(None)).order_by(Patient.name)).all(),doctors=db.session.scalars(select(Professional).where(Professional.kind=='Médico')).all(),specialties=db.session.scalars(select(Specialty)).all(),units=db.session.scalars(select(Unit)).all())

@app.post('/agenda/<int:appointment_id>/situacao')
@roles('admin','recepcao')
def appointment_status(appointment_id):
    obj=db.session.scalar(select(Appointment).where(Appointment.id==appointment_id).with_for_update())
    if not obj:abort(404)
    change_appointment(obj,request.form.get('status'))
    commit(f'Alterou agendamento #{obj.id} para {obj.status}')
    return redirect(url_for('agenda'))

@app.route('/agenda/<int:appointment_id>/atender',methods=['GET','POST'])
@roles('admin','medico')
def consultation_new(appointment_id):
    obj=db.get_or_404(Appointment,appointment_id)
    if g.user.role=='medico' and obj.doctor_id!=g.user.professional_id: abort(403)
    if obj.status not in ('Agendado','Confirmado'): raise BusinessError('Agendamento indisponível para atendimento.')
    if request.method=='POST':
        c=attend(obj,request.form);db.session.flush();commit(f'Registrou consulta #{c.id}')
        return redirect(url_for('consultation_detail',consultation_id=c.id))
    return render_template('consultation_form.html',title='Registrar atendimento',appointment=obj)

@app.get('/consultas')
@roles('admin','medico')
def consultation_list():
    rows=db.session.scalars(clinical_scope(select(Consultation).join(Appointment)).order_by(Consultation.attended_at.desc())).all()
    q=request.args.get('q','').lower().strip()
    if q: rows=[c for c in rows if q in (c.patient.name+' '+c.doctor.name).lower()]
    return render_template('consultations.html',title='Consultas e prontuários',rows=rows)

@app.get('/consultas/<int:consultation_id>')
@roles('admin','medico')
def consultation_detail(consultation_id):
    c=allowed_consultation(db.get_or_404(Consultation,consultation_id))
    return render_template('consultation.html',title=f'Consulta #{c.id:04d}',c=c,exams=db.session.scalars(select(Exam)).all(),medications=db.session.scalars(select(Medication)).all(),procedures=db.session.scalars(select(Procedure)).all(),professionals=c.appointment.unit.professionals)

@app.post('/consultas/<int:consultation_id>/<action>')
@roles('admin','medico')
def consultation_action(consultation_id,action):
    c=allowed_consultation(db.get_or_404(Consultation,consultation_id))
    actions={'exame':request_exam,'prescricao':prescribe,'procedimento':perform_procedure}
    if action not in actions: abort(404)
    actions[action](c,request.form);commit(f'Registrou {action} na consulta #{c.id}')
    return redirect(url_for('consultation_detail',consultation_id=c.id))

@app.get('/solicitacoes')
@roles('admin','medico')
def exam_requests():
    query=clinical_scope(select(ExamRequest).join(Consultation).join(Appointment)).order_by(ExamRequest.requested_at.desc())
    if request.args.get('pending'):query=query.where(ExamRequest.status.in_(['Solicitado','Agendado']))
    if request.args.get('patient_id'):query=query.where(Appointment.patient_id==get(Patient,request.args['patient_id']).id)
    return render_template('exam_requests.html',title='Solicitações de exames',rows=db.session.scalars(query).all(),patients=db.session.scalars(select(Patient).order_by(Patient.name)).all())

@app.post('/solicitacoes/<int:request_id>')
@roles('admin','medico')
def exam_update(request_id):
    row=db.get_or_404(ExamRequest,request_id)
    allowed_consultation(row.consultation)
    update_exam(row,request.form);commit(f'Atualizou solicitação de exame #{row.id}')
    return redirect(url_for('exam_requests'))

@app.get('/financeiro')
@roles('admin','financeiro')
def finance():
    rows=db.session.scalars(select(Charge).order_by(Charge.id.desc())).all()
    if request.args.get('pending'):rows=[r for r in rows if r.balance>0]
    q=request.args.get('q','').lower().strip()
    if q:rows=[r for r in rows if q in r.consultation.patient.name.lower()]
    return render_template('finance.html',title='Financeiro',rows=rows,consultations=db.session.scalars(select(Consultation).order_by(Consultation.id.desc())).all(),insurances=db.session.scalars(select(Insurance)).all())

@app.post('/financeiro/cobrancas')
@roles('admin','financeiro')
def charge_new():
    c=get(Consultation,request.form.get('consultation_id'))
    obj=create_charge(c,request.form);db.session.flush();commit(f'Criou cobrança #{obj.id}')
    return redirect(url_for('finance'))

@app.post('/financeiro/<int:charge_id>/pagamento')
@roles('admin','financeiro')
def payment_new(charge_id):
    obj=db.get_or_404(Charge,charge_id)
    pay(obj,request.form);commit(f'Registrou pagamento da cobrança #{obj.id}')
    return redirect(url_for('finance'))

@app.post('/financeiro/pagamentos/<int:payment_id>/situacao')
@roles('admin','financeiro')
def payment_status(payment_id):
    p=db.get_or_404(Payment,payment_id)
    charge=db.session.scalar(select(Charge).where(Charge.id==p.charge_id).with_for_update())
    status=request.form.get('status')
    if p.status!='Pendente' or status not in ('Pago','Cancelado'):raise BusinessError('Somente pagamentos pendentes podem ser liquidados ou cancelados.')
    if status=='Pago':
        remaining=charge.insurance_balance if p.method=='Convênio' else charge.patient_balance
        if p.amount>remaining:raise BusinessError('Este pagamento supera o saldo atual.')
        p.paid_at=today_local()
    p.status=status;commit(f'Alterou pagamento #{p.id} para {status}')
    return redirect(url_for('finance'))

def report_data():
    start=parse_date(request.args.get('start') or today_local().replace(day=1).isoformat())
    end=parse_date(request.args.get('end') or today_local().isoformat())
    if end<start:raise BusinessError('Data final deve ser posterior ou igual à inicial.')
    doctor=request.args.get('doctor_id','');specialty=request.args.get('specialty_id','');unit=request.args.get('unit_id','')
    def match(c):
        a=c.appointment
        return (not doctor or str(a.doctor_id)==doctor) and (not specialty or str(a.specialty_id)==specialty) and (not unit or str(a.unit_id)==unit)
    charges=[c for c in db.session.scalars(select(Charge)).all() if start<=c.created_at<=end and match(c.consultation)]
    payments=[p for p in db.session.scalars(select(Payment).where(Payment.status=='Pago',Payment.paid_at>=start,Payment.paid_at<=end)).all() if match(p.charge.consultation)]
    consults=[c for c in db.session.scalars(select(Consultation)).all() if start<=c.attended_at.date()<=end and match(c)]
    procedures=[p for p in db.session.scalars(select(PerformedProcedure).where(PerformedProcedure.performed_at>=start,PerformedProcedure.performed_at<=end)).all() if match(p.consultation)]
    # Faturamento por competência (cobranças emitidas); recebimentos por caixa (pagamentos pagos).
    groups={key:defaultdict(lambda:dict(billed=Decimal('0'),received=Decimal('0'),count=0)) for key in ('doctor','specialty','unit')}
    for key in groups:
        for c in charges:groups[key][label(getattr(c.consultation.appointment,key))]['billed']+=c.total
        for p in payments:groups[key][label(getattr(p.charge.consultation.appointment,key))]['received']+=p.amount
        for c in consults:groups[key][label(getattr(c.appointment,key))]['count']+=1
    return dict(start=start,end=end,groups=groups,charges=charges,payments=payments,consults=consults,procedures=procedures,
      billed=sum((c.total for c in charges),Decimal('0')),received=sum((p.amount for p in payments),Decimal('0')),
      doctors=db.session.scalars(select(Professional).where(Professional.kind=='Médico')).all(),specialties=db.session.scalars(select(Specialty)).all(),units=db.session.scalars(select(Unit)).all())

@app.get('/relatorios')
@roles('admin','financeiro')
def reports():return render_template('reports.html',title='Relatórios e indicadores',**report_data())

@app.get('/relatorios/exportar')
@roles('admin','financeiro')
def report_export():
    data=report_data();output=io.StringIO();output.write('\ufeff');writer=csv.writer(output,delimiter=';')
    writer.writerow(['Categoria','Nome','Faturamento emitido','Recebimentos','Consultas'])
    for kind,groups in data['groups'].items():
        for name,values in groups.items():writer.writerow([kind,name,str(values['billed']).replace('.',','),str(values['received']).replace('.',','),values['count']])
    return Response(output.getvalue(),mimetype='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename=relatorio-clinica.csv'})

@app.get('/auditoria')
@roles('admin')
def audit_list():return render_template('audit.html',title='Registro de atividades',rows=db.session.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(200)).all())

@app.get('/sobre')
def about():return render_template('about.html',title='Sobre o projeto')

@app.get('/tutorial')
def tutorial():
    return render_template('tutorial.html',title='Guia do sistema')

@app.cli.command('init-db')
def init_db():
    from seed import seed
    db.create_all();upgrade_schema()
    if DEMO_MODE:seed()
    print('Banco inicializado. Dados fictícios carregados.' if DEMO_MODE else 'Estrutura do banco inicializada.')

if __name__=='__main__':
    with app.app_context():
        from seed import seed
        db.create_all();upgrade_schema()
        if DEMO_MODE:seed()
    app.run(host='127.0.0.1',port=5000,debug=False)
