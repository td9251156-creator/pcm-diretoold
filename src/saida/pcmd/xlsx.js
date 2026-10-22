// Protótipo PCMD-02. Não altera rascunhos, biblioteca nem as exportações anteriores.
import { AVISO } from '../../logica/pacote.js';
import { MARCA, clarear } from '../../marca.js';
import { calcularCriticidade, LIMITES_CRITICIDADE, ESTRATEGIAS_CRITICIDADE } from '../../logica/criticidade.js';

export const ABA_ATIVOS = 'PCMD-02 Ativos e Criticidade';
export const LINHA_CABECALHO = 11;
export const PRIMEIRO_ATIVO = 12;
const COR_ENTRADA = 'FF' + clarear(MARCA.destaque, 0.88);
const COR_CALCULO = 'FF' + clarear(MARCA.primaria, 0.92);
const formula = (formula, result) => ({ formula, result });
const preencher = (aba, linha, texto, colunas = 12) => {
  aba.mergeCells(linha, 1, linha, colunas);
  aba.getCell(linha, 1).value = texto;
  aba.getCell(linha, 1).alignment = { wrapText: true, vertical: 'middle' };
};

function prepararAba(wb, nome, codigo, objetivo, guia, origem, data, colunas = 12) {
  const aba = wb.addWorksheet(nome);
  aba.properties.defaultRowHeight = 25;
  for (let c = 1; c <= colunas; c++) aba.getColumn(c).width = 16;
  preencher(aba, 1, `${codigo} — ${nome}`, colunas);
  aba.getCell('A1').font = { bold: true, size: 16, color: { argb: 'FF' + MARCA.primaria } };
  preencher(aba, 2, `Revisão 0.1 | Data: ${data} | Protótipo — validar com o responsável`, colunas);
  preencher(aba, 3, `Objetivo: ${objetivo}`, colunas);
  guia.forEach((texto, i) => preencher(aba, i + 4, texto, colunas));
  preencher(aba, 7, AVISO, colunas);
  aba.getRow(7).height = 56;
  aba.getCell('A7').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + MARCA.avisoFundo } };
  preencher(aba, 8, `Origem dos dados: ${origem}. Referência: GERAL (sem norma); requisitos não verificados, verificar na fonte oficial.`, colunas);
  aba.getRow(8).height = 44;
  for (let r = 3; r <= 6; r++) aba.getRow(r).height = 42;
  const fonteRodape = nome === ABA_ATIVOS ? 'M2, notas e Cadastros' : nome === 'Cadastros' ? 'PCMD e responsável' : nome === 'Listas' ? 'PCMD' : 'PCMD e M2';
  const rodape = `&7${AVISO}\nOrigem: ${fonteRodape}.`;
  if (rodape.length > 255) throw new Error('Rodapé excede o limite do Excel.');
  aba.headerFooter = { differentFirst: false, differentOddEven: false, oddFooter: rodape, evenFooter: rodape, firstFooter: rodape };
  aba.views = [{ state: 'frozen', xSplit: nome === ABA_ATIVOS ? 1 : 0, ySplit: LINHA_CABECALHO }];
  aba.pageSetup = { paperSize: 9, orientation: 'landscape', fitToPage: true, fitToWidth: 1, fitToHeight: 0,
    printTitlesRow: '11:11', margins: { left: 0.25, right: 0.25, top: 0.3, bottom: 0.7, header: 0.1, footer: 0.2 } };
  return aba;
}

function cabecalho(aba, titulos, notas) {
  titulos.forEach((titulo, i) => {
    const celula = aba.getCell(LINHA_CABECALHO, i + 1);
    celula.value = titulo;
    celula.note = notas?.[i] ?? `${titulo}. Consulte o guia acima antes de preencher.`;
    celula.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    celula.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + MARCA.primaria } };
    celula.alignment = { wrapText: true, vertical: 'middle' };
  });
  aba.getRow(LINHA_CABECALHO).height = 44;
}

function entrada(celula) {
  celula.protection = { locked: false };
  celula.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COR_ENTRADA } };
}

export async function montarPcmdWorkbook(dados, ExcelJS, opcoes = {}) {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'Thiago Oliveira Lima';
  wb.created = dados.geradoEm;
  wb.calcProperties = { fullCalcOnLoad: true };
  const data = dados.geradoEm.toISOString().slice(0, 10);
  const guiaComum = [
    'Quando usar: antes de revisar a estratégia. Quem preenche: responsável pelos ativos; revisar quando houver mudança.',
    'Como preencher: edite somente células em laranja claro; azul claro identifica cálculos. Exemplo fictício: Indústria Exemplo, Pessoa A.',
    'Erros comuns: notas incompletas e limites contraditórios. Relacionados: PCMD-03 e manuais W1/W2 (etapas futuras). Não há promessa de conformidade.',
  ];
  const leiame = prepararAba(wb, 'Leia-me', 'PCMD', 'orientar o uso do protótipo e sua validação.', guiaComum, 'instruções originais do PCMD', data, 2);
  const ativos = prepararAba(wb, ABA_ATIVOS, 'PCMD-02', 'cadastrar ativos e apoiar a avaliação de criticidade.', guiaComum,
    'M2: TAG, equipamento, setor e número do app; notas do responsável; limites de Cadastros', data);
  const listas = prepararAba(wb, 'Listas', 'M4', 'manter as opções de validação deste protótipo.', guiaComum, 'lista PCMD de notas permitidas', data, 2);
  const cadastros = prepararAba(wb, 'Cadastros', 'M1/M5', 'manter parâmetros únicos usados na matriz.', guiaComum, 'parâmetros propostos pelo PCMD e entradas do responsável', data, 3);
  cabecalho(leiame, ['Assunto', 'Orientação']);
  const orientacoes = [
    ['Ordem', '1. Confira os ativos; 2. valide os limites em Cadastros; 3. preencha as cinco notas; 4. revise pontuação, classe e orientação.'],
    ['Legenda', 'Laranja claro: entrada liberada. Azul claro: cálculo protegido. Demais dados: copiados do app.'],
    ['Critérios', 'O responsável deve definir o significado de cada nota 1, 2 e 3 antes de avaliar os ativos. Não há pesos nem critérios técnicos presumidos.'],
    ['Regra inicial', 'Soma de cinco notas. Segurança 3 resulta em A; demais: A ≥ 12, B ≥ 9 e C abaixo de 9. Limites ajustáveis e sujeitos à validação do mantenedor.'],
    ['Recálculo', 'Excel 2010 ou posterior. As fórmulas têm resultados em cache e o arquivo pede recálculo ao abrir. Se aparecer valor vazio, pressione F9.'],
    ['Proteção', 'Proteção sem senha evita alterações acidentais; não é controle de segurança. Entradas inválidas coladas continuam sinalizadas como Pendente.'],
    ['Escopo', 'Etapa 1: PCMD-02. Importação de alterações, histórico, Plano Mestre, cronograma e Word ainda não estão disponíveis neste pacote.'],
    ['Conservar o trabalho', 'Salve a planilha preenchida. Gerar outro arquivo no app não recupera as notas digitadas neste arquivo.'],
    ['Origem dos dados', 'PCMD-02: cadastro atual do app e notas do responsável. Cadastros: parâmetros únicos. Listas: opções de entrada.'],
    ['Referência', 'GERAL (sem norma). Qualquer requisito futuro começa não verificado; verificar na fonte oficial.'],
    ['Autor e licença', 'Thiago Oliveira Lima. Copyright (c) 2026 Thiago Oliveira Lima. MIT. Contato: pcmdireto@gmail.com.'],
  ];
  orientacoes.forEach((linha, i) => { leiame.getRow(PRIMEIRO_ATIVO + i).values = linha; leiame.getRow(PRIMEIRO_ATIVO + i).height = 36; });
  leiame.getColumn(1).width = 24; leiame.getColumn(2).width = 115;
  leiame.eachRow((row) => row.eachCell((c) => { c.alignment = { wrapText: true, vertical: 'middle' }; }));

  cabecalho(listas, ['Notas permitidas', 'Significado']);
  [1, 2, 3].forEach((n, i) => { listas.getRow(PRIMEIRO_ATIVO + i).values = [n, 'Critério a definir pelo responsável']; });
  listas.getColumn(2).width = 90;
  wb.definedNames.add(`Listas!$A$12:$A$14`, 'NotasCriticidade');

  cabecalho(cadastros, ['Parâmetro', 'Valor', 'Como usar']);
  const limites = opcoes.limites ?? LIMITES_CRITICIDADE;
  const registros = [
    ['Limite A', limites.a, 'Inteiro até 15; precisa ser maior que o limite B. Proposta: 12.'],
    ['Limite B', limites.b, 'Inteiro entre 5 e o limite A menos 1. Proposta: 9.'],
    ['M1 Organização', '', 'Opcional; exemplo fictício: Indústria Exemplo.'],
    ['M1 Elaborador', '', 'Exemplo fictício: Pessoa A.'],
    ['M1 Aprovador', '', 'Exemplo fictício: Pessoa B.'],
    ['Referencial', 'GERAL (sem norma)', 'M6 será ampliado em etapa posterior; verificar na fonte oficial.'],
    ['Meta de disponibilidade', 'a definir pelo responsável', 'Não há cálculo de disponibilidade nesta etapa.'],
    ['Meta de aderência', 'a definir pelo responsável', 'Não inventar meta.'],
    ['Revisão por classe', 'a definir pelo responsável', 'Não alterar intervalos de segurança com base na classe.'],
  ];
  registros.forEach((valores, i) => {
    const row = cadastros.getRow(PRIMEIRO_ATIVO + i); row.values = valores; row.height = 32;
    if (i !== 5) entrada(row.getCell(2));
    row.eachCell(c => { c.alignment = { wrapText: true, vertical: 'middle' }; });
  });
  cadastros.getColumn(1).width = 28; cadastros.getColumn(2).width = 34; cadastros.getColumn(3).width = 90;
  for (const [endereco, outra, maior] of [['B12', 'B13', true], ['B13', 'B12', false]]) {
    cadastros.getCell(endereco).dataValidation = { type: 'custom', allowBlank: false,
      formulae: [`AND(ISNUMBER(${endereco}),${endereco}=INT(${endereco}),${endereco}>=5,${endereco}<=15,${endereco}${maior ? '>' : '<'}${outra})`],
      showErrorMessage: true, errorStyle: 'stop', errorTitle: 'Limite inválido', error: 'Use limites inteiros: 5 ≤ B < A ≤ 15.' };
  }

  cabecalho(ativos, ['TAG', 'Equipamento', 'Setor', 'Nº', 'Segurança', 'Qualidade', 'Produção', 'Frequência de falha', 'Custo/tempo de reparo', 'Pontuação', 'Classe', 'Estratégia sugerida', 'ID do ativo'],
    ['TAG gerada pelo app; não alterar.', 'Descrição do equipamento no cadastro M2.', 'Setor do cadastro do app.', 'Número usado na TAG.',
      'Nota inteira de 1 a 3. Nota 3 implica classe A; critérios a definir pelo responsável.',
      'Nota inteira de 1 a 3; critérios a definir pelo responsável.', 'Nota inteira de 1 a 3; critérios a definir pelo responsável.',
      'Nota inteira de 1 a 3; critérios a definir pelo responsável.', 'Nota inteira de 1 a 3; critérios a definir pelo responsável.',
      'Soma das cinco notas válidas; não presume notas ausentes.', 'Segurança 3 = A; demais limites vêm de Cadastros.',
      'Orientação genérica. Não muda tarefas nem periodicidades.', 'Identificador estável do app; reservado para evolução futura.']);
  ativos.getColumn(1).width = 18; ativos.getColumn(2).width = 36; ativos.getColumn(12).width = 65; ativos.getColumn(13).hidden = true;
  const limiteA = 'Cadastros!$B$12'; const limiteB = 'Cadastros!$B$13';
  const limitesValidos = `AND(COUNT(Cadastros!$B$12:$B$13)=2,${limiteA}=INT(${limiteA}),${limiteB}=INT(${limiteB}),${limiteB}>=5,${limiteB}<${limiteA},${limiteA}<=15)`;
  dados.equipamentos.forEach((e, i) => {
    const r = PRIMEIRO_ATIVO + i;
    const notas = opcoes.notasPorId?.[e.id] ?? [];
    if (!Array.isArray(notas) || notas.length > 5) throw new Error('Informe no máximo cinco notas por ativo no protótipo.');
    const calculado = calcularCriticidade(notas, limites);
    const faixa = `E${r}:I${r}`;
    const notasValidas = `AND(COUNT(${faixa})=5,COUNTIF(${faixa},1)+COUNTIF(${faixa},2)+COUNTIF(${faixa},3)=5)`;
    ativos.getRow(r).values = [e.tag, e.descricao, e.setor, e.numero, ...Array.from({ length: 5 }, (_, n) => notas[n] ?? null),
      formula(`IFERROR(IF(${notasValidas},SUM(${faixa}),"Pendente"),"Pendente")`, calculado.pontuacao),
      formula(`IFERROR(IF(AND(ISNUMBER(J${r}),${limitesValidos}),IF(OR(E${r}=3,J${r}>=${limiteA}),"A",IF(J${r}>=${limiteB},"B","C")),"Pendente"),"Pendente")`, calculado.classe),
      formula(`IF(K${r}="A","${ESTRATEGIAS_CRITICIDADE.A}",IF(K${r}="B","${ESTRATEGIAS_CRITICIDADE.B}",IF(K${r}="C","${ESTRATEGIAS_CRITICIDADE.C}",IF(ISNUMBER(J${r}),"Corrija os limites na aba Cadastros.","Preencha cinco notas inteiras de 1 a 3."))))`, calculado.estrategia), e.id];
    ativos.getRow(r).height = 48;
    for (let c = 5; c <= 9; c++) {
      const celula = ativos.getCell(r, c); entrada(celula);
      celula.dataValidation = { type: 'list', allowBlank: true, formulae: ['NotasCriticidade'], showErrorMessage: true,
        errorStyle: 'stop', errorTitle: 'Nota inválida', error: 'Escolha uma nota inteira de 1 a 3; critérios a definir pelo responsável.' };
    }
    for (let c = 10; c <= 12; c++) ativos.getCell(r, c).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COR_CALCULO } };
    ativos.getRow(r).eachCell(c => { c.alignment = { wrapText: true, vertical: 'middle' }; });
    for (let c = 4; c <= 11; c++) ativos.getCell(r, c).alignment = { wrapText: true, vertical: 'middle', horizontal: 'center' };
  });
  const fim = Math.max(PRIMEIRO_ATIVO, PRIMEIRO_ATIVO + dados.equipamentos.length - 1);
  ativos.autoFilter = { from: { row: LINHA_CABECALHO, column: 1 }, to: { row: fim, column: 12 } };
  if (dados.equipamentos.length) {
    ativos.addConditionalFormatting({ ref: `E12:I${fim}`, rules: [{ type: 'expression', formulae: ['AND(E12<>"",NOT(AND(ISNUMBER(E12),OR(E12=1,E12=2,E12=3))))'],
      style: { fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + clarear(MARCA.seguranca, 0.85) } }, font: { color: { argb: 'FF' + MARCA.seguranca } } } }] });
    ativos.addConditionalFormatting({ ref: `J12:L${fim}`, rules: [{ type: 'expression', formulae: ['$K12="Pendente"'],
      style: { font: { color: { argb: 'FF' + MARCA.seguranca }, bold: true } } }] });
  }
  for (const aba of wb.worksheets) {
    aba.pageSetup.printArea = `A1:${aba === ativos ? 'L' : aba === cadastros ? 'C' : 'B'}${Math.max(12, aba.rowCount)}`;
    await aba.protect('', { selectLockedCells: true, selectUnlockedCells: true, autoFilter: true, spinCount: 1 });
  }
  return wb;
}

export async function gerarPcmdXlsx(dados, ExcelJS, opcoes = {}) {
  const wb = await montarPcmdWorkbook(dados, ExcelJS, opcoes);
  return wb.xlsx.writeBuffer();
}
