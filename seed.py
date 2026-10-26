"""Dados iniciais do sistema e atualização dos registros carregados por versões anteriores."""
from clock_local import now_local, today_local
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from models import *

def fake_cpf(number):
    digits=f'{number:09d}'
    for n in (9,10):
        check=(sum(int(digits[i])*(n+1-i) for i in range(n))*10)%11
        digits+=str(0 if check==10 else check)
    return digits

def seed():
    if db.session.scalar(select(User.id).limit(1)): return
    specs=[Specialty(name=n,description=d) for n,d in [
      ('Cardiologia','Saúde do coração e do sistema cardiovascular.'),('Dermatologia','Cuidados com a pele.'),
      ('Ortopedia','Sistema musculoesquelético.'),('Pediatria','Saúde da criança e do adolescente.'),
      ('Neurologia','Saúde do sistema nervoso.'),('Clínica Geral','Atenção integral e acompanhamento clínico.')]]
    center=Unit(name='Unidade Centro',address='Rua das Palmeiras, 100 - Centro, São Paulo/SP',phone='(11) 0000-1000',hours='Seg a sex, 08h às 18h',specialties=specs)
    south=Unit(name='Unidade Sul',address='Av. Interlagos, 250 - Santo Amaro, São Paulo/SP',phone='(11) 0000-2000',hours='Seg a sex, 08h às 18h',specialties=[specs[0],specs[3],specs[5]])
    docs=[]
    for i,(n,sp) in enumerate([('Dra. Helena Costa',0),('Dr. Rafael Nunes',5),('Dra. Camila Rocha',3),('Dr. Lucas Almeida',1),('Dra. Beatriz Lima',2),('Dr. André Dias',4)]):
        docs.append(Professional(name=n,cpf=fake_cpf(900000100+i),phone='(11) 0000-3000',email=f'medico{i}@example.com',birth_date=date(1982+i,3,12),
          registration=f'CRM DEMO {1000+i}',kind='Médico',crm=str(1000+i),crm_state='SP',specialties=[specs[sp]],units=[center,south] if sp in (0,3,5) else [center]))
    nurse=Professional(name='Enf. Marina Lopes',cpf=fake_cpf(900000120),phone='(11) 0000-3000',email='enfermagem@example.com',birth_date=date(1990,4,3),registration='COREN DEMO 2000',kind='Enfermeiro',units=[center,south])
    insurers=[Insurance(name='Vida Plena',cnpj='00000000000100',phone='(11) 0000-4000'),Insurance(name='Saúde Integral',cnpj='00000000000200',phone='(11) 0000-5000')]
    allergies=[Allergy(name='Penicilina',description='Reação a antibióticos betalactâmicos.'),Allergy(name='Látex',description='Reação ao contato com borracha natural.'),Allergy(name='Dipirona',description='Reação ao analgésico metamizol.')]
    exams=[Exam(name='Hemograma completo',kind='Laboratorial',description='Análise das células sanguíneas.'),Exam(name='Eletrocardiograma',kind='Cardiológico',description='Registro da atividade elétrica cardíaca.'),Exam(name='Glicemia de jejum',kind='Laboratorial',description='Dosagem de glicose.'),Exam(name='Radiografia',kind='Imagem',description='Exame de imagem.')]
    meds=[Medication(name='Paracetamol 750 mg',active_ingredient='Paracetamol',manufacturer='Genérico',presentation='Comprimido 750 mg'),Medication(name='Loratadina 10 mg',active_ingredient='Loratadina',manufacturer='Genérico',presentation='Comprimido 10 mg')]
    procs=[Procedure(name='Curativo simples',description='Limpeza e proteção de ferimento.',standard_price=Decimal('80')),Procedure(name='Eletrocardiograma em consultório',description='Registro da atividade elétrica do coração.',standard_price=Decimal('150')),Procedure(name='Retirada de pontos',description='Remoção de pontos de sutura.',standard_price=Decimal('100'))]
    names=['Ana Clara Martins','Pedro Henrique Souza','Mariana Oliveira','João Victor Santos','Luiza Fernandes','Gabriel Ribeiro','Sofia Carvalho','Miguel Pereira','Isabela Almeida','Arthur Gomes','Valentina Rocha','Davi Azevedo']
    patients=[]
    today=today_local()
    for i,n in enumerate(names):
        p=Patient(name=n,cpf=fake_cpf(800000100+i),birth_date=date(1985+i,2,10),sex='Feminino' if i%2==0 else 'Masculino',phone=f'(11) 0000-{6000+i}',email=f'paciente{i}@example.com',address=f'Rua das Acácias, {i+1} - Centro, São Paulo/SP',street='Rua das Acácias',number=str(i+1),neighborhood='Centro',city='São Paulo',state='SP',record=MedicalRecord(notes=''))
        if i%4==0: p.allergies=[allergies[i%3]]
        p.insurances=[PatientInsurance(insurance=insurers[i%2],card_number=f'CART-{10000+i}',joined_at=today-timedelta(days=90),status='Ativo')]
        patients.append(p)
    db.session.add_all([center,south,*docs,nurse,*insurers,*allergies,*exams,*meds,*procs,*patients])
    db.session.flush()
    for i in range(18):
        doctor=docs[i%6]; p=patients[i%12]
        when=datetime.combine(today-timedelta(days=18-i),datetime.min.time()).replace(hour=9+i%7,minute=30 if i%2 else 0)
        a=Appointment(patient=p,doctor=doctor,specialty=doctor.specialties[0],unit=center,starts_at=when,status='Realizado',notes='')
        c=Consultation(appointment=a,attended_at=when,complaint='Acompanhamento de rotina.',diagnosis='Quadro clínico estável.',conduct='Retorno de acompanhamento.',notes='Paciente sem queixas adicionais.')
        db.session.add(c)
        e=ExamRequest(consultation=c,exam=exams[i%4],requested_at=when.date(),status='Realizado' if i%3==0 else 'Solicitado',performed_at=when.date() if i%3==0 else None,result='Dentro dos valores de referência.' if i%3==0 else '')
        db.session.add(e)
        total=Decimal('250')+Decimal(i%4*50)
        charge=Charge(consultation=c,description='Consulta médica',total=total,covered=total*Decimal('0.6') if i%2==0 else Decimal('0'),insurance=insurers[i%2] if i%2==0 else None,due_date=when.date()+timedelta(days=10),created_at=when.date())
        db.session.add(charge)
        if i%3!=0:
            if charge.covered: db.session.add(Payment(charge=charge,amount=charge.covered,paid_at=when.date(),method='Convênio',status='Pago'))
            db.session.add(Payment(charge=charge,amount=total-charge.covered,paid_at=when.date(),method='PIX' if i%2 else 'Cartão de crédito',status='Pago'))
        if i%4==0:
            db.session.add(Prescription(consultation=c,created_at=when.date(),notes='Uso conforme orientação médica.',items=[PrescriptionItem(medication=meds[0],quantity=1,dose='1 comprimido',frequency='A cada 8 horas, se dor',duration='5 dias',notes='')]))
            db.session.add(PerformedProcedure(consultation=c,procedure=procs[0],professional=nurse,performed_at=when.date(),charged_price=Decimal('70')))
    for i in range(8):
        doctor=docs[i%6]
        db.session.add(Appointment(patient=patients[i],doctor=doctor,specialty=doctor.specialties[0],unit=center,starts_at=datetime.combine(today,datetime.min.time()).replace(hour=9+i),status='Confirmado' if i%2==0 else 'Agendado',notes=''))
    db.session.add(Appointment(patient=patients[10],doctor=docs[0],specialty=specs[0],unit=center,starts_at=datetime.combine(today-timedelta(days=2),datetime.min.time()).replace(hour=16),status='Não compareceu'))
    for role,name,email,professional in [('admin','Administrador','admin@clinicasilva.com.br',None),('recepcao','Recepção','recepcao@clinicasilva.com.br',None),('medico','Dra. Helena Costa','medico@clinicasilva.com.br',docs[0]),('financeiro','Financeiro','financeiro@clinicasilva.com.br',None)]:
        user=User(name=name,email=email,role=role,professional=professional)
        user.set_password('Clinica2026!')
        db.session.add(user)
    db.session.commit()

# Textos carregados por versões anteriores do sistema → valores atuais (executado na inicialização; idempotente).
OLD_TEXT = {
    (Unit,'address'): {'Rua Exemplo, 100 • Centro (fictício)':'Rua das Palmeiras, 100 - Centro, São Paulo/SP','Av. Demonstração, 250 (fictício)':'Av. Interlagos, 250 - Santo Amaro, São Paulo/SP'},
    (Insurance,'name'): {'Vida Plena (demonstração)':'Vida Plena','Saúde Integral (demonstração)':'Saúde Integral'},
    (Medication,'name'): {'Medicamento demonstrativo A':'Paracetamol 750 mg','Medicamento demonstrativo B':'Loratadina 10 mg'},
    (Medication,'active_ingredient'): {'Substância fictícia A':'Paracetamol','Substância fictícia B':'Loratadina'},
    (Medication,'manufacturer'): {'Laboratório Exemplo':'Genérico'},
    (Medication,'presentation'): {'Comprimidos • demonstração':'Comprimido 750 mg','Solução • demonstração':'Comprimido 10 mg'},
    (MedicalRecord,'notes'): {'Prontuário de demonstração, sem informações reais.':''},
    (Patient,'reference'): {'Dados de demonstração':None},
    (Appointment,'notes'): {'Agendamento de demonstração.':'','Atendimento fictício para demonstração.':''},
    (Consultation,'complaint'): {'Acompanhamento de rotina (caso fictício).':'Acompanhamento de rotina.'},
    (Consultation,'diagnosis'): {'Avaliação demonstrativa, sem validade clínica.':'Quadro clínico estável.'},
    (Consultation,'notes'): {'Dados sintéticos para fins acadêmicos.':'Paciente sem queixas adicionais.'},
    (ExamRequest,'result'): {'Resultado fictício sem validade clínica.':'Dentro dos valores de referência.'},
    (Prescription,'notes'): {'Exemplo didático. Sem validade médica.':'Uso conforme orientação médica.'},
    (PrescriptionItem,'dose'): {'Dose demonstrativa':'1 comprimido'},
    (PrescriptionItem,'frequency'): {'Frequência demonstrativa':'A cada 8 horas, se dor'},
    (PrescriptionItem,'duration'): {'Duração demonstrativa':'5 dias'},
    (PrescriptionItem,'notes'): {'Não utilizar como orientação de tratamento.':''},
    (User,'email'): {f'{r}@clinica.demo':f'{r}@clinicasilva.com.br' for r in ('admin','recepcao','medico','financeiro')},
}

def refresh_sample_data():
    from sqlalchemy import update, inspect
    if not inspect(db.engine).has_table('appointment'): return
    changed = False
    for (model, column), mapping in OLD_TEXT.items():
        for old, new in mapping.items():
            result = db.session.execute(update(model).where(getattr(model, column) == old).values({column: new}))
            changed = changed or result.rowcount > 0
    descriptions = {'Penicilina':'Reação a antibióticos betalactâmicos.','Látex':'Reação ao contato com borracha natural.','Dipirona':'Reação ao analgésico metamizol.'}
    for allergy in db.session.scalars(select(Allergy).where(Allergy.description == 'Alergia de demonstração.')):
        allergy.description = descriptions.get(allergy.name, ''); changed = True
    for procedure in db.session.scalars(select(Procedure).where(Procedure.description == 'Procedimento demonstrativo.')):
        procedure.description = {'Curativo simples':'Limpeza e proteção de ferimento.','Eletrocardiograma em consultório':'Registro da atividade elétrica do coração.','Retirada de pontos':'Remoção de pontos de sutura.'}.get(procedure.name, ''); changed = True
    for link in db.session.scalars(select(PatientInsurance).where(PatientInsurance.card_number.like('DEMO-%'))):
        link.card_number = 'CART-' + link.card_number[5:]; changed = True
    for p in db.session.scalars(select(Patient).where(db.or_(Patient.address.like('Rua Fictícia, %'), Patient.street == 'Rua Fictícia'))):
        number = (p.number or p.address.split(',')[1].split()[0]).strip()
        p.street, p.number, p.neighborhood, p.city, p.state = 'Rua das Acácias', number, p.neighborhood or 'Centro', p.city or 'São Paulo', p.state or 'SP'
        p.address = f'Rua das Acácias, {number} - {p.neighborhood}, {p.city}/{p.state}'; changed = True
    if changed: db.session.commit()
