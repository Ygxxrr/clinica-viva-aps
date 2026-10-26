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
    def login(self,email='admin@clinica.demo'):
        self.client.get('/login')
        return self.post('/login',{'email':email,'password':'Clinica2026!'})
    def test_all_pages_render(self):
        urls=['/','/agenda','/agenda/novo','/consultas','/consultas/1','/pacientes/1','/solicitacoes','/financeiro','/relatorios','/relatorios/exportar','/auditoria','/sobre','/health']
        urls += [f'/cadastros/{s}' for s in CATALOGS]
        urls += [f'/cadastros/{s}/novo' for s in CATALOGS]
        for url in urls:
            with self.subTest(url=url): self.assertEqual(self.client.get(url).status_code,200)
    def test_csrf_and_profile_permissions(self):
        self.assertEqual(self.client.post('/logout').status_code,400)
        self.login('recepcao@clinica.demo')
        self.assertEqual(self.client.get('/financeiro').status_code,403)
        self.assertEqual(self.client.get('/consultas').status_code,403)
        self.assertEqual(self.client.get('/pacientes/1').status_code,200)
        self.login('financeiro@clinica.demo')
        self.assertEqual(self.client.get('/pacientes/1').status_code,403)
        self.assertEqual(self.client.get('/agenda').status_code,403)
        self.login('medico@clinica.demo')
        c=db.session.scalar(select(Consultation).join(Appointment).where(Appointment.doctor_id!=1))
        self.assertEqual(self.client.get(f'/consultas/{c.id}').status_code,403)
        self.assertEqual(self.client.get('/cadastros/profissionais/novo').status_code,403)
    def test_patient_record_created_and_duplicate_cpf(self):
        data=dict(name='Paciente Teste',cpf=fake_cpf(777000100),birth_date='1998-01-01',sex='Não informado',phone='0000',email='test@example.com',address='Endereço fictício')
        r=self.post('/cadastros/pacientes/novo',data);self.assertEqual(r.status_code,302)
        p=db.session.scalar(select(Patient).where(Patient.cpf==data['cpf']))
        self.assertIsNotNone(p.record)
        self.assertEqual(self.post('/cadastros/pacientes/novo',data).status_code,409)
        self.assertEqual(Patient.query.filter_by(cpf=data['cpf']).count(),1)
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
