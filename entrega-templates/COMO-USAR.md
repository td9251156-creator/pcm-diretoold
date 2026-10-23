# Como usar os modelos PCMD do PCM Direto

> **Aviso:** O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

Modelo versão 1.0.0 (23/10/2026) · Autor: Thiago Oliveira Lima · Contato público: pcmdireto@gmail.com · Licença MIT.

## O que há nesta pasta

| Arquivo | Para que serve |
|---|---|
| `PCM-Direto-Modelos.xlsx` | Pasta Excel em branco, com cabeçalhos, validações, fórmulas e impressão configurada. |
| `PCM-Direto-Exemplo.xlsx` | Mesma estrutura, preenchida só com dados fictícios (Indústria Exemplo, Pessoa A, Pessoa B). |
| `PCMD-W1-Manual-Gestao-Ativos.docx` | Template do Manual de Gestão de Ativos, com marcadores `{{...}}` visíveis. |
| `PCMD-W2-Manual-Estrategia-Manutencao.docx` | Template do Manual de Estratégia de Manutenção. |
| `PCMD-W1-...-Exemplo.docx`, `PCMD-W2-...-Exemplo.docx` | Os manuais preenchidos com os dados fictícios. |
| `CONTRATO-CAMPOS.json` | Mapa proposto, versão 1, de cada campo, marcador e região para um futuro adaptador. |
| `DICIONARIO-DE-DADOS.md` | O mesmo conteúdo do contrato em tabelas legíveis. |
| `RELATORIO-DE-TESTES.md` | O que foi testado de fato, com qual programa, e as limitações. |
| `previas/` | PDFs gerados pelo LibreOffice só para conferir a impressão. Os arquivos editáveis são os XLSX/DOCX. |
| `gerador/` | Código-fonte da geração. `testes/` | Verificações automáticas dos arquivos gerados. |

Nada aqui altera o app, seus dados, exportações, backups ou workflows. O PCM Direto **ainda não** preenche estes arquivos:
a integração será feita depois, por um adaptador que vai ler o `CONTRATO-CAMPOS.json` e ser testado à parte.

## Usar a planilha (preenchimento manual)

1. Abra `PCM-Direto-Modelos.xlsx` no Excel 2010 ou posterior (ou LibreOffice Calc). Se pedir, permita o recálculo.
   Se aparecerem cálculos em branco: Excel `Ctrl+Alt+F9`; LibreOffice `Ctrl+Shift+F9`.
2. Siga a ordem da aba **Leia-me**: Leia-me (origem e data de emissão) → Cadastros → PCMD-02 Ativos → PCMD-03 Plano Mestre →
   PCMD-04 Ocorrências e PCMD-04 Cronograma → Execuções → PCMD-05 Ficha de Falha → PCMD-01 Lista Mestra e Revisões.
3. A linha 5 de cada tabela diz o papel da coluna: **ENTRADA**, **ID TÉCNICO**, **REFERÊNCIA**, **CÁLCULO** (não digitar),
   **MANUAL** ou **FUTURO** (manter vazio). Passe o mouse no cabeçalho para ver origem, regra de vazio e validação.
4. **PCMD-03 Plano Mestre** é protegido sem senha para não alterar sem querer a referência técnica. Para incluir tarefas da biblioteca,
   use *Revisão > Desproteger Planilha*, cole as colunas REFERÊNCIA e proteja de novo. Isso não é segurança de acesso.
5. **PCMD-04 Ocorrências** recebe uma linha por ativo + tarefa + data prevista (diária = uma linha por dia útil), com a fonte da data.
   Depois informe o ano em **PCMD-04 Cronograma**. O % do mês conta ocorrências com execução vinculada, nunca a data real.

Abas e códigos: `Leia-me`, `PCMD-01 Lista Mestra`, `PCMD-02 Ativos`, `PCMD-03 Plano Mestre`, `PCMD-04 Cronograma` (resumo),
`PCMD-04 Ocorrências` (tabela de ocorrências do PCMD-04), `PCMD-05 Ficha de Falha`, `Execuções`, `Cadastros`, `Listas`, `Revisões`.
O PCMD-04 foi dividido em duas abas para manter o resumo legível e a tabela de ocorrências filtrável.

### Capacidade e como ampliar

| Aba | Linhas com fórmulas e validações |
|---|---|
| PCMD-01 Lista Mestra | 50 (linhas 7 a 56) |
| PCMD-02 Ativos | 300 (7 a 306) |
| PCMD-03 Plano Mestre | 2.000 (7 a 2.006) |
| PCMD-04 Ocorrências | 5.000 (7 a 5.006) |
| Execuções | 3.000 (7 a 3.006) |
| PCMD-05 Ficha de Falha | 1.000 (7 a 1.006) |
| Revisões | 100 (7 a 106) |
| Cadastros | 30 setores, 60 pessoas, 60 requisitos |

A linha 4 de cada tabela mostra quantas linhas estão preenchidas e mostra **ATENÇÃO** se houver dados abaixo da capacidade.
Para ampliar sem perder fórmulas e validações:

1. (Plano Mestre) desproteja a aba.
2. Selecione a última linha da tabela inteira (todas as colunas) e copie.
3. Selecione as linhas novas abaixo e cole: fórmulas, formatos e validações são copiados juntos.
4. Em *Fórmulas > Gerenciador de Nomes*, estenda até a nova última linha os nomes da aba (lista completa no `DICIONARIO-DE-DADOS.md`,
   por exemplo `at_id`, `pl_chave`, `oc_chave`, `oc_conta`, `oc_concluida`, `ex_chave_oc`, `ex_cancelada`).
5. Ajuste a área de impressão e, se for o caso, o filtro. Proteja de novo o Plano Mestre.

### O que as validações não fazem

Validações e proteções do Excel evitam erros de digitação, mas podem ser contornadas por colagem ou por outro programa. Por isso as colunas
**Conferência** recalculam e mostram `ERRO:` ou `Verificar:` (por exemplo, tarefa de segurança com frequência reduzida). Elas não
substituem as travas do app.

## Usar os manuais Word

- Os marcadores ficam visíveis (laranja e negrito), por exemplo `{{organizacao.nome}}` e `{{documento.revisao}}`, no corpo, em células,
  no cabeçalho e no rodapé. Substitua manualmente ou, no futuro, pelo adaptador. A lista completa e o local de cada um estão no contrato.
- Tabelas com a legenda *Região repetível «nome»* têm uma linha modelo: repita a linha para cada registro.
- Sumário: no Word, botão direito no sumário > *Atualizar campo*; no LibreOffice, *Ferramentas > Atualizar > Atualizar tudo*.
  O número de páginas do rodapé também é campo e se atualiza ao abrir ou imprimir na maioria dos editores.
- Não há vínculo automático com Excel, banco de dados ou internet.
- Só preencha **aprovador** depois de uma aprovação efetiva. Estratégias, prazos por classe, metas e significado dos níveis ficam
  *A definir* até a definição do profissional responsável.

## Regerar os arquivos (reprodutível)

Na raiz do repositório:

```bash
python3 -m pip install -r entrega-templates/gerador/requirements.txt
python3 entrega-templates/gerador/gerar_tudo.py          # gera XLSX, DOCX, contrato e dicionário
python3 entrega-templates/testes/verificar_entrega.py    # testes nos arquivos gerados + prévias PDF
```

- A geração usa Node.js 18+ para rodar a lógica real do app (`src/logica/plano.js`, `cronograma.js`, `pacote.js`) e uma cópia de referência de
  `gestao.js` do ramo `interface/cadastros-operacao-sem-templates` (`gerador/referencia/`), só para os dados de demonstração.
- Os testes exigem LibreOffice com Python UNO e `pdftotext`/`pdfinfo` (poppler). Resultado em `testes/resultado-testes.json`.
- Os arquivos gerados têm data fixa de criação (23/10/2026) para facilitar a comparação entre gerações.

## Dados e privacidade

Pessoas, organização, falhas e execuções pertencem à gestão local. Não publique planilhas ou manuais preenchidos no catálogo público.
Os exemplos usam apenas dados fictícios; as tarefas do exemplo foram copiadas fielmente da biblioteca 0.1.0, com origem e versão.
