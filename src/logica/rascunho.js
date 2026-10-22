// Confere dados locais sem alterar a cópia recebida nem descartar a lista silenciosamente.
import { PERIODICIDADES } from './plano.js';
import { lerData, textoData } from './cronograma.js';
import { validarGestao } from './gestao.js';

export const objeto = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

export function dataValida(valor) {
  return typeof valor === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(valor) &&
    Number.isFinite(lerData(valor).getTime()) && textoData(lerData(valor)) === valor;
}

/** Retorna null quando não é seguro abrir; o chamador deve preservar o original. */
export function lerRascunho(salvo) {
  if (!objeto(salvo) || !Array.isArray(salvo.equipamentos)) return null;
  const ids = new Set();
  for (const e of salvo.equipamentos) {
    if (!objeto(e) || typeof e.id !== 'string' || !/^[A-Za-z0-9_-]+$/.test(e.id) || ids.has(e.id)) return null;
    ids.add(e.id);
    for (const campo of ['setor', 'tipo', 'descricao']) if (typeof e[campo] !== 'string') return null;
    for (const campo of ['fabricante', 'modelo']) if (e[campo] !== undefined && typeof e[campo] !== 'string') return null;
    if (e.numero !== null && e.numero !== undefined && typeof e.numero !== 'string' && !Number.isFinite(e.numero)) return null;
  }
  if (salvo.inicio !== undefined && !dataValida(salvo.inicio)) return null;
  const ajustes = salvo.ajustes ?? {};
  const capacidade = salvo.capacidade ?? {};
  if (!objeto(ajustes) || !objeto(capacidade)) return null;
  for (const [chave, a] of Object.entries(ajustes)) {
    if (!/^[A-Za-z0-9_-]+\|[A-Za-z0-9_-]+$/.test(chave) || !objeto(a)) return null;
    if (a.ativa !== undefined && typeof a.ativa !== 'boolean') return null;
    if (a.periodicidade !== undefined && !PERIODICIDADES.some((p) => p.nome === a.periodicidade)) return null;
  }
  if (Object.values(capacidade).some((v) => !Number.isFinite(v) || v < 0)) return null;
  if (salvo.gestao !== undefined && !validarGestao(salvo.gestao)) return null;
  return { ...salvo, ajustes, capacidade };
}
