// Componentes pequenos das telas de gestão, sem framework e sem envio de dados.
import { estado, atualizarGestao } from '../estado.js';
import { esc, avisar } from '../ui.js';

export const copiaGestao = () => structuredClone(estado.gestao);
export const pessoaNome = id => estado.gestao.pessoas.find(p => p.id === id)?.nome || 'Não informado';
export const campo = (nome, rotulo, valor = '', tipo = 'text', atributos = '') => `<div><label for="g-${nome}">${rotulo}</label><input id="g-${nome}" name="${nome}" type="${tipo}" value="${esc(valor ?? '')}" ${atributos}></div>`;
export const pessoasOpcoes = (atual = '') => '<option value="">Não informado</option>' + estado.gestao.pessoas.filter(p => p.ativo || p.id === atual).map(p => `<option value="${esc(p.id)}" ${p.id === atual ? 'selected' : ''}>${esc(p.nome)}${p.ativo ? '' : ' (inativa)'}</option>`).join('');
export const selecionarPessoa = (nome, rotulo, atual = '') => `<div><label for="g-${nome}">${rotulo}</label><select id="g-${nome}" name="${nome}">${pessoasOpcoes(atual)}</select></div>`;
export const tabela = (cabecalhos, linhas, vazio = 'Nenhum registro ainda.') => linhas.length ? `<div class="tabela-rolagem"><table><thead><tr>${cabecalhos.map(c => `<th scope="col">${c}</th>`).join('')}</tr></thead><tbody>${linhas.join('')}</tbody></table></div>` : `<p class="origem">${vazio}</p>`;
export function guardar(nova, redesenhar, foco) {
  const r = atualizarGestao(nova);
  if (!r.ok) { avisar(r.motivo); return false; }
  redesenhar();
  if (foco) document.getElementById(foco)?.focus();
  avisar(r.guardado ? 'Dados guardados neste aparelho.' : 'Alteração aplicada nesta sessão. O navegador não conseguiu salvar; baixe um backup antes de sair.');
  return true;
}
export const valorOpcional = texto => texto === '' ? null : Number(texto);
