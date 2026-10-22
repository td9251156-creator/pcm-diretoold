// Gera somente um exemplo fictício para revisão; não lê dados salvos do navegador.
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import ExcelJS from 'exceljs';
import { readFile } from 'node:fs/promises';
import { EXEMPLO } from '../src/dados/exemplo.js';
import { atribuirTags } from '../src/logica/tag.js';
import { siglasDaBiblioteca } from '../src/logica/plano.js';
import { montarDados } from '../src/logica/pacote.js';
import { gerarPcmdXlsx } from '../src/saida/pcmd/xlsx.js';

const biblioteca = JSON.parse(await readFile(new URL('../src/dados/biblioteca.json', import.meta.url), 'utf8'));
const equipamentos = atribuirTags(EXEMPLO.map((e, i) => ({ ...e, id: `exemplo-${i + 1}` })), siglasDaBiblioteca(biblioteca));
const dados = montarDados(equipamentos, biblioteca, {}, '2027-01-04');
dados.geradoEm = new Date('2026-10-22T12:00:00Z');
const casos = [
  { notas: [1, 1, 2, 2, 2], pontuacao: 8, classe: 'C' },
  { notas: [1, 2, 2, 2, 2], pontuacao: 9, classe: 'B' },
  { notas: [2, 2, 2, 2, 3], pontuacao: 11, classe: 'B' },
  { notas: [2, 2, 2, 3, 3], pontuacao: 12, classe: 'A' },
  { notas: [3, 1, 1, 1, 1], pontuacao: 7, classe: 'A' },
];
const notasPorId = Object.fromEntries(casos.map((c, i) => [equipamentos[i].id, c.notas]));
const destino = resolve(process.env.PCM_PROTOTIPO_DIR || 'artifacts/pcmd');
await mkdir(destino, { recursive: true });
await writeFile(join(destino, 'pcmd-02-exemplo.xlsx'), await gerarPcmdXlsx(dados, ExcelJS, { notasPorId }));
await writeFile(join(destino, 'valores-esperados.json'), JSON.stringify({
  descricao: 'Dados fictícios. Limites A=12 e B=9. Não comprova recálculo no Excel.',
  casos: casos.map((c, i) => ({ tag: equipamentos[i].tag, ...c })),
  demaisAtivos: 'Notas vazias: pontuação e classe Pendente.',
  validacaoManual: 'Excel 2010: editar notas e limites, pressionar F9 e conferir os resultados e a impressão.',
}, null, 2) + '\n');
console.log('Protótipo fictício e valores esperados gerados em ' + destino);
