"""Metadados dos formulários. As regras de negócio ficam em services.py."""
from models import *

def field(key, label, kind='text', required=True, choices=None, model=None):
    return dict(key=key, label=label, kind=kind, required=required, choices=choices, model=model)

def catalog(model, title, singular, fields, columns, roles=('admin',)):
    return dict(model=model, title=title, singular=singular, fields=fields, columns=columns, roles=roles)

F = field
UFS = [('AC','Acre'),('AL','Alagoas'),('AP','Amapá'),('AM','Amazonas'),('BA','Bahia'),('CE','Ceará'),('DF','Distrito Federal'),
 ('ES','Espírito Santo'),('GO','Goiás'),('MA','Maranhão'),('MT','Mato Grosso'),('MS','Mato Grosso do Sul'),('MG','Minas Gerais'),
 ('PA','Pará'),('PB','Paraíba'),('PR','Paraná'),('PE','Pernambuco'),('PI','Piauí'),('RJ','Rio de Janeiro'),('RN','Rio Grande do Norte'),
 ('RS','Rio Grande do Sul'),('RO','Rondônia'),('RR','Roraima'),('SC','Santa Catarina'),('SP','São Paulo'),('SE','Sergipe'),('TO','Tocantins')]
CATALOGS = {
 'pacientes': catalog(Patient,'Pacientes','paciente',[
    F('name','Nome completo'),F('cpf','CPF'),F('birth_date','Data de nascimento','date'),
    F('sex','Sexo','select',choices=['Feminino','Masculino','Outro','Não informado']),
    F('phone','Telefone'),F('email','E-mail','email',False),
    F('_endereco','Endereço','heading',False),
    F('street','Logradouro'),F('number','Número'),F('complement','Complemento','text',False),
    F('neighborhood','Bairro'),F('city','Cidade'),F('state','Estado','select',choices=UFS),
    F('reference','Ponto de referência','text',False),
    F('allergies','Alergias','allergies',False)],
    [('name','Paciente'),('cpf','CPF'),('birth_date','Nascimento'),('phone','Telefone')],('admin','recepcao')),
 'profissionais': catalog(Professional,'Profissionais','profissional',[
    F('name','Nome completo'),F('cpf','CPF'),F('birth_date','Data de nascimento','date'),
    F('phone','Telefone'),F('email','E-mail','email'),
    F('kind','Categoria','select',choices=['Médico','Enfermeiro','Fisioterapeuta','Outro']),
    F('registration','Registro profissional'),F('crm','CRM','text',False),F('crm_state','UF do CRM','text',False),
    F('specialties','Especialidades','multi',False,model=Specialty),F('units','Unidades de atendimento','multi',True,model=Unit)],
    [('name','Profissional'),('kind','Categoria'),('registration','Registro'),('units','Unidades')]),
 'especialidades': catalog(Specialty,'Especialidades','especialidade',[F('name','Nome'),F('description','Descrição','textarea',False)], [('name','Nome'),('description','Descrição')]),
 'unidades': catalog(Unit,'Unidades','unidade',[
    F('name','Nome'),F('address','Endereço'),F('phone','Telefone'),F('hours','Horário de funcionamento'),
    F('specialties','Especialidades disponíveis','multi',True,model=Specialty)],
    [('name','Unidade'),('address','Endereço'),('hours','Funcionamento'),('specialties','Especialidades')]),
 'convenios': catalog(Insurance,'Convênios','convênio',[F('name','Nome'),F('cnpj','CNPJ'),F('phone','Telefone')], [('name','Convênio'),('cnpj','CNPJ'),('phone','Telefone')]),
 'vinculos': catalog(PatientInsurance,'Planos dos pacientes','vínculo',[
    F('patient_id','Paciente','relation',model=Patient),F('insurance_id','Convênio','relation',model=Insurance),
    F('card_number','Número da carteirinha'),F('joined_at','Data de adesão','date'),F('status','Situação','select',choices=['Ativo','Inativo','Suspenso'])],
    [('patient','Paciente'),('insurance','Convênio'),('card_number','Carteirinha'),('status','Situação')],('admin','recepcao')),
 'exames': catalog(Exam,'Catálogo de exames','exame',[F('name','Nome'),F('kind','Tipo'),F('description','Descrição','textarea',False)], [('name','Exame'),('kind','Tipo'),('description','Descrição')]),
 'medicamentos': catalog(Medication,'Medicamentos','medicamento',[
    F('name','Nome'),F('active_ingredient','Princípio ativo'),F('manufacturer','Fabricante'),F('presentation','Apresentação')],
    [('name','Medicamento'),('active_ingredient','Princípio ativo'),('presentation','Apresentação')],('admin','medico')),
 'procedimentos': catalog(Procedure,'Catálogo de procedimentos','procedimento',[
    F('name','Nome'),F('description','Descrição','textarea',False),F('standard_price','Valor padrão (R$)','money')],
    [('name','Procedimento'),('description','Descrição'),('standard_price','Valor padrão')])
}
