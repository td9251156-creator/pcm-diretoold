# Interface funcional e modelos a fornecer

## Nova direção

O mantenedor criará os modelos Excel e Word e os enviará depois. Esta entrega desenvolve os
cadastros e a operação no navegador; não cria templates, fórmulas ou geradores PCMD novos.
O PR #31 com o protótipo anterior permanece separado e não deve ser integrado como dependência.
A planilha e o resumo antigos continuam disponíveis. Nenhum modelo enviado será interpretado
ou publicado automaticamente: primeiro será conferido o formato e definida sua conexão aos dados.

## Interface e fonte única dos dados

- **Cadastros:** organização, setores, pessoas e funções, frequências/tipos de consulta, metas e requisitos.
- **Equipamentos:** cadastro já existente, TAG gerada, validação e edição da lista.
- **Criticidade:** cinco notas por ativo, limites A/B e resultado calculado sem mudar tarefas.
- **Revisão:** plano e capacidade semanal existentes; responsável por tarefa cadastrado na criticidade/plano.
- **Mensal:** ocorrências das semanas agrupadas de janeiro a dezembro; fora do ano é mostrado separado.
- **Execuções:** registrar cada realização e sua data prevista opcional; consultar e cancelar registros.
- **Falhas:** registrar ocorrências com ativo, sintoma, causa, ação e horas de parada opcionais.
- **Entrega:** downloads existentes e lista dos documentos PCMD aguardando os arquivos do mantenedor.

Tudo fica no navegador e no backup JSON. A interface não possui login, servidor ou sincronização
entre aparelhos. Dados reais digitados pelo usuário permanecem locais; exemplos e testes são fictícios.

## Regras dos registros

Criticidade usa cinco notas de 1 a 3. Segurança 3 determina classe A, com todas as notas preenchidas;
demais A≥12, B≥9 e C abaixo de 9, com limites editáveis 5≤B<A≤15. Sem notas completas, Pendente.
Classe não altera automaticamente periodicidade nem proteção de segurança.
Metas e prazos técnicos não são presumidos; ausência de meta aparece como a definir.
Disponibilidade e MTBF/MTTR não são calculados sem definições técnicas do mantenedor.
Referencial inicial GERAL (sem norma); requisitos começam não verificados. Verificado exige
versão, data e URL HTTPS da fonte, sem o app certificar que o conteúdo da fonte foi revisado.
O cadastro de frequências é uma consulta das regras existentes, sem mudar a biblioteca nesta entrega.

Cada execução nova é um registro. O vínculo à ocorrência prevista é explícito, nunca inferido da data.
Marcações antigas migram como legado sem vínculo; continuam visíveis, sem multiplicar realizações.
Uma ocorrência concluída só conta uma vez no percentual, mesmo com vários registros associados.
Cancelar preserva o registro no histórico e o exclui da contagem. Datas de realização/falha futuras
são recusadas na interface. Não há calendário de feriados; diária considera os dias úteis da semana.
Remover um ativo não apaga o histórico de execução/falhas; os registros preservam TAG/descrição.

## Como você deve criar a planilha

Uma pasta XLSX, sem macros ou vínculos externos. Fonte única de cada informação, entradas
visualmente distintas dos cálculos e instruções curtas. Abas com nomes até 31 caracteres.
O app fornecerá os dados; o posicionamento exato das células será mapeado quando você enviar o modelo.
Use códigos PCMD próprios e exemplos Indústria Exemplo, Pessoa A e Pessoa B.

| Aba/documento | Colunas ou conteúdo necessário | Fonte no app |
|---|---|---|
| Leia-me | Objetivo, ordem de uso, legenda, recálculo, limitações e aviso | Texto do modelo e metadados |
| PCMD-01 Lista Mestra | Código, título, tipo, revisão, data, elaborador, aprovador, próxima revisão, situação | Organização e catálogo de documentos |
| PCMD-02 Ativos | TAG, equipamento, setor, número, cinco notas, pontuação e classe | Equipamentos e criticidade |
| PCMD-03 Plano Mestre | Chave de tarefa, TAG, atividade, origem/versão, frequência, especialidade, horas, responsável e segurança | Plano e pessoas |
| PCMD-04 Cronograma | Ano, meses, ocorrências e horas previstas, realizadas e percentual; fora do ano separado | Planejamento e histórico vinculado |
| PCMD-05 Ficha de Falha | ID, data, TAG, sintoma, causa, ação, horas de parada, peça e responsável | Registros de falha |
| Execuções | ID, chave de tarefa, TAG, data prevista, data realizada, observação, responsável, origem e cancelamento | Histórico completo |
| Cadastros | Organização/setores, pessoas/funções, metas e requisitos com fonte/versão/status | M1, M3, M5 e M6 |
| Listas | Frequências aceitas, tipos de tarefa e especialidades | M4 e biblioteca |
| Revisões | Revisão, data, descrição e responsável pela mudança do documento | Histórico documental do modelo |

Os identificadores internos de ativos, tarefas, pessoas e execuções deverão ter colunas técnicas
próprias, podendo ficar ocultas. TAG é rótulo, não substituto do ID. Não remova as tarefas de segurança
nem permita ampliar seus intervalos. Importação de planilhas exigirá projeto específico depois que
o formato for conhecido, com prévia e cópia recuperável; ela não faz parte desta entrega.

## Regras práticas para montar o Excel

- Células de entrada em cor distinta das calculadas; cabeçalhos com notas sobre o preenchimento.
- Criticidade: cinco notas inteiras de 1 a 3, soma entre 5 e 15, com Pendente enquanto faltar nota.
  Segurança 3 determina A; demais limites editáveis começam A=12 e B=9, sujeitos à sua validação.
- Não duplicar frequência em vários lugares: Plano Mestre é a fonte, Cronograma apenas a consulta.
- % realizado é por ocorrência prevista, não por tarefa que já foi marcada alguma vez. Canceladas
  não contam; sem previsão no mês, mostrar traço, sem divisão por zero. Legado sem vínculo fica separado.
- Usar somente funções clássicas do Excel 2010, sem VBA, macros ou matriz dinâmica. Evitar
  PROCX, FILTRO, ÚNICO, CLASSIFICAR, SEQUÊNCIA, LET e LAMBDA.
- Validações de lista entre abas usam intervalos nomeados; não referências diretas a outra aba.
- Configurar impressão A4, área de impressão, títulos repetidos e aviso completo em todo rodapé.
  O rodapé do Excel suporta 255 caracteres; o aviso tem 212, então a origem precisa ser curta.
- Datas e horas devem ser valores de data/número, sem misturar textos como “duas horas”. Identifique
  se a data é prevista ou realizada. Campo vazio não significa zero horas de parada.
- Não calcular MTBF, MTTR ou disponibilidade até aprovarmos o significado e a regra dos indicadores.

## Como você deve criar os manuais Word

Dois arquivos DOCX: **PCMD-W1 Manual de Gestão de Ativos** e **PCMD-W2 Manual de Estratégia de Manutenção**.
Em cada um: objetivo/escopo, referências M6 com status, conteúdo, responsabilidades M3, indicadores
com regra explícita, checklist de conferência e histórico de revisão. W1 descreve hierarquia,
criticidade, termos e cadastros. W2 descreve avaliação das consequências, escolha/revisão das
estratégias e prazos por classe, que só serão preenchidos após sua definição técnica.
Não inserir número de norma sem fonte oficial, versão e data. Metas e prazos não definidos devem
permanecer a definir. Documentos Word não terão vínculos automáticos externos ao Excel.
Ao enviar, informe onde cada campo deve aparecer; poderemos usar marcadores visíveis como
{{organizacao.nome}}, {{documento.revisao}} e tabelas reservadas para ativos, pessoas e requisitos.
O mecanismo de preenchimento será escolhido somente após inspecionar seus arquivos.

## Aviso e origem em todos os documentos

Incluir o texto exato no rodapé de todas as páginas Word e abas Excel, também na impressão:

> O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

Acrescentar uma origem curta dos dados; em cada coluna, explicar seu cadastro de origem.
Não prometer conformidade ou aprovação em auditoria. Autor: Thiago Oliveira Lima; contato
público: pcmdireto@gmail.com; licença MIT. Não usar arquivos, nomes ou procedimentos de empresas.
