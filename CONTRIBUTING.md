# Como contribuir

Obrigado pelo interesse no PCM Direto. Toda ajuda é bem-vinda, principalmente de quem trabalha com manutenção.

## Formas de ajudar

- **Biblioteca técnica:** sugerir, corrigir ou detalhar tarefas em `src/dados/biblioteca.json`.
  Siga o formato descrito em [BIBLIOTECA.md](BIBLIOTECA.md).
- **Problemas:** abrir uma *issue* descrevendo o que aconteceu, o que era esperado e como repetir.
- **Código:** corrigir erros ou melhorar telas, mantendo o projeto simples.

## Regras que não mudam

1. Preserve a gestão local. O catálogo Supabase é separado e só recebe contribuições explícitas.
2. Nenhuma referência a norma sem fonte oficial, com versão e data. Na dúvida, escreva "verificar na fonte oficial".
3. Nenhuma promessa de conformidade, de aprovação em auditoria ou de ganho.
4. O aviso permanente continua visível em todas as telas.
5. Tarefas de segurança não podem ser afrouxadas pelo usuário.
6. Use apenas dados fictícios. Nunca envie dados, planilhas ou documentos de empresas.

## Passo a passo para código

1. Faça um *fork* e crie um ramo: `git checkout -b minha-melhoria`.
2. Rode `npm ci`, depois `npm run verificar` antes de enviar.
3. Escreva o código e os comentários em português, de forma simples.
4. Abra um *pull request* explicando o antes e o depois.

Para desenvolvimento com agentes, siga [AGENTS.md](AGENTS.md), a
[estratégia de evolução](docs/EVOLUCAO-CONTINUA.md) e a [fila atual](docs/FILA.md).

Ao contribuir, você concorda que sua contribuição será publicada sob a [licença MIT](LICENSE)
e que seguirá o [Código de Conduta](CODE_OF_CONDUCT.md).


## Catálogo colaborativo: direção autorizada em 22/10/2026

A restrição anterior de ausência de login/banco é substituída somente para o catálogo público
de modelos reutilizáveis. A gestão da fábrica continua local e não é sincronizada. Contribuições
explícitas usam Supabase Auth/PostgreSQL, com revisão antes da publicação. Código preparado
não significa serviço online ativado. Consulte [configuração do catálogo](docs/CATALOGO-COLABORATIVO.md) e [ativação dos benefícios](docs/ATIVACAO-STUDENT.md).
