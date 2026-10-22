// Cadastros e movimentos locais; não cria documentos nem altera as regras do plano.
import { dataDaSemana, textoData } from './cronograma.js';

const objeto = valor => valor !== null && typeof valor === 'object' && !Array.isArray(valor) &&
  [Object.prototype, null].includes(Object.getPrototypeOf(valor));
const texto = (valor, limite = 120, obrigatorio = false) => typeof valor === 'string' &&
  valor.length <= limite && (!obrigatorio || valor.trim().length > 0);
const id = valor => typeof valor === 'string' && /^[A-Za-z0-9_-]+$/.test(valor);
const pessoaOpcional = valor => valor === '' || id(valor);
const chaveTarefa = valor => typeof valor === 'string' && /^[A-Za-z0-9_-]+\|[A-Za-z0-9_-]+$/.test(valor);
const lista = valor => Array.isArray(valor) && valor.length <= 100_000;
const limiteValido = limites => objeto(limites) && Number.isInteger(limites.a) && Number.isInteger(limites.b) &&
  limites.b >= 5 && limites.b < limites.a && limites.a <= 15;

function dataValida(valor) {
  if (typeof valor !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(valor)) return false;
  const [ano, mes, dia] = valor.split('-').map(Number);
  const data = new Date(ano, mes - 1, dia);
  return data.getFullYear() === ano && data.getMonth() === mes - 1 && data.getDate() === dia;
}

function fonteValida(valor) {
  if (!texto(valor, 2000)) return false;
  if (!valor) return true;
  try {
    const url = new URL(valor);
    return url.protocol === 'https:' && !url.username && !url.password;
  } catch { return false; }
}

function semChavesPerigosas(valor) {
  if (!valor || typeof valor !== 'object') return true;
  return Object.keys(valor).every(chave => !['__proto__', 'prototype', 'constructor'].includes(chave) && semChavesPerigosas(valor[chave]));
}

function registrosValidos(registros, verificar) {
  if (!lista(registros)) return false;
  const vistos = new Set();
  return registros.every(registro => {
    if (!objeto(registro) || !id(registro.id) || vistos.has(registro.id) || !verificar(registro)) return false;
    vistos.add(registro.id);
    return true;
  });
}

export function criarGestao() {
  return {
    versao: 1,
    organizacao: { nome: '', setores: [], elaborador: '', aprovador: '', padraoCodigo: 'PCMD', referencial: 'GERAL (sem norma)' },
    pessoas: [], metas: { disponibilidade: null, aderencia: null }, requisitos: [],
    criticidade: { limites: { a: 12, b: 9 }, notas: {} },
    responsaveis: {}, historico: [], falhas: [],
  };
}

/** Confere a estrutura inteira antes de abrir dados locais ou restaurar um backup. */
export function validarGestao(g) {
  try {
    if (!objeto(g) || g.versao !== 1 || !semChavesPerigosas(g)) return false;
    const o = g.organizacao;
    if (!objeto(o) || !texto(o.nome) || !texto(o.elaborador) || !texto(o.aprovador) ||
        !texto(o.padraoCodigo, 40, true) || !texto(o.referencial, 120, true) ||
        !lista(o.setores) || !o.setores.every(s => texto(s, 120, true)) || new Set(o.setores).size !== o.setores.length) return false;
    if (!registrosValidos(g.pessoas, p => texto(p.nome, 120, true) && texto(p.funcao) && texto(p.especialidade) && typeof p.ativo === 'boolean')) return false;
    if (!objeto(g.metas) || !['disponibilidade', 'aderencia'].every(c => g.metas[c] === null ||
      (Number.isFinite(g.metas[c]) && g.metas[c] >= 0 && g.metas[c] <= 100))) return false;
    if (!registrosValidos(g.requisitos, r => texto(r.referencia, 2000, true) && texto(r.versao) &&
        (r.data === '' || dataValida(r.data)) && fonteValida(r.fonte) && ['nao_verificado', 'verificado'].includes(r.status) &&
        (r.status !== 'verificado' || (!!r.versao.trim() && !!r.data && !!r.fonte)))) return false;
    if (!objeto(g.criticidade) || !limiteValido(g.criticidade.limites) || !objeto(g.criticidade.notas) ||
        !Object.entries(g.criticidade.notas).every(([chave, ns]) => id(chave) && Array.isArray(ns) && ns.length === 5 &&
          Array.from(ns).every(n => n === null || (Number.isInteger(n) && n >= 1 && n <= 3)))) return false;
    if (!objeto(g.responsaveis) || !Object.entries(g.responsaveis).every(([chave, valor]) => chaveTarefa(chave) && pessoaOpcional(valor))) return false;
    if (!registrosValidos(g.historico, h => id(h.equipamentoId) && id(h.tarefaId) && texto(h.tag, Number.MAX_SAFE_INTEGER) && texto(h.descricao, Number.MAX_SAFE_INTEGER) &&
        dataValida(h.data) && (h.dataPrevista === '' || dataValida(h.dataPrevista)) && texto(h.observacao, 2000) &&
        pessoaOpcional(h.responsavelId) && ['app', 'legado'].includes(h.origem) && typeof h.cancelada === 'boolean')) return false;
    return registrosValidos(g.falhas, f => id(f.equipamentoId) && texto(f.tag, Number.MAX_SAFE_INTEGER) && dataValida(f.data) &&
      texto(f.sintoma, 2000, true) && texto(f.causa, 2000) && texto(f.acao, 2000) && texto(f.peca) && pessoaOpcional(f.responsavelId) &&
      (f.horasParada === null || (Number.isFinite(f.horasParada) && f.horasParada >= 0)));
  } catch { return false; }
}

export function criticidadeAtivo(notas, limites = { a: 12, b: 9 }) {
  if (!Array.isArray(notas) || notas.length !== 5 || !Array.from(notas).every(n => Number.isInteger(n) && n >= 1 && n <= 3)) {
    return { pontuacao: null, classe: 'Pendente' };
  }
  const pontuacao = notas.reduce((total, nota) => total + nota, 0);
  if (!limiteValido(limites)) return { pontuacao, classe: 'Pendente' };
  return { pontuacao, classe: notas[0] === 3 || pontuacao >= limites.a ? 'A' : pontuacao >= limites.b ? 'B' : 'C' };
}

/** Converte a última marcação antiga sem inventar a ocorrência que foi executada. */
export function migrarExecucoesAntigas(gestao, execucoes, equipamentos = [], plano = []) {
  const nova = structuredClone(gestao);
  const pares = new Set(nova.historico.map(h => `${h.equipamentoId}|${h.tarefaId}`));
  const ids = new Set(nova.historico.map(h => h.id));
  for (const [chave, registro] of Object.entries(execucoes ?? {})) {
    if (!chaveTarefa(chave) || pares.has(chave) || !objeto(registro) || !dataValida(registro.data) || !texto(registro.observacao, 2000)) continue;
    const [equipamentoId, tarefaId] = chave.split('|');
    const equipamento = equipamentos.find(e => e.id === equipamentoId);
    const tarefa = plano.find(t => t.equipamentoId === equipamentoId && t.tarefaId === tarefaId);
    // O separador pode existir nos IDs antigos. O sufixo evita colisões sem perder registros.
    const base = `legado-${equipamentoId}-${tarefaId}`.slice(0, 110);
    let identificador = base; let sufixo = 1;
    while (ids.has(identificador)) identificador = `${base}-${sufixo++}`;
    nova.historico.push({ id: identificador, equipamentoId, tarefaId, tag: equipamento?.tag ?? tarefa?.tag ?? '',
      descricao: tarefa?.descricao ?? '', data: registro.data, dataPrevista: '', observacao: registro.observacao,
      responsavelId: '', origem: 'legado', cancelada: false });
    pares.add(chave); ids.add(identificador);
  }
  return nova;
}

/** Datas previstas derivadas das 52 semanas existentes; não faz novo balanceamento. */
export function ocorrenciasPlanejadas(dados) {
  const ocorrencias = []; const vistas = new Set();
  for (const item of dados.cronograma) {
    for (const semana of item.semanas) {
      if (!Number.isInteger(semana) || semana < 1 || semana > 52) continue;
      const inicioSemana = dataDaSemana(dados.inicio, semana);
      const diaria = item.vezesAno > 52;
      for (let deslocamento = 0; deslocamento < (diaria ? 7 : 1); deslocamento++) {
        const data = new Date(inicioSemana.getFullYear(), inicioSemana.getMonth(), inicioSemana.getDate() + deslocamento);
        if (diaria && (data.getDay() === 0 || data.getDay() === 6)) continue;
        const dataPrevista = textoData(data);
        const chave = `${item.equipamentoId}|${item.tarefaId}|${dataPrevista}`;
        if (vistas.has(chave)) continue;
        vistas.add(chave);
        ocorrencias.push({ chave, equipamentoId: item.equipamentoId, tarefaId: item.tarefaId, tag: item.tag,
          descricao: item.descricao, especialidade: item.especialidade, dataPrevista, horas: item.duracaoHoras });
      }
    }
  }
  return ocorrencias.sort((a, b) => a.dataPrevista.localeCompare(b.dataPrevista) || a.chave.localeCompare(b.chave));
}

export function resumoMensal(dados, gestao, ano = dados.inicio.getFullYear()) {
  const meses = Array.from({ length: 12 }, (_, i) => ({ mes: i + 1, previstas: 0, realizadas: 0, horas: 0, percentual: null }));
  const foraDoAno = { previstas: 0, horas: 0 };
  const ocorrencias = ocorrenciasPlanejadas(dados);
  const previstas = new Map(ocorrencias.map(o => [o.chave, o]));
  const realizadas = new Set();
  let semVinculo = 0;
  for (const h of gestao.historico) {
    if (h.cancelada) continue;
    const chave = `${h.equipamentoId}|${h.tarefaId}|${h.dataPrevista}`;
    if (h.dataPrevista && previstas.has(chave)) realizadas.add(chave);
    else if (Number(h.data.slice(0, 4)) === Number(ano)) semVinculo++;
  }
  for (const o of ocorrencias) {
    if (Number(o.dataPrevista.slice(0, 4)) !== Number(ano)) {
      foraDoAno.previstas++; foraDoAno.horas += o.horas;
      continue;
    }
    const mes = meses[Number(o.dataPrevista.slice(5, 7)) - 1];
    mes.previstas++; mes.horas += o.horas;
    if (realizadas.has(o.chave)) mes.realizadas++;
  }
  for (const mes of meses) if (mes.previstas) mes.percentual = mes.realizadas * 100 / mes.previstas;
  return { meses, foraDoAno, semVinculo };
}
