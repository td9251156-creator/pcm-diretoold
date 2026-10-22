import { beforeEach, afterEach, describe, it, expect, vi } from 'vitest';
import padrao from '../src/dados/biblioteca.json';
import { criarGestao } from '../src/logica/gestao.js';
import { criarBackup, verificarBackup } from '../src/logica/backup.js';

const eq = { id: 'eq1', setor: 'UTL', tipo: 'motor_eletrico', descricao: 'Motor fictício', numero: 1, tag: 'UTL-MOT-001' };
const CHAVE = 'pcm-direto:rascunho:v1';
let dados;
beforeEach(() => {
  vi.resetModules(); vi.useFakeTimers(); vi.setSystemTime(new Date('2026-10-22T12:00:00'));
  dados = new Map();
  vi.stubGlobal('localStorage', { getItem: k => dados.get(k) ?? null, setItem: (k, v) => dados.set(k, String(v)), removeItem: k => dados.delete(k) });
});
afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers(); });
async function abrir() {
  const app = await import('../src/estado.js'); app.carregar();
  app.estado.equipamentos = [structuredClone(eq)]; app.estado.inicio = '2026-01-05';
  return app;
}

describe('gestão e preservação dos dados', () => {
  it('abre marcação v1 como legado, preserva observação e não duplica ao reabrir', async () => {
    dados.set(CHAVE, JSON.stringify({ equipamentos: [eq], execucoes: { 'eq1|MOT-01': { data: '2026-10-20', observacao: 'Conferência fictícia' } } }));
    const app = await import('../src/estado.js'); app.carregar();
    expect(app.estado.gestao.historico).toHaveLength(1);
    expect(app.estado.gestao.historico[0]).toMatchObject({ origem: 'legado', dataPrevista: '', observacao: 'Conferência fictícia' });
    app.salvar(); app.carregar(); expect(app.estado.gestao.historico).toHaveLength(1);
    expect(app.cancelarExecucao(app.estado.gestao.historico[0].id).ok).toBe(true);
    app.carregar(); expect(app.estado.gestao.historico[0].cancelada).toBe(true);
    expect(app.estado.execucoes).toEqual({});
  });
  it('persiste cadastros e criticidade e faz roundtrip do backup v2', async () => {
    const app = await abrir(); const g = criarGestao();
    g.organizacao.nome = 'Indústria Exemplo';
    g.pessoas.push({ id: 'pessoa-a', nome: 'Pessoa A', funcao: 'Responsável', especialidade: 'Elétrica', ativo: true });
    g.criticidade.notas.eq1 = [3, 1, 1, 1, 1];
    g.metas.aderencia = 90;
    expect(app.atualizarGestao(g).ok).toBe(true);
    app.carregar(); expect(app.estado.gestao).toEqual(g);
    const backup = criarBackup(app.estado);
    expect(backup.versao).toBe(2); expect(verificarBackup(backup, padrao).ok).toBe(true);
    app.estado.gestao = criarGestao(); expect(app.restaurarBackup(backup).ok).toBe(true);
    expect(app.estado.gestao).toEqual(g);
  });
  it('não troca os dados quando o backup tem novos cadastros inválidos', async () => {
    const app = await abrir(); app.salvar(); const antes = new Map(dados);
    const backup = criarBackup(app.estado); backup.rascunho.gestao.metas.aderencia = 101;
    expect(app.restaurarBackup(backup).ok).toBe(false); expect(dados).toEqual(antes);
    backup.rascunho.gestao = null; expect(verificarBackup(backup, padrao).ok).toBe(false);
    expect(verificarBackup({ ...backup, versao: 3 }, padrao).ok).toBe(false);
  });
  it('preserva original de rascunho com gestão malformada e não o substitui silenciosamente', async () => {
    const original = JSON.stringify({ equipamentos: [eq], gestao: { versao: 99 } }); dados.set(CHAVE, original);
    const app = await import('../src/estado.js'); app.carregar();
    expect(dados.get(CHAVE)).toBe(original); expect(app.recuperacao).toEqual([{ chave: CHAVE, original }]);
    expect(app.estado.equipamentos).toEqual([]);
    app.salvar(); expect([...dados.values()].some(v => v.includes('"original"'))).toBe(true);
  });
  it('registra realizações distintas, recusa duplicidade de vínculo e datas futuras e preserva ao remover ativo', async () => {
    const app = await abrir(); const linha = app.dadosAtuais().plano.find(l => l.tarefaId === 'MOT-01');
    const { ocorrenciasPlanejadas } = await import('../src/logica/gestao.js');
    const prevista = ocorrenciasPlanejadas(app.dadosAtuais()).find(o => o.tarefaId === linha.tarefaId);
    const registro = { data: '2026-10-20', observacao: 'Teste fictício', dataPrevista: prevista.dataPrevista, responsavelId: '' };
    expect(app.registrarExecucao(linha, registro).ok).toBe(true);
    expect(app.registrarExecucao(linha, registro).ok).toBe(false);
    expect(app.registrarExecucao(linha, { ...registro, dataPrevista: '', data: '2026-10-21' }).ok).toBe(true);
    expect(app.registrarExecucao(linha, { ...registro, dataPrevista: '', data: '2026-10-23' }).ok).toBe(false);
    expect(app.estado.gestao.historico).toHaveLength(2);
    app.remover('eq1'); expect(app.estado.gestao.historico).toHaveLength(2);
    app.salvar(); app.carregar(); expect(app.estado.gestao.historico).toHaveLength(2);
    expect(app.estado.execucoes).toEqual({});
  });
  it('preserva cadastros e registros anteriores ao começar lista em branco', async () => {
    const app = await abrir(); app.estado.gestao.organizacao.nome = 'Indústria Exemplo';
    app.estado.gestao.falhas.push({ id: 'falha1', equipamentoId: 'eq1', tag: eq.tag, data: '2026-10-20', sintoma: 'Ruído fictício', causa: '', acao: '', horasParada: null, peca: '', responsavelId: '' });
    app.limpar(); app.carregar(); expect(app.estado.equipamentos).toEqual([]);
    expect(app.estado.gestao.organizacao.nome).toBe('Indústria Exemplo'); expect(app.estado.gestao.falhas).toHaveLength(1);
  });
  it('desfazer remoção não ressuscita uma execução cancelada enquanto o ativo estava fora da lista', async () => {
    const app = await abrir(); const linha = app.dadosAtuais().plano[0];
    expect(app.registrarExecucao(linha, { data: '2026-10-20', observacao: '', dataPrevista: '', responsavelId: '' }).ok).toBe(true);
    const id = app.estado.gestao.historico[0].id;
    app.remover('eq1'); app.cancelarExecucao(id);
    expect(app.desfazerRemocao().ok).toBe(true);
    expect(app.estado.execucoes).toEqual({});
    app.carregar(); expect(app.estado.execucoes).toEqual({});
    expect(app.estado.gestao.historico[0].cancelada).toBe(true);
  });
  it('migra e reabre tarefas antigas com descrição extensa sem truncar o histórico', async () => {
    const bib = structuredClone(padrao); bib.tipos[0].tarefas[0].descricao = 'Descrição fictícia extensa. '.repeat(150);
    dados.set('pcm-direto:biblioteca:v1', JSON.stringify(bib));
    dados.set(CHAVE, JSON.stringify({ equipamentos: [eq], execucoes: { 'eq1|MOT-01': { data: '2026-10-20', observacao: '' } } }));
    const app = await import('../src/estado.js'); app.carregar();
    expect(app.estado.gestao.historico[0].descricao).toBe(bib.tipos[0].tarefas[0].descricao);
    expect(app.salvar()).toBe(true); app.carregar();
    expect(app.recuperacao).toEqual([]); expect(app.estado.equipamentos).toHaveLength(1);
    expect(app.registrarExecucao(app.dadosAtuais().plano[0], { data: '2026-10-22', observacao: '' }).ok).toBe(true);
  });
});
