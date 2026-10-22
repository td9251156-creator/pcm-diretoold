// Prova externa opcional: exige LibreOffice instalado, sem acrescentar dependência ao app.
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import ExcelJS from 'exceljs';
import { montarPcmdWorkbook, ABA_ATIVOS, PRIMEIRO_ATIVO } from '../src/saida/pcmd/xlsx.js';
import { calcularCriticidade } from '../src/logica/criticidade.js';

const destino = process.env.PCM_PROTOTIPO_DIR || 'artifacts/pcmd';
const temporario = await mkdtemp(join(tmpdir(), 'pcmd-recalculo-'));
try {
  const perfil = join(temporario, 'perfil');
  const entrada = join(temporario, 'entrada'); const saida = join(temporario, 'saida');
  await Promise.all([mkdir(join(perfil, 'user'), { recursive: true }), mkdir(entrada), mkdir(saida)]);
  // O modo padrão pode conservar caches errados. Zero exige recálculo na importação OOXML.
  await writeFile(join(perfil, 'user', 'registrymodifications.xcu'),
    '<?xml version="1.0" encoding="UTF-8"?><oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item></oor:items>');
  const converter = (arquivos) => {
    const resultado = spawnSync(process.env.PCM_SOFFICE || 'soffice', [
      '-env:UserInstallation=' + pathToFileURL(perfil).href, '--headless', '--convert-to', 'xlsx', '--outdir', saida, ...arquivos,
    ], { encoding: 'utf8', timeout: 55_000 });
    assert.equal(resultado.status, 0, 'LibreOffice indisponível ou conversão falhou; recálculo NÃO comprovado. ' + (resultado.error?.code || resultado.stderr || ''));
  };
  const prova = new ExcelJS.Workbook(); const abaProva = prova.addWorksheet('Prova');
  abaProva.getCell('A1').value = 3; abaProva.getCell('A2').value = { formula: 'SUM(A1,9)', result: -1 };
  prova.calcProperties.fullCalcOnLoad = true;
  await prova.xlsx.writeFile(join(entrada, 'prova.xlsx'));
  converter([join(entrada, 'prova.xlsx')]);
  const provaRecalculada = new ExcelJS.Workbook(); await provaRecalculada.xlsx.readFile(join(saida, 'prova.xlsx'));
  assert.equal(provaRecalculada.worksheets[0].getCell('A2').result, 12, 'O motor preservou cache errado; recálculo NÃO comprovado.');

  const notas = [
    [1, 1, 2, 2, 2], [1, 2, 2, 2, 2], [2, 2, 2, 2, 3], [2, 2, 2, 3, 3], [3, 1, 1, 1, 1],
    [], ['2', 2, 2, 2, 2], [2.5, 2, 2, 2, 2], [null, 1, 1, 1, 1],
  ];
  const dados = { geradoEm: new Date('2026-10-22T12:00:00Z'), equipamentos: notas.map((_, i) => ({
    id: `ficticio-${i}`, tag: `PRS-MOT-${String(i + 1).padStart(3, '0')}`, descricao: `Ativo fictício ${i + 1}`, setor: 'PRS', numero: i + 1,
  })) };
  const cenarios = [{ nome: 'padrao', limites: { a: 12, b: 9 } },
    { nome: 'limites-editados', limites: { a: 10, b: 7 } }, { nome: 'limites-invalidos', limites: { a: 9, b: 9 } }];
  for (const cenario of cenarios) {
    const wb = await montarPcmdWorkbook(dados, ExcelJS);
    const ativos = wb.getWorksheet(ABA_ATIVOS);
    notas.forEach((ns, i) => { for (let j = 0; j < 5; j++) ativos.getCell(PRIMEIRO_ATIVO + i, 5 + j).value = ns[j] ?? null; });
    wb.getWorksheet('Cadastros').getCell('B12').value = cenario.limites.a;
    wb.getWorksheet('Cadastros').getCell('B13').value = cenario.limites.b;
    // Os inputs e limites mudaram após a geração: nenhum cache inicial pode provar o resultado.
    for (const aba of wb.worksheets) aba.eachRow(row => row.eachCell(cell => {
      if (cell.formula) cell.value = { formula: cell.formula, result: 'CACHE_PROPOSITALMENTE_ERRADO' };
    }));
    await wb.xlsx.writeFile(join(entrada, cenario.nome + '.xlsx'));
  }
  // Um arquivo por processo mantém o limite de tempo independente para cada cenário.
  for (const cenario of cenarios) converter([join(entrada, cenario.nome + '.xlsx')]);
  let conferidos = 0;
  for (const cenario of cenarios) {
    const wb = new ExcelJS.Workbook(); await wb.xlsx.load(await readFile(join(saida, cenario.nome + '.xlsx')));
    const aba = wb.getWorksheet(ABA_ATIVOS);
    notas.forEach((ns, i) => {
      const esperado = calcularCriticidade(ns, cenario.limites);
      ['pontuacao', 'classe', 'estrategia'].forEach((campo, j) => {
        assert.equal(aba.getCell(PRIMEIRO_ATIVO + i, 10 + j).result, esperado[campo], `${cenario.nome}, linha ${i + 1}, ${campo}`);
        conferidos++;
      });
    });
  }
  await mkdir(destino, { recursive: true });
  await writeFile(join(destino, 'recalculo-libreoffice.json'), JSON.stringify({
    resultado: 'aprovado', provaCacheErrado: '-1 recalculado para 12', cenarios: cenarios.map(c => c.nome),
    resultadosConferidos: conferidos, data: new Date().toISOString(),
    limite: 'Prova de fórmulas no LibreOffice; Excel 2010 e impressão física ainda precisam de conferência manual.',
  }, null, 2) + '\n');
  console.log(`Recálculo externo aprovado: prova pequena e ${conferidos} resultados, após mudar entradas e invalidar caches.`);
} finally {
  await rm(temporario, { recursive: true, force: true });
}
