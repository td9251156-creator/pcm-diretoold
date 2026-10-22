# Plano dos templates PCMD

## Objetivo e limites
Acrescentar o Pacote PCMD ao app existente, com conteúdo original e dados fictícios.
Uma etapa por PR e por tarefa: abrir o PR e parar, sem merge nem publicação.
Preservar exportações atuais, biblioteca, travas de segurança, rascunhos e backups.
Não ler arquivos de empresa; registrar apenas o caminho caso sejam encontrados.
Codex/Plus implementa; a proposta de créditos #30 permanece separada e sem ativação.

## Etapas e dependências de entrega
1. Plano e protótipo PCMD-02, com Leia-me, Listas e Cadastros mínimos.
2. PCMD-03 Plano Mestre.
2A. Histórico completo e aba Execuções; compatibilidade dos backups.
3. PCMD-04 Cronograma Anual e percentual por ocorrência.
4. PCMD-05 Ficha de Falha.
5. PCMD-01 Lista Mestra de Documentos.
6. Completar Leia-me, Listas, Cadastros M1–M6, Revisões e guias.
6A. Importação completa com prévia, confirmação e recuperação.
7. PCMD-W1 Manual de Gestão de Ativos.
8. PCMD-W2 Manual de Estratégia de Manutenção.
9. Ajustes compatíveis da biblioteca e BIBLIOTECA.md.
10. Conferência final, termos proibidos e roteiro manual.

## Dependências de software
Nenhuma dependência nova nem instalação global.
ExcelJS (MIT), já instalado: XLSX, fórmulas, estilos e validação.
docx (MIT), já instalado: manuais nas etapas 7 e 8.
Vitest e Playwright existentes: regras puras, arquivos e navegador offline.
LibreOffice somente se disponível e comprovadamente recalcular; não integra o app.

## Primeira etapa e interfaces
Gerador separado em src/saida/pcmd/; regras puras em src/logica/criticidade.js.
Contrato: gerarPcmdXlsx(dados, ExcelJS, opcoes), devolvendo buffer XLSX.
Dados conhecidos vêm do mesmo pacote usado pelas exportações atuais.
Notas opcionais por ID e limites nas opções permitem construir exemplos de teste.
Quatro abas: Leia-me, PCMD-02 Ativos e Criticidade, Listas, Cadastros.
Na Entrega, botão próprio do Pacote PCMD, identificado como protótipo PCMD-02.
Notas reais começam vazias; sem importação, persistência de notas ou Word nesta etapa.
Protótipo de exemplo entregue como artefato, não como documento binário versionado.

## Como provar os cálculos
Toda fórmula nova leva resultado em cache, calculado também por função pura JavaScript.
Testar fronteiras de classe (8, 9, 11, 12), segurança 3, entradas ausentes e inválidas.
Testar limites editáveis e inválidos, resultados e referências das fórmulas gravadas.
Testar funções proibidas, nomes definidos, aviso exato, origem e impressão em todas as abas.
Manter fullCalcOnLoad; Leia-me orienta F9 caso o leitor não atualize os valores.
LibreOffice só conta como prova se corrigir um cache deliberadamente errado.
A configuração padrão preservou cache errado; OOXMLRecalcMode=0 comprovou recálculo.
Comando npm run verificar:recalculo-pcmd: prova pequena e 81 resultados comparados.
Registrar a validação no Excel 2010 como pendente; nunca confundir ZIP válido com cálculo certo.
Executar npm run verificar e npm run test:navegador, além de revisão independente.

## Decisões confirmadas pelo mantenedor
Excel 2010; apenas funções clássicas em inglês, com vírgulas, sem macros.
Notas inteiras 1 a 3; soma; segurança 3 = A; demais A≥12, B≥9, C abaixo de 9.
Limites editáveis exigem 5≤B<A≤15. Dados incompletos ou inválidos = Pendente.
Metas e prazos de revisão sem valores inventados: a definir pelo responsável.
Cronograma janeiro–dezembro do ano inicial, derivado das semanas existentes.
Ocorrências fora do ano serão identificadas separadamente, sem sumir dos totais globais.
Meses de calendário para próximas execuções mensais ou maiores; dias úteis para diária.
Vencimento e semana planejada são conceitos diferentes, explicados nos guias.
Histórico completo no app e Excel; marcações antigas sem vínculo não multiplicam realizações.
Importação substitui os dados após prévia e confirmação, com cópia recuperável anterior.
Não confiar em fórmulas/cache importados: ler entradas permitidas e recalcular no app.
Alterações que exigem balanceamento mostram Regerar pelo app e ocultam resultados antigos.
Cadastros preenchidos no Excel alimentarão os manuais após importação; telas mestre ficam para depois.

## Perguntas e validações do mantenedor
Confirmar no PR os limites sugeridos A≥12, B≥9 e a exceção segurança 3 = A.
Conferir a linguagem das orientações por classe: não é determinação de estratégia ou conformidade.
Preencher metas e prazos por classe antes de tratá-los como regras técnicas.
Validar critérios e periodicidades com manuais; nenhuma norma sem fonte, versão e data.
Abrir o protótipo no Excel 2010 e conferir impressão e recálculo após editar notas/limites.
No PR final, decidir se as exportações atuais devem ser substituídas; até lá coexistem.

## Entrega e continuidade
Cada PR informa Antes, Depois, Como testar, Riscos, pendências e próxima etapa.
Nenhum teste comprova ausência absoluta de bugs; registrar limites das verificações realizadas.
Próxima tarefa só começa após revisão do PR anterior, seguindo a ordem da fila.
Se a etapa anterior ainda não estiver integrada, explicitar ramo e dependência no próximo PR.
