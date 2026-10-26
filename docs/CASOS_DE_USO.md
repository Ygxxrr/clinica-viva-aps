# Casos de uso

O diagrama UML em `casos-de-uso.puml` representa os atores externos e as funcionalidades do sistema. Administrador especializa os três perfis operacionais, pois possui seus acessos, além dos cadastros de apoio e da auditoria. O diagrama não trata banco de dados ou classes como atores.

## Catálogo

| ID | Caso de uso | Ator principal | Resultado |
|---|---|---|---|
| UC01 | Autenticar usuário | Todos | Sessão do perfil iniciada |
| UC02 | Manter paciente | Recepção | Cadastro e prontuário criado na inclusão |
| UC03 | Vincular convênio ao paciente | Recepção | Carteirinha, adesão e situação registradas |
| UC04 | Agendar consulta | Recepção | Horário disponível reservado |
| UC05 | Atualizar situação do agendamento | Recepção | Confirmação, cancelamento ou falta registrados |
| UC06 | Registrar consulta | Médico | Atendimento vinculado e agendamento realizado |
| UC07 | Consultar histórico do paciente | Médico | Prontuário, consultas e tratamentos consultados |
| UC08 | Manter prontuário e alergias | Médico | Notas gerais e alergias atualizadas |
| UC09 | Solicitar exame | Médico | Pedido vinculado à consulta |
| UC10 | Acompanhar exames e resultados | Médico | Situação e resultado atualizados |
| UC11 | Prescrever medicamentos | Médico | Prescrição com um ou mais itens salva |
| UC12 | Registrar procedimento | Médico | Execução, responsável e preço efetivo registrados |
| UC13 | Emitir cobrança | Financeiro | Total, cobertura, responsável e vencimento registrados |
| UC14 | Registrar pagamento | Financeiro | Pagamento vinculado a uma cobrança |
| UC15 | Consultar pendências | Financeiro | Pacientes e cobranças com saldo identificados |
| UC16 | Gerar relatórios | Financeiro | Faturamento, recebimentos, consultas e procedimentos por período |
| UC17 | Exportar / imprimir relatório | Financeiro | Arquivo CSV ou impressão do navegador |
| UC18 | Manter cadastros de apoio | Administrador | Profissionais, especialidades, unidades e catálogos disponíveis |
| UC19 | Consultar atividades | Administrador | Operações realizadas identificadas por usuário e data |

Autenticação é uma precondição dos casos de uso operacionais; o diagrama evita ligar cada operação a “Autenticar” com include, pois não se refaz o login a cada clique. Validações obrigatórias de agenda e saldo aparecem como casos incluídos. Exames, prescrições e procedimentos usam extend sobre o registro do atendimento para indicar comportamento clínico opcional no contexto da consulta; na interface são adicionados após salvar o registro principal.

## UC04 — Agendar consulta

- Precondições: usuário de recepção ou administrador; paciente, médico, especialidade e unidade cadastrados.
- Fluxo principal: selecionar paciente; selecionar médico; informar especialidade e unidade; informar horário; validar vínculos e disponibilidade; persistir agendamento Agendado; registrar operação.
- Alternativas: conflito de médico ou paciente impede gravação; médico fora da unidade/especialidade impede gravação; horário fora do intervalo de 30 minutos impede gravação.
- Pós-condição: agendamento está vinculado exatamente a um paciente e um médico.

## UC06 — Registrar consulta

- Precondições: perfil médico autorizado ou administrador; agendamento ativo.
- Fluxo principal: abrir atendimento; consultar alerta de alergias; preencher queixa, diagnóstico e conduta; salvar; criar consulta e marcar agendamento Realizado na mesma transação.
- Alternativas: agendamento Cancelado, Realizado ou Não compareceu é rejeitado; médico não pode editar consulta de outro profissional.
- Pós-condição: uma consulta vinculada ao agendamento; segunda consulta para o mesmo agendamento é impedida.

## UC11 — Prescrever medicamentos

- Precondições: consulta registrada; médico autor do atendimento ou administrador.
- Fluxo principal: adicionar medicamento; informar quantidade, dose, frequência, duração e observações; adicionar outros itens se necessário; salvar prescrição com seus itens.
- Alternativas: prescrição sem itens, quantidade não positiva ou posologia incompleta não é salva.
- Pós-condição: itens pertencem à prescrição e a prescrição pertence à consulta. O cadastro do medicamento permanece compartilhado.

## UC14 — Registrar pagamento

- Precondições: cobrança existente; perfil financeiro ou administrador.
- Fluxo principal: identificar paciente/convênio responsável; informar valor, forma, situação e data; validar saldo da respectiva parte; salvar pagamento.
- Alternativas: valor maior que o saldo, não positivo ou data futura para pagamento realizado é rejeitado; pagamento Pendente não entra nos recebimentos.
- Pós-condição: quando Pago, o saldo da parte correspondente diminui pelo valor registrado; a cobertura original da cobrança não muda.
