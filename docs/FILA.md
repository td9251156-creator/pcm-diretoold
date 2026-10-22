# Fila de evolução

Esta é a fila atual. [MELHORIAS.md](MELHORIAS.md) guarda o diagnóstico e as entregas anteriores.
O processo de trabalho está em [EVOLUCAO-CONTINUA.md](EVOLUCAO-CONTINUA.md).
Uma implementação por vez. Um item só termina com evidência e revisão independente.

| ID | Prioridade | Problema e resultado esperado | Critério de conclusão | Situação |
|---|---|---|---|---|
| F-001 | Alta | Organizar trabalho por agentes e impedir publicação manual de ramos não integrados. | Instruções, fila e revisão independente registradas; testes aprovados; execução manual fora da main pula a publicação. | [PR #18](https://github.com/td9251156-creator/pcm-direto/pull/18) integrado; revisão semanal executada e aprovada. |
| F-002 | Alta | Tornar o teste de navegador totalmente previsível: fixar a ferramenta de teste, recusar porta já ocupada e limitar a espera pelo serviço offline. | Uma porta ocupada e um serviço offline que não inicia falham com mensagem e tempo limite; ferramentas só de teste, separadas do aplicativo. | Implementado e revisado: ferramenta isolada com lockfile, oito testes de regressão e roteiro real aprovados. |
| F-003 | Média | Executar a conferência de navegador na rotina automática após F-002. | Fluxos de celular, backup, checklist e geração offline rodando em máquina limpa; falhas bloqueiam a revisão. | [PR #22](https://github.com/td9251156-creator/pcm-direto/pull/22) integrado; navegador aprovado na revisão semanal e antes da publicação. |
| F-004 | Média | Conferir leitor de tela, celular real e arquivos no Excel antigo. | Registrar aparelho/programa e versão, passos e resultado; corrigir problemas encontrados sem usar dados reais. | Aguardando acesso aos aparelhos/programas. |
| F-005 | Média | Definir cálculo de MTBF, MTTR e disponibilidade, item 14 do diagnóstico. | Mantenedor define funcionamento, falha, reparo, período e tratamento de paradas planejadas; exemplos numéricos aprovados antes de implementar. | Aguardando definição técnica. |
| F-006 | Média | Definir janelas e paradas programadas, item 15 do diagnóstico. | Mantenedor aprova exemplos e limites; nenhuma tarefa de segurança pode ser adiada fora da regra definida. | Aguardando definição técnica. |
| F-007 | Média | Preservar o foco de teclado ao ajustar a capacidade por especialidade na Revisão. O redesenho do quadro remove o campo focado após a primeira seta. | Setas consecutivas continuam ajustando o mesmo campo; Tab segue a ordem normal sem recuperar foco indevidamente; capacidade, carga e salvamento permanecem corretos; regressão coberta por teste. | Implementado e revisado; 150 testes e Chromium aprovados. |


## Templates PCMD — uma etapa por tarefa e PR

O plano em [PLANO-TEMPLATES.md](PLANO-TEMPLATES.md) registra decisões e verificações.
Não integrar nem publicar automaticamente. Exportações atuais continuam disponíveis.

| ID | Etapa | Resultado e critério de conclusão | Situação |
|---|---|---|---|
| T-01 | 1 | PCMD-02: ativos, criticidade, quatro abas, fórmulas/cache testados e download offline. | Implementado e revisado; 176 testes, Chromium offline e 81 comparações externas aprovados. Aguardando revisão do PR pelo mantenedor. |
| T-02 | 2 | PCMD-03: Plano Mestre único, frequências, segurança e próximas execuções verificadas. | Aguarda T-01 e nova tarefa. |
| T-02A | 2A | Histórico completo e aba Execuções; marcas antigas preservadas, backups compatíveis. | Aguarda T-02. |
| T-03 | 3 | PCMD-04: janeiro–dezembro, carga derivada das semanas e realizado por ocorrência. | Aguarda T-02A. |
| T-04 | 4 | PCMD-05: registro mínimo de falhas vinculado aos ativos. | Aguarda T-03. |
| T-05 | 5 | PCMD-01: lista dos documentos disponíveis e revisões. | Aguarda T-04. |
| T-06 | 6 | Completar abas de apoio, M1–M6, Revisões e guias. | Aguarda T-05. |
| T-06A | 6A | Importar planilha com prévia, confirmação, recálculo e recuperação em falhas. | Aguarda T-06. |
| T-07 | 7 | W1: manual original com referências e dados importados, sem promessa de conformidade. | Aguarda T-06A. |
| T-08 | 8 | W2: estratégia e revisão; metas e prazos indefinidos continuam a definir. | Aguarda T-07. |
| T-09 | 9 | Biblioteca com campos compatíveis e checklist atualizado, sem afrouxar segurança. | Aguarda T-08. |
| T-10 | 10 | Fórmulas, arquivos, termos proibidos e roteiro final conferidos. | Aguarda T-09. |

Excel 2010 e impressão física: validação manual pendente. Em 22/10, a conversão padrão
preservou um cache incorreto. Com perfil isolado e OOXMLRecalcMode=0, a prova pequena corrigiu
−1 para 12 e as 81 comparações das fórmulas reais passaram, após alterar entradas e limites.
O comando `npm run verificar:recalculo-pcmd` reproduz essa prova quando há LibreOffice.

## F-007 — primeira tarefa da execução por agentes

- **Evidência:** em 20/10/2026, no Chromium, abrir Revisão com o exemplo fictício e focar
  `#cap-Operação`. Após `ArrowUp`, o valor passa a `0.5`, mas `document.activeElement` passa
  de `INPUT#cap-Operação` para `BODY`. A segunda seta não ajusta o campo. O evento `change`
  em `src/telas/revisao.js` substitui todo o conteúdo de `#carga`, removendo o elemento focado.
- **Impacto:** quem usa teclado precisa localizar e focar o campo de novo a cada ajuste.
- **Resultado:** manter o foco da mesma especialidade se a atualização acontecer com o campo
  ainda focado. Não puxar o foco de volta quando a alteração tiver sido confirmada por Tab ou blur.
- **Escopo:** `src/telas/revisao.js`, eventual auxiliar JavaScript de interface e teste de regressão
  JavaScript em `testes/`; atualizar esta fila. Não mudar regras de capacidade, biblioteca técnica,
  dados salvos, dependências ou automações. Uma implementação pequena, dentro dos limites do executor.
- **Como conferir:** a partir do campo vazio, duas setas para cima devem chegar a `1.0` com foco
  no mesmo campo; uma seta para baixo retorna a `0.5`. Tab segue para o próximo controle sem
  reiniciar a navegação. Conferir atualização da carga e persistência ao reabrir a tela. Um teste
  relevante deve reproduzir a perda de foco antes e passar depois; executar também as verificações
  completas e o roteiro de navegador existentes.
- **Diagnóstico:** agente separado, somente leitura, com reprodução no Chromium. A proposta do executor recebeu correção complementar nesta sessão: aguardar a navegação do Tab
  antes de redesenhar e preservar o destino escolhido pelo navegador. Foram acrescentados testes
  de Tab e desmontagem da tela e uma regressão no roteiro real do Chromium. Os novos testes
  falharam antes da correção. Lint, 150 testes, build e roteiro de navegador aprovados localmente,
  com revisão independente. A entrega deve seguir por PR revisado e ter publicação conferida;
  testes locais sozinhos não comprovam disponibilidade no site.

## Modelo para adicionar um item

- **Problema e evidência:** o que aconteceu e como reproduzir com dados fictícios.
- **Impacto:** quem é afetado e o que deixa de conseguir fazer.
- **Resultado esperado:** comportamento observável, sem escolher uma reescrita antecipadamente.
- **Escopo:** arquivos ou parte do produto; registrar também o que fica para depois.
- **Critérios de conclusão:** verificações que podem falhar se a mudança estiver incorreta.
- **Dependências e decisões:** o que precisa existir antes de começar.
- **Responsável e revisão:** coordenador, implementador e revisor; registrar apenas quem participou.
- **Evidência:** PR, resultado dos testes e limitações reais.

Não abrir tarefas públicas com dados pessoais, segredos ou detalhes de falhas de segurança ainda sem correção.

## Evidência da primeira rodada com agentes

- Coordenação e implementação delimitada, com um agente preparando as instruções e outro fazendo revisão independente somente leitura.
- Instalação, `npm run verificar`, 133 testes e roteiro `npm run test:navegador` aprovados.
- Auditoria de dependências em 20/10/2026: nenhum alerta informado pelo serviço.
- [Execução manual fora da main](https://github.com/td9251156-creator/pcm-direto/actions/runs/39420496553): verificação aprovada e publicação pulada.
- A revisão semanal e as propostas do Dependabot estão configuradas na main. [Primeira revisão semanal](https://github.com/td9251156-creator/pcm-direto/actions/runs/39421631200) executada com sucesso; as próximas agendas dependem das condições do GitHub.

## Rodada de ativação das rotinas

- Playwright e Chromium preparados com versão fixada e lockfile separado do app. As dependências de produção não mudaram.
- 141 testes de lógica e infraestrutura aprovados; roteiro completo no navegador aprovado com a ferramenta fixada.
- Revisão independente dos workflows, prazos, fechamento de recursos e correção da espera entre rotas.
- Dependabot já gerou propostas no repositório; nenhuma atualização é integrada sem a revisão aplicável.
- Modo escolhido: tarefas do Codex com login do ChatGPT Plus. O Actions continua com testes, auditorias e publicação; o fluxo de IA por API foi desativado no GitHub e fica sem agenda, com pausa explícita no código. Veja [AGENTES-GITHUB-ACTIONS.md](AGENTES-GITHUB-ACTIONS.md).
- [Diagnóstico após cadastro da chave](https://github.com/td9251156-creator/pcm-direto/actions/runs/39499911020):
  o Actions recebeu `OPENAI_API_KEY`; modelo ausente e ativação desabilitada. Não houve chamada à IA,
  portanto validade da chave, saldo e acesso ao modelo ainda não foram testados. Tentativas de salvar
  as duas variáveis pela integração retornaram HTTP 403; precisam ser cadastradas nas configurações do GitHub.
