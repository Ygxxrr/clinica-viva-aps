# Clínica Viva

Sistema acadêmico de gestão de clínica médica desenvolvido para Análise e Projeto de Sistemas II. Integra pacientes, agenda, prontuários, exames, prescrições, procedimentos, convênios e financeiro.

Sistema publicado: **https://clinica-viva-aps.vercel.app**

Repositório: **https://github.com/Ygxxrr/clinica-viva-aps**

Materiais PDF ficam em `public/downloads/` e também podem ser abertos em **Sobre o projeto**.

## Executar no Windows

Requer Python 3.12 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe app.py
```

Abra `http://127.0.0.1:5000`. O banco SQLite local é criado em `instance/clinica.db`. Também é possível usar PostgreSQL configurando `DATABASE_URL` no `.env`.

## Perfis de demonstração

Senha para todos: `Clinica2026!`.

| Perfil | E-mail | Acesso |
|---|---|---|
| Administrador | admin@clinica.demo | Todos os módulos |
| Recepção | recepcao@clinica.demo | Pacientes, convênios e agendamentos |
| Médico | medico@clinica.demo | Agenda própria, atendimentos próprios e histórico dos pacientes |
| Financeiro | financeiro@clinica.demo | Cobranças, pagamentos e relatórios |

Dados inteiramente fictícios. O modo demonstrativo divulga intencionalmente suas contas. Não usar com pacientes reais. Este protótipo não substitui um sistema clínico homologado e não implementa assinatura digital de receitas, integrações com operadoras ou obrigações regulatórias de uma operação real.

## Funcionalidades

- Cadastro e edição de pacientes, profissionais, especialidades, unidades, convênios, alergias, exames, medicamentos e procedimentos.
- Prontuário único por paciente, histórico completo de consultas e alergias.
- Vínculo paciente–convênio com carteirinha, adesão e situação.
- Relações muitos para muitos entre médicos/especialidades, profissionais/unidades e unidades/especialidades.
- Agenda com horários de 30 minutos, validação de conflito e situação de atendimento.
- Atendimento com queixa, observações, diagnóstico e conduta.
- Solicitações de exames, acompanhamento, realização e resultado.
- Várias prescrições por consulta e até oito medicamentos por formulário de prescrição.
- Procedimentos com profissional, data e preço efetivo independente do preço padrão.
- Cobranças e pagamentos parciais com responsabilidade separada do paciente e do convênio.
- Faturamento emitido, recebimentos e quantidade de consultas por período/médico/especialidade/unidade.
- Filtro de pendências, exportação CSV e impressão de relatórios.
- Sessão autenticada, senhas com hash, autorização no servidor, CSRF, escape HTML e registro de operações.

## Arquitetura

```text
Navegador (HTML, CSS e JavaScript)
              │ requisição HTTP
              ▼
app.py (rotas, sessão, autorização)
              │
              ▼
services.py (regras de negócio)
              │
              ▼
models.py + SQLAlchemy (ORM)
              │ consulta parametrizada / transação
              ▼
SQLite local / PostgreSQL externo
              │
              └── Jinja renderiza a resposta HTML
```

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Ponto de entrada Flask, rotas, autenticação e relatórios |
| `models.py` | Classes do domínio, relacionamentos e restrições |
| `services.py` | Validações e operações transacionais |
| `catalog.py` | Metadados compartilhados dos cadastros |
| `seed.py` | Carga inicial de dados fictícios |
| `clock_local.py` | Datas de negócio em America/Sao_Paulo |
| `templates/` | Páginas renderizadas com Jinja |
| `public/` | CSS, JavaScript e favicon |
| `tests/test_system.py` | Testes HTTP e de regras de negócio |
| `docs/` | Requisitos, Scrum, diagramas e roteiro de apresentação |

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes usam um SQLite em memória isolado, sem alterar o banco da demonstração. Validam renderização das telas, permissões, CSRF, CPF, duplicidade, prontuário, conflitos, cancelamento, exames, prescrições, procedimentos e pagamentos.

## Publicar na Vercel

O Flask é detectado pelo `app.py`. `public/` contém os arquivos estáticos servidos pela CDN. O banco precisa ser externo: o filesystem das funções não serve para persistir SQLite.

1. Crie um PostgreSQL gratuito compatível (por exemplo, Neon) e obtenha a conexão com SSL.
2. Gere uma `SECRET_KEY` forte. Exemplo: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Configure localmente `DATABASE_URL`, `SECRET_KEY` e `DEMO_MODE=true` no `.env`, sem versionar esse arquivo.
4. Inicialize o PostgreSQL: `python -m flask --app app init-db`.
5. Na Vercel, importe o repositório GitHub e configure as mesmas variáveis em Production e Preview, quando usar ambos.
6. Publique e teste o login, uma gravação e `/health`.

Exemplo de conexão: `postgresql+psycopg://USUARIO:SENHA@HOST/BANCO?sslmode=require`. Use a conexão com pool de conexões recomendada pelo provedor. Nunca salve segredos no repositório.

Referência: [Flask na Vercel](https://vercel.com/docs/frameworks/backend/flask).

## Decisões e limites explícitos

- Consultas sempre derivam de um agendamento. A identificação de paciente, médico, especialidade e unidade é obtida desse vínculo, sem duplicar colunas na consulta.
- O paciente de uma solicitação de exame é obtido pela consulta de origem. Isso evita divergência entre dois identificadores de paciente.
- A cobrança é o valor devido; o pagamento é a movimentação financeira. Pagamento pendente ou cancelado não entra nos recebimentos.
- Registrar um procedimento não cria cobrança automaticamente. O financeiro cria uma ou mais cobranças para os serviços realizados, evitando faturamento duplicado implícito.
- O faturamento usa a data de emissão das cobranças; os recebimentos usam a data dos pagamentos pagos.
- Uma consulta pode ter nenhuma ou várias prescrições. Cada prescrição tem seus próprios itens.
- Não há envio de mensagens, pagamento bancário real, integração de laboratório ou upload de laudos: exames e pagamentos são registros internos.
- Não há exclusão de registros clínicos/financeiros. Situações de cancelamento preservam o histórico.
- A inicialização usa `create_all`; mudanças posteriores de esquema exigem migrações antes de uso continuado. Não há promessa de operação real, conformidade regulatória, backups automatizados ou monitoramento clínico.

## Documentação

- [Análise e requisitos](docs/ANALISE.md)
- [Rastreabilidade dos 45 pontos](docs/RASTREABILIDADE.md)
- [Scrum e planejamento](docs/SCRUM.md)
- [Diagrama de classes](docs/CLASSES.md)
- [Casos de uso](docs/CASOS_DE_USO.md)
- [Guia de apresentação e perguntas](docs/APRESENTACAO.md)

As sprints e os papéis propostos precisam ser adaptados à composição real do grupo. O documento não inventa integrantes, reuniões ou trabalho em datas anteriores.

## Regenerar a documentação

Instale `requirements-docs.txt` para gerar os PDFs com `python scripts/generate_documents.py`. As fontes UML e DOT podem ser atualizadas com `python scripts/generate_diagrams.py`. Os SVGs já renderizados estão incluídos no projeto.
