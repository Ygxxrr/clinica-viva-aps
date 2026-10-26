# Interface Roxo Aurora

Direção visual escolhida pelo usuário para a Clínica Silva. O monograma CS foi preservado e recebeu a paleta violeta.

## Organização da interface

- Cabeçalho com marca, acesso ao tutorial e identificação do usuário.
- Menu compacto com rótulos e ícones, expandido pelo botão de menu em telas pequenas.
- Cadastros de apoio em um menu próprio, com todos os catálogos e acesso à auditoria para administrador.
- Início com faixa de indicadores, seletor de dias, lista de atendimentos e cartão do paciente selecionado.
- Seleção de data e de atendimento feita por leitura HTTP; os dados vêm do banco e respeitam o perfil.
- Atalhos de atendimento, prontuário e cadastro apontam para as rotas existentes.
- O financeiro possui uma visão geral própria, sem acesso indevido aos módulos clínicos.
- Tutorial acessível por Ajuda, Como usar e rodapé, com cópia PDF para estudo offline.

## Arquivos

- templates/base.html: estrutura de navegação compartilhada.
- templates/dashboard.html: estação de atendimento e visão financeira.
- templates/tutorial.html: tutorial completo, fonte principal para a versão offline.
- public/aurora.css: estilo compartilhado da identidade Aurora e responsividade.
- public/app.js: menu de cadastros, menu móvel e melhorias já existentes dos formulários.
- app.py: seleção de data/atendimento com restrição por médico; rota de tutorial.

Não houve troca de banco de dados, alteração de regras financeiras ou mudança dos relacionamentos clínicos para esta repaginação.
