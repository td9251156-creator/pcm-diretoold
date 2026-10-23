# Como usar os modelos PCMD do PCM Direto

> **Aviso:** O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

Modelo versão 1.0.0 (23/10/2026) · Autor: Thiago Oliveira Lima · Contato público: pcmdireto@gmail.com · Licença MIT.

## Escolha o arquivo

Cada arquivo é independente: baixe só o que for usar. Todos têm uma versão **em branco** e uma versão **-Exemplo** com dados fictícios
(Indústria Exemplo, Pessoa A, Pessoa B, fabricantes fictícios).

| Arquivo | O que tem | Abas |
|---|---|---|
| `planilhas/PCMD-01-Controle-Documental.xlsx` | Lista mestra, revisões, organização, pessoas e requisitos | Início, Lista Mestra, Revisões, Organização, Pessoas, Requisitos, Listas |
| `planilhas/PCMD-02-Ativos-Criticidade.xlsx` | Inventário de ativos e classe A/B/C/Pendente | Início, Ativos, Critérios, Setores, Listas |
| `planilhas/PCMD-03-04-Plano-Cronograma.xlsx` | Plano mestre, ocorrências, execuções e resumo mensal com gráfico | Início, Plano Mestre, Cronograma, Ocorrências, Execuções, Listas |
| `planilhas/PCMD-05-Ficha-Falha.xlsx` | Registro de falhas | Início, Ficha de Falha |
| `manuais/PCMD-W1-Manual-Gestao-Ativos.docx` | Manual de Gestão de Ativos, com marcadores `{{...}}` | — |
| `manuais/PCMD-W2-Manual-Estrategia-Manutencao.docx` | Manual de Estratégia de Manutenção, com marcadores | — |

Outros itens: `previas/` (PDFs só para ver a impressão), `CONTRATO-CAMPOS.json` e `DICIONARIO-DE-DADOS.md` (mapa proposto para um futuro
adaptador), `RELATORIO-DE-TESTES.md`, `gerador/` e `testes/`.

Nada aqui altera o app, seus dados, exportações, backups ou workflows. O PCM Direto **ainda não** preenche estes arquivos.

## Planilhas: o básico

- Abra no Excel 2010 ou posterior (ou LibreOffice Calc). A aba **Início** lista as abas e os passos; informe ali a origem dos
  dados e a data de emissão.
- Cabeçalho **azul** = preencher; cabeçalho **cinza** = automático (fórmula, não digite). No Plano Mestre, as colunas de referência da
  biblioteca ficam bloqueadas.
- Colunas técnicas (chaves, ano, mês, contadores) ficam **ocultas**: continuam calculando e podem ser reexibidas, mas não devem ser
  editadas. A lista completa está no `DICIONARIO-DE-DADOS.md` (campo `coluna_oculta` no contrato).
- Só o que pede ação tem cor: `ERRO` em vermelho e `Pendente`/`Verificar` em amarelo. `OK` fica em cinza.
- Cálculos em branco? Recalcule: Excel `Ctrl+Alt+F9`; LibreOffice `Ctrl+Shift+F9`. Prévias de e-mail ou celular podem não calcular fórmulas.
- Como os arquivos são independentes, nomes de pessoas e TAGs são gravados como texto ao lado do ID. O vínculo é sempre o ID.

## Regras principais

**IDs e chaves.** Chave da tarefa = `ID do ativo|ID da tarefa`; chave da ocorrência = chave da tarefa + `|AAAA-MM-DD` (data prevista).
Cada execução e falha tem ID próprio. TAG e descrição do histórico ficam como foram registradas; remover ativo ou tarefa não apaga o histórico.

**Criticidade (PCMD-02).** Cinco notas inteiras de 1 a 3 (Segurança, Qualidade, Produção, Frequência de falha, Custo/tempo de reparo).
Faltando nota, nota inválida ou limites inválidos → Pendente. Com as cinco: Segurança = 3 → A; senão soma ≥ limite A → A; senão soma ≥ limite B → B;
senão C. Limites iniciais A = 12 e B = 9 (inteiros, 5 ≤ B < A ≤ 15), na aba Critérios. A classe nunca altera frequências.

**Cronograma (PCMD-03/04).** O plano vigente é a fonte; 52 semanas a partir do início, sem calendário ISO. Diária = cinco dias úteis por semana,
sem feriados, cada dia uma ocorrência com a duração de um dia. Concluída = ao menos uma execução não cancelada vinculada; duplicadas contam uma vez;
canceladas e sem vínculo aparecem separadas. O mês é o da data prevista; mês sem previsão mostra *Sem previsão*; previsões fora do ano ficam à parte.
Horas são estimadas, não trabalhadas.

**Segurança das tarefas.** Tarefa de segurança não pode ser retirada nem ter intervalo ampliado. A coluna Conferência do Plano Mestre mostra `ERRO`
quando isso acontece. O Plano Mestre é protegido sem senha só contra edição acidental: para incluir tarefas, use *Revisão > Desproteger Planilha*
e proteja de novo. Validações e proteção podem ser contornadas por colagem ou por outro programa; não substituem as travas do app.

**Datas, horas e vazios.** Datas reais do Excel (dd/mm/aaaa); horas em decimal (1,5 = uma hora e meia); vazio = não informado (horas de parada
vazias não viram zero); percentuais como fração com formato % (0,5 = 50%). Textos que começam com `=`, `+`, `-` ou `@` continuam texto.

**Metas, requisitos e indicadores.** Referencial inicial GERAL (sem norma). Requisitos começam Não verificado; Verificado exige versão, data e fonte
HTTPS e não certifica conformidade. Metas vazias ficam A definir. Não há cálculo de MTBF, MTTR ou disponibilidade sem regra aprovada.

## Capacidade e como ampliar

| Arquivo · aba | Linhas com fórmulas e validações |
|---|---|
| PCMD-01 · Lista Mestra / Revisões / Pessoas / Requisitos | 50 / 100 / 60 / 60 |
| PCMD-02 · Ativos / Setores | 300 / 30 |
| PCMD-03/04 · Plano Mestre / Ocorrências / Execuções | 2.000 / 5.000 / 3.000 |
| PCMD-05 · Ficha de Falha | 1.000 |

Todas as tabelas começam na linha 7. A linha 4 fica vazia enquanto está tudo certo; ela mostra **ATENÇÃO** se houver dados abaixo da
capacidade e avisa quantas linhas têm `ERRO`. O quadro Conferências do Cronograma também confere Ocorrências e Execuções. Para ampliar:

1. No Plano Mestre, desproteja a aba.
2. Copie a última linha da tabela inteira e cole nas linhas de baixo: fórmulas, formatos e validações vão juntos.
3. Em *Fórmulas > Gerenciador de Nomes*, estenda os nomes da aba até a nova última linha (lista no `DICIONARIO-DE-DADOS.md`,
   por exemplo `pl_chave`, `oc_chave`, `oc_conta`, `oc_concluida`, `ex_chave_oc`, `ex_cancelada`).
4. Ajuste a área de impressão e o filtro. Proteja de novo o Plano Mestre.

## Fórmulas e compatibilidade

Funções clássicas, sem PROCX, FILTRO, ÚNICO, CLASSIFICAR, SEQUÊNCIA, LET, LAMBDA, macros, VBA, Power Query, conexões ou vínculos externos.
As fórmulas ficam gravadas no padrão do formato (inglês) e o Excel em português mostra os nomes traduzidos: IF = SE, AND = E, OR = OU,
ISNUMBER = ÉNÚM, IFERROR = SEERRO, COUNTIF(S) = CONT.SE(S), COUNTA = CONT.VALORES, SUMIFS = SOMASES, INDEX = ÍNDICE, MATCH = CORRESP,
YEAR = ANO, MONTH = MÊS, DAY = DIA, LEFT = ESQUERDA, RIGHT = DIREITA, LEN = NÚM.CARACT, FIND = PROCURAR.

Impressão: A4, ajustada à largura. As tabelas imprimem a partir do cabeçalho (o nome do arquivo e da aba vão no cabeçalho da página);
Ativos, Plano Mestre e Execuções usam duas páginas de largura, repetindo as colunas de identificação. O cabeçalho da tabela se repete
e o aviso completo fica no rodapé de cada página.

## Manuais Word

- Layout único: título, grade de identificação, seções numeradas, tabelas com cabeçalho azul e um só estilo de destaque para regras.
  O aviso fica no rodapé de todas as páginas.
- Marcadores visíveis (laranja e negrito), como `{{organizacao.nome}}` e `{{documento.revisao}}`, no corpo, em células, no cabeçalho e no rodapé.
  Substitua à mão ou, no futuro, pelo adaptador. Lista completa e locais no contrato.
- Tabelas com *região repetível «nome»* têm uma linha modelo: repita a linha para cada registro.
- Só preencha **aprovador** depois de aprovação efetiva. Estratégias, prazos, metas e significado dos níveis ficam *A definir* até a definição
  do profissional responsável. Não há vínculo automático com Excel, banco de dados ou internet.

## Regerar os arquivos (reprodutível)

Na raiz do repositório:

```bash
python3 -m pip install -r entrega-templates/gerador/requirements.txt
python3 entrega-templates/gerador/gerar_tudo.py          # gera planilhas, manuais, contrato e dicionário
python3 entrega-templates/testes/verificar_entrega.py    # testes nos arquivos gerados + prévias PDF
```

- A geração usa Node.js 18+ para rodar a lógica real do app (`src/logica/plano.js`, `cronograma.js`, `pacote.js`) e uma cópia de referência de
  `gestao.js` do ramo `interface/cadastros-operacao-sem-templates` (`gerador/referencia/`), só para os dados de demonstração.
- Os testes exigem LibreOffice com Python UNO e `pdftotext`/`pdfinfo` (poppler). Resultado em `testes/resultado-testes.json`.
- Os arquivos gerados têm data fixa de criação (23/10/2026).

## Dados e privacidade

Pessoas, organização, falhas e execuções pertencem à gestão local. Não publique planilhas ou manuais preenchidos no catálogo público.
As tarefas do exemplo foram copiadas fielmente da biblioteca 0.1.0, com origem e versão.
