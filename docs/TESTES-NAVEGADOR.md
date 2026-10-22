# Conferência no navegador

Os testes de lógica continuam em `npm test`. O roteiro abaixo usa uma cópia de teste do navegador,
dados fictícios e um servidor local que encerra ao terminar. Não acessa os dados do navegador pessoal.

A ferramenta fica em `ferramentas/navegador`, com versão exata e arquivo de versões próprio.
Não é carregada pelo aplicativo nem acrescenta dependências à versão publicada. Prepare e execute:

```bash
npm ci
npm ci --prefix ferramentas/navegador
node ferramentas/navegador/node_modules/playwright/cli.js install chromium
npm run verificar
npm run test:navegador
```

No GitHub Actions, a instalação usa `install --with-deps chromium` para preparar também as bibliotecas
do sistema. O roteiro roda em PRs, antes de publicar na main e na revisão semanal. Uma falha bloqueia
a publicação. A instalação e a auditoria da ferramenta são separadas das dependências do app.

Em máquina com outro Chromium, `PCM_CHROMIUM` permite selecionar seu caminho. `PCM_PLAYWRIGHT`
permite selecionar outra instalação da ferramenta para diagnóstico; a CI usa sempre a versão fixada.
Em contêiner que já isola o processo e exige execução sem a sandbox interna do Chromium, use
`PCM_SEM_SANDBOX=1` apenas para estes testes locais. Não use essa opção para sites desconhecidos.

Neste ambiente em nuvem, o cache do npm e o diretório de navegadores precisam ser graváveis:

```bash
npm ci --cache /workspace/.npm-cache
npm ci --prefix ferramentas/navegador --cache /workspace/.npm-cache
export PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/pcm-playwright
node ferramentas/navegador/node_modules/playwright/cli.js install chromium
npm run verificar
npm run test:navegador
```

O servidor é criado pela API do Vite com porta exclusiva: se outro processo já ocupar a porta 4175,
o roteiro falha, em vez de testar um servidor antigo. Navegação, prontidão do serviço offline e
execução completa têm limites de tempo. O navegador e o servidor são fechados também após falhas.

O roteiro confere navegação por teclado, largura de celular, importação inválida sem perda da
biblioteca, abertura sem conexão, geração de XLSX e DOCX sem internet e preservação de rascunho
danificado. Leitor de tela, aparelhos reais e Excel antigo ainda exigem conferência manual.

O roteiro também confere checklist após recarregar, download e restauração do backup, recuperação
da última máquina removida, filtros de impressão e aviso visível após falha simulada de gravação.

O roteiro também cobre cadastros e edição de pessoas, metas e referências, rascunhos de
formulários independentes, notas de criticidade, responsável por tarefa, registro/correção de
falhas, vínculo de execução ao mensal, cancelamento preservado e backup completo versão 2.
A Entrega lista modelos pendentes sem criar download de template novo.
