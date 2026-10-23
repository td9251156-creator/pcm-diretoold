# Relatório de testes dos modelos PCMD

> **Aviso:** O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

Data da execução: 23/10/2026 · Script: `testes/verificar_entrega.py` · Resultado bruto: `testes/resultado-testes.json`

**Resultado da última execução: 157 verificações, 0 falhas.**

## Ambiente realmente usado

| Item | Versão |
|---|---|
| Programa de planilha/texto | LibreOffice 24.2.7.2 (headless, controlado por Python UNO) |
| Geração | Python 3.13.16, openpyxl 3.1.5, python-docx 1.2.0, Node.js 22.22.0 |
| PDF e texto do PDF | LibreOffice (exportação PDF), poppler `pdftotext`/`pdfinfo` 24.02 |
| Sistema | Linux em contêiner de nuvem |

**Não havia Microsoft Excel nem Microsoft Word.** Tudo que diz "abre", "recalcula" ou "imprime" foi conferido no LibreOffice.
Isso **não comprova** compatibilidade real com Excel 2010 ou com o Word. A compatibilidade foi reforçada por regras de construção
(funções clássicas, sem `_xlfn`, sem matrizes dinâmicas, sem macros), conferidas no XML, mas precisa de um teste manual no Excel/Word.

## O que foi executado nos arquivos gerados

Os números entre parênteses seguem a lista de testes de aceitação do pedido.

### (1) Abertura
- Os 6 arquivos (2 XLSX, 4 DOCX) foram abertos pelo LibreOffice com a opção de reparo desligada; nenhum falhou ao abrir.
  Limite: em modo headless não há janela de diálogo; um arquivo que exigisse reparo falharia ao abrir, mas um aviso não bloqueante não seria visto.
- Os DOCX também foram abertos pelo python-docx e os XLSX pelo openpyxl.

### (2) Estrutura e itens proibidos
- ZIP íntegro; nenhum `vbaProject.bin`, `externalLinks`, `connections.xml`, relação `TargetMode="External"` ou tipo `macroEnabled`.
- 114.121 fórmulas por pasta XLSX examinadas no XML: nenhuma usa PROCX/XLOOKUP, FILTRO, ÚNICO, CLASSIFICAR, SEQUÊNCIA, LET, LAMBDA,
  outras funções que exigem prefixo `_xlfn`, nem fórmula de matriz.
- 11 nomes de abas válidos (até 31 caracteres) e 52 intervalos nomeados válidos. Nenhuma validação de dados aponta direto para outra aba.
- DOCX: apenas campos PAGE, NUMPAGES e TOC; nenhum vínculo LINK/INCLUDE.

### (3) Tipos de dados
- Datas das execuções e ocorrências são datas reais do Excel com formato `dd/mm/aaaa`; horas são números; horas de parada `1,5`, vazio e `0`
  ficaram preservados (vazio não virou zero). IDs técnicos iguais aos dados de origem.
- Textos iniciados por `=`, `+`, `-` e `@` estão gravados como texto no XML e **continuaram texto depois de recalculados no LibreOffice**.

### (4) Criticidade (recalculado no LibreOffice)
Cenário escrito na pasta em branco, recalculado com `calculateAll()` e lido de volta:
cinco notas 1 → C; soma 9 sem Segurança 3 → B; soma 12 → A; Segurança 3 com soma 7 → A; nota ausente → Pendente; nota 4 → Pendente com
orientação "nota inválida"; nota 2,5 → Pendente; limites 12/12 → todas Pendente e aviso em Cadastros; limites válidos 10/8 → classes recalculadas.
A validação de dados das notas é inteiro de 1 a 3 com mensagem de erro (conferida no arquivo; a recusa ao digitar não foi exercida por clique).

### (5) Ocorrências e percentual (recalculado no LibreOffice)
Duas previstas e uma concluída → 50%; duplicar a execução → 50%; cancelar as duas execuções → 0% (registros continuam e aparecem como canceladas);
legado sem vínculo → não muda o percentual e aparece no quadro separado; mês sem previsão → "Sem previsão"; execução realizada em fevereiro para
ocorrência de janeiro → conta em janeiro.

### (6) Ano, diária, histórico e vazios
Previsões em 2025 e 2027 com ano 2026 → 1 antes e 1 depois do ano; diária com 5 dias úteis → 5 ocorrências e 1,25 h (0,25 h × 5, sem multiplicar
de novo); execução de ativo removido → "Ativo removido: histórico preservado" com a TAG gravada; horas de parada vazio × zero distinguidas;
sem meta → "A definir".

### (7) Segurança e capacidade
Segurança Mensal → Trimestral: `ERRO: intervalo ampliado...`; Mensal → Semanal: OK; segurança com Ativa = Não: `ERRO`. A aba PCMD-03 está protegida
sem senha, com as colunas REFERÊNCIA bloqueadas e as de entrada liberadas.
**Limite real da proteção offline:** qualquer pessoa pode desproteger a aba (não há senha), colar por cima de validações ou editar o arquivo em outro
programa. O que não some com isso é a coluna Conferência, que recalcula e mostra o erro. Não é uma trava de segurança.
Dado escrito abaixo da capacidade do PCMD-02 e do PCMD-04 Ocorrências gera alerta `ATENÇÃO` na linha 4 e no PCMD-04 Cronograma.

### (8) Recálculo comparado com a lógica do app
`PCM-Direto-Exemplo.xlsx` foi recalculado no LibreOffice (sem usar valores em cache: o gerador não grava resultados) e comparado com
`resumoMensal()` e `criticidadeAtivo()` executados no Node sobre os mesmos dados fictícios: os 12 meses (previstas, concluídas, %, horas),
fora do ano, execuções sem vínculo e as 4 classes coincidiram. Nenhum `#VALOR!`, `#N/D` ou `Err:` nas tabelas.

### (9) Impressão
PDFs exportados pelo LibreOffice, em `previas/`. O aviso completo foi encontrado no texto de **todas** as páginas de todos os PDFs
(exemplo XLSX: 123 páginas; modelo XLSX: 27; manuais: 6 a 9, incluindo a seção em paisagem). O cabeçalho da tabela se repete em todas as páginas
de PCMD-04 Ocorrências, PCMD-03 e Execuções. Nos templates Word, marcadores aparecem impressos no corpo, em células, no cabeçalho e no rodapé.
Páginas foram também conferidas visualmente por imagem (amostras). Limite: o rodapé do Excel usa fonte 7 em duas linhas para caber o aviso inteiro;
é legível, mas pequeno.

### (10) Contrato e estrutura
Modelo e exemplo XLSX têm as mesmas abas, nomes, cabeçalhos, validações e as mesmas 114.121 fórmulas nas mesmas células. O contrato é JSON válido
(versão 1), cobre todas as colunas (rótulo e posição conferidos contra o arquivo), todos os intervalos nomeados e todos os marcadores dos dois
templates Word (39 no W1, 45 no W2), sem marcador partido entre trechos de texto. O código atual do app (`npm run verificar`: lint, 150 testes e build)
continuou passando com a pasta nova.

## O que não foi testado

- Microsoft Excel (2010 ou outra versão) e Microsoft Word: indisponíveis. Recomendado abrir os 6 arquivos no Excel/Word, conferir se não há pedido
  de reparo, recalcular (Ctrl+Alt+F9) e visualizar a impressão.
- Atualização do sumário no Word e comportamento em leitores de celular.
- Digitação real em células validadas (testes conferem as regras gravadas, não um clique humano).
- Integração com o app: não existe ainda; o contrato é proposto e o adaptador será testado depois.

## Limitações conhecidas

- O mapeamento de `estado.gestao` foi conferido no ramo `interface/cadastros-operacao-sem-templates` (commit 81ec337), ainda não integrado na main.
- O PCMD-04 ocupa duas abas: `PCMD-04 Cronograma` (resumo) e `PCMD-04 Ocorrências` (tabela).
- Capacidades fixas (ex.: 5.000 ocorrências). Uma fábrica com muitas tarefas diárias passa disso em um ano: siga "Como ampliar" no COMO-USAR.md.
- A pasta XLSX tem cerca de 2 MB porque as fórmulas já vêm escritas em todas as linhas de capacidade.
- No exemplo, a impressão do PCMD-04 Ocorrências ocupa 102 páginas (761 ocorrências, duas páginas na largura para manter a leitura).
- O logo do Excel e do Word é o PNG original do app (`public/icones/icone-512.png`), reduzido mantendo a proporção; no XLSX, a biblioteca regrava o PNG.
- Validações e proteção do Excel não substituem a validação do app.
