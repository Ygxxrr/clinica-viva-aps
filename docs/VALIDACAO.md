# Registro de validação — 26/10/2026

## Ambiente local

- Python 3.12, Flask e SQLite em memória para os testes.
- Comando: `python -m unittest discover -s tests -v`.
- Resultado: 10 testes aprovados.
- Todas as telas e formulários de cadastro foram renderizados pelo cliente de testes.
- Cenários: autorização por perfil, CSRF, CPF inválido/duplicado, prontuário automático, conflito de agenda, bloqueio de agendamento cancelado, exame, prescrição com dois medicamentos, procedimento com valor efetivo, cobrança, pagamento parcial, saldo e escape HTML.

## Ambiente publicado

- URL: https://clinica-viva-aps.vercel.app
- Hospedagem: Vercel, aplicação Flask.
- Persistência: PostgreSQL Neon, plano Free, região São Paulo (gru1).
- Rota `/health`: HTTP 200, banco conectado.
- Login público do administrador validado no navegador.
- CSS e JavaScript publicados responderam HTTP 200.
- Repositório GitHub conectado ao projeto Vercel.

## Fluxo real de demonstração validado no navegador

1. Criado um agendamento fictício para Ana Clara Martins, Dra. Helena Costa, Cardiologia, Unidade Centro, em 26/10/2026 às 17h.
2. Confirmada a persistência desse registro diretamente no PostgreSQL.
3. Registrada a consulta #19 com diagnóstico e conduta explicitamente sintéticos; agendamento passou para Realizado.
4. Solicitado Hemograma completo vinculado à consulta.
5. Criada prescrição com dois medicamentos demonstrativos e posologias de exemplo.
6. Registrado Curativo simples com Enf. Marina Lopes por R$ 65,00, preservando o valor padrão de R$ 80,00 no catálogo.
7. Criada cobrança #19 de R$ 200,00: paciente R$ 80,00, convênio R$ 120,00.
8. Registrado pagamento de R$ 80,00 por PIX e R$ 120,00 por Convênio.
9. Verificado saldo zero e situação Pago.
10. Verificado relatório com R$ 5.950,00 de faturamento emitido, R$ 4.000,00 recebidos e 19 consultas na data do teste.

Esses números são da carga demonstrativa após a validação e podem mudar com novas operações. Não representam finanças ou atendimentos reais. A marcação das 17h foi usada como cenário didático; o registro do atendimento guarda o horário efetivo do teste.

## Documentação

- Documentação analítica: 16 páginas.
- Guia de apresentação: 5 páginas.
- Diagramas: 6 páginas, incluindo a visão completa e divisões por domínio.
- PDFs renderizados e revisados visualmente.
- SVGs mantêm qualidade vetorial para ampliar os diagramas.

## Limites dos testes

Não houve teste de carga, teste de concorrência, auditoria independente de segurança nem validação regulatória de prontuário. Os testes automatizados usam SQLite; o fluxo manual publicado foi validado com PostgreSQL. O protótipo usa contas públicas de demonstração e deve receber exclusivamente dados fictícios.
