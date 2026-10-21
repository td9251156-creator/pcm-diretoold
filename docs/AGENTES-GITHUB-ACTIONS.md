# Desenvolvimento com o Plus e GitHub Actions

> Atualização de 21/10/2026: autorizado o fluxo manual limitado de créditos até 30/10.
> Veja [orçamento, limites e operação](CREDITOS-OUTUBRO.md). O executor antigo permanece pausado.


## Modo escolhido: Codex com login do ChatGPT Plus

O mantenedor escolheu desenvolver nas tarefas do Codex vinculadas ao ChatGPT Plus,
aproveitando os limites disponíveis na conta. A chave `OPENAI_API_KEY` usa cobrança de API
separada e não consome a cota do Plus.

O trabalho por agentes segue `AGENTS.md`: uma implementação por vez, revisão independente,
testes e PR. As sessões do Codex podem atingir limites do plano; confira a disponibilidade
no cliente. Esta configuração não promete agentes trabalhando continuamente fora de uma tarefa
ativa nem agenda tarefas na conta do ChatGPT.

O GitHub Actions continua responsável pela revisão semanal de qualidade, pelas verificações de
PR e pela publicação após integração. O Dependabot continua propondo atualizações. O fluxo
`agentes-ia.yml` fica sem agenda e com a ativação de API fixada em `false` no código; mesmo uma
variável antiga `PCM_IA_ATIVA=true` não libera chamadas depois que esta configuração é integrada.

Para pausar a versão anterior já publicada, ajuste `PCM_IA_ATIVA=false` nas variáveis do GitHub
e cancele qualquer execução de IA ainda em andamento. Alterar a variável não interrompe um job
já iniciado. A conexão desta sessão apresentou HTTP 401 temporário. Após o acesso voltar, o workflow
foi desativado no GitHub e seu estado `disabled_manually` foi confirmado. A rodada anterior já
estava encerrada. A alteração do código acrescenta a pausa explícita à desativação remota. Mantenha o workflow desativado; sua reativação exige novo pedido do mantenedor.

Para iniciar uma rodada no Codex com seu login do Plus:

> Leia AGENTS.md e docs/FILA.md. Escolha a próxima tarefa pronta, faça uma implementação pequena,
> peça revisão independente a outro agente e execute as verificações necessárias. Preserve as regras
> de segurança e dados. Respeite as autorizações existentes para integrar e publicar; informe bloqueios
> concretos. Não reative a API do GitHub Actions.

## Fluxo de API preservado para eventual reativação

O executor escolhido é o GitHub Actions. O fluxo `Agentes de melhoria` tem uma agenda semanal
na versão anterior e execução manual. A agenda foi retirada nesta mudança. Ele só poderá voltar
a chamar IA depois de remover a pausa explícita do código com nova autorização de consumo.
A rotina de qualidade
semanal e o Dependabot continuam funcionando independentemente dessa ativação.

## Preparação pelo mantenedor

Em **Settings → Secrets and variables → Actions** do repositório:

1. Cadastre `OPENAI_API_KEY` como **secret**, usando uma chave de projeto exclusiva para esta
   automação. Não coloque chaves no código, nas issues ou no chat.
2. Cadastre a variável `PCM_IA_MODELO` com o identificador de um modelo Codex disponível nesse projeto.
3. Confira preços, créditos e limites no provedor antes de ativar. A assinatura do ChatGPT não
   fornece automaticamente créditos da API. Minutos do Actions também seguem os limites da conta.
   Limites de tempo e tamanho do fluxo não são um teto financeiro garantido; alertas de orçamento
   do provedor podem não interromper chamadas. Use os controles efetivamente disponíveis no projeto.
4. Somente com nova autorização de consumo, reabilite o workflow no GitHub, altere a pausa explícita no código e configure
   `PCM_IA_ATIVA=true`. A variável sozinha não reativa a versão pausada.
5. Em **Settings → Actions → General → Workflow permissions**, permita que o Actions crie PRs.
   O workflow concede escrita somente ao job que abre o PR.
6. Na tabela de `docs/FILA.md`, deixe uma tarefa pequena com critérios definidos e situação exatamente
   `Pronta`. Sem tarefa pronta, a agenda termina sem chamar a IA. Os itens que dependem de aparelhos
   ou decisões técnicas continuam bloqueados; configurar o executor não resolve essas dependências.

Depois, em **Actions → Agentes de melhoria → Run workflow**, execute primeiro o diagnóstico.
Ele informa os pré-requisitos sem exibir a chave e sem chamar o modelo. Para a primeira rodada
real, desative a opção de diagnóstico e acompanhe os jobs e o PR resultante.

As credenciais e permissões administrativas não puderam ser consultadas nesta sessão: a integração
retornou HTTP 403. A configuração do workflow não comprova que a chave exista ou que o modelo tenha
acesso. Só a primeira rodada real concluída comprova o funcionamento dos agentes.

## O que acontece em uma rodada

1. A preparação confere ativação, modelo, chave e existência de PR anterior da automação.
2. O implementador parte de uma versão imutável da `main` e escolhe uma única tarefa pronta da fila.
   Se não houver tarefa pronta, não deve inventar novas regras técnicas ou mudanças sem evidência.
3. O candidato é limitado a 12 arquivos e 500 linhas adicionadas/removidas, até 100 KB de patch.
   São aceitos apenas JavaScript e CSS de `src/` fora de `src/dados/`, testes JavaScript e `docs/FILA.md`.
   Links simbólicos, executáveis, arquivos binários e remoções de arquivos são recusados.
4. Um revisor separado recebe exatamente o candidato, sem poder editar, e precisa aprová-lo sem achados.
5. Outra máquina, sem credencial de IA ou permissão de escrita, executa lint, testes, build e navegador.
6. Só então um job separado abre um PR em rascunho. Ele não executa o código candidato, não integra
   a mudança e não publica. Uma verificação adicional é disparada explicitamente no ramo do PR.

PRs criados com o `GITHUB_TOKEN` não disparam automaticamente o evento `pull_request`. Por isso
o fluxo pede a verificação manual do ramo pelo workflow existente; não trate a ausência de checks
no PR como aprovação. Os resultados ficam ligados à execução e ao commit do ramo.

O revisor de IA pode errar. A aprovação automática não dispensa conferir as evidências e autorizar
a integração aplicável. Nenhum PR futuro recebe autorização irrestrita de publicação por este fluxo.

## Pausar e corrigir problemas

- Remova `PCM_IA_ATIVA` ou altere seu valor para `false` para impedir novas chamadas.
- Cancele uma execução em andamento em Actions se necessário; desativar a variável não cancela jobs já iniciados.
- Falta de chave, modelo ou ativação encerra a preparação sem invocar a IA.
- Um PR anterior aberto impede iniciar outra implementação. Revise, integre ou feche esse PR primeiro.
- Falha de revisão ou teste impede criar o PR; consulte os jobs antes de tentar outra rodada.
- Não configure tentativas ilimitadas, merge automático ou impressão da resposta completa dos agentes nos logs.

Código do repositório é enviado ao provedor para a tarefa de desenvolvimento. O aplicativo publicado
continua funcionando somente no navegador e não envia os dados dos seus usuários à automação.
