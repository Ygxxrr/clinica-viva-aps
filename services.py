"""Validações e operações do domínio, independentes dos templates HTML."""
from clock_local import now_local, today_local
import re
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
from sqlalchemy import select
from models import *

class BusinessError(ValueError): pass

def required(data, key, label=None):
    value = str(data.get(key, '')).strip()
    if not value: raise BusinessError(f'Informe {label or key}.')
    return value

def money(value):
    try:
        result = Decimal(str(value).replace(',','.')).quantize(Decimal('0.01'))
        if not result.is_finite() or result < 0: raise InvalidOperation
        return result
    except (InvalidOperation, ValueError): raise BusinessError('Informe um valor monetário válido e não negativo.')

def get(model, value):
    try: obj = db.session.get(model, int(value))
    except (TypeError, ValueError): obj = None
    if obj is None: raise BusinessError(f'Registro de {model.__name__} não encontrado.')
    return obj

def cpf_digits(value):
    digits = re.sub(r'\D', '', value)
    if len(digits) != 11 or len(set(digits)) == 1: raise BusinessError('CPF inválido: confira os 11 dígitos.')
    for n in (9, 10):
        check = (sum(int(digits[i]) * (n+1-i) for i in range(n)) * 10) % 11
        if (0 if check == 10 else check) != int(digits[n]): raise BusinessError('CPF inválido: dígitos verificadores não conferem.')
    return digits

def format_cpf(digits):
    digits = re.sub(r'\D', '', digits or '')
    return f'{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}' if len(digits) == 11 else digits

def phone_number(value):
    digits = re.sub(r'\D', '', value)
    if re.search(r'[^\d\s()+-]', value) or len(digits) not in (10, 11):
        raise BusinessError('Telefone inválido: use DDD + número, com 10 dígitos (fixo) ou 11 dígitos (celular).')
    if digits[0] == '0' or digits[1] == '0': raise BusinessError('Telefone inválido: DDD não pode começar ou terminar com 0.')
    if len(digits) == 11 and digits[2] != '9': raise BusinessError('Celular inválido: depois do DDD o número deve começar com 9.')
    return f'({digits[:2]}) {digits[2:-4]}-{digits[-4:]}'

def address_number(value):
    value = value.upper().replace(' ', '')
    if value in ('SN', 'S/N'): return 'S/N'
    if not re.fullmatch(r'\d{1,6}', value): raise BusinessError('Número do endereço deve conter apenas dígitos (ou S/N).')
    return value

def allergies_from_text(text):
    """Converte o texto livre ('Látex, amendoim') em alergias do catálogo, criando as que ainda não existem."""
    result, seen = [], set()
    for raw in re.split(r'[,;\n]', str(text or '')):
        name = ' '.join(raw.split())
        if not name or name.casefold() in seen: continue
        if len(name) > 120: raise BusinessError('Nome de alergia excede 120 caracteres.')
        seen.add(name.casefold())
        allergy = next((a for a in db.session.scalars(select(Allergy)) if a.name.casefold() == name.casefold()), None)
        if allergy is None:
            allergy = Allergy(name=name[0].upper() + name[1:], description='')
            db.session.add(allergy)
        result.append(allergy)
    return result

def compose_address(p):
    line = f'{p.street}, {p.number}' + (f' - {p.complement}' if p.complement else '')
    return f'{line} - {p.neighborhood}, {p.city}/{p.state}'[:240]

def parse_date(value):
    try: return date.fromisoformat(str(value))
    except ValueError: raise BusinessError('Informe uma data válida.')

def parse_datetime(value):
    try: return datetime.fromisoformat(str(value))
    except ValueError: raise BusinessError('Informe data e horário válidos.')

def save_catalog(meta, data, obj=None):
    obj = obj or meta['model']()
    for f in meta['fields']:
        key, kind = f['key'], f['kind']
        if kind == 'heading': continue
        if kind == 'allergies':
            setattr(obj, key, allergies_from_text(data.get(key, '')))
            continue
        if kind == 'multi':
            ids = data.getlist(key)
            if f['required'] and not ids: raise BusinessError(f'Selecione {f["label"]}.')
            setattr(obj,key,[get(f['model'], i) for i in dict.fromkeys(ids)])
            continue
        value = required(data,key,f['label']) if f['required'] else str(data.get(key,'')).strip()
        if key == 'cpf': value = cpf_digits(value)
        if key == 'phone': value = phone_number(value)
        if key == 'number' and isinstance(obj, Patient): value = address_number(value)
        if key == 'cnpj':
            value = re.sub(r'\D','',value)
            if len(value) != 14: raise BusinessError('CNPJ deve conter 14 dígitos.')
        if kind == 'date': value = parse_date(value)
        if key == 'birth_date' and value > today_local(): raise BusinessError('Nascimento não pode estar no futuro.')
        if kind == 'money': value = money(value)
        if kind == 'select' and value not in [c[0] if isinstance(c, tuple) else c for c in f['choices']]: raise BusinessError('Opção inválida.')
        if kind == 'relation': value = get(f['model'],value).id
        if kind == 'email' and value and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',value): raise BusinessError('E-mail inválido.')
        if key == 'crm_state': value = value.upper()
        if key in obj.__table__.columns and isinstance(value,str):
            length = getattr(obj.__table__.columns[key].type,'length',None)
            if length and len(value)>length: raise BusinessError(f'{f["label"]} excede {length} caracteres.')
        setattr(obj,key,value or None if key in ('crm','crm_state','complement','reference') else value)
    if isinstance(obj,Patient): obj.address = compose_address(obj)
    if isinstance(obj,Professional):
        if obj.kind == 'Médico' and (not obj.crm or len(obj.crm_state or '') != 2 or not obj.specialties):
            raise BusinessError('Médico precisa de CRM, UF e pelo menos uma especialidade.')
        if obj.kind != 'Médico' and obj.specialties: raise BusinessError('Especialidades médicas devem ser vinculadas a médicos.')
    db.session.add(obj)
    if isinstance(obj,Patient) and obj.record is None: obj.record = MedicalRecord(notes='')
    return obj

def schedule(data, obj=None):
    patient = get(Patient,data.get('patient_id'))
    doctor = get(Professional,data.get('doctor_id'))
    specialty = get(Specialty,data.get('specialty_id'))
    unit = get(Unit,data.get('unit_id'))
    starts = parse_datetime(required(data,'starts_at','data e horário'))
    if patient.archived_at: raise BusinessError('Paciente arquivado não pode receber novos agendamentos. Restaure o cadastro antes.')
    if doctor.kind != 'Médico': raise BusinessError('O atendimento deve ser agendado com um médico.')
    if specialty not in doctor.specialties: raise BusinessError('O médico não atende a especialidade selecionada.')
    if unit not in doctor.units: raise BusinessError('O médico não atende na unidade selecionada.')
    if specialty not in unit.specialties: raise BusinessError('A unidade não oferece esta especialidade.')
    if starts.minute not in (0,30) or starts.second: raise BusinessError('Use horários de 30 em 30 minutos.')
    conflict = select(Appointment).where(Appointment.status.in_(['Agendado','Confirmado','Realizado']),
        Appointment.starts_at > starts-timedelta(minutes=30), Appointment.starts_at < starts+timedelta(minutes=30),
        db.or_(Appointment.doctor_id==doctor.id,Appointment.patient_id==patient.id))
    if obj: conflict = conflict.where(Appointment.id != obj.id)
    if db.session.scalar(conflict): raise BusinessError('Já existe atendimento para este médico ou paciente neste horário.')
    obj = obj or Appointment()
    obj.patient, obj.doctor, obj.specialty, obj.unit = patient,doctor,specialty,unit
    obj.starts_at, obj.notes = starts,str(data.get('notes','')).strip()
    if not obj.status: obj.status='Agendado'
    db.session.add(obj)
    return obj

def remove_patient(patient):
    """Sem histórico: exclui de vez. Com agendamentos/consultas: arquiva e cancela os horários futuros."""
    if patient.appointments:
        patient.archived_at = now_local()
        for a in patient.appointments:
            if a.status in ('Agendado','Confirmado') and a.starts_at >= now_local(): a.status = 'Cancelado'
        return 'arquivado'
    for link in list(patient.insurances): db.session.delete(link)
    patient.allergies = []
    db.session.delete(patient)
    return 'excluído'

def change_appointment(obj, status):
    allowed = {'Agendado':{'Confirmado','Cancelado','Não compareceu'}, 'Confirmado':{'Cancelado','Não compareceu'}}
    if status not in allowed.get(obj.status,set()): raise BusinessError('Transição de situação não permitida.')
    obj.status=status

def attend(appointment, data):
    # Serializa atendimento/status concorrentes no PostgreSQL.
    appointment = db.session.scalar(select(Appointment).where(Appointment.id==appointment.id).with_for_update())
    if appointment.status not in ('Agendado','Confirmado') or appointment.consultation:
        raise BusinessError('Somente agendamento ativo e ainda não atendido pode gerar consulta.')
    consultation = Consultation(appointment=appointment, complaint=required(data,'complaint','queixa principal'),
        diagnosis=required(data,'diagnosis','diagnóstico'), conduct=required(data,'conduct','conduta'),
        notes=str(data.get('notes','')).strip(),attended_at=now_local())
    appointment.status='Realizado'
    db.session.add(consultation)
    return consultation

def request_exam(consultation,data):
    row=ExamRequest(consultation=consultation,exam=get(Exam,data.get('exam_id')),status='Solicitado',requested_at=today_local())
    db.session.add(row)
    return row

def update_exam(row,data):
    status=required(data,'status')
    transitions={'Solicitado':{'Solicitado','Agendado','Realizado','Cancelado'},'Agendado':{'Agendado','Realizado','Cancelado'},'Realizado':{'Realizado'},'Cancelado':{'Cancelado'}}
    if status not in transitions.get(row.status,set()): raise BusinessError('Transição de exame inválida.')
    if status=='Realizado':
        performed=parse_date(required(data,'performed_at','data de realização'))
        if performed < row.requested_at or performed > today_local(): raise BusinessError('A realização deve ocorrer entre a solicitação e hoje.')
        row.performed_at=performed
        row.result=required(data,'result','resultado')
    row.status=status

def prescribe(consultation,data):
    items=[]
    for i in range(8):
        if not data.get(f'medication_{i}'): continue
        med=get(Medication,data[f'medication_{i}'])
        try: quantity=int(data.get(f'quantity_{i}',0))
        except ValueError: raise BusinessError('Quantidade inválida.')
        if quantity<=0: raise BusinessError('Quantidade precisa ser maior que zero.')
        items.append(PrescriptionItem(medication=med,quantity=quantity,
          dose=required(data,f'dose_{i}','dose'),frequency=required(data,f'frequency_{i}','frequência'),
          duration=required(data,f'duration_{i}','duração'),notes=str(data.get(f'item_notes_{i}','')).strip()))
    if not items: raise BusinessError('Inclua pelo menos um medicamento na prescrição.')
    row=Prescription(consultation=consultation,notes=str(data.get('notes','')).strip(),items=items)
    db.session.add(row)
    return row

def perform_procedure(consultation,data):
    professional=get(Professional,data.get('professional_id'))
    if consultation.appointment.unit not in professional.units: raise BusinessError('Profissional não está vinculado à unidade da consulta.')
    performed=parse_date(required(data,'performed_at','data'))
    if performed < consultation.attended_at.date() or performed > today_local(): raise BusinessError('Data do procedimento deve estar entre a consulta e hoje.')
    row=PerformedProcedure(consultation=consultation,procedure=get(Procedure,data.get('procedure_id')),
        professional=professional,charged_price=money(required(data,'charged_price','valor cobrado')),performed_at=performed)
    db.session.add(row)
    return row

def create_charge(consultation,data):
    total=money(required(data,'total','valor total'))
    covered=money(data.get('covered') or '0')
    if total<=0 or covered>total: raise BusinessError('Total deve ser positivo e cobertura não pode superar o total.')
    insurance=get(Insurance,data.get('insurance_id')) if data.get('insurance_id') else None
    if covered>0 and insurance is None: raise BusinessError('Informe o convênio responsável pela cobertura.')
    if insurance:
        active=db.session.scalar(select(PatientInsurance).where(PatientInsurance.patient_id==consultation.patient.id,
            PatientInsurance.insurance_id==insurance.id,PatientInsurance.status=='Ativo',PatientInsurance.joined_at<=today_local()))
        if not active: raise BusinessError('Paciente não possui vínculo ativo com este convênio.')
    row=Charge(consultation=consultation,description=required(data,'description','descrição'),total=total,covered=covered,
        insurance=insurance,due_date=parse_date(required(data,'due_date','vencimento')))
    db.session.add(row)
    return row

def pay(charge,data):
    charge=db.session.scalar(select(Charge).where(Charge.id==charge.id).with_for_update())
    amount=money(required(data,'amount','valor'))
    method=required(data,'method','forma de pagamento')
    status=required(data,'status','situação')
    if method not in ('Dinheiro','Cartão de crédito','Cartão de débito','PIX','Convênio'): raise BusinessError('Forma de pagamento inválida.')
    if status not in ('Pago','Pendente','Cancelado'): raise BusinessError('Situação de pagamento inválida.')
    remaining=charge.insurance_balance if method=='Convênio' else charge.patient_balance
    if amount<=0 or amount>remaining: raise BusinessError(f'Valor excede o saldo desta parte da cobrança ({remaining:.2f}) ou não é positivo.')
    paid_at=parse_date(required(data,'paid_at','data'))
    if status=='Pago' and paid_at>today_local(): raise BusinessError('Pagamento realizado não pode ter data futura.')
    row=Payment(charge=charge,amount=amount,method=method,status=status,paid_at=paid_at)
    db.session.add(row)
    return row
