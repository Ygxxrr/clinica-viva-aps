# Rastreabilidade dos 45 pontos do enunciado

Os números seguem a seção “Dados a considerar” do PDF. A coluna de evidência identifica a implementação; a aprovação final exige revisão e demonstração pelo grupo.

| Ponto | Atendimento | Evidência |
|---|---|---|
| 1 | CPF único por paciente | Patient.cpf unique; services.cpf_digits; cadastro de pacientes |
| 2 | Várias consultas por paciente | Patient → Appointment → Consultation |
| 3 | Consulta de um único paciente | Consultation.appointment_id obrigatório; Appointment.patient_id obrigatório |
| 4 | Consulta de um único médico | Appointment.doctor_id obrigatório e validação de categoria |
| 5 | Várias consultas por médico | Professional → Appointment → Consultation |
| 6 | Uma ou mais especialidades por médico | doctor_specialty; validação de Professional em save_catalog |
| 7 | Vários médicos por especialidade | doctor_specialty; cadastro de profissionais |
| 8 | Mais de um convênio por paciente | PatientInsurance com múltiplos vínculos |
| 9 | Convênio para vários pacientes | PatientInsurance.insurance_id |
| 10 | Carteirinha e situação no vínculo | PatientInsurance.card_number/status; adesão em joined_at |
| 11 | Várias alergias por paciente | patient_allergy; cadastro e prontuário |
| 12 | Alergia em vários pacientes | patient_allergy; catálogo Allergy |
| 13 | Paciente possui prontuário | Criação automática de MedicalRecord no cadastro |
| 14 | Prontuário de um único paciente | MedicalRecord.patient_id obrigatório e único |
| 15 | Vários exames por consulta | Consultation.exam_requests |
| 16 | Mesmo exame em diversas consultas | ExamRequest.exam_id referencia o catálogo Exam |
| 17 | Pedido vinculado à consulta de origem | ExamRequest.consultation_id obrigatório |
| 18 | Nenhuma ou várias prescrições por consulta | Consultation.prescriptions |
| 19 | Vários medicamentos por prescrição | Prescription.items; formulário com múltiplos itens |
| 20 | Medicamento em várias prescrições | PrescriptionItem.medication_id |
| 21 | Dose, frequência e duração por item | PrescriptionItem.dose/frequency/duration |
| 22 | Vários procedimentos por consulta | Consultation.procedures |
| 23 | Procedimento em várias consultas | PerformedProcedure.procedure_id |
| 24 | Valor efetivo independente do padrão | Procedure.standard_price e PerformedProcedure.charged_price |
| 25 | Consulta gera pagamentos | Consultation → Charge → Payment |
| 26 | Valor, data, forma e situação do pagamento | Payment.amount/paid_at/method/status |
| 27 | Profissional em diferentes unidades | professional_unit |
| 28 | Unidade com diversos profissionais | professional_unit; cadastro de profissionais |
| 29 | Unidade com diversas especialidades | unit_specialty; cadastro de unidades |
| 30 | Especialidade em diversas unidades | unit_specialty |
| 31 | Vários agendamentos por paciente | Appointment.patient_id |
| 32 | Vários agendamentos por médico | Appointment.doctor_id |
| 33 | Situação do agendamento | Appointment.status; agenda com filtro e atualização |
| 34 | Cancelado não gera consulta | services.attend; teste de integração de cancelamento |
| 35 | Identificar faltantes | Agenda → filtro Não compareceu |
| 36 | Histórico completo do paciente | /pacientes/<id>; linha do tempo de consultas |
| 37 | Exames solicitados por paciente | /solicitacoes?patient_id=<id> |
| 38 | Identificar exames não realizados | /solicitacoes?pending=1; Solicitado e Agendado. Cancelados são exibidos no filtro geral |
| 39 | Medicamentos da consulta | /consultas/<id>; prescrições e itens |
| 40 | Faturamento por período | /relatorios; cobranças pela data de emissão |
| 41 | Faturamento por médico/especialidade/unidade | Filtros e agrupamentos em /relatorios; recebimentos apresentados separadamente |
| 42 | Pacientes com pagamentos pendentes | /financeiro?pending=1; saldo, paciente e vencimento |
| 43 | Quantidade de consultas por especialidade | Relatórios, gráfico e tabela; apenas Consultation |
| 44 | Médicos de determinada unidade | Cadastro de profissionais exibe unidades e permite busca textual pelo nome da unidade |
| 45 | Procedimentos por período | Relatórios → Procedimentos realizados no período |

## Exigências adicionais do texto

| Item | Evidência |
|---|---|
| Dados completos de paciente e profissional | models.py e formulários de cadastro |
| Data e horário de consulta | Consultation.attended_at |
| Queixa, observações, diagnóstico e conduta | Formulário de atendimento e registro clínico |
| Datas, situação e resultado de exame | ExamRequest e acompanhamento de solicitações |
| Quantidade e observações de medicamento | PrescriptionItem |
| Profissional e data de procedimento | PerformedProcedure |
| Dinheiro, crédito, débito, PIX e convênio | Formulário de pagamento e services.pay |
| Convênio utilizado, cobertura e parte do paciente | Charge.insurance_id/covered; patient_share derivado |
| Scrum, squads, papéis e datas | SCRUM.md — proposta transparente, a validar pelo grupo |
| Requisitos funcionais, não funcionais e regras | ANALISE.md |
| Casos de uso | CASOS_DE_USO.md e casos-de-uso.puml |
| Classes completas | CLASSES.md e classes.puml; atributos gerados dos modelos implementados |
