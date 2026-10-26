# Análise do sistema — Clínica Viva

## Problema e objetivo

Uma clínica registra parte das informações manualmente e precisa centralizar o atendimento. O sistema conecta os dados cadastrais à agenda, ao registro clínico e às movimentações financeiras, permitindo consultar o histórico do paciente e indicadores da operação.

O escopo acadêmico é um protótipo funcional com dados sintéticos. Regras adicionais adotadas pela implementação estão identificadas abaixo, sem atribuí-las ao enunciado.

## Atores

| Ator | Responsabilidade |
|---|---|
| Recepção | Cadastrar pacientes, associar convênios e controlar agendamentos |
| Médico | Registrar consulta, prescrever, solicitar exames, acompanhar resultados e consultar prontuário |
| Financeiro | Emitir cobranças, registrar pagamentos, acompanhar pendências e gerar relatórios |
| Administrador | Gerenciar cadastros de apoio, acessar todos os módulos e consultar auditoria |

Paciente é uma entidade do domínio, sem portal próprio nesta implementação. Convênio é uma entidade cadastrada, sem integração externa. Profissionais não médicos podem ser responsáveis por procedimentos, mas não possuem perfil de login separado no protótipo.

## Requisitos funcionais

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RF01 | Autenticar usuário e autorizar por perfil | Rotas rejeitam acesso de perfis não autorizados |
| RF02 | Cadastrar e editar pacientes | CPF único, dados obrigatórios e prontuário criado automaticamente |
| RF03 | Registrar alergias | Um paciente pode ter diversas alergias, compartilhadas com outros pacientes |
| RF04 | Manter prontuário e histórico | Exibir consultas, diagnósticos, condutas e vínculos com exames/prescrições |
| RF05 | Cadastrar profissionais | Registrar dados pessoais, registro profissional e CRM/UF para médicos |
| RF06 | Cadastrar especialidades | Código, nome e descrição |
| RF07 | Vincular médicos a especialidades | Aceitar várias especialidades por médico e vários médicos por especialidade |
| RF08 | Cadastrar unidades | Código, nome, endereço, telefone e funcionamento |
| RF09 | Vincular profissionais e especialidades a unidades | Um profissional e uma especialidade podem existir em diversas unidades |
| RF10 | Cadastrar convênios | Código, nome, CNPJ e telefone |
| RF11 | Vincular pacientes a convênios | Guardar carteirinha, adesão e situação do vínculo |
| RF12 | Agendar consulta | Selecionar paciente, médico, especialidade, unidade, data, horário e observações |
| RF13 | Alterar situação do agendamento | Agendado, Confirmado, Realizado, Cancelado e Não compareceu |
| RF14 | Registrar atendimento | Criar consulta a partir de agendamento ativo, registrando queixa, observações, diagnóstico e conduta |
| RF15 | Cadastrar exames | Código, nome, descrição e tipo |
| RF16 | Solicitar e acompanhar exames | Vincular pedido à consulta e ao exame, guardar datas, situação e resultado |
| RF17 | Identificar exames pendentes | Filtrar Solicitado/Agendado e paciente |
| RF18 | Cadastrar medicamentos | Nome, princípio ativo, fabricante e apresentação |
| RF19 | Criar prescrições com múltiplos itens | Cada item guarda medicamento, quantidade, dose, frequência, duração e observações |
| RF20 | Cadastrar procedimentos | Nome, descrição e valor padrão |
| RF21 | Registrar procedimentos realizados | Consulta, responsável, data e valor efetivo |
| RF22 | Emitir cobranças de serviços | Uma consulta aceita várias cobranças com total, vencimento e descrição |
| RF23 | Registrar pagamentos | Código, data, valor, forma de pagamento e situação; aceitar pagamentos parciais |
| RF24 | Separar cobertura e responsabilidade | Identificar convênio utilizado, cobertura e parte do paciente |
| RF25 | Identificar pagamentos pendentes | Filtrar cobranças com saldo e exibir paciente e vencimento |
| RF26 | Relatar faturamento e recebimentos | Filtrar período e agrupar por médico, especialidade e unidade |
| RF27 | Consultar quantidade de consultas por especialidade | Contar consultas efetivamente realizadas no período |
| RF28 | Consultar procedimentos por período | Mostrar execução, responsável, paciente e valor |
| RF29 | Exportar e imprimir relatórios | CSV em português e impressão pelo navegador |
| RF30 | Registrar operações | Guardar usuário, data e operação de alteração bem-sucedida |

## Requisitos não funcionais

| ID | Requisito | Evidência / limite |
|---|---|---|
| RNF01 | Legibilidade e separação de responsabilidades | Rotas, serviços, modelos e templates em arquivos distintos |
| RNF02 | Persistência relacional | SQLite local; PostgreSQL externo para o deploy |
| RNF03 | Integridade | Chaves estrangeiras, unicidade de CPF, prontuário e consulta de agendamento; constraints de valores |
| RNF04 | Proteção básica de acesso | Hash de senha, sessão assinada, autorização por rota e CSRF |
| RNF05 | Escape de saída e consultas parametrizadas | Jinja com autoescape e ORM SQLAlchemy |
| RNF06 | Interface responsiva | Layout adaptado a telas pequenas, menu móvel e rolagem de tabelas |
| RNF07 | Rastreabilidade | Auditoria interna de alterações; não substitui um log imutável de produção |
| RNF08 | Testabilidade | Testes de integração com banco em memória isolado |
| RNF09 | Portabilidade | Python 3.12+, dependências declaradas e configuração por variáveis de ambiente |
| RNF10 | Consistência de horário | Datas de negócio em America/Sao_Paulo |
| RNF11 | Independência da internet para executar localmente | Backend, dados e assets locais; fontes web usam fallback do sistema |
| RNF12 | Uso de valores decimais | Numeric/Decimal com duas casas para evitar erro binário de float em dinheiro |

Não foi realizado teste de carga nem estabelecido SLA. Não se afirma conformidade regulatória para prontuários reais. O protótipo não possui recuperação de senha, gestão completa de usuários, migrações versionadas ou integração com serviços externos.

## Regras de negócio do enunciado

| ID | Regra |
|---|---|
| RN01 | CPF de paciente é único |
| RN02 | Cada consulta identifica exatamente um paciente e um médico |
| RN03 | Médico possui uma ou mais especialidades; especialidade pode ter vários médicos |
| RN04 | Paciente pode ter vários convênios; vínculo guarda carteirinha, adesão e situação |
| RN05 | Paciente tem um prontuário e pode ter várias alergias |
| RN06 | Agendamento cancelado não gera consulta realizada |
| RN07 | Consulta pode solicitar vários exames; pedido pertence à consulta de origem |
| RN08 | Solicitação de exame registra situação, datas e resultado |
| RN09 | Consulta pode ter nenhuma ou várias prescrições; cada prescrição contém vários itens |
| RN10 | Cada item prescrito guarda quantidade, dose, frequência, duração e observações |
| RN11 | Procedimento realizado registra data, responsável e valor efetivo, diferente ou igual ao padrão |
| RN12 | Consulta pode gerar várias cobranças e pagamentos |
| RN13 | Pagamento registra data, valor, forma e situação |
| RN14 | Cobertura do convênio e parte do paciente precisam ser identificáveis |
| RN15 | Profissionais e especialidades podem atender em várias unidades |

## Decisões adicionais adotadas

| ID | Decisão da implementação | Justificativa |
|---|---|---|
| DA01 | Slots de agenda de 30 minutos | Regra simples e demonstrável para conflito de horários |
| DA02 | Bloquear médico ou paciente com outro agendamento ativo no mesmo slot | Evitar sobreposição; inclui atendimento já realizado |
| DA03 | Validar médico–especialidade, médico–unidade e unidade–especialidade | Impedir agendamento incoerente |
| DA04 | Consulta sempre nasce de um agendamento | Uma origem explícita e rastreável para o atendimento |
| DA05 | Consultas não duplicam paciente/médico em colunas | Dados derivados do agendamento, evitando inconsistência |
| DA06 | Resultado e realização são obrigatórios ao concluir exame | Exame realizado fica documentado; datas não podem ser futuras ou anteriores ao pedido |
| DA07 | Cobertura não supera total; valores são positivos/não negativos conforme o campo | Preservar consistência financeira |
| DA08 | Cobertura exige vínculo ativo do paciente com o convênio | Relacionar a conta à operadora correta |
| DA09 | Pagamentos são separados por responsável e não superam seu saldo | Evitar que pagamento do paciente liquide parte do convênio indevidamente |
| DA10 | Apenas pagamentos com situação Pago compõem recebimentos | Pendente e Cancelado não são caixa recebido |
| DA11 | Faturamento por emissão e recebimento por data de pagamento | Distinguir competência e caixa |
| DA12 | Consulta e prontuário sem exclusão pela interface | Preservar histórico; cancelamentos mantêm registros |
| DA13 | Médico edita seus atendimentos e visualiza o histórico completo dos pacientes | Combinar responsabilidade de autoria com continuidade do cuidado no protótipo |
| DA14 | Até oito medicamentos em cada formulário de prescrição | Limite da interface, sem limite equivalente na relação do banco |

## Estados principais

Agendamento: `Agendado → Confirmado → Realizado`. Também pode ir de Agendado/Confirmado para Cancelado ou Não compareceu. Realizado é atribuído apenas ao registrar a consulta. Estados finais não voltam a ativos pela interface.

Exame: Solicitado pode passar para Agendado, Realizado ou Cancelado. Agendado pode passar para Realizado ou Cancelado. Realizado e Cancelado são finais.

Pagamento: é registrado como Pago, Pendente ou Cancelado. Um pagamento Pendente pode ser liquidado como Pago ou cancelado. Pagamentos já pagos não são estornados nesta versão; um sistema operacional precisaria de um fluxo de estorno auditável.
