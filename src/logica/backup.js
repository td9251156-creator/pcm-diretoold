// Backup completo e versionado; valores permanecem somente no navegador e no arquivo baixado.
import { lerRascunho } from './rascunho.js';
import { validarExecucoes } from './execucao.js';
import { verificarBibliotecaEditada } from './edicao.js';

export function criarBackup(estado, hoje = new Date()) {
  const { equipamentos, ajustes, execucoes, exemplo, inicio, capacidade, biblioteca, gestao } = estado;
  return JSON.parse(JSON.stringify({ aplicativo: 'PCM Direto', versao: gestao ? 2 : 1, geradoEm: hoje.toISOString(), biblioteca,
    rascunho: { equipamentos, ajustes, execucoes, exemplo, inicio, capacidade, ...(gestao ? { gestao } : {}) } }));
}

export function verificarBackup(arquivo, padrao) {
  if (arquivo?.aplicativo !== 'PCM Direto' || ![1, 2].includes(arquivo?.versao) || (arquivo.versao === 2 && !arquivo.rascunho?.gestao)) return { ok: false, motivo: 'Escolha um backup completo válido do PCM Direto, versão 1 ou 2.' };
  const problemas = verificarBibliotecaEditada(padrao, arquivo.biblioteca);
  if (problemas.length) return { ok: false, motivo: 'Biblioteca do backup: ' + problemas[0] };
  const rascunho = lerRascunho(arquivo.rascunho);
  if (!rascunho || !validarExecucoes(rascunho.execucoes ?? {})) return { ok: false, motivo: 'O backup contém dados incompletos ou inválidos. A lista atual foi mantida.' };
  return { ok: true, biblioteca: arquivo.biblioteca, rascunho };
}
