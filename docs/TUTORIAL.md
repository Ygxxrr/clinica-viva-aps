# Tutorial completo - Clínica Silva

Navegação e funcionalidades da versão Roxo Aurora.

## Como começar

Entre com um dos perfis de acesso. Todos usam a senha `Clinica2026!`.

| Perfil | E-mail | O que pode fazer |
| --- | --- | --- |
| Administrador | admin@clinicasilva.com.br | Acessar todos os módulos e manter os cadastros de apoio. |
| Recepção | recepcao@clinicasilva.com.br | Gerenciar pacientes, vínculos com convênios e agendamentos. |
| Médico | medico@clinicasilva.com.br | Ver a própria agenda, registrar seus atendimentos e consultar o histórico dos pacientes. |
| Financeiro | financeiro@clinicasilva.com.br | Gerenciar cobranças, pagamentos e relatórios financeiros. |

### Onde ficam as abas?

No computador, use o menu compacto à esquerda: **Início, Agenda, Pacientes, Consultas, Exames, Financeiro, Relatórios, Cadastros e Ajuda**. Os itens disponíveis mudam conforme o perfil. Em telas pequenas, abra o menu pelo botão no topo.

**Cadastros** abre uma lista com profissionais, unidades, especialidades, convênios e catálogos. As prescrições e os procedimentos realizados ficam **dentro de cada consulta**. **Como usar**, no topo, e **Ajuda**, no menu, abrem este tutorial.

## Entenda a visão geral

- Confira os indicadores: pacientes cadastrados, agendamentos na data, valores recebidos e saldo a receber. Os perfis sem acesso financeiro veem indicadores do próprio contexto.
- Na faixa com os dias da semana, selecione uma data. A agenda será consultada para esse dia.
- Clique em um atendimento da lista. O cartão à direita mostra o paciente, o médico, o horário, os convênios ativos e a situação reais daquele agendamento.
- Use **Iniciar atendimento** para registrar uma consulta ativa, ou **Abrir consulta** para rever um atendimento realizado. Na recepção, um agendamento ainda não confirmado oferece **Confirmar presença**.
- Use **Prontuário** ou **Ver paciente** para abrir o cadastro correspondente. O histórico clínico completo só aparece para médico e administrador.

Se não houver horários na data, a tela exibe uma mensagem. Isso não é erro: escolha outro dia ou crie um agendamento. Para o médico, só aparecem os horários do profissional vinculado ao seu login.

## Cadastrar, localizar e acompanhar pacientes

Cadastro: administrador / recepção · Histórico clínico: administrador / médico
- Abra **Pacientes**. Use a busca por nome, CPF ou outra informação exibida e clique em **Buscar**.
- Para incluir, clique em **Adicionar paciente**. Preencha os campos obrigatórios. CPF e telefone aceitam somente números e já saem formatados; o CPF precisa ter 11 dígitos válidos e não pode estar repetido, e o telefone tem DDD + 8 dígitos (fixo) ou DDD + 9 dígitos (celular). O e-mail, quando informado, precisa ter @. O endereço é dividido em logradouro, número (ou S/N), complemento, bairro, cidade, estado e ponto de referência. Em **Alergias**, digite livremente as alergias separadas por vírgula.
- Salve. O sistema cria automaticamente um prontuário único para o paciente.
- Para remover um paciente, use **Excluir** e confirme. Quem nunca teve agendamento é apagado; quem tem histórico é arquivado, sai da lista e do agendamento, e pode voltar em **Ver arquivados → Restaurar**.
- Para alterar os dados, use **Editar**. Para abrir o histórico, use **Prontuário**; na recepção, a ação aparece como **Detalhes**.
- No prontuário, médico e administrador podem salvar anotações gerais e alergias. A linha do tempo apresenta consultas de diferentes médicos, com queixa, diagnóstico, conduta e quantidade de itens clínicos vinculados.

### Como vincular um convênio?

Abra **Cadastros → Planos dos pacientes** ou use **Vincular convênio** no paciente. Selecione paciente e convênio, informe carteirinha, data de adesão e situação. Um paciente pode ter vários convênios, mas não pode repetir o mesmo vínculo com uma operadora.

Não invente um CPF aleatório durante a apresentação: ele pode falhar na validação. Para ensaiar o fluxo clínico, use um dos pacientes fictícios já cadastrados.

## Agendar, confirmar, cancelar e registrar faltas

Agendamento e situação: administrador / recepção · Atendimento: administrador / médico
- Abra **Agenda → Novo agendamento** ou **Agendar consulta** no Início.
- Escolha o paciente e o médico. O formulário auxilia a seleção de especialidade e unidade, mas a validação definitiva ocorre no servidor.
- Informe uma data e um horário terminado em **:00 ou :30**. Cada slot possui 30 minutos. Adicione observações se necessário.
- Clique em **Confirmar agendamento**. O sistema rejeita conflito de horário do médico ou do paciente e combinações inválidas de médico, unidade e especialidade.
- Na agenda, filtre por data, situação, paciente ou médico. Para ver faltas, escolha **Não compareceu**.
- Nos agendamentos ativos, selecione uma nova situação e clique em **Aplicar**. A recepção pode confirmar, cancelar ou registrar ausência.
- Para registrar o atendimento, médico ou administrador usa **Atender**. A situação **Realizado** é atribuída quando a consulta é salva.

Agendamentos cancelados, faltantes ou já realizados não podem gerar uma nova consulta. Não há botão de reagendar nesta versão: cancele o horário antigo e crie um novo, preservando o histórico.

## Registrar uma consulta e consultar o histórico

Administrador / médico
- Na Agenda ou no Início, abra um agendamento ativo e selecione **Atender / Iniciar atendimento**.
- Observe os alertas de alergia. Preencha **Queixa principal, Diagnóstico e Conduta adotada**. Observações médicas são opcionais.
- Clique em **Registrar consulta**. O sistema cria o atendimento e marca o agendamento como Realizado na mesma transação.
- A página da consulta reúne registro clínico, exames, prescrições e procedimentos. Os botões de inclusão ficam nessa página.
- Para voltar depois, abra **Consultas**, busque paciente ou médico e use **Abrir consulta**. O médico só abre para edição os seus próprios atendimentos.
- Para a história completa do paciente, use **Ver prontuário**. O histórico é consolidado, mesmo quando outros médicos fizeram os atendimentos.

Não existe edição do texto de uma consulta já salva pela interface. O protótipo mantém o registro original. Um sistema clínico operacional precisaria de retificação e versionamento auditáveis.

## Solicitar e acompanhar um exame

Administrador / médico
- Abra uma consulta. Em **Exames solicitados**, escolha um exame e clique em **Adicionar solicitação**.
- O pedido recebe a situação **Solicitado** e fica vinculado à consulta e, por ela, ao paciente.
- Abra a aba **Exames**. Filtre pelo paciente ou por **Somente pendentes**.
- Expanda **Atualizar solicitação**. Escolha Agendado, Realizado ou Cancelado, conforme o caso.
- Para concluir como Realizado, informe a data de realização e o resultado. A data precisa estar entre a solicitação e hoje.
- Clique em **Salvar acompanhamento**. Exames realizados ou cancelados deixam de ser pendências e ficam preservados no histórico.

O catálogo de tipos de exames fica em **Cadastros → Catálogo de exames**. Ele é diferente das solicitações de um paciente. Não há upload de laudos nem integração com laboratório; o resultado é registrado em texto.

## Prescrever vários medicamentos em uma consulta

Administrador / médico
- Abra uma consulta e expanda **Criar prescrição com medicamentos**.
- Selecione um medicamento e informe quantidade, dose, frequência e duração. Observações do item são opcionais.
- Use **Adicionar outro medicamento** para criar novos itens. O formulário aceita até oito itens por prescrição.
- Preencha as observações gerais, se necessário, e clique em **Salvar prescrição**.
- A prescrição aparece na própria consulta com todos os itens e suas posologias. Uma consulta pode ter várias prescrições.

O catálogo fica em **Cadastros → Medicamentos**. O princípio ativo, o fabricante e a apresentação pertencem ao catálogo. Quantidade, dose, frequência e duração pertencem ao item de cada prescrição.

A impressão da consulta não é uma receita eletrônica assinada ou válida para uso clínico.

## Registrar execução e valor efetivo

Administrador / médico
- Abra uma consulta e expanda **Registrar procedimento**.
- Escolha o procedimento. A interface sugere o valor padrão do catálogo.
- Selecione o profissional responsável, que deve atender na unidade da consulta. Ele pode ser médico ou outro profissional cadastrado, como enfermeiro.
- Informe a data e o valor efetivamente cobrado. A data não pode ser anterior à consulta ou futura.
- Salve. O valor efetivo fica preservado, mesmo que o preço padrão seja alterado posteriormente.

Registrar o procedimento não cria cobrança automaticamente. O financeiro deve emitir a cobrança dos serviços correspondentes, evitando duplicar valores implicitamente.

## Cobrar, receber e acompanhar saldos

Administrador / financeiro

### Criar cobrança

- Abra **Financeiro → Nova cobrança**.
- Selecione a consulta de origem e informe descrição, total e vencimento.
- Para particular, deixe o convênio em Particular e a cobertura em zero. Para convênio, selecione uma operadora com vínculo ativo no paciente e informe quanto ela cobre.
- Clique em **Salvar cobrança**. A parte do paciente será calculada como total menos cobertura.

### Registrar pagamento

- Na cobrança, expanda **Gerenciar**.
- Confira os saldos do paciente e do convênio. Informe valor, forma de pagamento, situação e data.
- Use PIX, Dinheiro, Cartão de crédito ou débito para a parte do paciente. Use **Convênio** para a cobertura da operadora.
- Clique em **Registrar pagamento**. Só a situação **Pago** reduz o saldo e entra nos recebimentos.
- Um pagamento Pendente pode ser alterado para Pago ou Cancelado. Um pagamento já Pago não possui fluxo de estorno nesta versão.

**Exemplo:** cobrança de R$ 200, cobertura de R$ 120 e parte do paciente de R$ 80. Registre R$ 80 por PIX e R$ 120 como Convênio: o saldo passa a zero. Não é possível pagar acima do saldo de cada responsável.

Para encontrar pendências, escolha **Somente com saldo pendente** e clique em Filtrar. A tela informa o paciente, o vencimento e se a cobrança está em atraso. O sistema registra pagamentos; ele não movimenta dinheiro ou faz uma cobrança bancária real.

## Interpretar os indicadores corretamente

Administrador / financeiro
- Abra **Relatórios** e escolha data inicial e final. Opcionalmente, filtre médico, especialidade e unidade.
- Clique em **Aplicar**. Confira os totais, o gráfico de consultas e as tabelas por médico, especialidade e unidade.
- **Faturamento emitido** soma cobranças pela data de criação. **Recebimentos** soma pagamentos Pago pela data do pagamento. Os valores podem ser diferentes.
- A quantidade de consultas considera atendimentos realizados na data do atendimento, independentemente de pagamento.
- Mais abaixo, veja os procedimentos realizados no período, com paciente, responsável e valor efetivo.
- Use **Exportar CSV** para baixar os dados dos agrupamentos financeiros e da quantidade de consultas, ou **Imprimir relatório** para imprimir a página pelo navegador.

Os filtros usam datas inclusivas. Uma cobrança emitida em um mês e recebida em outro entra em períodos diferentes nos dois indicadores.

## A estrutura que sustenta os atendimentos

Abra **Cadastros** no menu. Para incluir, use o botão de adicionar; para corrigir dados, use **Editar**. Os perfis sem permissão de alteração veem somente a lista.

| Cadastro | O que mantém | Como se conecta |
| --- | --- | --- |
| Especialidades | Nome e descrição da área médica. | Vinculada a médicos e unidades. |
| Unidades | Endereço, telefone, funcionamento e especialidades. | Define onde o atendimento pode ocorrer. |
| Profissionais | Dados, categoria, registro, CRM/UF, especialidades e unidades. | Médico precisa de CRM, UF e uma ou mais especialidades. |
| Convênios | Nome, CNPJ e contato da operadora. | Operadora compartilhada entre vários pacientes. |
| Planos dos pacientes | Paciente, operadora, carteirinha, adesão e situação. | Guarda os dados próprios do vínculo. |
| Alergias | Nome e descrição. | Vinculadas ao paciente no prontuário ou cadastro. |
| Catálogo de exames | Nome, descrição e tipo. | Usado ao criar uma solicitação em uma consulta. |
| Medicamentos | Nome, princípio ativo, fabricante e apresentação. | Usado nos itens das prescrições. |
| Catálogo de procedimentos | Nome, descrição e valor padrão. | Usado ao registrar execuções em consultas. |

### Registro de atividades e Sobre o projeto

O administrador encontra **Registro de atividades** no menu Cadastros. A tela mostra as últimas 200 alterações bem-sucedidas com usuário, data e ação. Não é um sistema completo de auditoria clínica imutável.

**Sobre o projeto** explica a arquitetura e oferece documentação, diagramas e guia de apresentação em PDF, além do link para o código no GitHub. O tutorial também está acessível pelo rodapé de todas as páginas.

## Uma apresentação de 8 a 10 minutos

- **Acesse como administrador.** Mostre o Início, a seleção de dia e o cartão de atendimento. Explique que os perfis têm acessos diferentes.
- **Abra Ana Clara Martins em Pacientes.** Mostre convênio, alergia e histórico. Explique o prontuário único e os relacionamentos muitos para muitos.
- **Abra um agendamento ativo na Agenda.** Registre queixa, diagnóstico e conduta. Salve e mostre a situação Realizado.
- **Na consulta recém-criada,** solicite um exame, crie uma prescrição com dois medicamentos e registre um procedimento com preço diferente do padrão.
- **No Financeiro,** crie uma cobrança de R$ 200 para essa consulta com cobertura de R$ 120 do convênio ativo de Ana. Registre PIX de R$ 80 e Convênio de R$ 120 e confira saldo zero.
- **Abra Relatórios.** Filtre a data de hoje e explique faturamento emitido versus recebimentos. Mostre agrupamentos e procedimentos.
- **Termine com a arquitetura:** navegador envia formulário → Flask identifica a rota → serviços validam regras → SQLAlchemy grava no banco → Jinja devolve a página. No deploy, o banco persistente é PostgreSQL.

Ensaie antes. Um agendamento já atendido não pode ser atendido novamente. Se necessário, crie outro horário livre; não use dois atendimentos do mesmo médico ou paciente no mesmo slot. Os dados da demonstração mudam quando você testa.

## O que foi testado e o que não se deve prometer

A suíte de integração verifica telas, acesso por perfil, CSRF, CPF, prontuário automático, conflito de agenda, bloqueio de cancelamentos inválidos e o fluxo clínico-financeiro. O fluxo publicado também foi testado de ponta a ponta. Isso não garante ausência de erros em todos os dispositivos, situações ou operações simultâneas.

- Não há recuperação de senha, gestão completa de usuários, integrações de laboratório ou operadoras, assinatura digital de receita, pagamento bancário, envio de mensagens ou upload de laudos.
- O sistema não exclui registros clínicos ou financeiros pela interface; cancelamentos preservam o histórico.
- Não há retificação de consulta salva nem estorno de pagamento Pago pela interface.
- A agenda usa slots fixos de 30 minutos. A verificação atual de conflitos na aplicação precisa de proteção adicional para concorrência elevada em operação real.
- Este é um protótipo acadêmico com dados sintéticos. Não é um sistema validado para atendimento clínico real.
- As sprints e os papéis propostos na documentação precisam corresponder ao que o grupo realmente realizou.

Se um formulário for rejeitado, leia a mensagem, use **Voltar e corrigir** e revise os campos. Sessão expirada pede novo acesso; falta de permissão pede o perfil correto; ausência de resultados pede conferir os filtros.
