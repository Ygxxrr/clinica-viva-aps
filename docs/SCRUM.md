# Scrum e organização do trabalho

## Transparência do registro

Este projeto foi implementado em uma sessão concentrada em 26/10/2026. O trabalho foi realizado individualmente e não há registro de sprints anteriores ou reuniões passadas. Os quadros de planejamento abaixo organizam as entregas; o registro de revisões no final deve ser completado com as validações efetivamente feitas. Uma divisão de horas em um único dia é um plano emergencial de entrega; não equivale a afirmar que se praticou integralmente Scrum em ciclos anteriores.

## Time e squads propostos

O projeto foi desenvolvido individualmente por **Ygor Silva Matos (RGM 40986616)**, que acumula todos os papéis do Scrum. As frentes de trabalho abaixo organizam o backlog em três squads lógicas, todas conduzidas pelo mesmo integrante. O termo SQUAD é usado no enunciado como organização das frentes; não é um papel oficial do Scrum.

| Frente / squad | Entregas | Papéis sugeridos |
|---|---|---|
| Atendimento e experiência | Pacientes, agenda, consultas, prontuário, exames e prescrições | Developer — Ygor Silva Matos |
| Gestão e dados | Convênios, unidades, financeiro, relatórios e persistência | Developer — Ygor Silva Matos |
| Qualidade e integração (transversal) | Requisitos, diagramas, validação e integração | Developer e Scrum Master — Ygor Silva Matos |

| Papel Scrum | Responsabilidade | Integrante real |
|---|---|---|
| Product Owner | Ordenar Product Backlog e validar valor das entregas | Ygor Silva Matos — RGM 40986616 |
| Scrum Master | Facilitar eventos, remover impedimentos e apoiar o processo | Ygor Silva Matos — RGM 40986616 |
| Developers | Analisar, implementar, testar, documentar e integrar | Ygor Silva Matos — RGM 40986616 |

Como o time tem um único integrante, a separação entre Product Owner, Scrum Master e Developer é de responsabilidades, não de pessoas: as decisões de prioridade, a remoção de impedimentos e a implementação foram exercidas pelo mesmo membro.

## Product Goal

Permitir demonstrar a jornada integrada de um paciente, do cadastro ao acompanhamento clínico e à liquidação financeira, com persistência e rastreabilidade.

## Product Backlog ordenado

| Ordem | Item | Requisitos | Aceitação |
|---|---|---|---|
| 1 | Base de dados e cadastros | RF02–RF11 | Dados e relações persistem com integridade |
| 2 | Agenda e consulta | RF12–RF14 | Agendar e atender sem conflito ou cancelamento inválido |
| 3 | Continuidade clínica | RF03–RF04, RF15–RF21 | Exames, prescrições e procedimentos vinculados ao atendimento |
| 4 | Financeiro e relatórios | RF22–RF29 | Cobrar e receber sem exceder saldos; relatório confere |
| 5 | Acesso, qualidade e publicação | RF01, RF30; RNF01–RNF12 | Perfis autorizados, testes aprovados e demonstração acessível |

## Planejamento emergencial sugerido — 26/10/2026

Os intervalos são janelas de planejamento, não registros de reuniões ou datas históricas de entrega.

| Incremento / sprint proposto | Data e janela | Sprint Goal | Escopo | Evidência disponível no código |
|---|---|---|---|---|
| 1 — Fundação | 26/10, 12h–13h | Estruturar dados e cadastro | RF02–RF11 | models.py, catalog.py e formulários |
| 2 — Jornada clínica | 26/10, 13h–14h | Conectar agenda ao prontuário | RF12–RF21 | services.py, agenda e consultas |
| 3 — Gestão financeira | 26/10, 14h–15h | Controlar valores e indicadores | RF22–RF29 | Cobrança, pagamento, relatórios e CSV |
| 4 — Validação e apresentação | 26/10, 15h–16h30 | Validar e demonstrar o incremento | RF01/RF30 e não funcionais | Testes, perfis, documentação e deploy quando concluído |

Como as funcionalidades foram construídas em conjunto, a existência do código não comprova entrega em cada janela. Registre as datas reais de revisão e aceite após a validação do grupo.

## Eventos e artefatos a demonstrar

- Sprint Planning: selecionar o objetivo e itens prioritários; registrar critérios de aceite.
- Daily Scrum: inspeção do progresso pelos Developers, impedimentos e plano até o próximo encontro. Em trabalho de um único dia, realizar checkpoints curtos sem inventar dailies de dias anteriores.
- Sprint Review: demonstrar o fluxo com os interessados e colher feedback.
- Sprint Retrospective: registrar o que funcionou e uma melhoria concreta para o próximo ciclo.
- Artefatos: Product Backlog, Sprint Backlog e Incremento. Compromissos: Product Goal, Sprint Goal e Definition of Done.

## Definition of Done

1. Requisito implementado e vinculado à matriz de rastreabilidade.
2. Regra de negócio validada no servidor e restrições relevantes no banco.
3. Interface abre sem erro e oferece resultado compreensível.
4. Teste do fluxo relevante aprovado e sem regressão conhecida.
5. Código e documentação versionados sem credenciais.
6. Funcionalidade demonstrada com dados fictícios.
7. Quando houver deploy: verificar URL, login, gravação persistente e relatório antes de declarar a publicação concluída.

## Registro real a completar pelo grupo

| Revisão | Data/hora real | Quem validou | Resultado |
|---|---|---|---|
| Cadastros e agenda | Preencher | Preencher | Preencher |
| Atendimento e prontuário | Preencher | Preencher | Preencher |
| Financeiro e relatórios | Preencher | Preencher | Preencher |
| Publicação e ensaio | Preencher | Preencher | Preencher |
