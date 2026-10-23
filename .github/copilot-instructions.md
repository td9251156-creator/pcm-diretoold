# Orientações do PCM Direto para o Copilot

Siga `AGENTS.md`, as decisões atuais e `docs/FILA.md`. Trabalhe em português do Brasil.
Escolha uma tarefa pronta e pequena por ramo/PR. Se uma definição técnica ou conta externa
estiver pendente, registre o bloqueio e avance somente no trabalho independente autorizado.

Mantenha a gestão da fábrica local. O catálogo Supabase é separado e recebe apenas campos
explicitamente preenchidos para contribuição. Não envie inventário, TAGs, pessoas, falhas,
execuções ou backups. Não inclua credenciais nos arquivos, prompts, logs ou testes.

Preserve tarefas de segurança, backups antigos, recuperação de dados e funcionamento offline.
Não crie templates Excel/Word neste repositório; o mantenedor os fornecerá a partir de
`docs/PROMPT-CLAUDE-TEMPLATES.md`. Não invente referências normativas ou indicadores.

Para cada alteração, execute `npm run verificar`; quando afetar telas, armazenamento ou
exportação, execute `npm run test:navegador`. Para o catálogo, execute também
`npm run test:catalogo:navegador` e `npm run test:catalogo:banco` conforme seus pré-requisitos.
Use dados fictícios e registre verificações não executadas. Solicite revisão independente.

Não faça merge ou publicação sem autorização aplicável. Não ative API de IA, gasto excedente,
agendas de agentes ou serviços pagos. Copilot Student depende do resgate e da franquia da conta;
este arquivo configura orientações, não habilita uma assinatura ou execução permanente.
