"""Gera UML com os atributos reais das classes. Renderização opcional no PlantUML."""
import sys
from pathlib import Path
import re
from html import escape
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import models
from sqlalchemy import inspect

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
groups={
 'Cadastros e estrutura':['Patient','MedicalRecord','Allergy','PatientInsurance','Insurance','Professional','Specialty','Unit'],
 'Atendimento':['Appointment','Consultation','Exam','ExamRequest','Medication','Prescription','PrescriptionItem','Procedure','PerformedProcedure'],
 'Financeiro':['Charge','Payment'],
 'Acesso e rastreabilidade':['User','AuditLog']}
relations=[
 ('Patient','1','MedicalRecord','1','possui'),
 ('Patient','1','Appointment','0..*','agenda'),
 ('Professional','1','Appointment','0..*','médico responsável'),
 ('Specialty','1','Appointment','0..*','especialidade'),
 ('Unit','1','Appointment','0..*','local'),
 ('Appointment','1','Consultation','0..1','origina'),
 ('Patient','1','PatientInsurance','0..*','possui'),
 ('Insurance','1','PatientInsurance','0..*','atende'),
 ('Patient','0..*','Allergy','0..*','patient_allergy'),
 ('Professional','0..*','Specialty','0..*','doctor_specialty'),
 ('Professional','0..*','Unit','1..*','professional_unit'),
 ('Unit','0..*','Specialty','1..*','unit_specialty'),
 ('Consultation','1','ExamRequest','0..*','solicita'),
 ('Exam','1','ExamRequest','0..*','tipo de exame'),
 ('Consultation','1','Prescription','0..*','gera'),
 ('Prescription','1','PrescriptionItem','1..*','contém'),
 ('Medication','1','PrescriptionItem','0..*','é prescrito'),
 ('Consultation','1','PerformedProcedure','0..*','envolve'),
 ('Procedure','1','PerformedProcedure','0..*','catálogo'),
 ('Professional','1','PerformedProcedure','0..*','executa'),
 ('Consultation','1','Charge','0..*','gera'),
 ('Insurance','0..1','Charge','0..*','cobre'),
 ('Charge','1','Payment','0..*','recebe'),
 ('Professional','0..1','User','0..*','identifica perfil'),
 ('User','1','AuditLog','0..*','realiza')]
properties={'Consultation':['/patient: Patient','/doctor: Professional'],
 'ExamRequest':['/patient: Patient'],
 'Charge':['/patient_share: Decimal','/paid: Decimal','/balance: Decimal','/patient_balance: Decimal','/insurance_balance: Decimal']}
methods={'User':['+set_password(password)','+verify_password(password): bool']}

def type_name(column):
    kind=str(column.type)
    if kind.startswith('VARCHAR'):return 'String'
    return {'INTEGER':'Integer','DATE':'Date','DATETIME':'DateTime','TEXT':'Text','NUMERIC(12, 2)':'Decimal'}.get(kind,kind)

def class_body(name,plantuml=True):
    lines=[]
    for c in inspect(getattr(models,name)).columns:
        flags=[]
        if c.primary_key:flags.append('PK')
        if c.foreign_keys:flags.append('FK')
        if c.unique:flags.append('unique')
        if c.nullable:flags.append('optional')
        flags=' ['+', '.join(flags)+']' if flags else ''
        lines.append(f'  +{c.name}: {type_name(c)}{flags}')
    lines += ['  '+p for p in properties.get(name,[])]
    lines += ['  '+p for p in methods.get(name,[])]
    return lines

def write_sources():
    p=['@startuml','skinparam backgroundColor #FFFFFF','skinparam shadowing false','skinparam defaultFontName Arial',
     'skinparam classAttributeIconSize 0','skinparam linetype ortho','skinparam nodesep 50','skinparam ranksep 70',
     'skinparam class {\n BackgroundColor #F0F8F3\n BorderColor #468C75\n FontColor #234D3C\n}',
     'skinparam package {\n BorderColor #A8C7B5\n BackgroundColor #FAFCFA\n FontColor #4B745C\n}',
     'title Clínica Silva — Diagrama de classes da implementação']
    md=['# Diagrama de classes\n','Os atributos são gerados diretamente de models.py. Os nomes em inglês correspondem ao código. As relações abaixo mostram multiplicidades do domínio; regras como pelo menos uma especialidade para médico são validadas também em services.py.\n',
      'O modelo usa Professional com atributo kind em vez de uma hierarquia de subclasses. A categoria Médico exige CRM/UF e especialidades. O paciente e o médico de uma consulta são derivados do agendamento; o paciente do exame é derivado da consulta.\n',
      'As quatro tabelas associativas sem atributos adicionais são doctor_specialty, professional_unit, unit_specialty e patient_allergy. PatientInsurance, PrescriptionItem e PerformedProcedure são classes associativas com dados próprios.\n',
      '## Visão completa\n','```mermaid','classDiagram']
    for group,names in groups.items():
        p.append(f'package "{group}" {{')
        for name in names:
            body=class_body(name)
            p.extend([f'class {name} {{',*body,'}'])
            md.append(f'class {name} {{')
            md.extend(line.split(' [')[0].replace('/','derived_') for line in body)
            md.append('}')
        p.append('}')
    for a,ca,b,cb,label in relations:
        connector='*--' if (a,b) in [('Prescription','PrescriptionItem')] else '--'
        p.append(f'{a} "{ca}" {connector} "{cb}" {b} : {label}')
        md.append(f'{a} "{ca}" {connector} "{cb}" {b} : {label}')
    p.extend(['note bottom of Professional','Médico: CRM e UF obrigatórios; uma ou mais especialidades.','Os demais profissionais não possuem especialidades médicas.','end note',
     'note bottom of Consultation','patient e doctor são propriedades derivadas do agendamento.','Uma consulta não duplica esses identificadores.','end note',
     'note bottom of Charge','patient_share = total - covered','balance = total - pagamentos Pago','Saldos de paciente e convênio são independentes.','end note','@enduml'])
    md.extend(['```','\n## Regras de multiplicidade\n',
     '- Patient–MedicalRecord é 1:1 no domínio. O serviço cria o prontuário automaticamente; a unicidade e a chave estrangeira impedem prontuário duplicado ou órfão. Um INSERT direto de Patient fora do serviço não cria automaticamente um MedicalRecord.',
     '- Professional–Specialty é muitos para muitos. Para a categoria Médico, o serviço exige 1..* especialidades; outras categorias usam 0.',
     '- Patient–PatientInsurance–Insurance guarda dados do vínculo e evita repetir o mesmo par paciente/operadora.',
     '- Appointment–Consultation é 1 para 0..1. Cada consulta exige um agendamento único.',
     '- Prescription–PrescriptionItem é composição, com pelo menos um item validado pelo serviço.',
     '- Consultation–Charge e Charge–Payment permitem vários registros, preservando pagamentos parciais.',
     '\n## Fontes e diagramas renderizados\n',
     '- classes.puml: diagrama UML editável completo.',
     '- classes.svg: versão vetorial, quando renderizada.',
     '- casos-de-uso.puml e casos-de-uso.svg: atores e funcionalidades.',
     '\nPara regenerar os atributos e fontes UML/DOT: `python scripts/generate_diagrams.py`. Os SVGs são renderizados localmente com Graphviz (Viz.js), com a mesma estrutura de classes e associações.'])
    (DOCS/'classes.puml').write_text('\n'.join(p),encoding='utf-8')
    (DOCS/'CLASSES.md').write_text('\n'.join(md),encoding='utf-8')

def write_dot():
    for filename,selected in [('classes',[n for group in groups.values() for n in group])]+[(f'classes-{i+1}',names) for i,names in enumerate(groups.values())]:
        lines=['digraph G {','graph [rankdir=TB, bgcolor="white", pad="0.5", nodesep="0.6", ranksep="1.0", splines=polyline, fontname="Arial", fontsize=22, label="Clínica Silva · Diagrama de classes", labelloc=t];',
         'node [shape=plain, fontname="Arial", fontsize=12];','edge [fontname="Arial", fontsize=10, color="#719487", fontcolor="#47695A", arrowsize=0.7, dir=none];']
        for i,(group,names) in enumerate(groups.items()):
            chosen=[n for n in names if n in selected]
            if not chosen:continue
            lines.append(f'subgraph cluster_{i} {{ label="{group}"; color="#D5E6DC"; style="rounded"; fontcolor="#638C76"; fontsize=16; margin=25;')
            for name in chosen:
                body=class_body(name)
                fields=''.join(f'<TR><TD ALIGN="LEFT">{escape(row.strip())}</TD></TR>' for row in body)
                lines.append(f'{name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="7" COLOR="#76A58D" BGCOLOR="#FFFFFF"><TR><TD BGCOLOR="#EAF4ED"><B>{name}</B></TD></TR><TR><TD HEIGHT="1" BGCOLOR="#76A58D"></TD></TR>{fields}</TABLE>>];')
            lines.append('}')
        for a,ca,b,cb,label in relations:
            if a in selected and b in selected:
                edge='dir=both, arrowtail=diamond, arrowhead=none,' if (a,b)==('Prescription','PrescriptionItem') else ''
                lines.append(f'{a} -> {b} [{edge} taillabel="{ca}", headlabel="{cb}", label="{label}", labeldistance=2.0];')
        lines.append('}')
        (DOCS/f'{filename}.dot').write_text('\n'.join(lines),encoding='utf-8')
    source=(DOCS/'casos-de-uso.puml').read_text(encoding='utf-8')
    # Corrige a formatação dos blocos PlantUML sem alterar o conteúdo UML.
    source=source.replace('skinparam usecase { BackgroundColor #EFF8F3; BorderColor #398D78; FontColor #21483C }','skinparam usecase {\n BackgroundColor #EFF8F3\n BorderColor #398D78\n FontColor #21483C\n}')
    source=source.replace('skinparam rectangle { BorderColor #86B5A1; FontColor #21483C }','skinparam rectangle {\n BorderColor #86B5A1\n FontColor #21483C\n}')
    (DOCS/'casos-de-uso.puml').write_text(source,encoding='utf-8')
    actors=re.findall(r'actor "([^"]+)" as (\w+)',source)
    cases=re.findall(r'usecase "([^"]+)" as (\w+)',source)
    lines=['digraph G {','graph [rankdir=LR, bgcolor="white", pad=0.5, nodesep=0.35, ranksep=1.2, splines=polyline, fontname="Arial", fontsize=22, label="Clínica Silva · Casos de uso", labelloc=t];',
      'node [fontname="Arial", fontsize=12, color="#75A68E", style=filled, fillcolor="#F0F8F3"];',
      'edge [fontname="Arial", fontsize=10, color="#789787", fontcolor="#4E7860", arrowsize=0.7];']
    for title,name in actors:lines.append(f'{name} [shape=box, fillcolor="#FFFFFF", label="«ator»\\n{title}"];')
    lines.append('subgraph cluster_system { label="Sistema de gestão de clínica médica"; fontname="Arial"; fontsize=16; color="#A0C2AC"; style=rounded; margin=25;')
    for title,name in cases:lines.append(f'{name} [shape=ellipse, label="{title}"];')
    lines.append('}')
    for a,b in re.findall(r'^(\w+) --> (\w+)$',source,re.M):lines.append(f'{a} -> {b} [dir=none];')
    for a,b in re.findall(r'^(\w+) --\|> (\w+)$',source,re.M):lines.append(f'{a} -> {b} [arrowhead=empty];')
    for a,b,kind in re.findall(r'^(\w+) \.\.> (\w+) : <<(\w+)>>$',source,re.M):lines.append(f'{a} -> {b} [style=dashed, label="«{kind}»", arrowhead=vee];')
    lines.append('}')
    (DOCS/'casos-de-uso.dot').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__':
    write_sources()
    write_dot()
    print('Fontes UML e DOT geradas a partir dos modelos.')
