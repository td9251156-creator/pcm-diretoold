# Créditos de desenvolvimento até outubro de 2026

**Estado: proposta em revisão.** Ainda não integrada nem ativada. O mantenedor enviará
novas definições sobre o app. Nenhuma chamada paga foi iniciada por esta implementação.

O mantenedor autorizou implementar a estratégia para os US$ 9 informados, válidos até 31/10.
O Codex com login do Plus continua fazendo implementação, testes e revisão independente.
O novo workflow **Créditos de outubro — consulta limitada** fornece um parecer técnico por
execução manual. O executor antigo `agentes-ia.yml` permanece desativado.

## Orçamento e prazo

- Até 28/10: reservar no máximo US$ 6 para diagnósticos de erros e sugestões de correção.
- Em 29 e 30/10: reservar no máximo US$ 3 para revisão final das entregas.
- Bloqueio a partir de **31/10/2026 às 00h de São Paulo (03h UTC)**, um dia de margem
  em relação à data de validade informada. Não presumimos o horário de expiração do provedor.
- Cada execução reserva **US$ 0,10**, antes da chamada, no ramo
  `controles/creditos-outubro-2026`, arquivo `orcamento.json`.
- A reserva não é o valor faturado. Mesmo timeout, cancelamento, erro da API ou resposta
  incompleta mantém a reserva utilizada. Não apagar, recriar, reescrever ou devolver reservas.
- O fluxo recusa histórico inválido, ID repetido, fase esgotada e data fora do prazo.
  A gravação precisa chegar ao GitHub antes da consulta; conflito no push interrompe o fluxo.
- Sem agenda, ferramentas do modelo, repetição automática ou reexecução de jobs pagos.
  Uma nova tentativa exige uma nova execução manual, com outra reserva.

O modelo fixo é `gpt-5.4-mini`, em processamento padrão. Na documentação oficial consultada
em 21/10/2026: entrada US$ 0,75 e saída US$ 4,50 por milhão de tokens.
Fonte: https://developers.openai.com/api/docs/models/gpt-5.4-mini

O pacote limita a entrada a 48.000 bytes UTF-8, incluindo instruções, e a saída a 8.000 tokens,
incluindo raciocínio. Contando conservadoramente um token por byte de entrada mais 1.024 tokens
de margem, o custo calculado é inferior a US$ 0,073 por chamada. A reserva de US$ 0,10
acrescenta margem. Não há ferramentas pagas nem chamadas extras. Confira novamente as tarifas
antes de modificar modelo, limites ou prazo; o código não permite selecionar outro modelo.

Este controle limita **este workflow**, não o saldo global da conta. Outras chaves e aplicações,
cobranças anteriores, mudanças de tarifa e recarga automática da conta não são controladas aqui.
O saldo informado não foi consultado pela integração. O orçamento do painel do provedor pode ser
apenas um alerta. Confira o Usage e a configuração de recarga na sua conta; não envie a chave.

Não é necessário gastar todo o saldo: o objetivo é obter correções úteis. O restante da fase
inicial não aumenta automaticamente os US$ 3 da revisão. Os limites são tetos, não metas de gasto.

## Como usar

1. Abra Actions → **Créditos de outubro — consulta limitada** → **Run workflow**, na `main`.
2. Escreva uma pergunta específica e informe os arquivos necessários, um caminho por linha.
   O diagnóstico vem marcado por padrão: valida o pacote sem chamar a API nem reservar valor.
3. Para obter o parecer, inicie outra execução desmarcando diagnóstico. Usa o secret já existente
   `OPENAI_API_KEY`; não exige alterar `PCM_IA_ATIVA` nem reabilitar o executor antigo.
4. Baixe o artefato `parecer-e-consumo`: relatório e uso de tokens/custo estimado. Uma resposta
   incompleta deve ser tratada como inconclusiva. O texto do modelo não é executado pelo Actions.
5. No Codex, reproduza o achado antes de editar, acrescente teste que falha antes da correção,
   implemente uma mudança, peça revisão independente e rode as verificações. Integre por PR.
6. Se a API falhar, investigue no Codex antes de autorizar outra consulta. Não repetir o mesmo
   pedido indefinidamente. Não usar “Re-run jobs”: a proteção bloqueia chamadas em reexecuções.

Somente código e documentação versionados dos caminhos permitidos entram no pacote. Não informar
dados reais, backups de usuários ou segredos na pergunta ou nos arquivos. O aplicativo publicado
continua local: essa consulta usa código do repositório, não informações dos usuários do app.

## Sequência de trabalho

1. Backup e restauração: investigar perda de dados e interrupção de gravação com dados fictícios.
2. Importação e checklist: conferir validação e compatibilidade, uma área por consulta.
3. Teclado e mensagens: reproduzir achados no Chromium antes de editar.
4. Em 29–30/10: revisar as mudanças efetivamente entregues e lacunas dos testes.

MTBF, MTTR e janelas de segurança continuam aguardando definições técnicas. Nenhum parecer
substitui essas decisões. Cada resultado útil entra na fila com evidência e critérios de conclusão.
