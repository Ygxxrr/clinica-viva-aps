"""Modelo de domínio: classes Python mapeadas para tabelas relacionais."""
from clock_local import now_local, today_local
from datetime import date, datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

doctor_specialty = db.Table('doctor_specialty',
    db.Column('doctor_id', db.ForeignKey('professional.id'), primary_key=True),
    db.Column('specialty_id', db.ForeignKey('specialty.id'), primary_key=True))
professional_unit = db.Table('professional_unit',
    db.Column('professional_id', db.ForeignKey('professional.id'), primary_key=True),
    db.Column('unit_id', db.ForeignKey('unit.id'), primary_key=True))
unit_specialty = db.Table('unit_specialty',
    db.Column('unit_id', db.ForeignKey('unit.id'), primary_key=True),
    db.Column('specialty_id', db.ForeignKey('specialty.id'), primary_key=True))
patient_allergy = db.Table('patient_allergy',
    db.Column('patient_id', db.ForeignKey('patient.id'), primary_key=True),
    db.Column('allergy_id', db.ForeignKey('allergy.id'), primary_key=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='recepcao')
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'))
    professional = db.relationship('Professional')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def verify_password(self, password): return check_password_hash(self.password_hash, password)

class Specialty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, default='')

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(240), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    hours = db.Column(db.String(120), nullable=False)
    specialties = db.relationship('Specialty', secondary=unit_specialty, backref='units')

class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    registration = db.Column(db.String(60), nullable=False)
    kind = db.Column(db.String(30), nullable=False, default='Médico')
    crm = db.Column(db.String(30))
    crm_state = db.Column(db.String(2))
    specialties = db.relationship('Specialty', secondary=doctor_specialty, backref='doctors')
    units = db.relationship('Unit', secondary=professional_unit, backref='professionals')

class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)

class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, default='')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    name = db.Column(db.String(140), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(160), default='')
    address = db.Column(db.String(240), nullable=False)  # endereço completo montado a partir das partes abaixo
    street = db.Column(db.String(160))
    number = db.Column(db.String(10))
    complement = db.Column(db.String(80))
    neighborhood = db.Column(db.String(80))
    city = db.Column(db.String(80))
    state = db.Column(db.String(2))
    reference = db.Column(db.String(160))
    archived_at = db.Column(db.DateTime)  # paciente arquivado: sai das listas, mas o histórico é preservado
    allergies = db.relationship('Allergy', secondary=patient_allergy, backref='patients')
    @property
    def allergy_text(self): return ', '.join(a.name for a in self.allergies)
    record = db.relationship('MedicalRecord', back_populates='patient', uselist=False, cascade='all, delete-orphan')
    insurances = db.relationship('PatientInsurance', back_populates='patient')

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local, nullable=False)
    notes = db.Column(db.Text, default='')
    patient = db.relationship('Patient', back_populates='record')

class PatientInsurance(db.Model):
    __table_args__ = (UniqueConstraint('patient_id','insurance_id', name='uq_patient_insurance'),)
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    insurance_id = db.Column(db.Integer, db.ForeignKey('insurance.id'), nullable=False)
    card_number = db.Column(db.String(80), nullable=False)
    joined_at = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    patient = db.relationship('Patient', back_populates='insurances')
    insurance = db.relationship('Insurance')

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialty.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Agendado')
    notes = db.Column(db.Text, default='')
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Professional', backref='appointments')
    specialty = db.relationship('Specialty')
    unit = db.relationship('Unit')
    consultation = db.relationship('Consultation', back_populates='appointment', uselist=False)

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
    attended_at = db.Column(db.DateTime, default=now_local, nullable=False)
    complaint = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, default='')
    diagnosis = db.Column(db.Text, nullable=False)
    conduct = db.Column(db.Text, nullable=False)
    appointment = db.relationship('Appointment', back_populates='consultation')
    @property
    def patient(self): return self.appointment.patient
    @property
    def doctor(self): return self.appointment.doctor

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, default='')
    kind = db.Column(db.String(80), nullable=False)

class ExamRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    requested_at = db.Column(db.Date, default=today_local, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Solicitado')
    performed_at = db.Column(db.Date)
    result = db.Column(db.Text, default='')
    consultation = db.relationship('Consultation', backref='exam_requests')
    exam = db.relationship('Exam')
    @property
    def patient(self): return self.consultation.patient

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    active_ingredient = db.Column(db.String(160), nullable=False)
    manufacturer = db.Column(db.String(120), nullable=False)
    presentation = db.Column(db.String(120), nullable=False)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
    created_at = db.Column(db.Date, default=today_local, nullable=False)
    notes = db.Column(db.Text, default='')
    consultation = db.relationship('Consultation', backref='prescriptions')
    items = db.relationship('PrescriptionItem', back_populates='prescription', cascade='all, delete-orphan')

class PrescriptionItem(db.Model):
    __table_args__ = (CheckConstraint('quantity > 0', name='positive_quantity'),)
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    dose = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, default='')
    prescription = db.relationship('Prescription', back_populates='items')
    medication = db.relationship('Medication')

class Procedure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, default='')
    standard_price = db.Column(db.Numeric(12,2), nullable=False)
    __table_args__ = (CheckConstraint('standard_price >= 0', name='positive_standard_price'),)

class PerformedProcedure(db.Model):
    __table_args__ = (CheckConstraint('charged_price >= 0', name='positive_charged_price'),)
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    performed_at = db.Column(db.Date, default=today_local, nullable=False)
    charged_price = db.Column(db.Numeric(12,2), nullable=False)
    consultation = db.relationship('Consultation', backref='procedures')
    procedure = db.relationship('Procedure')
    professional = db.relationship('Professional')

class Charge(db.Model):
    __table_args__ = (CheckConstraint('total > 0 AND covered >= 0 AND covered <= total', name='valid_charge_amounts'),)
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
    description = db.Column(db.String(180), nullable=False)
    total = db.Column(db.Numeric(12,2), nullable=False)
    insurance_id = db.Column(db.Integer, db.ForeignKey('insurance.id'))
    covered = db.Column(db.Numeric(12,2), nullable=False, default=Decimal('0'))
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.Date, default=today_local, nullable=False)
    consultation = db.relationship('Consultation', backref='charges')
    insurance = db.relationship('Insurance')
    payments = db.relationship('Payment', back_populates='charge')
    @property
    def patient_share(self): return self.total - self.covered
    @property
    def paid(self): return sum((p.amount for p in self.payments if p.status == 'Pago'), Decimal('0'))
    @property
    def balance(self): return self.total - self.paid
    @property
    def patient_balance(self):
        return self.patient_share - sum((p.amount for p in self.payments if p.status == 'Pago' and p.method != 'Convênio'), Decimal('0'))
    @property
    def insurance_balance(self):
        return self.covered - sum((p.amount for p in self.payments if p.status == 'Pago' and p.method == 'Convênio'), Decimal('0'))

class Payment(db.Model):
    __table_args__ = (CheckConstraint('amount > 0', name='positive_payment'),)
    id = db.Column(db.Integer, primary_key=True)
    charge_id = db.Column(db.Integer, db.ForeignKey('charge.id'), nullable=False)
    paid_at = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(12,2), nullable=False)
    method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Pago')
    charge = db.relationship('Charge', back_populates='payments')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(240), nullable=False)
    created_at = db.Column(db.DateTime, default=now_local, nullable=False)
    user = db.relationship('User')

def upgrade_schema():
    """Adiciona colunas novas em bancos já existentes (create_all não altera tabelas criadas)."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if not inspector.has_table('patient'): return
    existing = {c['name'] for c in inspector.get_columns('patient')}
    missing = [c for c in Patient.__table__.columns if c.name not in existing]
    if not missing: return
    with db.engine.begin() as conn:
        for column in missing:
            conn.execute(text(f'ALTER TABLE patient ADD COLUMN {db.engine.dialect.identifier_preparer.quote(column.name)} {column.type.compile(db.engine.dialect)}'))
