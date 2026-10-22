import { describe, it, expect } from 'vitest';
import ExcelJS from 'exceljs';
import { calcularCriticidade, limitesCriticidadeValidos, ESTRATEGIAS_CRITICIDADE } from '../src/logica/criticidade.js';
import { gerarPcmdXlsx, montarPcmdWorkbook, ABA_ATIVOS, PRIMEIRO_ATIVO } from '../src/saida/pcmd/xlsx.js';
import { AVISO } from '../src/logica/pacote.js';
import { MARCA, clarear } from '../src/marca.js';

const equipamento = { id: 'exemplo1', tag: 'PRS-MOT-001', descricao: 'Motor fictício', setor: 'PRS', numero: 1 };
const dados = { geradoEm: new Date('2026-10-22T12:00:00Z'), equipamentos: [equipamento] };
async function abrir(opcoes, entrada = dados) {
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(await gerarPcmdXlsx(entrada, ExcelJS, opcoes));
  return wb;
}
const cenarios = [
  { notas: [1, 1, 2, 2, 2], pontos: 8, classe: 'C' },
  { notas: [1, 2, 2, 2, 2], pontos: 9, classe: 'B' },
  { notas: [2, 2, 2, 2, 3], pontos: 11, classe: 'B' },
  { notas: [2, 2, 2, 3, 3], pontos: 12, classe: 'A' },
  { notas: [3, 1, 1, 1, 1], pontos: 7, classe: 'A' },
];

describe('regra de criticidade', () => {
  it.each(cenarios)('soma e classifica $notas em $classe', ({ notas, pontos, classe }) => {
    expect(calcularCriticidade(notas)).toEqual({ pontuacao: pontos, classe, estrategia: ESTRATEGIAS_CRITICIDADE[classe] });
  });
  it.each([[], [1, 1, 1, 1], [null, 1, 1, 1, 1], ['', 1, 1, 1, 1], ['1', 1, 1, 1, 1], [0, 1, 1, 1, 1], [4, 1, 1, 1, 1], [1.5, 1, 1, 1, 1], [NaN, 1, 1, 1, 1]].map(notas => ({ notas })))('não presume uma nota inválida: $notas', ({ notas }) => {
    expect(calcularCriticidade(notas)).toMatchObject({ pontuacao: 'Pendente', classe: 'Pendente' });
  });
  it('respeita parâmetros diferentes e recusa limites contraditórios, texto e frações', () => {
    expect(calcularCriticidade([2, 2, 2, 2, 2], { a: 10, b: 7 }).classe).toBe('A');
    for (const limites of [{ a: 9, b: 9 }, { a: 16, b: 9 }, { a: 12, b: 4 }, { a: '12', b: 9 }, { a: 12.5, b: 9 }, null]) {
      expect(limitesCriticidadeValidos(limites)).toBe(false);
      expect(calcularCriticidade([3, 1, 1, 1, 1], limites).classe).toBe('Pendente');
    }
  });
});

describe('arquivo PCMD-02', () => {
  it.each(cenarios)('grava fórmula e resultado em cache conferidos para $classe / $pontos', async ({ notas, pontos, classe }) => {
    const wb = await abrir({ notasPorId: { exemplo1: notas } });
    const aba = wb.getWorksheet(ABA_ATIVOS);
    expect(aba.getCell('J12').value).toEqual({ formula: 'IFERROR(IF(AND(COUNT(E12:I12)=5,COUNTIF(E12:I12,1)+COUNTIF(E12:I12,2)+COUNTIF(E12:I12,3)=5),SUM(E12:I12),"Pendente"),"Pendente")', result: pontos });
    expect(aba.getCell('K12').result).toBe(classe);
    expect(aba.getCell('K12').formula).toContain('COUNT(Cadastros!$B$12:$B$13)=2');
    expect(aba.getCell('K12').formula).toContain('IF(OR(E12=3,J12>=Cadastros!$B$12),"A",IF(J12>=Cadastros!$B$13,"B","C"))');
    expect(aba.getCell('L12').result).toBe(ESTRATEGIAS_CRITICIDADE[classe]);
    expect(aba.getCell('L12').formula).toContain(ESTRATEGIAS_CRITICIDADE[classe]);
  });
  it('abre sem notas e sem classes inventadas; não altera os equipamentos', async () => {
    const anterior = structuredClone(dados);
    const wb = await abrir(); const aba = wb.getWorksheet(ABA_ATIVOS);
    expect(dados).toEqual(anterior);
    for (let c = 5; c <= 9; c++) expect(aba.getCell(PRIMEIRO_ATIVO, c).value).toBeNull();
    expect(aba.getCell('J12').result).toBe('Pendente');
    expect(aba.getCell('K12').result).toBe('Pendente');
    expect(aba.getCell('A12').value).toBe(equipamento.tag);
    expect(aba.getCell('M12').value).toBe(equipamento.id);
  });
  it('preserva cache de pendência em notas inválidas e parâmetros inválidos', async () => {
    const notaInvalida = await abrir({ notasPorId: { exemplo1: ['2', 2, 2, 2, 2] } });
    expect(notaInvalida.getWorksheet(ABA_ATIVOS).getCell('J12').result).toBe('Pendente');
    const limiteInvalido = await abrir({ notasPorId: { exemplo1: [2, 2, 2, 2, 2] }, limites: { a: 9, b: 9 } });
    expect(limiteInvalido.getWorksheet(ABA_ATIVOS).getCell('K12').result).toBe('Pendente');
    const limiteValido = await abrir({ notasPorId: { exemplo1: [2, 2, 2, 2, 2] }, limites: { a: 10, b: 7 } });
    expect(limiteValido.getWorksheet(ABA_ATIVOS).getCell('K12').result).toBe('A');
  });
  it('tem nomes válidos, ordem, guias, aviso exato, rodapé completo e impressão A4 em todas as abas', async () => {
    const wb = await abrir();
    expect(wb.worksheets.map(a => a.name)).toEqual(['Leia-me', ABA_ATIVOS, 'Listas', 'Cadastros']);
    for (const aba of wb.worksheets) {
      expect(aba.name.length).toBeLessThanOrEqual(31);
      expect(aba.name).not.toMatch(/[/\\?*[\]:]/);
      expect(aba.getCell('A7').value).toBe(AVISO);
      expect(aba.getCell('A8').value).toContain('Origem dos dados:');
      for (const rodape of ['oddFooter', 'evenFooter', 'firstFooter']) {
        expect(aba.headerFooter[rodape]).toContain(AVISO);
        expect(aba.headerFooter[rodape]).toContain('Origem:');
        expect(aba.headerFooter[rodape].length).toBeLessThanOrEqual(255);
      }
      for (const r of [4, 5, 6]) expect(aba.getCell(r, 1).value).toBeTypeOf('string');
      expect(aba.pageSetup.paperSize).toBe(9);
      expect(aba.pageSetup.orientation).toBe('landscape');
      expect(aba.pageSetup.printTitlesRow).toBe('11:11');
      expect(aba.pageSetup.printArea).toBeTruthy();
      const ultimaColunaImpressa = aba.pageSetup.printArea.split(':')[1].replace(/[0-9$]/g, '');
      const numeroColuna = letras => [...letras].reduce((n, letra) => n * 26 + letra.charCodeAt(0) - 64, 0);
      for (const mescla of aba.model.merges) {
        const ultimaColunaMescla = mescla.split(':')[1].replace(/[0-9$]/g, '');
        expect(numeroColuna(ultimaColunaMescla)).toBeLessThanOrEqual(numeroColuna(ultimaColunaImpressa));
      }
      expect(aba.views[0].state).toBe('frozen');
      expect(aba.getCell('A11').note).toBeTruthy();
      expect(aba.sheetProtection.sheet).toBe(true);
    }
    expect((await montarPcmdWorkbook(dados, ExcelJS)).calcProperties.fullCalcOnLoad).toBe(true);
  });
  it('libera só entradas, usa lista nomeada e distingue cálculos com a marca', async () => {
    const wb = await abrir(); const aba = wb.getWorksheet(ABA_ATIVOS);
    for (let c = 4; c <= 11; c++) expect(aba.getCell(12, c).alignment.horizontal).toBe('center');
    expect(aba.getCell('E12').protection.locked).toBe(false);
    expect(aba.getCell('J12').protection?.locked ?? true).toBe(true);
    expect(aba.getCell('A12').protection?.locked ?? true).toBe(true);
    expect(aba.getCell('E12').dataValidation.formulae).toEqual(['NotasCriticidade']);
    expect(wb.definedNames.getRanges('NotasCriticidade').ranges).toEqual(['Listas!$A$12:$A$14']);
    expect(aba.getCell('E12').fill.fgColor.argb).toBe('FF' + clarear(MARCA.destaque, 0.88));
    expect(aba.getCell('J12').fill.fgColor.argb).toBe('FF' + clarear(MARCA.primaria, 0.92));
    expect(wb.getWorksheet('Cadastros').getCell('B12').protection.locked).toBe(false);
    expect(wb.getWorksheet('Cadastros').getCell('B12').dataValidation.formulae[0]).toContain('B12>B13');
  });
  it('cada fórmula tem cache e usa somente funções clássicas; não contém referência externa', async () => {
    const wb = await abrir(); let formulas = 0;
    for (const aba of wb.worksheets) aba.eachRow(row => row.eachCell(c => {
      if (!c.formula) return;
      formulas++;
      expect(Object.hasOwn(c.value, 'result')).toBe(true);
      expect(c.formula).not.toMatch(/(?:_xlfn\.|\b(?:FILTER|XLOOKUP|UNIQUE|SORT|SEQUENCE|LET|LAMBDA)\s*\(|\[[^\]]+\])/i);
    }));
    expect(formulas).toBe(3);
  });
  it('gera um protótipo válido sem ativos, sem criar ativo fictício no cadastro do usuário', async () => {
    const wb = await abrir(undefined, { ...dados, equipamentos: [] });
    expect(wb.getWorksheet(ABA_ATIVOS).getCell('A12').value).toBeNull();
  });
});
