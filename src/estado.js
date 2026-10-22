// Estado do app (equipamentos, ajustes, biblioteca e capacidade) e o que fica salvo no navegador.
import padrao from './dados/biblioteca.json';
import { EXEMPLO } from './dados/exemplo.js';
import { atribuirTags, gerarTag, proximoNumero } from './logica/tag.js';
import { siglasDaBiblioteca } from './logica/plano.js';
import { novoId } from './logica/entrada.js';
import { montarDados } from './logica/pacote.js';
import { proximaSegunda, textoData } from './logica/cronograma.js';
import { lerRascunho } from './logica/rascunho.js';
import { verificarBibliotecaEditada } from './logica/edicao.js';
import { validarExecucoes } from './logica/execucao.js';
import { verificarBackup } from './logica/backup.js';
import { recuperarTransacao, lerDadoLocal, guardarBackupLocal } from './armazenamento.js';
import { criarGestao, validarGestao, migrarExecucoesAntigas, ocorrenciasPlanejadas } from './logica/gestao.js';
import { marcarExecucao } from './logica/execucao.js';
import { chaveAjuste } from './logica/plano.js';

const CHAVE = 'pcm-direto:rascunho:v1';
const CHAVE_BIBLIOTECA = 'pcm-direto:biblioteca:v1';
const originaisPendentes = new Map();
export const recuperacao = [];
export const armazenamento = { rascunho: true, biblioteca: true, leitura: true };
let ultimaRemocao = null;
export const podeDesfazerRemocao = () => ultimaRemocao !== null;

function lerLocal(chave) {
  let original;
  try { original = lerDadoLocal(chave); } catch { armazenamento.leitura = false; return null; }
  if (original === null) return null;
  try { return { valor: JSON.parse(original), original }; }
  catch { return { valor: null, original }; }
}

function preservar(chave, original) {
  originaisPendentes.set(chave, original);
  recuperacao.push({ chave, original });
}

/** Guarda os originais antes de permitir qualquer substituição dos dados locais. */
function prepararGravacao() {
  try {
    if (!recuperarTransacao()) return false;
    for (const [chave, original] of originaisPendentes) {
      localStorage.setItem(`pcm-direto:recuperacao:v1:${novoId()}`, JSON.stringify({ chave, original }));
      originaisPendentes.delete(chave);
    }
    return true;
  } catch { return false; }
}

/** Biblioteca que vem com o app (src/dados/biblioteca.json). Nunca é alterada. */
export const BIBLIOTECA_PADRAO = padrao;
const copia = (obj) => JSON.parse(JSON.stringify(obj));

export const estado = {
  equipamentos: [],
  ajustes: {}, // ajustes da revisão: { "idEquipamento|idTarefa": { periodicidade, ativa } }
  execucoes: {}, // última marcação por equipamento e tarefa; não altera o plano
  exemplo: false, // true enquanto a lista for o exemplo da abertura
  inicio: textoData(proximaSegunda()), // data da semana 1 do cronograma
  capacidade: {}, // horas disponíveis por semana em cada especialidade: { Mecânica: 8 }
  biblioteca: copia(padrao), // biblioteca em uso (pode ter sido editada no app)
  bibliotecaEditada: false,
  gestao: criarGestao(),
};

/** Siglas por tipo da biblioteca em uso: { motor_eletrico: 'MOT', ... } */
export function siglas() {
  return siglasDaBiblioteca(estado.biblioteca);
}

/** Plano, cronograma e resumo da lista atual. */
export function dadosAtuais() {
  return montarDados(estado.equipamentos, estado.biblioteca, estado.ajustes, estado.inicio, estado.capacidade);
}

/** Recalcula a TAG de um equipamento a partir de setor, tipo e número. */
export function atualizarTag(eq) {
  eq.tag = gerarTag(eq.setor, siglas()[eq.tipo] ?? '???', eq.numero);
}

/** Lista de exemplo (dados fictícios), com ids e TAGs. */
export function listaExemplo() {
  return atribuirTags(EXEMPLO.map((e) => ({ ...e, id: novoId() })), siglas());
}

/** Lê o que está salvo. Na primeira abertura (nada salvo), carrega o exemplo. */
export function carregar() {
  ultimaRemocao = null;
  Object.assign(armazenamento, { rascunho: true, biblioteca: true, leitura: true });
  if (!recuperarTransacao()) armazenamento.leitura = false;
  recuperacao.length = 0;
  originaisPendentes.clear();
  estado.biblioteca = copia(padrao);
  estado.bibliotecaEditada = false;
  const biblioteca = lerLocal(CHAVE_BIBLIOTECA);
  if (biblioteca && verificarBibliotecaEditada(padrao, biblioteca.valor).length === 0) {
    estado.biblioteca = biblioteca.valor;
    estado.bibliotecaEditada = true;
  } else if (biblioteca) preservar(CHAVE_BIBLIOTECA, biblioteca.original);

  estado.inicio = textoData(proximaSegunda());
  estado.capacidade = {};
  const local = lerLocal(CHAVE);
  const lido = local && lerRascunho(local.valor);
  const salvo = lido && validarExecucoes(lido.execucoes ?? {}) ? lido : null;
  estado.execucoes = salvo?.execucoes ?? {};
  estado.gestao = salvo?.gestao ?? criarGestao();
  if (salvo) {
    estado.equipamentos = salvo.equipamentos.map((e) => ({ ...e }));
    for (const e of estado.equipamentos) atualizarTag(e);
    estado.ajustes = salvo.ajustes ?? {};
    estado.exemplo = !!salvo.exemplo;
    if (salvo.inicio) estado.inicio = salvo.inicio;
    estado.capacidade = salvo.capacidade ?? {};
  } else {
    if (local) preservar(CHAVE, local.original);
    estado.equipamentos = local ? [] : listaExemplo();
    estado.ajustes = {};
    estado.exemplo = !local;
  }
  estado.gestao = migrarExecucoesAntigas(estado.gestao, estado.execucoes, estado.equipamentos, dadosAtuais().plano);
  atualizarUltimasExecucoes();
}

/** Valida tudo antes de restaurar; mantém os originais se a gravação não terminar. */
export function restaurarBackup(arquivo) {
  const r = verificarBackup(arquivo, padrao);
  if (!r.ok) return r;
  if (!prepararGravacao() || !guardarBackupLocal(r.biblioteca, r.rascunho)) {
    armazenamento.rascunho = false;
    return { ok: false, motivo: 'Não foi possível guardar o backup neste aparelho. Os dados anteriores foram preservados; baixe uma cópia antes de sair.' };
  }
  carregar();
  return { ok: true };
}

/** Salva a lista no navegador. Se o navegador bloquear, o app continua funcionando. */
export function salvar() {
  try {
    if (!prepararGravacao()) { armazenamento.rascunho = false; return false; }
    localStorage.setItem(CHAVE, JSON.stringify({
      equipamentos: estado.equipamentos,
      ajustes: estado.ajustes,
      execucoes: estado.execucoes,
      exemplo: estado.exemplo,
      inicio: estado.inicio,
      capacidade: estado.capacidade,
      gestao: estado.gestao,
      salvoEm: new Date().toISOString(),
    }));
    armazenamento.rascunho = true;
    return true;
  } catch {
    armazenamento.rascunho = false;
    return false;
  }
}

/** Troca a biblioteca em uso (depois de editar ou importar) e salva no navegador. */
export function usarBiblioteca(nova) {
  estado.biblioteca = nova;
  estado.bibliotecaEditada = true;
  for (const eq of estado.equipamentos) atualizarTag(eq); // a sigla de um tipo pode ter mudado
  try {
    if (!prepararGravacao()) throw new Error('Cópia de recuperação indisponível');
    localStorage.setItem(CHAVE_BIBLIOTECA, JSON.stringify(nova));
    armazenamento.biblioteca = true;
  } catch { armazenamento.biblioteca = false; }
  return salvar() && armazenamento.biblioteca;
}

/** Volta para a biblioteca que vem com o app. */
export function restaurarBiblioteca() {
  estado.biblioteca = copia(padrao);
  estado.bibliotecaEditada = false;
  for (const eq of estado.equipamentos) atualizarTag(eq);
  try {
    if (!prepararGravacao()) throw new Error('Cópia de recuperação indisponível');
    localStorage.removeItem(CHAVE_BIBLIOTECA);
    armazenamento.biblioteca = true;
  } catch { armazenamento.biblioteca = false; }
  return salvar() && armazenamento.biblioteca;
}

/** Adiciona equipamentos já lidos (cadastro, colagem ou arquivo), numerando os que não têm número. */
export function adicionar(novos) {
  if (estado.exemplo) { estado.exemplo = false; }
  for (const e of novos) {
    const eq = { ...e };
    if (!eq.numero) eq.numero = proximoNumero(estado.equipamentos, eq.setor, eq.tipo);
    atualizarTag(eq);
    estado.equipamentos.push(eq);
  }
  salvar();
}

export function remover(id) {
  const indice = estado.equipamentos.findIndex((e) => e.id === id);
  if (indice < 0) return;
  estado.gestao = migrarExecucoesAntigas(estado.gestao, estado.execucoes, estado.equipamentos, dadosAtuais().plano);
  const selecionar = (dados) => Object.fromEntries(Object.entries(dados).filter(([k]) => k.startsWith(id + '|')));
  ultimaRemocao = {
    equipamento: { ...estado.equipamentos[indice] }, indice,
    ajustes: selecionar(estado.ajustes), execucoes: selecionar(estado.execucoes),
  };
  estado.equipamentos = estado.equipamentos.filter((e) => e.id !== id);
  // Remove também os ajustes desse equipamento
  for (const k of Object.keys(estado.ajustes)) if (k.startsWith(id + '|')) delete estado.ajustes[k];
  for (const k of Object.keys(estado.execucoes)) if (k.startsWith(id + '|')) delete estado.execucoes[k];
  salvar();
}

/** Desfaz uma remoção desta sessão, recuperando também ajustes e marcações. */
export function desfazerRemocao() {
  if (!ultimaRemocao) return { ok: false, motivo: 'Não há remoção para desfazer nesta sessão.' };
  const { equipamento, indice, ajustes, execucoes } = ultimaRemocao;
  const eq = { ...equipamento };
  atualizarTag(eq);
  if (estado.equipamentos.some((e) => e.id === eq.id || e.tag === eq.tag)) {
    return { ok: false, motivo: 'A TAG removida já está em uso. Corrija a numeração desse equipamento antes de desfazer.' };
  }
  estado.equipamentos.splice(indice, 0, eq);
  Object.assign(estado.ajustes, ajustes);
  Object.assign(estado.execucoes, execucoes);
  atualizarUltimasExecucoes();
  ultimaRemocao = null;
  salvar();
  return { ok: true };
}

/** Começa uma lista vazia. */
export function limpar() {
  ultimaRemocao = null;
  estado.equipamentos = [];
  estado.ajustes = {};
  estado.execucoes = {};
  estado.gestao.criticidade.notas = {};
  estado.gestao.responsaveis = {};
  estado.exemplo = false;
  salvar();
}

/** Volta para o exemplo da abertura. */
export function carregarExemplo() {
  ultimaRemocao = null;
  estado.equipamentos = listaExemplo();
  estado.ajustes = {};
  estado.execucoes = {};
  estado.gestao.criticidade.notas = {};
  estado.gestao.responsaveis = {};
  estado.exemplo = true;
  salvar();
}

/** Atualiza somente dados de gestão válidos. Falha de armazenamento é informada pela interface. */
export function atualizarGestao(nova) {
  if (!validarGestao(nova)) return { ok: false, motivo: 'Confira os campos: há dados de gestão inválidos.' };
  estado.gestao = nova;
  return { ok: true, guardado: salvar() };
}

/** Registra cada execução sem alterar frequência ou planejamento. */
export function registrarExecucao(linha, alteracao) {
  const r = marcarExecucao(estado.execucoes, linha, { ...alteracao, concluida: true });
  if (!r.ok) return r;
  const dataPrevista = alteracao.dataPrevista || '';
  if (dataPrevista && !ocorrenciasPlanejadas(dadosAtuais()).some(o => o.equipamentoId === linha.equipamentoId && o.tarefaId === linha.tarefaId && o.dataPrevista === dataPrevista)) {
    return { ok: false, motivo: 'Escolha uma ocorrência prevista do plano atual ou deixe sem vínculo.' };
  }
  if (dataPrevista && estado.gestao.historico.some(h => !h.cancelada && h.equipamentoId === linha.equipamentoId && h.tarefaId === linha.tarefaId && h.dataPrevista === dataPrevista)) {
    return { ok: false, motivo: 'Essa ocorrência já tem execução registrada. Cancele o registro anterior para corrigir.' };
  }
  const registro = { id: novoId(), equipamentoId: linha.equipamentoId, tarefaId: linha.tarefaId,
    tag: linha.tag, descricao: linha.descricao, data: alteracao.data, dataPrevista,
    observacao: alteracao.observacao.trim(), responsavelId: alteracao.responsavelId || '', origem: 'app', cancelada: false };
  const nova = { ...estado.gestao, historico: [...estado.gestao.historico, registro] };
  if (!validarGestao(nova)) return { ok: false, motivo: 'Não foi possível registrar a execução: confira os campos.' };
  estado.gestao = nova;
  atualizarUltimasExecucoes();
  return { ok: true, guardado: salvar() };
}

function atualizarUltimasExecucoes() {
  const ultimas = {};
  const ativos = new Set(estado.equipamentos.map(e => e.id));
  for (const h of estado.gestao.historico) {
    if (h.cancelada || !ativos.has(h.equipamentoId)) continue;
    const chave = chaveAjuste(h.equipamentoId, h.tarefaId);
    if (!ultimas[chave] || h.data >= ultimas[chave].data) ultimas[chave] = { data: h.data, observacao: h.observacao };
  }
  estado.execucoes = ultimas;
}

export function cancelarExecucao(id) {
  if (!estado.gestao.historico.some(h => h.id === id && !h.cancelada)) return { ok: false, motivo: 'Registro não encontrado ou já cancelado.' };
  estado.gestao = { ...estado.gestao, historico: estado.gestao.historico.map(h => h.id === id ? { ...h, cancelada: true } : h) };
  atualizarUltimasExecucoes();
  return { ok: true, guardado: salvar() };
}
