import { describe, it, expect } from 'vitest';
import { criarGestao, validarGestao, criticidadeAtivo, migrarExecucoesAntigas, ocorrenciasPlanejadas, resumoMensal } from '../src/logica/gestao.js';

const historico = (mudancas = {}) => ({ id: 'h1', equipamentoId: 'eq1', tarefaId: 'MOT-01', tag: 'PRS-MOT-001', descricao: 'Inspeção fictícia', data: '2026-01-08', dataPrevista: '', observacao: '', responsavelId: '', origem: 'app', cancelada: false, ...mudancas });
const item = (mudancas = {}) => ({ equipamentoId: 'eq1', tarefaId: 'MOT-01', tag: 'PRS-MOT-001', descricao: 'Inspeção fictícia', especialidade: 'Elétrica', duracaoHoras: 0.5, vezesAno: 52, semanas: [1, 2], ...mudancas });
const dados = (itens = [item()], inicio = new Date(2026, 0, 5)) => ({ inicio, cronograma: itens });

describe('cadastros e movimentos de gestão', () => {
  it('cria cadastros independentes e válidos sem metas ou pessoas inventadas', () => {
    const a = criarGestao(); const b = criarGestao();
    expect(validarGestao(a)).toBe(true);
    expect(a.metas).toEqual({ disponibilidade: null, aderencia: null });
    a.organizacao.setores.push('PRS');
    expect(b.organizacao.setores).toEqual([]);
    expect(validarGestao(undefined)).toBe(false);
  });
  it('confere pessoas, metas e notas sem aceitar IDs inseguros ou limites contraditórios', () => {
    const g = criarGestao();
    g.pessoas.push({ id: 'p1', nome: 'Pessoa A', funcao: 'Responsável', especialidade: 'Elétrica', ativo: true });
    g.metas = { disponibilidade: 0, aderencia: 100 };
    g.criticidade.notas.eq1 = [null, 1, 2, 3, 1];
    g.responsaveis['eq1|MOT-01'] = 'p1';
    expect(validarGestao(g)).toBe(true);
    for (const alterar of [
      x => { x.pessoas.push({ ...x.pessoas[0] }); },
      x => { x.pessoas[0].id = 'p"1'; },
      x => { x.metas.aderencia = 101; },
      x => { x.metas.disponibilidade = '90'; },
      x => { x.criticidade.limites = { a: 9, b: 9 }; },
      x => { x.criticidade.notas.eq1 = [1, 1, 1, '2', 1]; },
      x => { x.responsaveis['chave inválida'] = 'p1'; },
    ]) { const copia = structuredClone(g); alterar(copia); expect(validarGestao(copia)).toBe(false); }
    const perigoso = JSON.parse(JSON.stringify(g));
    perigoso.responsaveis = JSON.parse('{"__proto__":{}}');
    expect(validarGestao(perigoso)).toBe(false);
  });
  it('só permite requisito verificado com versão, data real e fonte HTTPS', () => {
    const g = criarGestao();
    const r = { id: 'r1', referencia: 'Referência fictícia', versao: '', data: '', fonte: '', status: 'nao_verificado' };
    g.requisitos.push(r);
    expect(validarGestao(g)).toBe(true);
    r.status = 'verificado'; expect(validarGestao(g)).toBe(false);
    Object.assign(r, { versao: '1', data: '2028-02-29', fonte: 'https://exemplo.invalid/referencia' });
    expect(validarGestao(g)).toBe(true);
    for (const campo of [{ data: '2027-02-29' }, { data: '2026-13-01' }, { fonte: 'javascript:alert(1)' }, { fonte: 'http://exemplo.invalid' }, { fonte: 'https://usuario:senha@exemplo.invalid' }]) {
      expect(validarGestao({ ...g, requisitos: [{ ...r, ...campo }] })).toBe(false);
    }
  });
  it('valida datas e horas de falhas e preserva snapshots sem exigir ativo atual', () => {
    const g = criarGestao();
    g.historico = [historico()];
    g.falhas = [{ id: 'f1', equipamentoId: 'eq1', tag: 'PRS-MOT-001', data: '2026-10-20', sintoma: 'Ruído fictício', causa: '', acao: '', horasParada: null, peca: '', responsavelId: '' }];
    expect(validarGestao(g)).toBe(true);
    g.falhas[0].horasParada = -1; expect(validarGestao(g)).toBe(false);
    g.falhas[0].horasParada = 1.5; expect(validarGestao(g)).toBe(true);
    g.historico[0].data = '2026-02-30'; expect(validarGestao(g)).toBe(false);
  });
  it('classifica fronteiras e segurança sem presumir notas ausentes', () => {
    for (const [notas, classe] of [[[1, 1, 2, 2, 2], 'C'], [[1, 2, 2, 2, 2], 'B'], [[2, 2, 2, 2, 3], 'B'], [[2, 2, 2, 3, 3], 'A'], [[3, 1, 1, 1, 1], 'A']]) {
      expect(criticidadeAtivo(notas).classe).toBe(classe);
    }
    for (const notas of [undefined, [], [3, null, 1, 1, 1], [2, 2, '2', 2, 2], new Array(5)]) expect(criticidadeAtivo(notas)).toEqual({ pontuacao: null, classe: 'Pendente' });
    expect(criticidadeAtivo([2, 2, 2, 2, 2], { a: 10, b: 7 }).classe).toBe('A');
    expect(criticidadeAtivo([3, 1, 1, 1, 1], { a: 9, b: 9 }).classe).toBe('Pendente');
  });
});

describe('migração da última marcação', () => {
  it('preserva data e observação, sem inventar vínculo, alterar origem ou duplicar ao reabrir', () => {
    const g = criarGestao(); const antigas = { 'eq1|MOT-01': { data: '2026-10-20', observacao: 'Conferência fictícia' } };
    const nova = migrarExecucoesAntigas(g, antigas, [{ id: 'eq1', tag: 'PRS-MOT-001' }], [item()]);
    expect(g.historico).toEqual([]);
    expect(nova.historico).toHaveLength(1);
    expect(nova.historico[0]).toMatchObject({ data: '2026-10-20', observacao: 'Conferência fictícia', dataPrevista: '', origem: 'legado', tag: 'PRS-MOT-001' });
    expect(validarGestao(nova)).toBe(true);
    expect(migrarExecucoesAntigas(nova, antigas).historico).toEqual(nova.historico);
    nova.historico[0].cancelada = true;
    expect(migrarExecucoesAntigas(nova, antigas).historico).toEqual(nova.historico);
  });
  it('não perde pares com IDs que produziriam o mesmo identificador legado', () => {
    const antigas = { 'a-b|c': { data: '2026-10-20', observacao: '' }, 'a|b-c': { data: '2026-10-20', observacao: '' } };
    const nova = migrarExecucoesAntigas(criarGestao(), antigas);
    expect(nova.historico).toHaveLength(2);
    expect(new Set(nova.historico.map(h => h.id)).size).toBe(2);
    expect(validarGestao(nova)).toBe(true);
  });
});

describe('cronograma mensal derivado', () => {
  it('distribui cinco dias úteis por janela semanal, mesmo quando o início não é segunda', () => {
    const ocorrencias = ocorrenciasPlanejadas(dados([item({ vezesAno: 260, semanas: [1, 1] })], new Date(2026, 0, 7)));
    expect(ocorrencias.map(o => o.dataPrevista)).toEqual(['2026-01-07', '2026-01-08', '2026-01-09', '2026-01-12', '2026-01-13']);
    expect(ocorrencias.reduce((s, o) => s + o.horas, 0)).toBe(2.5);
  });
  it('mantém ocorrência no seu mês previsto, conta realização uma vez e ignora canceladas/sem vínculo', () => {
    const d = dados(); const g = criarGestao();
    g.historico = [historico({ dataPrevista: '2026-01-05', data: '2026-02-01' }), historico({ id: 'h2', dataPrevista: '2026-01-05' }),
      historico({ id: 'h3', dataPrevista: '2026-01-12', cancelada: true }), historico({ id: 'h4', dataPrevista: '' })];
    const resumo = resumoMensal(d, g);
    expect(resumo.meses[0]).toEqual({ mes: 1, previstas: 2, realizadas: 1, horas: 1, percentual: 50 });
    expect(resumo.meses[1].percentual).toBeNull();
    expect(resumo.semVinculo).toBe(1);
  });
  it('separa ocorrências fora do ano sem perder horas e não conta registros sem previsão atual', () => {
    const d = dados([item({ semanas: [1, 2] })], new Date(2026, 11, 28));
    const g = criarGestao();
    g.historico = [historico({ data: '2026-12-29', dataPrevista: '2026-12-20' })];
    const resumo = resumoMensal(d, g);
    expect(resumo.meses[11].previstas).toBe(1);
    expect(resumo.foraDoAno).toEqual({ previstas: 1, horas: 0.5 });
    expect(resumo.semVinculo).toBe(1);
    expect(resumoMensal(d, g, 2027).meses[0].previstas).toBe(1);
  });
});
