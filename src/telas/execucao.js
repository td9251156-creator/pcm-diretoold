// Checklist e histórico completo, guardados somente neste aparelho.
import { estado, dadosAtuais, registrarExecucao, cancelarExecucao } from '../estado.js';
import { chaveAjuste } from '../logica/plano.js';
import { ocorrenciasPlanejadas } from '../logica/gestao.js';
import { pessoasOpcoes, pessoaNome, tabela } from './gestao-ui.js';
import { textoData } from '../logica/cronograma.js';
import { esc, avisar, baixar } from '../ui.js';

export function telaExecucao(main) {
  const dados = dadosAtuais();
  const hoje = textoData(new Date());
  const ativas = dados.plano.filter((l) => l.ativa);
  const previstas = ocorrenciasPlanejadas(dados);
  const realizadas = new Set(estado.gestao.historico.filter(h => !h.cancelada && h.dataPrevista).map(h => `${h.equipamentoId}|${h.tarefaId}|${h.dataPrevista}`));
  main.innerHTML = `
    <section class="cartao">
      <h2>Checklist de execução</h2>
      <p>Marque o que foi executado e registre a data e uma observação técnica, sem dados pessoais.
      Cada envio registra uma nova execução no histórico. Escolha uma ocorrência prevista para contar no percentual realizado; registros sem vínculo continuam guardados.</p>
      <p>Marcar uma tarefa não altera a periodicidade nem as datas do plano. Confira o cronograma e o manual antes de executar.</p>
      <p><a href="#revisao">Voltar à revisão</a> · <a href="#entrega">Ir para a entrega</a></p>
      <button type="button" id="baixar-execucoes">Baixar histórico de execuções (.json)</button>
    </section>
    <div id="checklists">${dados.equipamentos.map((e) => `
      <details class="cartao">
        <summary><strong>${esc(e.tag)}</strong> — ${esc(e.descricao)}</summary>
        ${ativas.filter((l) => l.equipamentoId === e.id).map((l) => {
    const chave = chaveAjuste(l.equipamentoId, l.tarefaId);
    const r = estado.execucoes[chave];
    const id = `${l.equipamentoId}-${l.tarefaId}`;
    return `<form class="cartao" data-equipamento="${esc(l.equipamentoId)}" data-tarefa="${esc(l.tarefaId)}">
      <h3>${esc(l.tarefaId)} — ${esc(l.descricao)} ${l.seguranca ? '<span class="selo-seguranca">SEGURANÇA</span>' : ''}</h3>
      <p>${esc(l.periodicidade)} · ${esc(l.especialidade)}</p>
      <label class="caixa"><input type="checkbox" name="concluida" ${r ? 'checked' : ''}> Execução realizada</label>
      <p class="origem">${r ? `Última execução: ${esc(r.data)}. O envio abaixo registra uma nova realização.` : 'Sem execução registrada.'}</p>
      <div class="grade duas">
        <div><label for="data-${id}">Data da execução</label><input id="data-${id}" name="data" type="date" max="${hoje}" value="${hoje}" min="1900-01-01"></div>
        <div><label for="nota-${id}">Observação técnica (opcional, sem dados pessoais)</label><textarea id="nota-${id}" name="observacao" maxlength="2000"></textarea></div>
        <div><label for="prevista-${id}">Ocorrência prevista (opcional)</label><select id="prevista-${id}" name="dataPrevista"><option value="">Sem vínculo — não contar no percentual</option>${previstas.filter(o => o.equipamentoId === l.equipamentoId && o.tarefaId === l.tarefaId && !realizadas.has(o.chave)).map(o => `<option value="${o.dataPrevista}">${o.dataPrevista}</option>`).join('')}</select></div>
        <div><label for="responsavel-${id}">Responsável pela execução</label><select id="responsavel-${id}" name="responsavelId">${pessoasOpcoes(estado.gestao.responsaveis[chave])}</select></div>
      </div>
      <div class="acoes"><button id="registrar-${id}" type="submit">Registrar nova execução de ${esc(l.tarefaId)}</button></div>
    </form>`;
  }).join('') || '<p>Não há tarefas ativas para este equipamento.</p>'}
      </details>`).join('') || '<p>Nenhum equipamento válido para executar. <a href="#equipamentos">Conferir equipamentos</a>.</p>'}
    </div>`;

  main.querySelector('#checklists').addEventListener('submit', (e) => {
    e.preventDefault();
    const form = e.target;
    const linha = ativas.find((l) => l.equipamentoId === form.dataset.equipamento && l.tarefaId === form.dataset.tarefa);
    const concluida = form.elements.concluida.checked;
    const chave = chaveAjuste(linha.equipamentoId, linha.tarefaId);
    let r;
    if (!concluida) {
      const candidatos = estado.gestao.historico.filter(h => !h.cancelada && h.equipamentoId === linha.equipamentoId && h.tarefaId === linha.tarefaId).sort((a, b) => a.data.localeCompare(b.data));
      const ultimo = candidatos.at(-1);
      if (!ultimo || !estado.execucoes[chave]) { avisar('Marque Execução realizada para registrar uma nova execução.'); return; }
      if (!confirm('Cancelar a última execução desta tarefa? O registro permanece no histórico e o plano não será alterado.')) return;
      r = cancelarExecucao(ultimo.id);
    } else {
      r = registrarExecucao(linha, { data: form.elements.data.value, observacao: form.elements.observacao.value,
        dataPrevista: form.elements.dataPrevista.value, responsavelId: form.elements.responsavelId.value });
    }
    if (!r.ok) { avisar(r.motivo); return; }
    telaExecucao(main);
    const botao = document.getElementById(`registrar-${linha.equipamentoId}-${linha.tarefaId}`);
    if (botao) { botao.closest('details').open = true; botao.focus(); }
    avisar(r.guardado ? 'Execução atualizada no histórico deste aparelho.' : 'Alteração aplicada nesta sessão; baixe um backup antes de sair.');
  });
  const secao = document.createElement('section'); secao.className = 'cartao';
  secao.innerHTML = '<h3>Histórico completo de execuções</h3>' + tabela(['Data / ativo', 'Tarefa', 'Ocorrência / responsável', 'Observação / origem', 'Situação'], estado.gestao.historico.slice().reverse().map(h => `<tr><td>${esc(h.data)}<br>${esc(h.tag || h.equipamentoId)}${!estado.equipamentos.some(e => e.id === h.equipamentoId) ? '<br>Ativo fora da lista atual' : ''}</td><td>${esc(h.tarefaId)}<br>${esc(h.descricao)}</td><td>${esc(h.dataPrevista || 'Sem vínculo')}<br>${esc(pessoaNome(h.responsavelId))}</td><td>${esc(h.observacao)}<br><span class="origem">${h.origem === 'legado' ? 'Marcação antiga preservada' : 'Registro no app'}</span></td><td>${h.cancelada ? 'Cancelada' : `<button type="button" class="secundario" data-cancelar="${h.id}">Cancelar registro de ${esc(h.tag || h.tarefaId)}</button>`}</td></tr>`)) + '<p class="origem">Registros antigos não possuem vínculo presumido. Cancelar não apaga o histórico nem altera tarefas de segurança.</p>';
  main.append(secao);
  secao.addEventListener('click', e => {
    const id = e.target.closest('[data-cancelar]')?.dataset.cancelar;
    if (!id || !confirm('Cancelar este registro? Ele será mantido no histórico, sem contar no realizado.')) return;
    const r = cancelarExecucao(id); if (!r.ok) { avisar(r.motivo); return; }
    telaExecucao(main); main.focus(); avisar(r.guardado ? 'Registro cancelado e preservado no histórico.' : 'Cancelamento aplicado nesta sessão; baixe um backup antes de sair.');
  });
  main.querySelector('#baixar-execucoes').addEventListener('click', () => baixar(JSON.stringify(estado.gestao.historico, null, 2), 'pcm-direto-execucoes.json', 'application/json'));
}
