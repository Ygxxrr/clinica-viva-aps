"""Testes de integração das regras essenciais e das telas HTTP."""
import os
os.environ['DATABASE_URL']='sqlite://'
os.environ['SECRET_KEY']='integration-test-only'
import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal
from werkzeug.datastructures import MultiDict
from sqlalchemy import select
from app import app, db
from models import *
from services import *
from catalog import CATALOGS
from seed import seed, fake_cpf

class SystemTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING']=True
        self.ctx=app.app_context();self.ctx.push();db.create_all();seed()
        self.client=app.test_client()
        self.login()
    def tearDown(self):
        db.session.remove();db.drop_all();self.ctx.pop()
    def token(self):
        with self.client.session_transaction() as s:return s['csrf']
    def post(self,url,data=None,**kwargs):
        return self.client.post(url,data={'csrf':self.token(),**(data or {})},**kwargs)
    def login(self,email='admin@clinicasilva.com.br'):
        with self.client.session_transaction() as current:
            signed_in=bool(current.get('user_id'))
            token=current.get('csrf')
        if signed_in:self.client.post('/logout',data={'csrf':token})
        self.client.get('/login')
        return self.post('/login',{'email':email,'password':'Clinica2026!'})
    def test_all_pages_render(self):
        urls=['/','/agenda','/agenda/novo','/consultas','/consultas/1','/pacientes/1','/solicitacoes','/financeiro','/relatorios','/relatorios/exportar','/auditoria','/sobre','/tutorial','/health']
        urls += [f'/cadastros/{s}' for s in CATALOGS]
        urls += [f'/cadastros/{s}/novo' for s in CATALOGS]
        for url in urls:
            with self.subTest(url=url): self.assertEqual(self.client.get(url).status_code,200)
    def test_csrf_and_profile_permissions(self):
        self.assertEqual(self.client.post('/logout').status_code,400)
        self.login('recepcao@clinicasilva.com.br')
        self.assertEqual(self.client.get('/financeiro').status_code,403)
        self.assertEqual(self.client.get('/consultas').status_code,403)
        self.assertEqual(self.client.get('/pacientes/1').status_code,200)
        self.login('financeiro@clinicasilva.com.br')
        self.assertEqual(self.client.get('/pacientes/1').status_code,403)
        self.assertEqual(self.client.get('/agenda').status_code,403)
        self.login('medico@clinicasilva.com.br')
        c=db.session.scalar(select(Consultation).join(Appointment).where(Appointment.doctor_id!=1))
        self.assertEqual(self.client.get(f'/consultas/{c.id}').status_code,403)
        self.assertEqual(self.client.get('/cadastros/profissionais/novo').status_code,403)
    def test_dashboard_date_selection_preserves_medical_scope(self):
        self.login('medico@clinicasilva.com.br')
        user=db.session.scalar(select(User).where(User.email=='medico@clinicasilva.com.br'))
        own=db.session.scalar(select(Appointment).where(Appointment.doctor_id==user.professional_id,Appointment.status=='Confirmado'))
        foreign=db.session.scalar(select(Appointment).where(Appointment.doctor_id!=user.professional_id))
        response=self.client.get(f'/?day={own.starts_at.date()}&appointment_id={own.id}')
        self.assertEqual(response.status_code,200)
        self.assertIn(f'data-selected-appointment="{own.id}"',response.get_data(as_text=True))
        response=self.client.get(f'/?day={own.starts_at.date()}&appointment_id={foreign.id}')
        self.assertNotIn(f'data-selected-appointment="{foreign.id}"',response.get_data(as_text=True))
        self.assertEqual(self.client.get('/?day=not-a-date').status_code,422)
    def test_patient_record_created_and_duplicate_cpf(self):
        data=dict(name='Paciente Teste',cpf=fake_cpf(777000100),birth_date='1998-01-01',sex='Não informado',phone='(11) 91234-5678',email='test@example.com',
          street='Rua Teste',number='10',neighborhood='Centro',city='São Paulo',state='SP',allergies='látex, Amendoim')
        r=self.post('/cadastros/pacientes/novo',data);self.assertEqual(r.status_code,302)
        p=db.session.scalar(select(Patient).where(Patient.cpf==data['cpf']))
        self.assertIsNotNone(p.record)
        self.assertEqual(self.post('/cadastros/pacientes/novo',data).status_code,409)
        self.assertEqual(Patient.query.filter_by(cpf=data['cpf']).count(),1)
    def test_patient_fields_validation(self):
        base=dict(name='Paciente Validação',cpf=fake_cpf(777000200),birth_date='1990-05-05',sex='Feminino',phone='(11) 3234-5678',
          email='ok@example.com',street='Av. Teste',number='S/N',complement='Apto 3',neighborhood='Jardim',city='Campinas',state='SP',reference='Perto da praça',allergies='Látex; poeira, Poeira')
        self.assertEqual(self.post('/cadastros/pacientes/novo',base).status_code,302)
        p=db.session.scalar(select(Patient).where(Patient.cpf==base['cpf']))
        self.assertEqual(p.phone,'(11) 3234-5678')
        self.assertEqual(p.address,'Av. Teste, S/N - Apto 3 - Jardim, Campinas/SP')
        self.assertEqual(sorted(a.name for a in p.allergies),['Látex','Poeira'])
        self.assertEqual(Allergy.query.filter(Allergy.name=='Látex').count(),1)
        for key,bad in [('cpf','123abc'),('cpf',fake_cpf(777000300)+'9'),('phone','11abc12345'),('phone','119123'),('phone','(11) 81234-5678'),
                        ('email','semarroba.com'),('number','12a'),('state','XX'),('street','')]:
            with self.subTest(key=key,value=bad):
                data={**base,'cpf':fake_cpf(777000400),key:bad}
                self.assertEqual(self.post('/cadastros/pacientes/novo',data).status_code,422)
        page=self.client.get(f'/cadastros/pacientes/{p.id}/editar').get_data(as_text=True)
        self.assertIn(format_cpf(p.cpf),page);self.assertIn('Látex, Poeira',page)
    def test_record_allergies_free_text(self):
        p=db.session.get(Patient,1)
        self.post(f'/pacientes/{p.id}/prontuario',{'notes':'x','allergies':'Ibuprofeno, dipirona'})
        db.session.refresh(p)
        self.assertEqual(sorted(a.name for a in p.allergies),['Dipirona','Ibuprofeno'])
    def test_patient_delete_and_archive(self):
        self.login('recepcao@clinicasilva.com.br')
        data=dict(name='Paciente Sem Histórico',cpf=fake_cpf(777000500),birth_date='1990-01-01',sex='Masculino',phone='(11) 3234-5678',
          street='Rua A',number='1',neighborhood='Centro',city='São Paulo',state='SP',allergies='Látex')
        self.post('/cadastros/pacientes/novo',data)
        fresh=db.session.scalar(select(Patient).where(Patient.cpf==data['cpf']))
        self.assertEqual(self.post(f'/pacientes/{fresh.id}/excluir').status_code,302)
        db.session.expire_all()
        self.assertIsNone(db.session.get(Patient,fresh.id))
        self.assertEqual(Allergy.query.filter_by(name='Látex').count(),1)
        busy=db.session.scalar(select(Patient).join(Appointment).where(Appointment.status.in_(['Agendado','Confirmado'])))
        future=[a.id for a in busy.appointments if a.status in ('Agendado','Confirmado') and a.starts_at>=datetime.now()]
        consultations=Consultation.query.count()
        self.post(f'/pacientes/{busy.id}/excluir')
        db.session.expire_all();busy=db.session.get(Patient,busy.id)
        self.assertIsNotNone(busy.archived_at)
        self.assertEqual(Consultation.query.count(),consultations)
        for a_id in future: self.assertEqual(db.session.get(Appointment,a_id).status,'Cancelado')
        self.assertNotIn(f'<strong>{busy.name}</strong>',self.client.get('/cadastros/pacientes').get_data(as_text=True))
        self.assertIn(f'<strong>{busy.name}</strong>',self.client.get('/cadastros/pacientes?arquivados=1').get_data(as_text=True))
        self.assertNotIn(f'>{busy.name}<',self.client.get('/agenda/novo').get_data(as_text=True))
        self.assertEqual(self.client.get(f'/pacientes/{busy.id}').status_code,200)
        self.post(f'/pacientes/{busy.id}/restaurar')
        db.session.expire_all();self.assertIsNone(db.session.get(Patient,busy.id).archived_at)
        self.login('medico@clinicasilva.com.br')
        self.assertEqual(self.post(f'/pacientes/{busy.id}/excluir').status_code,403)
    def test_invalid_cpf(self):
        with self.assertRaises(BusinessError):cpf_digits('11111111111')
        with self.assertRaises(BusinessError):cpf_digits('12345678900')
    def future_slot(self):return (datetime.now()+timedelta(days=3)).replace(hour=10,minute=0,second=0,microsecond=0)
    def appointment_data(self):return dict(patient_id=2,doctor_id=1,specialty_id=1,unit_id=1,starts_at=self.future_slot().isoformat())
    def test_schedule_conflicts_and_doctor_specialty_unit(self):
        data=self.appointment_data();schedule(data);db.session.commit()
        with self.assertRaises(BusinessError):schedule(data)
        data={**data,'specialty_id':2}
        with self.assertRaises(BusinessError):schedule(data)
        data={**self.appointment_data(),'doctor_id':4,'unit_id':2,'specialty_id':2}
        with self.assertRaises(BusinessError):schedule(data)
    def test_canceled_appointment_cannot_generate_consultation(self):
        a=schedule(self.appointment_data());db.session.flush();change_appointment(a,'Cancelado');db.session.commit()
        self.assertEqual(self.post(f'/agenda/{a.id}/atender',dict(complaint='Teste',diagnosis='Teste',conduct='Teste')).status_code,422)
        self.assertIsNone(a.consultation)
    def test_end_to_end_consultation_exams_prescription_procedure_payment(self):
        data=self.appointment_data();r=self.post('/agenda/novo',data);self.assertEqual(r.status_code,302)
        a=db.session.scalar(select(Appointment).where(Appointment.starts_at==self.future_slot()))
        self.assertEqual(self.post(f'/agenda/{a.id}/atender',dict(complaint='Caso fictício',diagnosis='Avaliação fictícia',conduct='Retorno')).status_code,302)
        db.session.expire_all();c=a.consultation;self.assertEqual(a.status,'Realizado')
        self.assertEqual(self.post(f'/consultas/{c.id}/exame',dict(exam_id=1)).status_code,302)
        e=c.exam_requests[0]
        self.assertEqual(self.post(f'/solicitacoes/{e.id}',dict(status='Realizado',performed_at=date.today().isoformat(),result='Resultado fictício')).status_code,302)
        self.assertEqual(self.post(f'/consultas/{c.id}/prescricao',dict(medication_0=1,quantity_0=2,dose_0='Teste',frequency_0='Teste',duration_0='Teste',medication_1=2,quantity_1=1,dose_1='Teste',frequency_1='Teste',duration_1='Teste')).status_code,302)
        self.assertEqual(len(c.prescriptions[0].items),2)
        self.assertEqual(self.post(f'/consultas/{c.id}/procedimento',dict(procedure_id=1,professional_id=7,performed_at=date.today().isoformat(),charged_price='65')).status_code,302)
        self.assertEqual(c.procedures[0].charged_price,Decimal('65'))
        insurance_id=c.patient.insurances[0].insurance_id
        self.assertEqual(self.post('/financeiro/cobrancas',dict(consultation_id=c.id,description='Teste',total='100',covered='60',insurance_id=insurance_id,due_date=date.today().isoformat())).status_code,302)
        charge=c.charges[0]
        self.assertEqual(self.post(f'/financeiro/{charge.id}/pagamento',dict(amount='40',method='PIX',status='Pago',paid_at=date.today().isoformat())).status_code,302)
        self.assertEqual(self.post(f'/financeiro/{charge.id}/pagamento',dict(amount='60',method='Convênio',status='Pago',paid_at=date.today().isoformat())).status_code,302)
        db.session.expire_all();self.assertEqual(charge.balance,0)
        self.assertEqual(self.post(f'/financeiro/{charge.id}/pagamento',dict(amount='1',method='PIX',status='Pago',paid_at=date.today().isoformat())).status_code,422)
    def test_money_and_exam_rules(self):
        for value in ('nan','inf','-1','abc'):
            with self.assertRaises(BusinessError):money(value)
        c=db.session.get(Consultation,1)
        with self.assertRaises(BusinessError):create_charge(c,dict(total='100',covered='101',description='teste',due_date=date.today().isoformat()))
        with self.assertRaises(BusinessError):create_charge(c,dict(total='100',covered='60',insurance_id=2,description='teste',due_date=date.today().isoformat()))
        e=ExamRequest(consultation=c,exam_id=1,requested_at=date.today(),status='Solicitado')
        with self.assertRaises(BusinessError):update_exam(e,dict(status='Realizado',performed_at=date.today().isoformat(),result=''))
    def test_pending_payments_do_not_count_as_received(self):
        charge=db.session.scalar(select(Charge).where(Charge.id==1))
        before=charge.paid
        pay(charge,dict(amount='10',method='PIX',status='Pendente',paid_at=date.today().isoformat()));db.session.commit()
        self.assertEqual(charge.paid,before)
        p=charge.payments[-1]
        self.assertEqual(self.post(f'/financeiro/pagamentos/{p.id}/situacao',dict(status='Pago')).status_code,302)
        db.session.expire_all();self.assertEqual(charge.paid,before+Decimal('10'))
    def test_reports_dates_and_escaping(self):
        self.assertEqual(self.client.get('/relatorios?start=2026-10-20&end=2026-10-01').status_code,422)
        p=db.session.get(Patient,1);p.name='<script>alert(1)</script>';db.session.commit()
        body=self.client.get('/cadastros/pacientes').get_data(as_text=True)
        self.assertNotIn('<script>alert(1)</script>',body)
        self.assertIn('&lt;script&gt;',body)

if __name__=='__main__':unittest.main(verbosity=2)
