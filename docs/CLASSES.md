# Diagrama de classes

Os atributos são gerados diretamente de models.py. Os nomes em inglês correspondem ao código. As relações abaixo mostram multiplicidades do domínio; regras como pelo menos uma especialidade para médico são validadas também em services.py.

O modelo usa Professional com atributo kind em vez de uma hierarquia de subclasses. A categoria Médico exige CRM/UF e especialidades. O paciente e o médico de uma consulta são derivados do agendamento; o paciente do exame é derivado da consulta.

As quatro tabelas associativas sem atributos adicionais são doctor_specialty, professional_unit, unit_specialty e patient_allergy. PatientInsurance, PrescriptionItem e PerformedProcedure são classes associativas com dados próprios.

## Visão completa

```mermaid
classDiagram
class Patient {
  +id: Integer
  +cpf: String
  +name: String
  +birth_date: Date
  +sex: String
  +phone: String
  +email: String
  +address: String
}
class MedicalRecord {
  +id: Integer
  +patient_id: Integer
  +created_at: DateTime
  +notes: Text
}
class Allergy {
  +id: Integer
  +name: String
  +description: Text
}
class PatientInsurance {
  +id: Integer
  +patient_id: Integer
  +insurance_id: Integer
  +card_number: String
  +joined_at: Date
  +status: String
}
class Insurance {
  +id: Integer
  +name: String
  +cnpj: String
  +phone: String
}
class Professional {
  +id: Integer
  +name: String
  +cpf: String
  +phone: String
  +email: String
  +birth_date: Date
  +registration: String
  +kind: String
  +crm: String
  +crm_state: String
}
class Specialty {
  +id: Integer
  +name: String
  +description: Text
}
class Unit {
  +id: Integer
  +name: String
  +address: String
  +phone: String
  +hours: String
}
class Appointment {
  +id: Integer
  +patient_id: Integer
  +doctor_id: Integer
  +specialty_id: Integer
  +unit_id: Integer
  +starts_at: DateTime
  +status: String
  +notes: Text
}
class Consultation {
  +id: Integer
  +appointment_id: Integer
  +attended_at: DateTime
  +complaint: Text
  +notes: Text
  +diagnosis: Text
  +conduct: Text
  derived_patient: Patient
  derived_doctor: Professional
}
class Exam {
  +id: Integer
  +name: String
  +description: Text
  +kind: String
}
class ExamRequest {
  +id: Integer
  +consultation_id: Integer
  +exam_id: Integer
  +requested_at: Date
  +status: String
  +performed_at: Date
  +result: Text
  derived_patient: Patient
}
class Medication {
  +id: Integer
  +name: String
  +active_ingredient: String
  +manufacturer: String
  +presentation: String
}
class Prescription {
  +id: Integer
  +consultation_id: Integer
  +created_at: Date
  +notes: Text
}
class PrescriptionItem {
  +id: Integer
  +prescription_id: Integer
  +medication_id: Integer
  +quantity: Integer
  +dose: String
  +frequency: String
  +duration: String
  +notes: Text
}
class Procedure {
  +id: Integer
  +name: String
  +description: Text
  +standard_price: Decimal
}
class PerformedProcedure {
  +id: Integer
  +consultation_id: Integer
  +procedure_id: Integer
  +professional_id: Integer
  +performed_at: Date
  +charged_price: Decimal
}
class Charge {
  +id: Integer
  +consultation_id: Integer
  +description: String
  +total: Decimal
  +insurance_id: Integer
  +covered: Decimal
  +due_date: Date
  +created_at: Date
  derived_patient_share: Decimal
  derived_paid: Decimal
  derived_balance: Decimal
  derived_patient_balance: Decimal
  derived_insurance_balance: Decimal
}
class Payment {
  +id: Integer
  +charge_id: Integer
  +paid_at: Date
  +amount: Decimal
  +method: String
  +status: String
}
class User {
  +id: Integer
  +name: String
  +email: String
  +password_hash: String
  +role: String
  +professional_id: Integer
  +set_password(password)
  +verify_password(password): bool
}
class AuditLog {
  +id: Integer
  +user_id: Integer
  +action: String
  +created_at: DateTime
}
Patient "1" -- "1" MedicalRecord : possui
Patient "1" -- "0..*" Appointment : agenda
Professional "1" -- "0..*" Appointment : médico responsável
Specialty "1" -- "0..*" Appointment : especialidade
Unit "1" -- "0..*" Appointment : local
Appointment "1" -- "0..1" Consultation : origina
Patient "1" -- "0..*" PatientInsurance : possui
Insurance "1" -- "0..*" PatientInsurance : atende
Patient "0..*" -- "0..*" Allergy : patient_allergy
Professional "0..*" -- "0..*" Specialty : doctor_specialty
Professional "0..*" -- "1..*" Unit : professional_unit
Unit "0..*" -- "1..*" Specialty : unit_specialty
Consultation "1" -- "0..*" ExamRequest : solicita
Exam "1" -- "0..*" ExamRequest : tipo de exame
Consultation "1" -- "0..*" Prescription : gera
Prescription "1" *-- "1..*" PrescriptionItem : contém
Medication "1" -- "0..*" PrescriptionItem : é prescrito
Consultation "1" -- "0..*" PerformedProcedure : envolve
Procedure "1" -- "0..*" PerformedProcedure : catálogo
Professional "1" -- "0..*" PerformedProcedure : executa
Consultation "1" -- "0..*" Charge : gera
Insurance "0..1" -- "0..*" Charge : cobre
Charge "1" -- "0..*" Payment : recebe
Professional "0..1" -- "0..*" User : identifica perfil
User "1" -- "0..*" AuditLog : realiza
```

## Regras de multiplicidade

- Patient–MedicalRecord é 1:1 no domínio. O serviço cria o prontuário automaticamente; a unicidade e a chave estrangeira impedem prontuário duplicado ou órfão. Um INSERT direto de Patient fora do serviço não cria automaticamente um MedicalRecord.
- Professional–Specialty é muitos para muitos. Para a categoria Médico, o serviço exige 1..* especialidades; outras categorias usam 0.
- Patient–PatientInsurance–Insurance guarda dados do vínculo e evita repetir o mesmo par paciente/operadora.
- Appointment–Consultation é 1 para 0..1. Cada consulta exige um agendamento único.
- Prescription–PrescriptionItem é composição, com pelo menos um item validado pelo serviço.
- Consultation–Charge e Charge–Payment permitem vários registros, preservando pagamentos parciais.

## Fontes e diagramas renderizados

- classes.puml: diagrama UML editável completo.
- classes.svg: versão vetorial, quando renderizada.
- casos-de-uso.puml e casos-de-uso.svg: atores e funcionalidades.

Para regenerar os atributos e fontes UML/DOT: `python scripts/generate_diagrams.py`. Os SVGs são renderizados localmente com Graphviz (Viz.js), com a mesma estrutura de classes e associações.