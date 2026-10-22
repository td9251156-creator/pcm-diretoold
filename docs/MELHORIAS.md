# Melhorias do PCM Direto

Diagnóstico de 20/10/2026, a partir da revisão `18e06e1`. Ordem de trabalho: erros e riscos,
qualidade, funções novas e melhorias de uso. Um assunto por pull request (PR); o mantenedor
revisa antes de publicar. Itens ainda não implementados não são promessas de entrega.

## Verificação inicial

- Leitura de README, decisões, roteiro, biblioteca, contribuição, segurança, código e testes.
- Base: 54 testes em 7 arquivos, lint e geração da versão final aprovados.
- `npm audit`: nenhum alerta informado pelo serviço em 20/10/2026; não substitui revisão do código.
- O app roda com Node.js 24 e sem serviço externo. O cache do npm neste ambiente deve ficar
  em `/workspace/.npm-cache`: `npm ci --cache /workspace/.npm-cache`.
- Esta rodada inclui conferência da importação no Chromium em tela de 390 × 844 pixels.
  Ainda falta avaliação com leitor de tela, aparelhos reais e Excel antigo.

## Erros e riscos — executar primeiro, nesta ordem

| Ordem | Problema e evidência | Impacto para quem usa | Esforço | Risco da mudança | Situação |
|---|---|---|---|---|---|
| 01 | Importar JSON válido, mas com estrutura errada, causa erro ao procurar tipos ou tarefas. Durações em texto e códigos de tipo repetidos também eram aceitos. | A importação para sem explicar o problema; dados incorretos podem afetar o plano. | Pequeno | Médio: arquivos fora do formato passam a ser recusados; preservar arquivos válidos e travas de segurança. | Implementado; [PR #1](https://github.com/td9251156-creator/pcm-direto/pull/1), integrado à main. |
| 02 | Ao reabrir o app, `carregar()` verifica apenas se existem listas no arquivo salvo. Não repete a validação completa da biblioteca nem do rascunho. | Dados locais incompletos podem impedir a abertura ou afetar o plano. | Médio | Alto: proteger a lista existente, sem apagar ou substituir dados silenciosamente. | Implementado; [PR #2](https://github.com/td9251156-creator/pcm-direto/pull/2), integrado à main. |
| 03 | `montarDados()` recebe todos os equipamentos, embora Revisão e Impressão digam que os que têm pendência ficaram fora. Um motor sem descrição ainda gera 8 tarefas no resumo. | Carga e impressão podem incluir equipamentos que a tela afirma ter excluído. | Pequeno | Médio: definir e aplicar a mesma lista válida em resumo, impressão e arquivos. | Implementado; [PR #3](https://github.com/td9251156-creator/pcm-direto/pull/3), integrado à main. |
| 04 | Na ativação, o service worker remove todos os caches de mesma origem que não sejam o atual. | Pode apagar o funcionamento offline de outro aplicativo no mesmo domínio. | Pequeno | Médio: apagar só caches pertencentes ao PCM Direto e testar atualização. | Implementado; [PR #4](https://github.com/td9251156-creator/pcm-direto/pull/4), integrado à main. |
| 05 | A versão do cache usa nomes dos arquivos, sem o conteúdo dos arquivos fixos de `public/`. | Uma alteração só no manifesto ou ícone pode não chegar a quem usa offline. | Médio | Médio: testar publicação nova, troca de versão e abertura sem conexão. | Implementado; [PR #5](https://github.com/td9251156-creator/pcm-direto/pull/5), integrado à main. |
| 06 | CSV com quebra de linha dentro de uma descrição exportada volta como dois equipamentos na importação. | A lista muda ao exportar e importar novamente. | Pequeno | Médio: manter separadores, aspas, acentos e cabeçalhos já aceitos. | Implementado; [PR #6](https://github.com/td9251156-creator/pcm-direto/pull/6), integrado à main. |
| 07 | Quando já existe número 999 no setor/tipo, a correção sugerida pode ser 1000, fora do limite aceito. | O botão de correção não resolve a pendência. | Pequeno | Baixo: procurar número livre e explicar quando os 999 estiverem ocupados. | Implementado; [PR #7](https://github.com/td9251156-creator/pcm-direto/pull/7), integrado à main. |
| 08 | `lerXlsx()` aceita linhas da primeira aba não vazia mesmo sem identificar uma tabela de equipamentos. | Uma capa de planilha pode virar equipamento em vez da aba correta. | Médio | Médio: preservar importação sem cabeçalho quando ela for intencional. | Implementado; [PR #8](https://github.com/td9251156-creator/pcm-direto/pull/8), integrado à main. |
| 09 | Falha ao gravar no navegador retorna `false`, mas as telas em geral continuam anunciando que os dados foram salvos. | A pessoa pode fechar o app acreditando que a lista está guardada. | Médio | Médio: mensagens claras e possibilidade de guardar cópia sem apagar o rascunho. | Implementado; [PR #9](https://github.com/td9251156-creator/pcm-direto/pull/9), integrado à main. |

## Qualidade — depois dos erros e riscos

| Ordem | Problema | Impacto para quem usa | Esforço | Risco da mudança | Situação |
|---|---|---|---|---|---|
| 10 | Faltam testes de carregar/salvar, falha de armazenamento e compatibilidade com rascunhos antigos. | Menos proteção contra perda de listas em atualizações. | Médio | Baixo: usar exemplos fictícios e armazenamento simulado. | Implementado; [PR #10](https://github.com/td9251156-creator/pcm-direto/pull/10), integrado à main. |
| 11 | Não há testes de troca de versão e funcionamento offline do PWA. | Falhas podem aparecer só depois de publicar. | Médio | Médio: testar caches e atualização sem mudar a biblioteca técnica. | Implementado; [PR #11](https://github.com/td9251156-creator/pcm-direto/pull/11), integrado à main. |
| 12 | Os testes atuais concentram-se na lógica; faltam verificações das telas por teclado e em celular. | Botões, foco e mensagens podem falhar mesmo com os testes atuais aprovados. | Médio | Baixo: começar com fluxos principais; avaliar ferramenta antes de adicionar dependência. | Implementado; [PR #12](https://github.com/td9251156-creator/pcm-direto/pull/12), integrado à main. |

## Funções novas — respeitar o roteiro

| Ordem | Proposta e problema atendido | Impacto para quem usa | Esforço | Risco da mudança | Situação |
|---|---|---|---|---|---|
| 13 | Etapa 2: checklist de execução por tarefa, começando por marcação e anotação de evidência fictícia, sem dados pessoais adicionais. | Registrar o que foi executado, além do planejamento. | Grande | Alto: definir armazenamento e limites; assinatura e fotos de pessoas exigem decisão do mantenedor diante da regra sobre dados pessoais. | Implementado; [PR #13](https://github.com/td9251156-creator/pcm-direto/pull/13), integrado à main. |
| 14 | Etapa 4: registro de falhas e indicadores MTBF, MTTR e disponibilidade. | Acompanhar o histórico de manutenção. | Grande | Alto: validar com o mantenedor definições de tempo de operação, parada e período antes de calcular. | Aguardando definição técnica do mantenedor, conforme o escopo combinado. |
| 15 | Etapa 5: paradas programadas e agrupamento de tarefas por janela. | Preparar serviços em períodos disponíveis. | Grande | Alto: não adiar tarefas de segurança; confirmar regras de janela com o mantenedor. | Aguardando definição técnica do mantenedor, conforme o escopo combinado. |

A Etapa 3 (normas) permanece fora desta rodada: somente com fonte oficial, versão, data e revisão
por profissional habilitado. Não ampliar tarefas técnicas ou periodicidades sem revisar origem e versão.

## Experiência de uso — após as prioridades acima

| Ordem | Proposta e problema atendido | Impacto para quem usa | Esforço | Risco da mudança | Situação |
|---|---|---|---|---|---|
| 16 | Backup e restauração da lista completa, ajustes e biblioteca em JSON; CSV não guarda tudo. | Levar o trabalho a outro aparelho e recuperar uma cópia. | Médio | Alto: validar antes de substituir; manter compatibilidade e confirmar a troca. | Implementado; [PR #14](https://github.com/td9251156-creator/pcm-direto/pull/14), integrado à main. |
| 17 | Desfazer a última remoção de equipamento. A confirmação já existe. | Recuperar um clique errado sem recadastrar os dados. | Médio | Médio: recuperar também os ajustes daquela máquina. | Implementado; [PR #15](https://github.com/td9251156-creator/pcm-direto/pull/15), integrado à main. |
| 18 | Filtros por setor/especialidade e instruções mais claras sobre semanas acima da capacidade. | Encontrar tarefas e entender limites sem precisar conhecer o sistema. | Médio | Médio: deixar claro o que está filtrado e não ocultar alertas de segurança. | Implementado; [PR #16](https://github.com/td9251156-creator/pcm-direto/pull/16), integrado à main. |

## Rodada 1 — importação de biblioteca

- Arquivos com estrutura incorreta são recusados com mensagem, antes de substituir a biblioteca atual.
- Códigos de tipos não podem repetir; códigos seguem o formato documentado.
- Descrição, especialidade, origem e versão exigem texto; duração exige número positivo e finito.
- Tipos novos sem tarefas e observação omitida continuam aceitos. As travas de segurança continuam ativas.
- O rascunho, as chaves de armazenamento, as periodicidades e as tarefas padrão não mudam.
- Validação final: `npm ci`, lint, 82 testes em 7 arquivos e build aprovados. Importação conferida
  no Chromium em 390 × 844: recusas sem erro de JavaScript e biblioteca válida mantida após recarregar.
- Ramo enviado: `correcao/validar-importacao-biblioteca`; a `main` não foi alterada.
- Revisão aberta: [PR #1](https://github.com/td9251156-creator/pcm-direto/pull/1).
- O item 02 e os demais itens concluídos nesta rodada estão relacionados abaixo e em [REVISOES.md](REVISOES.md).

## Rodada 2 — correções, proteção de dados e checklist

- Itens 02 a 12, primeira versão do item 13 e itens 16 a 18 implementados em ramos separados.
- Itens 14 e 15 ficam para definição das regras de indicadores e janelas pelo mantenedor. Não houve
  mudança normativa ou alteração de periodicidades técnicas. Fotos e assinaturas não foram incluídas.
- Verificação final: instalação, lint, 133 testes em 12 arquivos e build aprovados.
- Conferência no Chromium: tela de celular, teclado, importação, checklist após recarregar, backup
  e restauração, desfazer remoção, filtros, aviso de gravação, recuperação e geração offline de XLSX/DOCX.
- Os 16 PRs foram integrados à main por solicitação do mantenedor. A publicação é executada pelo fluxo do GitHub Pages.
- Leitor de tela, aparelhos reais e Excel antigo ainda precisam de conferência manual.

## Templates PCMD — etapa 1 (22/10/2026)

PCMD-02 acrescentado como exportação separada, com notas vazias, limites editáveis e
criticidade calculada sem alterar o cadastro ou as tarefas do app. Plano completo em
[PLANO-TEMPLATES.md](PLANO-TEMPLATES.md), fila T-01 a T-10 com etapas intermediárias.
Lint, 176 testes, build, Chromium (inclusive PCMD offline) e revisão independente aprovados.
LibreOffice com recálculo forçado corrigiu cache errado e conferiu 81 resultados após mudar
notas e limites. Conversão padrão sem recálculo não foi aceita como evidência.
Áreas de impressão, cabeçalhos repetidos e origem dos rodapés corrigidos na revisão.
PR aguardará o mantenedor: sem merge, publicação, consumo de API ou início da etapa 2.
Excel 2010 e impressão física continuam pendentes de conferência manual.
