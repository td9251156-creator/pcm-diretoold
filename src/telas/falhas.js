import { estado, dadosAtuais } from '../estado.js';
import { novoId } from '../logica/entrada.js';
import { textoData } from '../logica/cronograma.js';
import { esc, avisar, baixar, num } from '../ui.js';
import { campo, selecionarPessoa, tabela, copiaGestao, guardar, valorOpcional, pessoaNome } from './gestao-ui.js';

export function telaFalhas(main) {
  const equipamentos = dadosAtuais().equipamentos; const hoje = textoData(new Date());
  main.innerHTML = `<div id="tela-falhas"><section class="cartao"><h2>Registro de falhas</h2><p>Registre fatos observados, sem dados pessoais nas descrições. Causa provável não é uma causa comprovada. Este registro não calcula MTBF, MTTR ou disponibilidade.</p><form id="form-falha"><input type="hidden" name="id"><div class="grade duas">
    <div><label for="falha-equipamento">Equipamento</label><select id="falha-equipamento" name="equipamentoId" required><option value="">Escolha o ativo</option>${equipamentos.map(e => `<option value="${e.id}">${esc(e.tag)} · ${esc(e.descricao)}</option>`).join('')}</select></div>
    ${campo('data-falha', 'Data da falha', hoje, 'date', `min="1900-01-01" max="${hoje}" required`)}${campo('sintoma', 'Sintoma observado', '', 'text', 'maxlength="2000" required')}${campo('causa', 'Causa provável (opcional)', '', 'text', 'maxlength="2000"')}${campo('acao', 'Ação tomada (opcional)', '', 'text', 'maxlength="2000"')}${campo('horasParada', 'Horas de parada (opcional)', '', 'number', 'min="0" step="0.01"')}${campo('peca', 'Peça trocada (opcional)', '', 'text', 'maxlength="120"')}${selecionarPessoa('responsavelId', 'Responsável')}
    </div><div class="acoes"><button id="salvar-falha" ${!equipamentos.length ? 'disabled' : ''}>Registrar falha</button><button type="reset" class="secundario">Limpar edição</button></div></form>${!equipamentos.length ? '<p><a href="#equipamentos">Cadastre um equipamento válido para registrar uma falha.</a></p>' : ''}</section>
    <section class="cartao"><h3>Histórico de falhas</h3><button type="button" class="secundario" id="baixar-falhas">Baixar registros (.json)</button>
    ${tabela(['Data / ativo', 'Sintoma / causa provável', 'Ação / peça', 'Parada / responsável', 'Ações'], estado.gestao.falhas.slice().reverse().map(f => `<tr><td>${esc(f.data)}<br>${esc(f.tag)}${!equipamentos.some(e => e.id === f.equipamentoId) ? '<br>Ativo fora da lista atual' : ''}</td><td>${esc(f.sintoma)}<br><span class="origem">${esc(f.causa || 'Causa não informada')}</span></td><td>${esc(f.acao || 'Não informada')}<br>${esc(f.peca)}</td><td>${f.horasParada === null ? 'Parada não informada' : num(f.horasParada, 2) + ' h'}<br>${esc(pessoaNome(f.responsavelId))}</td><td><button type="button" class="secundario" data-editar-falha="${f.id}">Corrigir registro</button></td></tr>`))}</section></div>`;
  const form = main.querySelector('#form-falha');
  form.addEventListener('submit', e => {
    e.preventDefault(); const f = form.elements; const nova = copiaGestao();
    const anterior = nova.falhas.find(r => r.id === f.id.value);
    const eq = equipamentos.find(e => e.id === f.equipamentoId.value);
    if (!eq && (!anterior || f.equipamentoId.value !== anterior.equipamentoId)) { avisar('Escolha um ativo válido da lista.'); return; }
    if (!f['data-falha'].value || f['data-falha'].value > hoje) { avisar('Informe uma data válida até hoje.'); return; }
    const r = { id: anterior?.id || novoId(), equipamentoId: eq?.id || anterior.equipamentoId, tag: eq?.tag || anterior.tag,
      data: f['data-falha'].value, sintoma: f.sintoma.value.trim(), causa: f.causa.value.trim(), acao: f.acao.value.trim(),
      horasParada: valorOpcional(f.horasParada.value), peca: f.peca.value.trim(), responsavelId: f.responsavelId.value };
    nova.falhas = anterior ? nova.falhas.map(x => x.id === r.id ? r : x) : [...nova.falhas, r];
    guardar(nova, () => telaFalhas(main), 'g-sintoma');
  });
  form.addEventListener('reset', () => { form.elements.id.value = ''; main.querySelector('#salvar-falha').textContent = 'Registrar falha'; });
  main.querySelector('#baixar-falhas').addEventListener('click', () => baixar(JSON.stringify(estado.gestao.falhas, null, 2), 'pcm-direto-falhas.json', 'application/json'));
  main.querySelector('#tela-falhas').addEventListener('click', e => {
    const b = e.target.closest('[data-editar-falha]'); if (!b) return;
    const r = estado.gestao.falhas.find(f => f.id === b.dataset.editarFalha); const f = form.elements;
    if (!equipamentos.some(eq => eq.id === r.equipamentoId) && !Array.from(f.equipamentoId.options).some(o => o.value === r.equipamentoId)) {
      f.equipamentoId.add(new Option(`${r.tag} (fora da lista atual)`, r.equipamentoId));
    }
    f.id.value = r.id; f.equipamentoId.value = r.equipamentoId; f['data-falha'].value = r.data;
    for (const nome of ['sintoma', 'causa', 'acao', 'peca', 'horasParada']) f[nome].value = r[nome] ?? '';
    if (r.responsavelId && !Array.from(f.responsavelId.options).some(o => o.value === r.responsavelId)) f.responsavelId.add(new Option(pessoaNome(r.responsavelId), r.responsavelId));
    f.responsavelId.value = r.responsavelId; main.querySelector('#salvar-falha').disabled = false;
    main.querySelector('#salvar-falha').textContent = 'Salvar correção'; f.sintoma.focus();
  });
}
