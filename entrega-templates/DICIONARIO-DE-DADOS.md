# Dicionário de dados dos modelos PCMD

Modelo versão 1.0.0 · gerado a partir de `gerador/especificacao.py` (mesma fonte do `CONTRATO-CAMPOS.json`).

> **Aviso:** O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

**Situação do mapeamento: proposto, ainda não validado.** A coluna Origem indica de onde o futuro adaptador poderia ler cada dado. Campos marcados como *ramo de gestão* existem apenas no ramo `interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main`. O app ainda não preenche estes arquivos.

Legenda de papel: ENTRADA, ID TÉCNICO, REFERÊNCIA (protegida no Plano Mestre), CÁLCULO (não escrever), MANUAL (documental), FUTURO (manter vazio).

## PCMD-01 Lista Mestra

Cabeçalho na linha 6; dados de 7 a 56 (capacidade 50 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `documento.codigo` | Código | ENTRADA | texto (célula com formato Texto) | obrigatório | Código PCMD do modelo (documental) | manual | Vazio = não informado. | Texto; código PCMD-xx ou PCMD-Wx. |
| B | `documento.titulo` | Título | ENTRADA | texto (célula com formato Texto) | obrigatório | Título do documento (documental) | manual | Vazio = não informado. | — |
| C | `documento.tipo` | Tipo | ENTRADA | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | Lista lst_tipo_documento. |
| D | `documento.revisao` | Revisão | MANUAL | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | Texto (ex.: 00, 01). |
| E | `documento.data` | Data da revisão (dd/mm/aaaa) | MANUAL | data dd/mm/aaaa | opcional | Documental | manual | Vazio = não informado. | Data válida. |
| F | `documento.elaborador` | Elaborador (nome) | MANUAL | texto (célula com formato Texto) | opcional | Sugestão: nome de gestao.pessoas[] cujo id = gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| G | `documento.aprovador` | Aprovador (nome) | MANUAL | texto (célula com formato Texto) | opcional | Sugestão: nome de gestao.pessoas[] cujo id = gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| H | `documento.proxima_revisao` | Próxima revisão (dd/mm/aaaa) | MANUAL | data dd/mm/aaaa | opcional | Documental: não existe no app | manual | Vazio = a definir. | date |
| I | `documento.situacao` | Situação | MANUAL | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | Lista lst_situacao_documento (proposta, editável). |
| J | `documento.conferencia` | Conferência | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| K | `documento.observacao` | Observação | MANUAL | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | — |

## PCMD-02 Ativos

Cabeçalho na linha 6; dados de 7 a 306 (capacidade 300 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `ativo.id` | ID do ativo | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].id | app (main) | Vazio = não informado. | Único; sem espaços e sem \|. |
| B | `ativo.tag` | TAG | ENTRADA | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].tag (SETOR-SIGLA-NNN, src/logica/tag.js) | app (main) | Vazio = não informado. | — |
| C | `ativo.descricao` | Descrição do equipamento | ENTRADA | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].descricao | app (main) | Vazio = não informado. | — |
| D | `ativo.tipo_id` | Tipo (ID) | ENTRADA | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].tipo (id do tipo na biblioteca) | app (main) | Vazio = não informado. | Lista lst_tipo_id. |
| E | `ativo.tipo_nome` | Tipo (nome) | CÁLCULO | texto | opcional | Fórmula a partir de Listas (biblioteca.tipos[].nome) | cálculo | Vazio = não informado. | — |
| F | `ativo.fabricante` | Fabricante | ENTRADA | texto (célula com formato Texto) | opcional | estado.equipamentos[].fabricante | app (main) | Vazio = não informado. | — |
| G | `ativo.modelo` | Modelo | ENTRADA | texto (célula com formato Texto) | opcional | estado.equipamentos[].modelo | app (main) | Vazio = não informado. | — |
| H | `ativo.setor` | Setor (sigla) | ENTRADA | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].setor | app (main) | Vazio = não informado. | Lista cad_setor. |
| I | `ativo.numero` | Número | ENTRADA | inteiro 1–999 | obrigatório | estado.equipamentos[].numero | app (main) | Vazio = não informado. | whole |
| J | `ativo.tag_conferencia` | Conferência da TAG | CÁLCULO | texto | opcional | Fórmula: SETOR-SIGLA-NNN | cálculo | Vazio = não informado. | — |
| K | `criticidade.nota_seguranca` | N1 Segurança (1–3) | ENTRADA | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][0] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| L | `criticidade.nota_qualidade` | N2 Qualidade (1–3) | ENTRADA | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][1] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| M | `criticidade.nota_producao` | N3 Produção (1–3) | ENTRADA | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][2] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| N | `criticidade.nota_frequencia_falha` | N4 Frequência de falha (1–3) | ENTRADA | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][3] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| O | `criticidade.nota_custo_reparo` | N5 Custo/tempo de reparo (1–3) | ENTRADA | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][4] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| P | `criticidade.notas_validas` | Notas válidas (de 5) | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| Q | `criticidade.pontuacao` | Pontuação (5–15) | CÁLCULO | texto | opcional | Fórmula (equivale a criticidadeAtivo().pontuacao) | cálculo | Vazio enquanto houver nota ausente ou inválida. | — |
| R | `criticidade.classe` | Classe | CÁLCULO | texto | opcional | Fórmula (equivale a criticidadeAtivo().classe) | cálculo | Vazio = não informado. | A, B, C ou Pendente. |
| S | `criticidade.orientacao` | Orientação | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## PCMD-03 Plano Mestre

Cabeçalho na linha 6; dados de 7 a 2006 (capacidade 2000 linhas); aba protegida sem senha.

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `tarefa.ativo_id` | ID do ativo | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | plano[].equipamentoId (gerarPlano, src/logica/plano.js) | app (main) | Vazio = não informado. | custom |
| B | `tarefa.id` | ID da tarefa | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | plano[].tarefaId (biblioteca.tipos[].tarefas[].id) | app (main) | Vazio = não informado. | custom |
| C | `tarefa.chave` | Chave da tarefa (ativo\|tarefa) | CÁLCULO | texto | opcional | Fórmula: equipamentoId\|tarefaId (chaveAjuste) | cálculo | Vazio = não informado. | — |
| D | `tarefa.tag` | TAG | CÁLCULO | texto | opcional | Fórmula a partir de PCMD-02 (plano[].tag) | cálculo | Vazio = não informado. | — |
| E | `tarefa.atividade` | Atividade | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].descricao | app (main) | Vazio = não informado. | — |
| F | `tarefa.origem` | Origem | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].origem | app (main) | Vazio = não informado. | — |
| G | `tarefa.versao` | Versão | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].versao | app (main) | Vazio = não informado. | — |
| H | `tarefa.frequencia_referencia` | Frequência de referência | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].periodicidadeOriginal | app (main) | Vazio = não informado. | Lista lst_frequencias. |
| I | `tarefa.seguranca` | Segurança (referência) | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].seguranca (true → Sim) | app (main) | Vazio = não informado. | Sim ou Não. |
| J | `tarefa.frequencia_vigente` | Frequência vigente | ENTRADA | texto (célula com formato Texto) | obrigatório | plano[].periodicidade (após ajustes válidos) | app (main) | Vazio = não informado. | Lista lst_frequencias; segurança não pode ser menos frequente. |
| K | `tarefa.vezes_ano` | Execuções no ciclo de 52 semanas | CÁLCULO | texto | opcional | Fórmula (vezesPorAno) | cálculo | Vazio = não informado. | — |
| L | `tarefa.especialidade` | Especialidade | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].especialidade | app (main) | Vazio = não informado. | list |
| M | `tarefa.duracao_horas` | Duração estimada por execução (h) | REFERÊNCIA | número decimal de horas | obrigatório | plano[].duracaoHoras (biblioteca duracao_horas) | app (main) | Vazio = não informado. | decimal |
| N | `tarefa.horas_ciclo` | Horas estimadas no ciclo (h) | CÁLCULO | número decimal de horas | opcional | Fórmula: duração × execuções no ciclo | cálculo | Vazio = não informado. | — |
| O | `tarefa.ativa` | Ativa no plano | ENTRADA | texto (célula com formato Texto) | obrigatório | plano[].ativa (true → Sim) | app (main) | Vazio = não informado. | list |
| P | `tarefa.responsavel_id` | Responsável (ID) | ENTRADA | texto (célula com formato Texto) | opcional | gestao.responsaveis['equipamentoId\|tarefaId'] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| Q | `tarefa.responsavel_nome` | Responsável (nome) | CÁLCULO | texto | opcional | Fórmula a partir de Cadastros | cálculo | Vazio = não informado. | — |
| R | `tarefa.conferencia` | Conferência de segurança e frequência | CÁLCULO | texto | opcional | Fórmula (equivale a podeAlterar) | cálculo | Vazio = não informado. | — |
| S | `tarefa.observacao` | Observação técnica | REFERÊNCIA | texto (célula com formato Texto) | opcional | plano[].observacao | app (main) | Vazio = não informado. | — |

## PCMD-04 Ocorrências

Cabeçalho na linha 6; dados de 7 a 5006 (capacidade 5000 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `ocorrencia.ativo_id` | ID do ativo | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | ocorrenciasPlanejadas(dados)[].equipamentoId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `ocorrencia.tarefa_id` | ID da tarefa | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | ocorrenciasPlanejadas(dados)[].tarefaId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| C | `ocorrencia.data_prevista` | Data prevista (dd/mm/aaaa) | ENTRADA | data dd/mm/aaaa | obrigatório | ocorrenciasPlanejadas(dados)[].dataPrevista (AAAA-MM-DD → data Excel) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | date |
| D | `ocorrencia.fonte` | Fonte da data prevista | ENTRADA | texto (célula com formato Texto) | obrigatório | Texto do adaptador ou de quem digitou | manual | Vazio = não informado. | — |
| E | `ocorrencia.chave_tarefa` | Chave da tarefa | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| F | `ocorrencia.chave` | Chave da ocorrência (ativo\|tarefa\|AAAA-MM-DD) | CÁLCULO | texto | opcional | Fórmula (equivale a ocorrencia.chave do app) | cálculo | Vazio = não informado. | — |
| G | `ocorrencia.linha_plano` | Linha no plano (técnico) | CÁLCULO | texto | opcional | Fórmula: posição da chave no PCMD-03 | cálculo | Vazio = não informado. | — |
| H | `ocorrencia.tag` | TAG | CÁLCULO | texto | opcional | Fórmula a partir do PCMD-03 | cálculo | Vazio = não informado. | — |
| I | `ocorrencia.atividade` | Atividade | CÁLCULO | texto | opcional | Fórmula a partir do PCMD-03 | cálculo | Vazio = não informado. | — |
| J | `ocorrencia.especialidade` | Especialidade | CÁLCULO | texto | opcional | Fórmula a partir do PCMD-03 | cálculo | Vazio = não informado. | — |
| K | `ocorrencia.horas_estimadas` | Horas estimadas (h) | CÁLCULO | número decimal de horas | opcional | Fórmula: duração por execução do PCMD-03 | cálculo | Vazio = não informado. | — |
| L | `ocorrencia.ano` | Ano previsto | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| M | `ocorrencia.mes` | Mês previsto | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| N | `ocorrencia.posicao` | Posição em relação ao ano consultado | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| O | `ocorrencia.primeira` | Primeira linha da chave (1/0) | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| P | `ocorrencia.conta` | Prevista válida (1/0) | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| Q | `ocorrencia.execucoes_ativas` | Execuções ativas vinculadas | CÁLCULO | texto | opcional | Fórmula: CONT.SES em Execuções | cálculo | Vazio = não informado. | — |
| R | `ocorrencia.concluida` | Concluída (1/0) | CÁLCULO | texto | opcional | Fórmula: 1 se prevista válida com execução ativa | cálculo | Vazio = não informado. | — |
| S | `ocorrencia.conferencia` | Conferência | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Execuções

Cabeçalho na linha 6; dados de 7 a 3006 (capacidade 3000 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `execucao.id` | ID do registro | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | gestao.historico[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `execucao.ativo_id` | ID do ativo | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | gestao.historico[].equipamentoId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| C | `execucao.tarefa_id` | ID da tarefa | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | gestao.historico[].tarefaId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| D | `execucao.chave_tarefa` | Chave da tarefa | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| E | `execucao.tag` | TAG preservada | ENTRADA | texto (célula com formato Texto) | obrigatório | gestao.historico[].tag — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| F | `execucao.descricao` | Descrição preservada | ENTRADA | texto (célula com formato Texto) | opcional | gestao.historico[].descricao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| G | `execucao.data_prevista` | Data prevista (opcional, dd/mm/aaaa) | ENTRADA | data dd/mm/aaaa | opcional | gestao.historico[].dataPrevista ('' → vazio) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = execução sem vínculo (não entra no percentual). | date |
| H | `execucao.data` | Data realizada (dd/mm/aaaa) | ENTRADA | data dd/mm/aaaa | obrigatório | gestao.historico[].data — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | date |
| I | `execucao.chave_ocorrencia` | Chave da ocorrência vinculada | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| J | `execucao.observacao` | Observação | ENTRADA | texto (célula com formato Texto) | opcional | gestao.historico[].observacao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| K | `execucao.responsavel_id` | Responsável (ID) | ENTRADA | texto (célula com formato Texto) | opcional | gestao.historico[].responsavelId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| L | `execucao.responsavel_nome` | Responsável (nome) | CÁLCULO | texto | opcional | Fórmula a partir de Cadastros | cálculo | Vazio = não informado. | — |
| M | `execucao.origem` | Origem do registro | ENTRADA | texto (célula com formato Texto) | obrigatório | gestao.historico[].origem (app \| legado) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| N | `execucao.cancelada` | Cancelada | ENTRADA | texto (célula com formato Texto) | obrigatório | gestao.historico[].cancelada (true → Sim) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio é tratado como Não (ativa). | list |
| O | `execucao.vinculo` | Vínculo | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| P | `execucao.ano` | Ano realizado | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| Q | `execucao.situacao_ativo` | Situação do ativo | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| R | `execucao.conferencia` | Conferência | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| S | `execucao.duracao_real_horas` | Duração real (h) — FUTURO, não integrado | FUTURO | número decimal de horas | opcional | Não existe no histórico atual do app | futuro | Manter vazio. Não é somado em nenhuma fórmula. | decimal |

## PCMD-05 Ficha de Falha

Cabeçalho na linha 6; dados de 7 a 1006 (capacidade 1000 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `falha.id` | ID do registro | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | gestao.falhas[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `falha.ativo_id` | ID do ativo | ID TÉCNICO | texto (célula com formato Texto) | obrigatório | gestao.falhas[].equipamentoId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| C | `falha.data` | Data da falha (dd/mm/aaaa) | ENTRADA | data dd/mm/aaaa | obrigatório | gestao.falhas[].data — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | date |
| D | `falha.tag` | TAG preservada | ENTRADA | texto (célula com formato Texto) | obrigatório | gestao.falhas[].tag — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| E | `falha.sintoma` | Sintoma | ENTRADA | texto (célula com formato Texto) | obrigatório | gestao.falhas[].sintoma — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| F | `falha.causa` | Causa | ENTRADA | texto (célula com formato Texto) | opcional | gestao.falhas[].causa — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| G | `falha.acao` | Ação | ENTRADA | texto (célula com formato Texto) | opcional | gestao.falhas[].acao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| H | `falha.horas_parada` | Horas de parada (h, opcional) | ENTRADA | número decimal de horas | opcional | gestao.falhas[].horasParada (null → vazio) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado; nunca converter em zero. | decimal |
| I | `falha.peca` | Peça | ENTRADA | texto (célula com formato Texto) | opcional | gestao.falhas[].peca — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| J | `falha.responsavel_id` | Responsável (ID) | ENTRADA | texto (célula com formato Texto) | opcional | gestao.falhas[].responsavelId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| K | `falha.responsavel_nome` | Responsável (nome) | CÁLCULO | texto | opcional | Fórmula a partir de Cadastros | cálculo | Vazio = não informado. | — |
| L | `falha.parada_situacao` | Parada informada? | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| M | `falha.situacao_ativo` | Situação do ativo | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| N | `falha.conferencia` | Conferência | CÁLCULO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Revisões

Cabeçalho na linha 6; dados de 7 a 106 (capacidade 100 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `revisao.documento` | Documento (código) | MANUAL | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |
| B | `revisao.numero` | Revisão | MANUAL | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |
| C | `revisao.data` | Data (dd/mm/aaaa) | MANUAL | data dd/mm/aaaa | obrigatório | Documental | manual | Vazio = não informado. | date |
| D | `revisao.descricao` | Descrição da mudança | MANUAL | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |
| E | `revisao.responsavel` | Responsável (nome) | MANUAL | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |

## Cadastros

### Células únicas

| Célula | Campo | Rótulo | Papel | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|
| Cadastros!B8 | `organizacao.nome` | Nome da organização | ENTRADA | gestao.organizacao.nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | Até 120 caracteres. |
| Cadastros!B9 | `organizacao.referencial` | Referencial | ENTRADA | gestao.organizacao.referencial — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão: GERAL (sem norma). | Até 120 caracteres; não citar norma sem fonte. |
| Cadastros!B10 | `organizacao.prefixo` | Prefixo dos documentos | ENTRADA | gestao.organizacao.padraoCodigo — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão: PCMD. | Até 40 caracteres. |
| Cadastros!B11 | `organizacao.elaborador_id` | Elaborador padrão (ID) | ENTRADA | gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | Lista cad_pessoa_id. |
| Cadastros!B12 | `organizacao.aprovador_id` | Aprovador padrão (ID) | ENTRADA | gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado; não presumir aprovação. | Lista cad_pessoa_id. |
| Cadastros!B16 | `criticidade.limite_a` | Limite A | ENTRADA | gestao.criticidade.limites.a — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 12. | Inteiro; 5 ≤ B < A ≤ 15. |
| Cadastros!B17 | `criticidade.limite_b` | Limite B | ENTRADA | gestao.criticidade.limites.b — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 9. | Inteiro; 5 ≤ B < A ≤ 15. |
| Cadastros!B18 | `criticidade.limites_ok` | Limites válidos? | CÁLCULO | Fórmula | cálculo | — | VERDADEIRO/FALSO. |
| Cadastros!B24:D28 | `criticidade.niveis` | Significado dos níveis 1/2/3 por critério | MANUAL | Definição do mantenedor; não existe no app | manual | Vazio = A definir pelo mantenedor. | Texto livre. |
| Cadastros!B32 | `metas.disponibilidade` | Meta de disponibilidade (%) | ENTRADA | gestao.metas.disponibilidade (0–100 no app → dividir por 100) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir (null no app). | 0% a 100%. |
| Cadastros!B33 | `metas.aderencia` | Meta de aderência preventiva (%) | ENTRADA | gestao.metas.aderencia (0–100 no app → dividir por 100) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir (null no app). | 0% a 100%. |
| Leia-me!B7 | `emissao.origem_dados` | Origem dos dados | ENTRADA | Texto curto do adaptador ou de quem preenche | futuro | Vazio = não informado. | — |
| Leia-me!B8 | `emissao.data` | Data de emissão | ENTRADA | Data em que o arquivo é gerado/preenchido | futuro | Vazio = não informado. | — |
| PCMD-04 Cronograma!C7 | `cronograma.ano` | Ano consultado | ENTRADA | Escolha do usuário (resumoMensal(dados, gestao, ano)) | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| PCMD-04 Cronograma!C8 | `cronograma.inicio` | Início do ciclo (semana 1) | ENTRADA | estado.inicio (AAAA-MM-DD, main) | app (main) | Vazio = não informado. | — |
| PCMD-04 Cronograma!C9 | `cronograma.fonte` | Fonte das ocorrências | ENTRADA | Texto do adaptador | futuro | Vazio = não informado. | — |

### Bloco Setores

Cabeçalho na linha 37; dados de 38 a 67.

| Col. | Campo | Cabeçalho | Papel | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|---|
| A | `setor.sigla` | Sigla do setor | ENTRADA | gestao.organizacao.setores[] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main; também estado.equipamentos[].setor (main) | app (ramo de gestão, não integrado) | Vazio = não informado. |
| B | `setor.descricao` | Descrição do setor | MANUAL | Não existe no app (o app guarda só a sigla) | manual | Vazio = não informado. |
| C | `setor.conferencia` | Conferência | CÁLCULO | Fórmula | cálculo | Vazio = não informado. |

### Bloco Pessoas

Cabeçalho na linha 70; dados de 71 a 130.

| Col. | Campo | Cabeçalho | Papel | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|---|
| A | `pessoa.id` | ID da pessoa | ID TÉCNICO | gestao.pessoas[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| B | `pessoa.nome` | Nome | ENTRADA | gestao.pessoas[].nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| C | `pessoa.funcao` | Função | ENTRADA | gestao.pessoas[].funcao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| D | `pessoa.especialidade` | Especialidade | ENTRADA | gestao.pessoas[].especialidade — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| E | `pessoa.ativo` | Ativa | ENTRADA | gestao.pessoas[].ativo (true → Sim) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| F | `pessoa.conferencia` | Conferência | CÁLCULO | Fórmula | cálculo | Vazio = não informado. |

### Bloco Requisitos

Cabeçalho na linha 133; dados de 134 a 193.

| Col. | Campo | Cabeçalho | Papel | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|---|
| A | `requisito.id` | ID do requisito | ID TÉCNICO | gestao.requisitos[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| B | `requisito.referencia` | Referência ou título | ENTRADA | gestao.requisitos[].referencia — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| C | `requisito.versao` | Versão | ENTRADA | gestao.requisitos[].versao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir. |
| D | `requisito.data` | Data da referência (dd/mm/aaaa) | ENTRADA | gestao.requisitos[].data ('' → vazio) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir. |
| E | `requisito.fonte` | Fonte oficial (link HTTPS) | ENTRADA | gestao.requisitos[].fonte — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| F | `requisito.status` | Status de verificação | ENTRADA | gestao.requisitos[].status (nao_verificado \| verificado) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. |
| G | `requisito.conferencia` | Conferência | CÁLCULO | Fórmula | cálculo | Vazio = não informado. |

## Intervalos nomeados

| Nome | Referência |
|---|---|
| `at_descricao` | `'PCMD-02 Ativos'!$C$7:$C$306` |
| `at_id` | `'PCMD-02 Ativos'!$A$7:$A$306` |
| `at_tag` | `'PCMD-02 Ativos'!$B$7:$B$306` |
| `cad_limite_a` | `'Cadastros'!$B$16` |
| `cad_limite_b` | `'Cadastros'!$B$17` |
| `cad_limites_ok` | `'Cadastros'!$B$18` |
| `cad_meta_aderencia` | `'Cadastros'!$B$33` |
| `cad_meta_disponibilidade` | `'Cadastros'!$B$32` |
| `cad_org_nome` | `'Cadastros'!$B$8` |
| `cad_pessoa_id` | `'Cadastros'!$A$71:$A$130` |
| `cad_pessoa_nome` | `'Cadastros'!$B$71:$B$130` |
| `cad_prefixo` | `'Cadastros'!$B$10` |
| `cad_referencial` | `'Cadastros'!$B$9` |
| `cad_setor` | `'Cadastros'!$A$38:$A$67` |
| `crono_ano` | `'PCMD-04 Cronograma'!$C$7` |
| `crono_inicio` | `'PCMD-04 Cronograma'!$C$8` |
| `ex_ano` | `'Execuções'!$P$7:$P$3006` |
| `ex_cancelada` | `'Execuções'!$N$7:$N$3006` |
| `ex_chave_oc` | `'Execuções'!$I$7:$I$3006` |
| `ex_id` | `'Execuções'!$A$7:$A$3006` |
| `ex_vinculo` | `'Execuções'!$O$7:$O$3006` |
| `fa_id` | `'PCMD-05 Ficha de Falha'!$A$7:$A$1006` |
| `fa_parada` | `'PCMD-05 Ficha de Falha'!$L$7:$L$1006` |
| `lst_especialidades` | `'Listas'!$E$7:$E$36` |
| `lst_frequencias` | `'Listas'!$A$7:$A$14` |
| `lst_frequencias_vezes` | `'Listas'!$B$7:$B$14` |
| `lst_origem_execucao` | `'Listas'!$M$7:$M$8` |
| `lst_sim_nao` | `'Listas'!$K$7:$K$8` |
| `lst_situacao_documento` | `'Listas'!$Q$7:$Q$16` |
| `lst_status_requisito` | `'Listas'!$O$7:$O$8` |
| `lst_tipo_documento` | `'Listas'!$S$7:$S$16` |
| `lst_tipo_id` | `'Listas'!$G$7:$G$36` |
| `lst_tipo_nome` | `'Listas'!$H$7:$H$36` |
| `lst_tipo_sigla` | `'Listas'!$I$7:$I$36` |
| `oc_ano` | `'PCMD-04 Ocorrências'!$L$7:$L$5006` |
| `oc_chave` | `'PCMD-04 Ocorrências'!$F$7:$F$5006` |
| `oc_concluida` | `'PCMD-04 Ocorrências'!$R$7:$R$5006` |
| `oc_conferencia` | `'PCMD-04 Ocorrências'!$S$7:$S$5006` |
| `oc_conta` | `'PCMD-04 Ocorrências'!$P$7:$P$5006` |
| `oc_horas` | `'PCMD-04 Ocorrências'!$K$7:$K$5006` |
| `oc_mes` | `'PCMD-04 Ocorrências'!$M$7:$M$5006` |
| `oc_posicao` | `'PCMD-04 Ocorrências'!$N$7:$N$5006` |
| `pcmd_emissao` | `'Leia-me'!$B$8` |
| `pcmd_origem` | `'Leia-me'!$B$7` |
| `pl_ativa` | `'PCMD-03 Plano Mestre'!$O$7:$O$2006` |
| `pl_atividade` | `'PCMD-03 Plano Mestre'!$E$7:$E$2006` |
| `pl_chave` | `'PCMD-03 Plano Mestre'!$C$7:$C$2006` |
| `pl_duracao` | `'PCMD-03 Plano Mestre'!$M$7:$M$2006` |
| `pl_especialidade` | `'PCMD-03 Plano Mestre'!$L$7:$L$2006` |
| `pl_seguranca` | `'PCMD-03 Plano Mestre'!$I$7:$I$2006` |
| `pl_tag` | `'PCMD-03 Plano Mestre'!$D$7:$D$2006` |
| `pl_vezes` | `'PCMD-03 Plano Mestre'!$K$7:$K$2006` |

## PCMD-W1-Manual-Gestao-Ativos.docx

### Marcadores

| Marcador | Descrição | Locais | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|
| `{{organizacao.nome}}` | Nome da organização | cabeçalho, célula de tabela (identificação), parágrafo | gestao.organizacao.nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.revisao}}` | Revisão do documento | célula de tabela (identificação), rodapé | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.data}}` | Data da revisão (dd/mm/aaaa) | célula de tabela (identificação) | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.elaborador}}` | Nome do elaborador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.aprovador}}` | Nome do aprovador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir (aprovação não registrada)'. Nunca presumir aprovação. |
| `{{documento.proxima_revisao}}` | Próxima revisão (dd/mm/aaaa) | célula de tabela (identificação), parágrafo | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.situacao}}` | Situação do documento | célula de tabela (identificação) | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'Em elaboração'. |
| `{{organizacao.referencial}}` | Referencial adotado | célula de tabela (identificação), parágrafo | gestao.organizacao.referencial — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 'GERAL (sem norma)'. |
| `{{origem.dados}}` | Origem dos dados | célula de tabela (identificação) | Texto curto do adaptador (ex.: PCM Direto, backup local de dd/mm/aaaa) | futuro | Vazio → 'Não informada'. |
| `{{emissao.data}}` | Data de emissão do arquivo (dd/mm/aaaa) | célula de tabela (identificação) | Data em que o adaptador gera o arquivo | futuro | Vazio → 'A definir'. |
| `{{criticidade.limite_a}}` | Limite A da criticidade | célula de tabela, parágrafo | gestao.criticidade.limites.a — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{criticidade.limite_b}}` | Limite B da criticidade | célula de tabela, parágrafo | gestao.criticidade.limites.b — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{metas.disponibilidade}}` | Meta de disponibilidade | célula de tabela | gestao.metas.disponibilidade — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | null → 'A definir'. |

### Regiões repetíveis

| Região | Tabela nº (corpo, a partir de 0) | Linha modelo | Marcadores da linha |
|---|---|---|---|
| `requisitos` | 2 | 1 | `{{requisito.referencia}}` `{{requisito.versao}}` `{{requisito.data}}` `{{requisito.fonte}}` `{{requisito.status}}` |
| `pessoas` | 4 | 1 | `{{pessoa.nome}}` `{{pessoa.funcao}}` `{{pessoa.especialidade}}` `{{pessoa.responsabilidade}}` |
| `setores` | 5 | 1 | `{{setor.sigla}}` `{{setor.descricao}}` |
| `revisoes` | 11 | 1 | `{{revisao.numero}}` `{{revisao.data}}` `{{revisao.descricao}}` `{{revisao.responsavel}}` |
| `ativos` | 12 | 1 | `{{ativo.tag}}` `{{ativo.descricao}}` `{{ativo.setor}}` `{{ativo.tipo_nome}}` `{{criticidade.nota_seguranca}}` `{{criticidade.nota_qualidade}}` `{{criticidade.nota_producao}}` `{{criticidade.nota_frequencia_falha}}` `{{criticidade.nota_custo_reparo}}` `{{criticidade.pontuacao}}` `{{criticidade.classe}}` |

## PCMD-W2-Manual-Estrategia-Manutencao.docx

### Marcadores

| Marcador | Descrição | Locais | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|
| `{{organizacao.nome}}` | Nome da organização | cabeçalho, célula de tabela (identificação), parágrafo | gestao.organizacao.nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.revisao}}` | Revisão do documento | célula de tabela (identificação), rodapé | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.data}}` | Data da revisão (dd/mm/aaaa) | célula de tabela (identificação) | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.elaborador}}` | Nome do elaborador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.aprovador}}` | Nome do aprovador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir (aprovação não registrada)'. Nunca presumir aprovação. |
| `{{documento.proxima_revisao}}` | Próxima revisão (dd/mm/aaaa) | célula de tabela (identificação) | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.situacao}}` | Situação do documento | célula de tabela (identificação) | PCMD-01 Lista Mestra (manual) | manual | Vazio → 'Em elaboração'. |
| `{{organizacao.referencial}}` | Referencial adotado | célula de tabela (identificação), parágrafo | gestao.organizacao.referencial — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 'GERAL (sem norma)'. |
| `{{origem.dados}}` | Origem dos dados | célula de tabela (identificação) | Texto curto do adaptador (ex.: PCM Direto, backup local de dd/mm/aaaa) | futuro | Vazio → 'Não informada'. |
| `{{emissao.data}}` | Data de emissão do arquivo (dd/mm/aaaa) | célula de tabela (identificação) | Data em que o adaptador gera o arquivo | futuro | Vazio → 'A definir'. |
| `{{estrategia.responsavel}}` | Profissional responsável pela estratégia | célula de tabela, parágrafo | Manual: não existe no app | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_a.estrategia}}` | Estratégia predominante para a classe A | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_a.prazo}}` | Prazo de atendimento para a classe A | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_a.revisao}}` | Revisão do plano para a classe A | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_b.estrategia}}` | Estratégia predominante para a classe B | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_b.prazo}}` | Prazo de atendimento para a classe B | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_b.revisao}}` | Revisão do plano para a classe B | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_c.estrategia}}` | Estratégia predominante para a classe C | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_c.prazo}}` | Prazo de atendimento para a classe C | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.classe_c.revisao}}` | Revisão do plano para a classe C | célula de tabela | Manual: definição do profissional responsável | manual | Vazio → 'A definir'. |
| `{{estrategia.periodicidade_revisao}}` | Periodicidade de revisão da estratégia | parágrafo | Manual: definição do mantenedor | manual | Vazio → 'A definir'. |
| `{{metas.aderencia}}` | Meta de aderência preventiva | célula de tabela | gestao.metas.aderencia — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | null → 'A definir'. |
| `{{metas.disponibilidade}}` | Meta de disponibilidade | célula de tabela | gestao.metas.disponibilidade — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | null → 'A definir'. |

### Regiões repetíveis

| Região | Tabela nº (corpo, a partir de 0) | Linha modelo | Marcadores da linha |
|---|---|---|---|
| `requisitos` | 2 | 1 | `{{requisito.referencia}}` `{{requisito.versao}}` `{{requisito.data}}` `{{requisito.fonte}}` `{{requisito.status}}` |
| `pessoas` | 4 | 1 | `{{pessoa.nome}}` `{{pessoa.funcao}}` `{{pessoa.especialidade}}` `{{pessoa.responsabilidade}}` |
| `revisoes` | 8 | 1 | `{{revisao.numero}}` `{{revisao.data}}` `{{revisao.descricao}}` `{{revisao.responsavel}}` |
| `tarefas` | 9 | 1 | `{{tarefa.tag}}` `{{tarefa.id}}` `{{tarefa.atividade}}` `{{tarefa.frequencia_vigente}}` `{{tarefa.especialidade}}` `{{tarefa.duracao_horas}}` `{{tarefa.seguranca}}` `{{tarefa.origem_versao}}` `{{tarefa.responsavel_nome}}` |
