# Prompt para criar os templates no Claude Code

Copie o conteúdo entre os delimitadores abaixo para uma sessão do Claude Code. Se ele não tiver
acesso ao repositório, envie também `docs/INTERFACE-E-MODELOS.md`, `src/marca.js` e o logo de
`public/icones/logo.svg`. Solicite os arquivos gerados, o código de geração e o relatório de testes.
Este pedido prepara documentos externos; não autoriza alterações ou publicação do aplicativo.

--- INÍCIO DO PROMPT ---

Você desenvolverá os modelos de documentos do **PCM Direto**, uma ferramenta aberta de
Planejamento e Controle de Manutenção em português do Brasil, licença MIT, de Thiago Oliveira Lima.
Entregue os arquivos reais e editáveis, com apresentação profissional, legibilidade e fórmulas
conferidas. Não entregue apenas imagens, instruções, PDFs ou um roteiro para fazer depois.

## 1. Escopo e limites

Crie uma pasta XLSX e dois documentos DOCX, com versões em branco e demonstração fictícia.
Prepare o contrato dos campos para uma integração futura. Não altere o app, seu banco, suas
exportações, seus backups ou seus workflows. Não implemente importador, integração automática,
conexão externa, macros, autenticação ou envio de dados. Não faça merge ou publicação.
O protótipo do PR #31 não é dependência deste trabalho.

Se houver acesso ao repositório, leia `AGENTS.md`, `docs/INTERFACE-E-MODELOS.md`, `BIBLIOTECA.md`,
`src/marca.js` e a lógica atual antes de definir os campos. Respeite alterações preexistentes.
Use uma pasta separada `entrega-templates/` para todos os seus arquivos. Se faltar o repositório,
use este prompt como especificação e identifique o mapeamento como proposto, ainda não validado.

O produto distingue três coisas:

- **Modelo de máquina compartilhado:** referência reutilizável do catálogo público, sujeito à
  revisão. Não é o inventário de uma fábrica, nem um template Excel/Word.
- **Ativo local:** equipamento efetivo com ID próprio, setor, TAG, plano, criticidade e histórico.
  Pessoas, organização, falhas e execuções pertencem à gestão local e não devem virar publicação.
- **Template documental:** os arquivos Excel/Word solicitados aqui, preenchidos futuramente com
  dados locais. Não devem consultar o catálogo pela internet nem enviar qualquer dado.

Usar um modelo de máquina cria um cadastro local; tarefas da contribuição não substituem
automaticamente a biblioteca validada nem suas proteções. Não presuma sincronização com o catálogo.

## 2. Arquivos obrigatórios

Entregue:

1. `PCM-Direto-Modelos.xlsx` — pasta limpa, com cabeçalhos, validações e fórmulas prontas para uso.
2. `PCM-Direto-Exemplo.xlsx` — mesma estrutura, preenchida apenas com dados fictícios para os testes.
3. `PCMD-W1-Manual-Gestao-Ativos.docx` — template do Manual de Gestão de Ativos.
4. `PCMD-W2-Manual-Estrategia-Manutencao.docx` — template do Manual de Estratégia de Manutenção.
5. Os dois manuais preenchidos em versão `-Exemplo.docx`, sem substituir os templates.
6. `CONTRATO-CAMPOS.json`, `DICIONARIO-DE-DADOS.md` e `COMO-USAR.md`.
7. Código-fonte de geração, dependências com versões/licenças e instrução reproduzível de execução.
8. `RELATORIO-DE-TESTES.md`, descrevendo o que foi efetivamente executado e as limitações.

Se exportar PDFs para conferir a impressão, entregue-os como prévias adicionais. Os arquivos
editáveis continuam obrigatórios. Nunca diga que um teste passou se não o executou.

## 3. Identidade visual e usabilidade

Use o logo original, preservando proporção e conteúdo. Não invente uma nova marca. Cores:
azul principal `#0B3D63`, destaque `#B85C00`, fundo de aviso `#FFF4C2`, segurança `#7A0019`.
O logo possui azul `#13304A` e laranja `#D97030`; mantenha essas cores próprias.
Se o logo não estiver disponível, use texto PCM Direto e registre essa limitação.

Use fonte comum e legível, como Arial, tamanho adequado à leitura impressa. Não dependa de
fontes externas, recursos remotos ou cor isolada para transmitir significado. Identifique entrada,
cálculo, campo pendente e tarefa de segurança também por texto/legenda. Separe claramente os
campos editáveis dos resultados. Evite células mescladas dentro de tabelas de dados e não use
objetos decorativos que prejudiquem filtro, navegação ou impressão.

Inclua instruções curtas, títulos claros, unidades nos cabeçalhos, filtros e painéis congelados.
Configure A4, orientação por aba, margens, área de impressão e cabeçalhos repetidos. Prefira várias
páginas legíveis a reduzir centenas de linhas para uma única página de altura.

## 4. Estrutura da pasta Excel

Todas as abas devem ter nome válido de até 31 caracteres. Use estas abas ou nomes equivalentes
documentados, preservando os códigos PCMD:

| Aba | Conteúdo obrigatório |
|---|---|
| Leia-me | Objetivo, sequência de preenchimento, legenda, limites, recálculo, origem e aviso. |
| PCMD-01 Lista Mestra | Código, título, tipo, revisão, data, elaborador, aprovador, próxima revisão e situação dos documentos. |
| PCMD-02 Ativos | ID técnico, TAG, descrição, tipo, fabricante, modelo, setor, número, cinco notas, pontuação e classe. |
| PCMD-03 Plano Mestre | ID do ativo, ID e chave da tarefa, TAG, atividade, origem, versão, frequência, especialidade, duração estimada em horas, responsável e segurança. |
| PCMD-04 Cronograma | Ano consultado, ocorrências previstas com ID/chave, datas previstas, horas estimadas e resumo mensal de previsto, realizado e percentual; fora do ano em quadro separado. |
| PCMD-05 Ficha de Falha | ID do registro, ID do ativo, data, TAG preservada, sintoma, causa, ação, horas de parada opcionais, peça e responsável. |
| Execuções | ID do registro, IDs de ativo/tarefa, chave, TAG e descrição preservadas, data prevista opcional, data realizada, observação, responsável, origem e cancelamento. |
| Cadastros | Organização/setores, pessoas/funções/especialidades/ativo, metas, limites de criticidade e requisitos com fonte/versão/data/status. |
| Listas | Frequências, tipos e especialidades aceitos, com intervalos nomeados para validação. |
| Revisões | Revisão documental, data, descrição da mudança e responsável. |

Não invente valores para campos sem fonte no app. Campos exclusivamente documentais, como próxima
revisão do documento, precisam ser identificados como preenchimento manual no contrato.

Preserve IDs técnicos separados dos rótulos; eles podem ficar ocultos, mas precisam ser explicados.
TAG, nome de pessoa, número de linha ou título não substituem os IDs. A chave da tarefa no plano
é o par `equipamentoId|tarefaId`; a chave da ocorrência acrescenta `|dataPrevista` no formato
`AAAA-MM-DD`. O histórico possui seu próprio ID, pois pode haver vários registros para o mesmo par.
Renomear um ativo ou uma pessoa não pode quebrar o vínculo nem reescrever a descrição histórica.

## 5. Excel e fórmulas

Compatibilidade alvo: Excel 2010 ou posterior, sem macros, VBA, scripts incorporados, vínculos
externos, conexões de dados, Power Query obrigatório ou matrizes dinâmicas. Não usar PROCX,
FILTRO, ÚNICO, CLASSIFICAR, SEQUÊNCIA, LET ou LAMBDA. Use funções clássicas, como SE, E, OU,
CONT.SE/CONT.SES, SOMA, SOMASES, PROCV, ÍNDICE e CORRESP. Validação de lista entre abas deve
usar intervalo nomeado, sem referência direta a outra aba na fórmula de validação.

Se a biblioteca gravar fórmulas no formato OOXML, use nomes de função em inglês e sintaxe OOXML;
na documentação para o usuário, explique os equivalentes em português. Solicite recálculo ao abrir.
Não confunda fórmula escrita no XML com fórmula realmente calculada por um programa de planilha.
Documente a capacidade de linhas e o procedimento para ampliá-la sem perder fórmulas/validações.
Proteção de planilha, se usada para evitar edição acidental, não representa segurança de acesso.

Datas devem ser datas reais do Excel, exibidas em `dd/mm/aaaa`. Horas são números decimais,
não textos nem horário do dia. Vazio significa não informado; não converter horas de parada vazias
em zero. Percentuais são valores numéricos com formato percentual; não misturar escala 0–1 com 0–100.
Textos recebidos que começam com `=`, `+`, `-` ou `@` devem continuar textos, sem virar fórmulas.

### Criticidade

Cinco critérios, nesta ordem: Segurança, Qualidade, Produção, Frequência de falha e Custo/tempo
de reparo. Confira a implementação se houver acesso ao repositório. Cada nota é um inteiro
de 1 a 3; ausência é ausência, não zero.
Enquanto alguma nota faltar ou for inválida, classe **Pendente**, sem somar parcialmente como
resultado definitivo. Com cinco notas válidas, soma de 5 a 15:

1. Segurança igual a 3 → classe A.
2. Senão, soma ≥ limite A → A.
3. Senão, soma ≥ limite B → B.
4. Senão → C.

Limites iniciais A=12 e B=9, editáveis sob `5 ≤ B < A ≤ 15`, inteiros. Limites inválidos resultam
em Pendente com orientação para corrigir. Não invente o significado técnico de cada nível 1/2/3;
reserve campo para o mantenedor definir. A classe nunca muda automaticamente uma frequência.

### Cronograma, execuções e percentuais

O plano vigente do app é a fonte do cronograma. Trabalha com 52 semanas a partir da data de início;
não o substitua por calendário ISO nem redistribua tarefas para outro mês. Datas das ocorrências
devem ser fornecidas pelo futuro adaptador ou por tabela explícita de entrada, com fonte indicada.
Tarefa diária considera os cinco dias úteis de cada semana, sem calendário de feriados. Não
conte cinco dias no registro e multiplique por cinco novamente ao somar horas.

Conte o realizado pelo vínculo explícito à ocorrência prevista, não pela coincidência da data real:

- Uma ocorrência é o trio ativo + tarefa + data prevista.
- Só conta se existir no cronograma e tiver pelo menos uma execução não cancelada vinculada.
- Duas execuções da mesma ocorrência contam **uma** ocorrência concluída.
- Execuções canceladas não contam e continuam no histórico.
- Legado ou execução sem vínculo não entra no numerador; apresentar em quadro separado.
- O mês é o da data prevista, mesmo se a realização acontecer em outro mês.
- Percentual = ocorrências concluídas distintas / ocorrências previstas distintas.
- Mês sem previsão mostra traço ou Sem previsão, sem divisão por zero e sem 100% artificial.
- Previsões fora do ano consultado ficam separadas, sem serem descartadas.

Implemente uma linha por ocorrência com indicador 0/1 obtido da existência de execução ativa,
por exemplo com CONT.SES, para impedir duplicação. O resumo soma esses indicadores por mês.
Horas previstas são estimadas a partir da duração da tarefa. O histórico atual não informa duração
real da execução: não apresente horas estimadas como horas efetivamente trabalhadas. Se reservar
esse campo futuro, deixe-o vazio e claramente manual/não integrado.

## 6. Segurança técnica e referências

Não invente tarefas de manutenção, periodicidades, durações, prazos por classe, metas ou requisitos
legais para deixar o exemplo preenchido. Se usar tarefas de demonstração, copie fielmente tarefas
da biblioteca existente com sua origem e versão, ou indique conteúdo técnico A definir. Uma tarefa
genérica usa a origem exata `base genérica a validar com manual do fabricante`.

Tarefa marcada como segurança não pode ser excluída, desmarcada nem ter intervalo ampliado em
relação à referência. Se o template permitir edição de frequência, mantenha referência técnica
protegida e validação coerente, com alerta visível para inconsistência. Explique que validações e
proteções de Excel não substituem a validação do app e podem ser contornadas por colagem/edição
externa; não afirme que um arquivo offline impede toda alteração. Não crie uma trava falsa.

Não cite número de norma sem fonte oficial, versão e data verificáveis. Referencial inicial:
**GERAL (sem norma)**. Requisitos começam Não verificado. Verificado exige fonte HTTPS, versão
e data, mas não certifica conformidade. Requisitos sem fonte suficiente continuam pendentes.
Metas ausentes permanecem A definir. Não calcular MTBF, MTTR, disponibilidade, vida útil,
intervalos por criticidade ou prazos de parada sem regras aprovadas pelo mantenedor.

## 7. Dois manuais Word

Crie DOCX editáveis com estilos reais de título, hierarquia lógica, cabeçalho, rodapé, número de
página e tabelas legíveis. Repita cabeçalhos de tabelas longas e evite linhas cortadas sem necessidade.
Se houver sumário automático, documente sua atualização; não prometa atualização automática em
qualquer leitor. Não use vínculos automáticos externos com Excel ou banco.

Ambos devem conter identificação documental, revisão/data, objetivo e escopo, termos, referências
com status, responsabilidades, processo descrito, indicadores com regra explícita ou A definir,
checklist de conferência e histórico de revisão. Não escreva procedimentos perigosos ou declare
aprovação por profissional sem que ela tenha ocorrido.

- **W1 — Manual de Gestão de Ativos:** cadastro e hierarquia dos ativos, IDs/TAGs, setores,
  criticidade com critérios e limites, responsáveis, conservação do histórico, requisitos/fontes,
  controle documental e distinção entre cadastro local e modelo público.
- **W2 — Manual de Estratégia de Manutenção:** avaliação das consequências, escolha e revisão
  das estratégias pelo profissional responsável, origem das tarefas, planejamento e execução,
  tratamento de falhas e revisão. Estratégias/prazos por classe e indicadores indefinidos ficam
  A definir, sem virar regras técnicas inventadas.

Use marcadores visíveis estáveis, por exemplo `{{organizacao.nome}}`, `{{documento.revisao}}`,
`{{documento.data}}`, `{{documento.elaborador}}` e `{{documento.aprovador}}`. Reserve tabelas para
ativos, pessoas e requisitos. Liste todos os marcadores e regiões repetíveis no contrato. Documente
se o marcador está em parágrafo, célula, cabeçalho ou rodapé. Não afirme que o app já os preenche.

## 8. Contrato de campos separado e versionado

`CONTRATO-CAMPOS.json` deve ser JSON válido, versão 1, sem dados reais, com arquivos/abas/regiões
e, para cada campo: identificador estável, rótulo, tipo, obrigatório/opcional, formato/unidade,
origem proposta, destino no documento, regra de vazio, validação, se é entrada ou cálculo,
privacidade e observações. Registre também fórmulas, intervalos nomeados, tabelas e IDs técnicos.

Distinga os campos existentes dos manuais e futuros. Não apresente um esquema proposto como
formato de backup/API já aceito pelo PCM Direto. O adaptador de integração será implementado
e testado posteriormente, depois de receber e inspecionar estes arquivos.

Se tiver acesso ao app, confira as fontes reais: equipamentos/biblioteca/plano/cronograma e
`gestao.organizacao`, `gestao.pessoas`, `gestao.metas`, `gestao.requisitos`,
`gestao.criticidade`, `gestao.responsaveis`, `gestao.historico` e `gestao.falhas`.
Não deduza que `dadosAtuais()` já inclui toda a gestão ou que o exportador antigo escreve estes
templates. O contrato é um mapa de integração futura, não autorização de upload do backup.

## 9. Aviso obrigatório

Texto exato, sem abreviação, em todas as abas Excel e no rodapé impresso de cada aba, e no rodapé
de todas as páginas Word, incluindo primeira página e seções com orientações diferentes:

O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas com o manual do fabricante.

No Excel, verifique o limite de 255 caracteres de cada seção do rodapé, incluindo códigos de
formatação; não corte o aviso para acrescentar marca ou origem. Use outra seção ou uma célula
visível para informação adicional quando necessário. Origem dos dados e data de emissão devem
aparecer de forma legível. Autor: Thiago Oliveira Lima. Contato público: pcmdireto@gmail.com.
Licença MIT. Não prometa conformidade, aprovação em auditoria ou ganhos garantidos.

## 10. Dados fictícios e testes de aceitação

Use somente Indústria Exemplo, Pessoa A, Pessoa B e fabricantes/modelos explicitamente fictícios.
Não use nomes, manuais, logotipos ou procedimentos de empresas reais. Não gere credenciais.

Execute e documente verificações nos arquivos gerados, não somente no código-fonte:

1. XLSX/DOCX abrem sem solicitação de reparo no programa disponível; registre nome e versão.
   Se não houver Excel/Word, use LibreOffice quando disponível e identifique que isso não comprova
   compatibilidade real com Excel 2010/Word. Abrir ZIP/XML sozinho não prova cálculo nem impressão.
2. Nenhuma macro, relação externa, conexão ou fórmula proibida; nomes de abas/intervalos válidos.
3. Datas numéricas, horas numéricas, textos perigosos preservados como texto e IDs intactos.
4. Criticidade: cinco notas 1→C; soma 9 sem Segurança 3→B; soma 12→A; Segurança 3 com soma 7→A;
   nota ausente→Pendente; nota 4 ou limite B≥A recusado/sinalizado. Alterar limites válidos recalcula.
5. Ocorrências: duas previstas e uma concluída→50%; duplicar execução da concluída continua 50%;
   cancelar todas as execuções vinculadas dessa ocorrência→0%; legado sem vínculo não aumenta
   percentual; mês sem previsão mostra traço; executar em outro mês conta no mês previsto.
6. Passagem de ano, ocorrência diária, ativo removido com histórico preservado e parada vazia
   diferente de zero. Ausência de meta não produz meta inventada.
7. Tarefa de segurança mantém referência e alerta de edição inválida; confirme os limites reais
   da proteção offline. Fórmula fora do intervalo previsto não pode falhar silenciosamente.
8. Recalcular o XLSX em programa de planilha quando disponível e conferir resultados numéricos;
   não usar apenas valores em cache fornecidos pelo gerador como evidência de recálculo.
9. Visualizar impressão/PDF: títulos repetidos, tabelas legíveis e aviso completo em todas as
   páginas/abas. Conferir DOCX com tabelas longas e marcadores em células/cabeçalhos/rodapés.
10. Contrato cobre todos os campos e marcadores; versões em branco e exemplo têm a mesma estrutura.

Ao finalizar, entregue os artefatos com caminhos e instrução de uso. Explique o que está pronto,
os testes executados, o que depende de validação técnica e o que aguarda integração no app.
Não use “sem bugs” ou “compatibilidade garantida” como substituto de evidência.

--- FIM DO PROMPT ---
