# Dicionário de dados dos modelos PCMD

Modelo versão 1.0.0 · gerado a partir de `gerador/especificacao.py` (mesma fonte do `CONTRATO-CAMPOS.json`).

> **Aviso:** O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

**Situação do mapeamento: proposto, ainda não validado.** A coluna Origem indica de onde o futuro adaptador poderia ler cada dado. Campos marcados como *ramo de gestão* existem apenas no ramo `interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main`. O app ainda não preenche estes arquivos.

Papéis: PREENCHER (entrada ou manual), ID (identificador técnico), REFERÊNCIA (protegida no Plano Mestre), AUTOMÁTICO (fórmula; não escrever), FUTURO (manter vazio). Colunas marcadas *oculta* são técnicas: ficam ocultas na planilha e continuam calculando.

# planilhas/PCMD-01-Controle-Documental.xlsx

PCMD-01 · Controle documental. Abas: Início, Lista Mestra, Revisões, Organização, Pessoas, Requisitos, Listas. Versão com dados fictícios: `planilhas/PCMD-01-Controle-Documental-Exemplo.xlsx`.

## Lista Mestra

Cabeçalho na linha 6; dados de 7 a 56 (capacidade 50 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `documento.codigo` | Código | PREENCHER | texto (célula com formato Texto) | obrigatório | Código PCMD do modelo (documental) | manual | Vazio = não informado. | Texto; código PCMD-xx ou PCMD-Wx. |
| B | `documento.titulo` | Título | PREENCHER | texto (célula com formato Texto) | obrigatório | Título do documento (documental) | manual | Vazio = não informado. | — |
| C | `documento.tipo` | Tipo | PREENCHER | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | Lista lst_tipo_documento. |
| D | `documento.revisao` | Revisão | PREENCHER | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | Texto (ex.: 00, 01). |
| E | `documento.data` | Data da revisão | PREENCHER | data dd/mm/aaaa | opcional | Documental | manual | Vazio = não informado. | Data válida. |
| F | `documento.elaborador` | Elaborador | PREENCHER | texto (célula com formato Texto) | opcional | Sugestão: nome de gestao.pessoas[] cujo id = gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| G | `documento.aprovador` | Aprovador | PREENCHER | texto (célula com formato Texto) | opcional | Sugestão: nome de gestao.pessoas[] cujo id = gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| H | `documento.proxima_revisao` | Próxima revisão | PREENCHER | data dd/mm/aaaa | opcional | Documental: não existe no app | manual | Vazio = a definir. | date |
| I | `documento.situacao` | Situação | PREENCHER | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | Lista lst_situacao_documento (proposta, editável). |
| J | `documento.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| K | `documento.observacao` | Observação | PREENCHER | texto (célula com formato Texto) | opcional | Documental | manual | Vazio = não informado. | — |

## Revisões

Cabeçalho na linha 6; dados de 7 a 106 (capacidade 100 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `revisao.documento` | Documento | PREENCHER | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |
| B | `revisao.numero` | Revisão | PREENCHER | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |
| C | `revisao.data` | Data | PREENCHER | data dd/mm/aaaa | obrigatório | Documental | manual | Vazio = não informado. | date |
| D | `revisao.descricao` | Descrição da mudança | PREENCHER | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |
| E | `revisao.responsavel` | Responsável | PREENCHER | texto (célula com formato Texto) | obrigatório | Documental | manual | Vazio = não informado. | — |

## Pessoas

Cabeçalho na linha 6; dados de 7 a 66 (capacidade 60 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `pessoa.id` | ID da pessoa | ID | texto (célula com formato Texto) | obrigatório | gestao.pessoas[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `pessoa.nome` | Nome | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.pessoas[].nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| C | `pessoa.funcao` | Função | PREENCHER | texto (célula com formato Texto) | opcional | gestao.pessoas[].funcao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| D | `pessoa.especialidade` | Especialidade | PREENCHER | texto (célula com formato Texto) | opcional | gestao.pessoas[].especialidade — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| E | `pessoa.ativo` | Ativa | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.pessoas[].ativo (true → Sim) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| F | `pessoa.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Requisitos

Cabeçalho na linha 6; dados de 7 a 66 (capacidade 60 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `requisito.id` | ID do requisito | ID | texto (célula com formato Texto) | obrigatório | gestao.requisitos[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `requisito.referencia` | Referência | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.requisitos[].referencia — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| C | `requisito.versao` | Versão | PREENCHER | texto (célula com formato Texto) | opcional | gestao.requisitos[].versao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir. | — |
| D | `requisito.data` | Data | PREENCHER | data dd/mm/aaaa | opcional | gestao.requisitos[].data ('' → vazio) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir. | date |
| E | `requisito.fonte` | Fonte oficial (HTTPS) | PREENCHER | texto (célula com formato Texto) | opcional | gestao.requisitos[].fonte — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | Vazio ou começa com https://. |
| F | `requisito.status` | Status | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.requisitos[].status (nao_verificado \| verificado) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| G | `requisito.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Células únicas

| Aba!Célula | Campo | Rótulo | Papel | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|
| Organização!B7 | `organizacao.nome` | Nome da organização | PREENCHER | gestao.organizacao.nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | Até 120 caracteres. |
| Organização!B8 | `organizacao.referencial` | Referencial | PREENCHER | gestao.organizacao.referencial — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão: GERAL (sem norma). | Até 120 caracteres; não citar norma sem fonte. |
| Organização!B9 | `organizacao.prefixo` | Prefixo dos documentos | PREENCHER | gestao.organizacao.padraoCodigo — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão: PCMD. | Até 40 caracteres. |
| Organização!B10 | `organizacao.elaborador_id` | Elaborador padrão (ID) | PREENCHER | gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | Lista cad_pessoa_id. |
| Organização!B11 | `organizacao.aprovador_id` | Aprovador padrão (ID) | PREENCHER | gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado; não presumir aprovação. | Lista cad_pessoa_id. |
| Organização!B12 | `metas.disponibilidade` | Meta de disponibilidade (%) | PREENCHER | gestao.metas.disponibilidade (0–100 no app → dividir por 100) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir (null no app). | 0% a 100%. |
| Início!C20 | `emissao.origem_dados` | Origem dos dados | PREENCHER | Texto curto do adaptador ou de quem preenche | futuro | Vazio = não informado. | Texto. |
| Início!C21 | `emissao.data` | Data de emissão | PREENCHER | Data em que o arquivo é gerado/preenchido | futuro | Vazio = não informado. | Data válida. |

## Intervalos nomeados

| Nome | Referência |
|---|---|
| `cad_meta_disponibilidade` | `'Organização'!$B$12` |
| `cad_org_nome` | `'Organização'!$B$7` |
| `cad_pessoa_id` | `'Pessoas'!$A$7:$A$66` |
| `cad_pessoa_nome` | `'Pessoas'!$B$7:$B$66` |
| `cad_prefixo` | `'Organização'!$B$9` |
| `cad_referencial` | `'Organização'!$B$8` |
| `lst_sim_nao` | `'Listas'!$E$7:$E$8` |
| `lst_situacao_documento` | `'Listas'!$C$7:$C$16` |
| `lst_status_requisito` | `'Listas'!$G$7:$G$8` |
| `lst_tipo_documento` | `'Listas'!$A$7:$A$16` |
| `pcmd_emissao` | `'Início'!$C$21` |
| `pcmd_origem` | `'Início'!$C$20` |

# planilhas/PCMD-02-Ativos-Criticidade.xlsx

PCMD-02 · Ativos e criticidade. Abas: Início, Ativos, Critérios, Setores, Listas. Versão com dados fictícios: `planilhas/PCMD-02-Ativos-Criticidade-Exemplo.xlsx`.

## Ativos

Cabeçalho na linha 6; dados de 7 a 306 (capacidade 300 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `ativo.id` | ID do ativo | ID | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].id | app (main) | Vazio = não informado. | Único; sem espaços e sem \|. |
| B | `ativo.tag` | TAG | PREENCHER | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].tag (SETOR-SIGLA-NNN, src/logica/tag.js) | app (main) | Vazio = não informado. | — |
| C | `ativo.descricao` | Descrição | PREENCHER | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].descricao | app (main) | Vazio = não informado. | — |
| D | `ativo.tipo_id` | Tipo | PREENCHER | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].tipo (id do tipo na biblioteca) | app (main) | Vazio = não informado. | Lista lst_tipo_id. |
| E | `ativo.tipo_nome` | Tipo (nome) | AUTOMÁTICO · oculta | texto | opcional | Fórmula a partir de Listas (biblioteca.tipos[].nome) | cálculo | Vazio = não informado. | — |
| F | `ativo.fabricante` | Fabricante | PREENCHER | texto (célula com formato Texto) | opcional | estado.equipamentos[].fabricante | app (main) | Vazio = não informado. | — |
| G | `ativo.modelo` | Modelo | PREENCHER | texto (célula com formato Texto) | opcional | estado.equipamentos[].modelo | app (main) | Vazio = não informado. | — |
| H | `ativo.setor` | Setor | PREENCHER | texto (célula com formato Texto) | obrigatório | estado.equipamentos[].setor | app (main) | Vazio = não informado. | Lista cad_setor. |
| I | `ativo.numero` | Número | PREENCHER | inteiro 1–999 | obrigatório | estado.equipamentos[].numero | app (main) | Vazio = não informado. | whole |
| J | `ativo.tag_conferencia` | Conferência TAG | AUTOMÁTICO | texto | opcional | Fórmula: SETOR-SIGLA-NNN | cálculo | Vazio = não informado. | — |
| K | `criticidade.nota_seguranca` | N1 Segurança | PREENCHER | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][0] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| L | `criticidade.nota_qualidade` | N2 Qualidade | PREENCHER | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][1] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| M | `criticidade.nota_producao` | N3 Produção | PREENCHER | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][2] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| N | `criticidade.nota_frequencia_falha` | N4 Freq. de falha | PREENCHER | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][3] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| O | `criticidade.nota_custo_reparo` | N5 Custo/tempo reparo | PREENCHER | inteiro 1–3 | condicional | gestao.criticidade.notas[ativo.id][4] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não avaliado (nunca zero). | Inteiro de 1 a 3. |
| P | `criticidade.notas_validas` | Notas válidas (de 5) | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| Q | `criticidade.pontuacao` | Pontuação | AUTOMÁTICO | texto | opcional | Fórmula (equivale a criticidadeAtivo().pontuacao) | cálculo | Vazio enquanto houver nota ausente ou inválida. | — |
| R | `criticidade.classe` | Classe | AUTOMÁTICO | texto | opcional | Fórmula (equivale a criticidadeAtivo().classe) | cálculo | Vazio = não informado. | A, B, C ou Pendente. |
| S | `criticidade.orientacao` | Orientação | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Setores

Cabeçalho na linha 6; dados de 7 a 36 (capacidade 30 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `setor.sigla` | Sigla | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.organizacao.setores[] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main; também estado.equipamentos[].setor (main) | app (ramo de gestão, não integrado) | Vazio = não informado. | 2 a 4 letras maiúsculas/números (normalizarSetor). |
| B | `setor.descricao` | Descrição | PREENCHER | texto (célula com formato Texto) | opcional | Não existe no app (o app guarda só a sigla) | manual | Vazio = não informado. | — |
| C | `setor.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Células únicas

| Aba!Célula | Campo | Rótulo | Papel | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|
| Critérios!B7 | `criticidade.limite_a` | Limite A | PREENCHER | gestao.criticidade.limites.a — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 12. | Inteiro; 5 ≤ B < A ≤ 15. |
| Critérios!B8 | `criticidade.limite_b` | Limite B | PREENCHER | gestao.criticidade.limites.b — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 9. | Inteiro; 5 ≤ B < A ≤ 15. |
| Critérios!B9 | `criticidade.limites_ok` | Limites válidos? | AUTOMÁTICO | Fórmula | cálculo | — | VERDADEIRO/FALSO. |
| Critérios!B13:D17 | `criticidade.niveis` | Significado dos níveis 1/2/3 por critério | PREENCHER | Definição do mantenedor; não existe no app | manual | Vazio = A definir pelo mantenedor. | Texto livre. |
| Início!C18 | `emissao.origem_dados` | Origem dos dados | PREENCHER | Texto curto do adaptador ou de quem preenche | futuro | Vazio = não informado. | Texto. |
| Início!C19 | `emissao.data` | Data de emissão | PREENCHER | Data em que o arquivo é gerado/preenchido | futuro | Vazio = não informado. | Data válida. |

## Intervalos nomeados

| Nome | Referência |
|---|---|
| `at_descricao` | `'Ativos'!$C$7:$C$306` |
| `at_id` | `'Ativos'!$A$7:$A$306` |
| `at_tag` | `'Ativos'!$B$7:$B$306` |
| `cad_limite_a` | `'Critérios'!$B$7` |
| `cad_limite_b` | `'Critérios'!$B$8` |
| `cad_limites_ok` | `'Critérios'!$B$9` |
| `cad_setor` | `'Setores'!$A$7:$A$36` |
| `lst_tipo_id` | `'Listas'!$A$7:$A$36` |
| `lst_tipo_nome` | `'Listas'!$B$7:$B$36` |
| `lst_tipo_sigla` | `'Listas'!$C$7:$C$36` |
| `pcmd_emissao` | `'Início'!$C$19` |
| `pcmd_origem` | `'Início'!$C$18` |

# planilhas/PCMD-03-04-Plano-Cronograma.xlsx

PCMD-03/04 · Plano mestre e cronograma. Abas: Início, Plano Mestre, Cronograma, Ocorrências, Execuções, Listas. Versão com dados fictícios: `planilhas/PCMD-03-04-Plano-Cronograma-Exemplo.xlsx`.

## Plano Mestre

Cabeçalho na linha 6; dados de 7 a 2006 (capacidade 2000 linhas); aba protegida sem senha.

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `tarefa.ativo_id` | ID do ativo | ID | texto (célula com formato Texto) | obrigatório | plano[].equipamentoId (gerarPlano, src/logica/plano.js) | app (main) | Vazio = não informado. | custom |
| B | `tarefa.id` | ID da tarefa | ID | texto (célula com formato Texto) | obrigatório | plano[].tarefaId (biblioteca.tipos[].tarefas[].id) | app (main) | Vazio = não informado. | custom |
| C | `tarefa.chave` | Chave da tarefa (ativo\|tarefa) | AUTOMÁTICO · oculta | texto | opcional | Fórmula: equipamentoId\|tarefaId (chaveAjuste) | cálculo | Vazio = não informado. | — |
| D | `tarefa.tag` | TAG | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].tag (TAG vigente do ativo) | app (main) | Vazio = não informado. | — |
| E | `tarefa.atividade` | Atividade | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].descricao | app (main) | Vazio = não informado. | — |
| F | `tarefa.origem` | Origem | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].origem | app (main) | Vazio = não informado. | — |
| G | `tarefa.versao` | Versão | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].versao | app (main) | Vazio = não informado. | — |
| H | `tarefa.frequencia_referencia` | Frequência referência | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].periodicidadeOriginal | app (main) | Vazio = não informado. | Lista lst_frequencias. |
| I | `tarefa.seguranca` | Segurança | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].seguranca (true → Sim) | app (main) | Vazio = não informado. | Sim ou Não. |
| J | `tarefa.frequencia_vigente` | Frequência vigente | PREENCHER | texto (célula com formato Texto) | obrigatório | plano[].periodicidade (após ajustes válidos) | app (main) | Vazio = não informado. | Lista lst_frequencias; segurança não pode ser menos frequente. |
| K | `tarefa.vezes_ano` | Vezes/ano | AUTOMÁTICO | texto | opcional | Fórmula (vezesPorAno) | cálculo | Vazio = não informado. | — |
| L | `tarefa.especialidade` | Especialidade | REFERÊNCIA | texto (célula com formato Texto) | obrigatório | plano[].especialidade | app (main) | Vazio = não informado. | list |
| M | `tarefa.duracao_horas` | Duração (h) | REFERÊNCIA | número decimal de horas | obrigatório | plano[].duracaoHoras (biblioteca duracao_horas) | app (main) | Vazio = não informado. | decimal |
| N | `tarefa.horas_ciclo` | Horas/ano | AUTOMÁTICO | número decimal de horas | opcional | Fórmula: duração × execuções no ciclo | cálculo | Vazio = não informado. | — |
| O | `tarefa.ativa` | Ativa | PREENCHER | texto (célula com formato Texto) | obrigatório | plano[].ativa (true → Sim) | app (main) | Vazio = não informado. | list |
| P | `tarefa.responsavel_id` | Responsável (ID) | PREENCHER · oculta | texto (célula com formato Texto) | opcional | gestao.responsaveis['equipamentoId\|tarefaId'] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| Q | `tarefa.responsavel_nome` | Responsável | PREENCHER | texto (célula com formato Texto) | opcional | nome de gestao.pessoas[] com id = gestao.responsaveis['equipamentoId\|tarefaId'] — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| R | `tarefa.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula (equivale a podeAlterar) | cálculo | Vazio = não informado. | — |
| S | `tarefa.observacao` | Observação | REFERÊNCIA | texto (célula com formato Texto) | opcional | plano[].observacao | app (main) | Vazio = não informado. | — |

## Ocorrências

Cabeçalho na linha 6; dados de 7 a 5006 (capacidade 5000 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `ocorrencia.ativo_id` | ID do ativo | ID | texto (célula com formato Texto) | obrigatório | ocorrenciasPlanejadas(dados)[].equipamentoId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `ocorrencia.tarefa_id` | ID da tarefa | ID | texto (célula com formato Texto) | obrigatório | ocorrenciasPlanejadas(dados)[].tarefaId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| C | `ocorrencia.data_prevista` | Data prevista | PREENCHER | data dd/mm/aaaa | obrigatório | ocorrenciasPlanejadas(dados)[].dataPrevista (AAAA-MM-DD → data Excel) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | date |
| D | `ocorrencia.fonte` | Fonte da data | PREENCHER | texto (célula com formato Texto) | obrigatório | Texto do adaptador ou de quem digitou | manual | Vazio = não informado. | — |
| E | `ocorrencia.chave_tarefa` | Chave da tarefa | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| F | `ocorrencia.chave` | Chave da ocorrência (ativo\|tarefa\|AAAA-MM-DD) | AUTOMÁTICO · oculta | texto | opcional | Fórmula (equivale a ocorrencia.chave do app) | cálculo | Vazio = não informado. | — |
| G | `ocorrencia.linha_plano` | Linha no plano (técnico) | AUTOMÁTICO · oculta | texto | opcional | Fórmula: posição da chave no Plano Mestre | cálculo | Vazio = não informado. | — |
| H | `ocorrencia.tag` | TAG | AUTOMÁTICO | texto | opcional | Fórmula a partir do Plano Mestre | cálculo | Vazio = não informado. | — |
| I | `ocorrencia.atividade` | Atividade | AUTOMÁTICO | texto | opcional | Fórmula a partir do Plano Mestre | cálculo | Vazio = não informado. | — |
| J | `ocorrencia.especialidade` | Especialidade | AUTOMÁTICO | texto | opcional | Fórmula a partir do Plano Mestre | cálculo | Vazio = não informado. | — |
| K | `ocorrencia.horas_estimadas` | Horas (h) | AUTOMÁTICO | número decimal de horas | opcional | Fórmula: duração por execução do Plano Mestre | cálculo | Vazio = não informado. | — |
| L | `ocorrencia.ano` | Ano previsto | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| M | `ocorrencia.mes` | Mês previsto | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| N | `ocorrencia.posicao` | Posição em relação ao ano consultado | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| O | `ocorrencia.primeira` | Primeira linha da chave (1/0) | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| P | `ocorrencia.conta` | Prevista válida (1/0) | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| Q | `ocorrencia.execucoes_ativas` | Execuções ativas vinculadas | AUTOMÁTICO · oculta | texto | opcional | Fórmula: CONT.SES em Execuções | cálculo | Vazio = não informado. | — |
| R | `ocorrencia.concluida` | Concluída | AUTOMÁTICO | texto | opcional | Fórmula: 1 se prevista válida com execução ativa | cálculo | Vazio = não informado. | — |
| S | `ocorrencia.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Execuções

Cabeçalho na linha 6; dados de 7 a 3006 (capacidade 3000 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `execucao.id` | ID do registro | ID | texto (célula com formato Texto) | obrigatório | gestao.historico[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `execucao.ativo_id` | ID do ativo | ID | texto (célula com formato Texto) | obrigatório | gestao.historico[].equipamentoId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| C | `execucao.tarefa_id` | ID da tarefa | ID | texto (célula com formato Texto) | obrigatório | gestao.historico[].tarefaId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| D | `execucao.chave_tarefa` | Chave da tarefa | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| E | `execucao.tag` | TAG | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.historico[].tag — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| F | `execucao.descricao` | Descrição | PREENCHER | texto (célula com formato Texto) | opcional | gestao.historico[].descricao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| G | `execucao.data_prevista` | Data prevista | PREENCHER | data dd/mm/aaaa | opcional | gestao.historico[].dataPrevista ('' → vazio) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = execução sem vínculo (não entra no percentual). | date |
| H | `execucao.data` | Data realizada | PREENCHER | data dd/mm/aaaa | obrigatório | gestao.historico[].data — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | date |
| I | `execucao.chave_ocorrencia` | Chave da ocorrência vinculada | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| J | `execucao.observacao` | Observação | PREENCHER | texto (célula com formato Texto) | opcional | gestao.historico[].observacao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| K | `execucao.responsavel_id` | Responsável (ID) | PREENCHER · oculta | texto (célula com formato Texto) | opcional | gestao.historico[].responsavelId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| L | `execucao.responsavel_nome` | Responsável | PREENCHER | texto (célula com formato Texto) | opcional | nome de gestao.pessoas[] com id = gestao.historico[].responsavelId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| M | `execucao.origem` | Origem | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.historico[].origem (app \| legado) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | list |
| N | `execucao.cancelada` | Cancelada | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.historico[].cancelada (true → Sim) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio é tratado como Não (ativa). | list |
| O | `execucao.vinculo` | Vínculo | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| P | `execucao.ano` | Ano realizado | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| Q | `execucao.situacao_plano` | No plano? | AUTOMÁTICO | texto | opcional | Fórmula: chave da tarefa no Plano Mestre | cálculo | Vazio = não informado. | — |
| R | `execucao.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| S | `execucao.duracao_real_horas` | Duração real (h) — FUTURO, não integrado | FUTURO · oculta | número decimal de horas | opcional | Não existe no histórico atual do app | futuro | Manter vazio. Não é somado em nenhuma fórmula. | decimal |

## Células únicas

| Aba!Célula | Campo | Rótulo | Papel | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|
| Cronograma!C7 | `cronograma.ano` | Ano consultado | PREENCHER | escolha do usuário (resumoMensal(dados, gestao, ano)) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = resumo em branco. | Inteiro de 1900 a 9999. |
| Cronograma!C8 | `cronograma.inicio` | Início do ciclo (semana 1) | PREENCHER | estado.inicio (AAAA-MM-DD, main) | app (main) | Vazio = não informado. | Data válida. |
| Cronograma!C9 | `cronograma.fonte` | Fonte das ocorrências | PREENCHER | Texto do adaptador ou de quem preenche | futuro | Vazio = não informado. | Texto. |
| Cronograma!C11 | `metas.aderencia` | Meta de aderência preventiva (%) | PREENCHER | gestao.metas.aderencia (0–100 no app → dividir por 100) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = A definir (null no app). | 0% a 100%. |
| Início!C20 | `emissao.origem_dados` | Origem dos dados | PREENCHER | Texto curto do adaptador ou de quem preenche | futuro | Vazio = não informado. | Texto. |
| Início!C21 | `emissao.data` | Data de emissão | PREENCHER | Data em que o arquivo é gerado/preenchido | futuro | Vazio = não informado. | Data válida. |

## Intervalos nomeados

| Nome | Referência |
|---|---|
| `crono_ano` | `'Cronograma'!$C$7` |
| `crono_inicio` | `'Cronograma'!$C$8` |
| `crono_meta_aderencia` | `'Cronograma'!$C$11` |
| `ex_ano` | `'Execuções'!$P$7:$P$3006` |
| `ex_cancelada` | `'Execuções'!$N$7:$N$3006` |
| `ex_chave_oc` | `'Execuções'!$I$7:$I$3006` |
| `ex_id` | `'Execuções'!$A$7:$A$3006` |
| `ex_vinculo` | `'Execuções'!$O$7:$O$3006` |
| `lst_especialidades` | `'Listas'!$E$7:$E$36` |
| `lst_frequencias` | `'Listas'!$A$7:$A$14` |
| `lst_frequencias_vezes` | `'Listas'!$B$7:$B$14` |
| `lst_origem_execucao` | `'Listas'!$I$7:$I$8` |
| `lst_sim_nao` | `'Listas'!$G$7:$G$8` |
| `oc_ano` | `'Ocorrências'!$L$7:$L$5006` |
| `oc_chave` | `'Ocorrências'!$F$7:$F$5006` |
| `oc_concluida` | `'Ocorrências'!$R$7:$R$5006` |
| `oc_conferencia` | `'Ocorrências'!$S$7:$S$5006` |
| `oc_conta` | `'Ocorrências'!$P$7:$P$5006` |
| `oc_horas` | `'Ocorrências'!$K$7:$K$5006` |
| `oc_mes` | `'Ocorrências'!$M$7:$M$5006` |
| `oc_posicao` | `'Ocorrências'!$N$7:$N$5006` |
| `pcmd_emissao` | `'Início'!$C$21` |
| `pcmd_origem` | `'Início'!$C$20` |
| `pl_ativa` | `'Plano Mestre'!$O$7:$O$2006` |
| `pl_atividade` | `'Plano Mestre'!$E$7:$E$2006` |
| `pl_chave` | `'Plano Mestre'!$C$7:$C$2006` |
| `pl_duracao` | `'Plano Mestre'!$M$7:$M$2006` |
| `pl_especialidade` | `'Plano Mestre'!$L$7:$L$2006` |
| `pl_seguranca` | `'Plano Mestre'!$I$7:$I$2006` |
| `pl_tag` | `'Plano Mestre'!$D$7:$D$2006` |
| `pl_vezes` | `'Plano Mestre'!$K$7:$K$2006` |

# planilhas/PCMD-05-Ficha-Falha.xlsx

PCMD-05 · Ficha de falha. Abas: Início, Ficha de Falha. Versão com dados fictícios: `planilhas/PCMD-05-Ficha-Falha-Exemplo.xlsx`.

## Ficha de Falha

Cabeçalho na linha 6; dados de 7 a 1006 (capacidade 1000 linhas).

| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|---|---|
| A | `falha.id` | ID do registro | ID | texto (célula com formato Texto) | obrigatório | gestao.falhas[].id — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| B | `falha.ativo_id` | ID do ativo | ID | texto (célula com formato Texto) | obrigatório | gestao.falhas[].equipamentoId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| C | `falha.data` | Data | PREENCHER | data dd/mm/aaaa | obrigatório | gestao.falhas[].data — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | date |
| D | `falha.tag` | TAG | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.falhas[].tag — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| E | `falha.sintoma` | Sintoma | PREENCHER | texto (célula com formato Texto) | obrigatório | gestao.falhas[].sintoma — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| F | `falha.causa` | Causa | PREENCHER | texto (célula com formato Texto) | opcional | gestao.falhas[].causa — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| G | `falha.acao` | Ação | PREENCHER | texto (célula com formato Texto) | opcional | gestao.falhas[].acao — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| H | `falha.horas_parada` | Parada (h) | PREENCHER | número decimal de horas | opcional | gestao.falhas[].horasParada (null → vazio) — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado; nunca converter em zero. | decimal |
| I | `falha.peca` | Peça | PREENCHER | texto (célula com formato Texto) | opcional | gestao.falhas[].peca — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| J | `falha.responsavel_id` | Responsável (ID) | PREENCHER · oculta | texto (célula com formato Texto) | opcional | gestao.falhas[].responsavelId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | custom |
| K | `falha.responsavel_nome` | Responsável | PREENCHER | texto (célula com formato Texto) | opcional | nome de gestao.pessoas[] com id = gestao.falhas[].responsavelId — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio = não informado. | — |
| L | `falha.parada_situacao` | Parada informada? | AUTOMÁTICO · oculta | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |
| M | `falha.conferencia` | Conferência | AUTOMÁTICO | texto | opcional | Fórmula | cálculo | Vazio = não informado. | — |

## Células únicas

| Aba!Célula | Campo | Rótulo | Papel | Origem proposta | Situação | Vazio | Validação |
|---|---|---|---|---|---|---|---|
| Início!C15 | `emissao.origem_dados` | Origem dos dados | PREENCHER | Texto curto do adaptador ou de quem preenche | futuro | Vazio = não informado. | Texto. |
| Início!C16 | `emissao.data` | Data de emissão | PREENCHER | Data em que o arquivo é gerado/preenchido | futuro | Vazio = não informado. | Data válida. |

## Intervalos nomeados

| Nome | Referência |
|---|---|
| `fa_id` | `'Ficha de Falha'!$A$7:$A$1006` |
| `fa_parada` | `'Ficha de Falha'!$L$7:$L$1006` |
| `pcmd_emissao` | `'Início'!$C$16` |
| `pcmd_origem` | `'Início'!$C$15` |

# manuais/PCMD-W1-Manual-Gestao-Ativos.docx

### Marcadores

| Marcador | Descrição | Locais | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|
| `{{organizacao.nome}}` | Nome da organização | cabeçalho, célula de tabela (identificação), parágrafo | gestao.organizacao.nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.revisao}}` | Revisão do documento | célula de tabela (identificação), rodapé | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{organizacao.referencial}}` | Referencial adotado | célula de tabela (identificação), parágrafo | gestao.organizacao.referencial — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 'GERAL (sem norma)'. |
| `{{documento.data}}` | Data da revisão (dd/mm/aaaa) | célula de tabela (identificação) | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.elaborador}}` | Nome do elaborador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.aprovador}}` | Nome do aprovador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir (aprovação não registrada)'. Nunca presumir aprovação. |
| `{{documento.proxima_revisao}}` | Próxima revisão (dd/mm/aaaa) | célula de tabela (identificação), parágrafo | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.situacao}}` | Situação do documento | célula de tabela (identificação) | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'Em elaboração'. |
| `{{origem.dados}}` | Origem dos dados | célula de tabela (identificação) | Texto curto do adaptador (ex.: PCM Direto, backup local de dd/mm/aaaa) | futuro | Vazio → 'Não informada'. |
| `{{emissao.data}}` | Data de emissão do arquivo (dd/mm/aaaa) | célula de tabela (identificação) | Data em que o adaptador gera o arquivo | futuro | Vazio → 'A definir'. |
| `{{criticidade.limite_a}}` | Limite A da criticidade | célula de tabela | gestao.criticidade.limites.a — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{criticidade.limite_b}}` | Limite B da criticidade | célula de tabela | gestao.criticidade.limites.b — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{metas.disponibilidade}}` | Meta de disponibilidade | célula de tabela | gestao.metas.disponibilidade — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | null → 'A definir'. |

### Regiões repetíveis

| Região | Tabela nº (corpo, a partir de 0) | Linha modelo | Marcadores da linha |
|---|---|---|---|
| `pessoas` | 3 | 1 | `{{pessoa.nome}}` `{{pessoa.funcao}}` `{{pessoa.especialidade}}` `{{pessoa.responsabilidade}}` |
| `setores` | 5 | 1 | `{{setor.sigla}}` `{{setor.descricao}}` |
| `requisitos` | 9 | 1 | `{{requisito.referencia}}` `{{requisito.versao}}` `{{requisito.data}}` `{{requisito.fonte}}` `{{requisito.status}}` |
| `revisoes` | 13 | 1 | `{{revisao.numero}}` `{{revisao.data}}` `{{revisao.descricao}}` `{{revisao.responsavel}}` |
| `ativos` | 14 | 1 | `{{ativo.tag}}` `{{ativo.descricao}}` `{{ativo.setor}}` `{{ativo.tipo_nome}}` `{{criticidade.nota_seguranca}}` `{{criticidade.nota_qualidade}}` `{{criticidade.nota_producao}}` `{{criticidade.nota_frequencia_falha}}` `{{criticidade.nota_custo_reparo}}` `{{criticidade.pontuacao}}` `{{criticidade.classe}}` |

# manuais/PCMD-W2-Manual-Estrategia-Manutencao.docx

### Marcadores

| Marcador | Descrição | Locais | Origem proposta | Situação | Vazio |
|---|---|---|---|---|---|
| `{{organizacao.nome}}` | Nome da organização | cabeçalho, célula de tabela (identificação), parágrafo | gestao.organizacao.nome — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.revisao}}` | Revisão do documento | célula de tabela (identificação), rodapé | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{organizacao.referencial}}` | Referencial adotado | célula de tabela (identificação), parágrafo | gestao.organizacao.referencial — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Padrão 'GERAL (sem norma)'. |
| `{{documento.data}}` | Data da revisão (dd/mm/aaaa) | célula de tabela (identificação) | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.elaborador}}` | Nome do elaborador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.elaborador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir'. |
| `{{documento.aprovador}}` | Nome do aprovador | célula de tabela, célula de tabela (identificação) | nome de gestao.pessoas[] com id = gestao.organizacao.aprovador — ramo interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main | app (ramo de gestão, não integrado) | Vazio → 'A definir (aprovação não registrada)'. Nunca presumir aprovação. |
| `{{documento.proxima_revisao}}` | Próxima revisão (dd/mm/aaaa) | célula de tabela (identificação) | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'A definir'. |
| `{{documento.situacao}}` | Situação do documento | célula de tabela (identificação) | PCMD-01, aba Lista Mestra (manual) | manual | Vazio → 'Em elaboração'. |
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
| `pessoas` | 3 | 1 | `{{pessoa.nome}}` `{{pessoa.funcao}}` `{{pessoa.especialidade}}` `{{pessoa.responsabilidade}}` |
| `requisitos` | 8 | 1 | `{{requisito.referencia}}` `{{requisito.versao}}` `{{requisito.data}}` `{{requisito.fonte}}` `{{requisito.status}}` |
| `revisoes` | 10 | 1 | `{{revisao.numero}}` `{{revisao.data}}` `{{revisao.descricao}}` `{{revisao.responsavel}}` |
| `tarefas` | 11 | 1 | `{{tarefa.tag}}` `{{tarefa.id}}` `{{tarefa.atividade}}` `{{tarefa.frequencia_vigente}}` `{{tarefa.especialidade}}` `{{tarefa.duracao_horas}}` `{{tarefa.seguranca}}` `{{tarefa.origem_versao}}` `{{tarefa.responsavel_nome}}` |
