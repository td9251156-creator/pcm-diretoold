import { estado } from '../estado.js';
import { PERIODICIDADES } from '../logica/plano.js';
import { novoId } from '../logica/entrada.js';
import { esc, avisar } from '../ui.js';
import { campo, selecionarPessoa, tabela, copiaGestao, guardar, valorOpcional } from './gestao-ui.js';

export function telaCadastros(main) {
  const g = estado.gestao; const o = g.organizacao;
  const setores = [...new Set([...o.setores, ...estado.equipamentos.map(e => e.setor).filter(s => /^[A-Z0-9]{2,4}$/.test(s))])].filter(Boolean);
  function reapresentar(formularioSalvo = '') {
    const rascunhos = Array.from(main.querySelectorAll('form')).filter(f => f.getAttribute('id') !== formularioSalvo).map(f => ({
      id: f.getAttribute('id'), campos: Array.from(f.elements).filter(c => c.name).map(c => ({ nome: c.name, valor: c.value, rotulo: c.selectedOptions?.[0]?.textContent })),
    }));
    telaCadastros(main);
    for (const r of rascunhos) {
      const f = main.querySelector(`#${r.id}`);
      for (const c of r.campos) {
        const campo = f.elements[c.nome];
        if (campo.tagName === 'SELECT' && c.valor && !Array.from(campo.options).some(o => o.value === c.valor)) campo.add(new Option(c.rotulo || c.valor, c.valor));
        campo.value = c.valor;
      }
    }
    if (main.querySelector('#form-pessoa').elements.id.value) main.querySelector('#salvar-pessoa').textContent = 'Salvar pessoa';
    if (main.querySelector('#form-requisito').elements.id.value) main.querySelector('#salvar-requisito').textContent = 'Salvar referência';
  }
  main.innerHTML = `<div id="tela-cadastros"><section class="cartao"><h2>Cadastros mestre</h2><p>Preencha uma vez para organizar seu PCM. Tudo fica neste aparelho e no backup completo.</p><p><a href="#equipamentos">M2 · Equipamentos</a> · <a href="#criticidade">Avaliar criticidade</a> · <a href="#entrega">Documentos</a></p></section>
    <section class="cartao"><h3>M1 · Organização</h3><form id="form-organizacao"><div class="grade duas">
      ${campo('nome', 'Nome da organização (opcional)', o.nome, 'text', 'maxlength="120" placeholder="Indústria Exemplo"')}
      ${campo('setores', 'Setores (siglas separadas por vírgula)', setores.join(', '), 'text', 'maxlength="1000" placeholder="UTL, PRD, EXP"')}
      ${selecionarPessoa('elaborador', 'Elaborador padrão', o.elaborador)}${selecionarPessoa('aprovador', 'Aprovador padrão', o.aprovador)}
      ${campo('padraoCodigo', 'Prefixo dos documentos', o.padraoCodigo, 'text', 'readonly')}${campo('referencial', 'Referencial', o.referencial, 'text', 'maxlength="120" required')}
    </div><p class="origem">Cadastre pessoas no M3 para escolher elaborador e aprovador. Setores já utilizados em ativos serão preservados.</p><button id="salvar-organizacao">Salvar organização</button></form></section>
    <section class="cartao"><h3>M3 · Pessoas e funções</h3><p>Use apenas os dados necessários. Pessoas inativadas permanecem nos registros anteriores.</p>
    <form id="form-pessoa"><input type="hidden" name="id"><div class="grade tres">${campo('pessoa-nome', 'Nome', '', 'text', 'maxlength="120" required placeholder="Pessoa A"')}${campo('funcao', 'Função', '', 'text', 'maxlength="120"')}${campo('especialidade', 'Especialidade', '', 'text', 'maxlength="120" list="especialidades"')}</div>
    <datalist id="especialidades">${[...new Set(estado.biblioteca.tipos.flatMap(t => t.tarefas.map(t => t.especialidade)))].map(e => `<option value="${esc(e)}"></option>`).join('')}</datalist>
    <div class="acoes"><button id="salvar-pessoa">Adicionar pessoa</button><button type="reset" class="secundario">Limpar edição</button></div></form>
    ${tabela(['Pessoa', 'Função / especialidade', 'Situação', 'Ações'], g.pessoas.map(p => `<tr><td>${esc(p.nome)}</td><td>${esc(p.funcao)} / ${esc(p.especialidade)}</td><td>${p.ativo ? 'Ativa' : 'Inativa'}</td><td><button type="button" class="secundario" data-editar-pessoa="${p.id}" aria-label="Editar ${esc(p.nome)}">Editar</button> <button type="button" class="secundario" data-ativar-pessoa="${p.id}">${p.ativo ? 'Inativar' : 'Reativar'} ${esc(p.nome)}</button></td></tr>`))}</section>
    <section class="cartao"><h3>M4 · Frequências e tipos de tarefa</h3><p>Consulta das frequências aceitas. A edição das tarefas continua na <a href="#biblioteca">Biblioteca técnica</a>, com as travas de segurança.</p>
    ${tabela(['Frequência', 'Execuções previstas no ciclo de 52 semanas'], PERIODICIDADES.map(p => `<tr><td>${p.nome}</td><td>${p.vezes}</td></tr>`))}
    <p>Diária considera cinco dias úteis por semana, sem calendário de feriados. Tipos de referência: preventiva, preditiva, lubrificação, inspeção e autônoma. A classificação das tarefas será conectada aos modelos quando você os fornecer.</p></section>
    <section class="cartao"><h3>M5 · Metas</h3><form id="form-metas"><div class="grade duas">${campo('disponibilidade', 'Meta de disponibilidade (%)', g.metas.disponibilidade, 'number', 'min="0" max="100" step="0.1" placeholder="A definir"')}${campo('aderencia', 'Meta de aderência preventiva (%)', g.metas.aderencia, 'number', 'min="0" max="100" step="0.1" placeholder="A definir"')}</div><p>Deixe em branco quando a meta não estiver definida. Disponibilidade, MTBF e MTTR não são calculados: as regras técnicas continuam pendentes.</p><button id="salvar-metas">Salvar metas</button></form></section>
    <section class="cartao"><h3>M6 · Requisitos e referências</h3><p>Comece com GERAL (sem norma). Marcar como verificado registra sua conferência; o app não valida o conteúdo da fonte nem certifica conformidade.</p>
    <form id="form-requisito"><input type="hidden" name="id"><div class="grade duas">${campo('referencia', 'Referência ou título', '', 'text', 'maxlength="2000" required')}${campo('versao', 'Versão', '', 'text', 'maxlength="120"')}${campo('data', 'Data da referência', '', 'date', 'min="1900-01-01" max="9999-12-31"')}${campo('fonte', 'Link HTTPS da fonte oficial', '', 'url', 'maxlength="2000" placeholder="https://"')}
    <div><label for="g-status">Status de verificação</label><select id="g-status" name="status"><option value="nao_verificado">Não verificado</option><option value="verificado">Verificado pelo responsável</option></select></div></div>
    <div class="acoes"><button id="salvar-requisito">Adicionar referência</button><button type="reset" class="secundario">Limpar edição</button></div></form>
    ${tabela(['Referência', 'Versão / data', 'Situação', 'Ações'], g.requisitos.map(r => `<tr><td>${esc(r.referencia)}${r.fonte ? `<br><a href="${esc(r.fonte)}" target="_blank" rel="noopener noreferrer">Abrir fonte informada</a>` : ''}</td><td>${esc(r.versao || 'A definir')} / ${esc(r.data || 'A definir')}</td><td>${r.status === 'verificado' ? 'Verificado pelo responsável' : 'Não verificado — verificar na fonte oficial'}</td><td><button type="button" class="secundario" data-editar-requisito="${r.id}">Editar referência</button> <button type="button" class="secundario" data-remover-requisito="${r.id}">Remover referência</button></td></tr>`))}</section></div>`;

  main.querySelector('#form-organizacao').addEventListener('submit', e => {
    e.preventDefault(); const f = e.target; const nova = copiaGestao();
    const digitados = f.elements.setores.value.split(/[,;\n]/).map(s => s.trim().toUpperCase()).filter(Boolean);
    if (digitados.some(s => !/^[A-Z0-9]{2,4}$/.test(s))) { avisar('Use siglas de setor com 2 a 4 letras ou números.'); f.elements.setores.focus(); return; }
    nova.organizacao = { nome: f.elements.nome.value.trim(), setores: [...new Set([...digitados, ...estado.equipamentos.map(e => e.setor).filter(s => /^[A-Z0-9]{2,4}$/.test(s))])],
      elaborador: f.elements.elaborador.value, aprovador: f.elements.aprovador.value, padraoCodigo: o.padraoCodigo, referencial: f.elements.referencial.value.trim() };
    guardar(nova, () => reapresentar('form-organizacao'), 'salvar-organizacao');
  });
  const fp = main.querySelector('#form-pessoa');
  fp.addEventListener('submit', e => {
    e.preventDefault(); const f = e.target; const nova = copiaGestao(); const atual = nova.pessoas.find(p => p.id === f.elements.id.value);
    const p = { id: atual?.id || novoId(), nome: f.elements['pessoa-nome'].value.trim(), funcao: f.elements.funcao.value.trim(), especialidade: f.elements.especialidade.value.trim(), ativo: atual?.ativo ?? true };
    nova.pessoas = atual ? nova.pessoas.map(x => x.id === p.id ? p : x) : [...nova.pessoas, p]; guardar(nova, () => reapresentar('form-pessoa'), 'g-pessoa-nome');
  });
  fp.addEventListener('reset', () => { fp.elements.id.value = ''; main.querySelector('#salvar-pessoa').textContent = 'Adicionar pessoa'; });
  main.querySelector('#form-metas').addEventListener('submit', e => { e.preventDefault(); const nova = copiaGestao(); nova.metas = { disponibilidade: valorOpcional(e.target.elements.disponibilidade.value), aderencia: valorOpcional(e.target.elements.aderencia.value) }; guardar(nova, () => reapresentar('form-metas'), 'salvar-metas'); });
  const fr = main.querySelector('#form-requisito');
  fr.addEventListener('submit', e => {
    e.preventDefault(); const f = e.target; const nova = copiaGestao();
    const r = { id: f.elements.id.value || novoId(), referencia: f.elements.referencia.value.trim(), versao: f.elements.versao.value.trim(), data: f.elements.data.value, fonte: f.elements.fonte.value.trim(), status: f.elements.status.value };
    if (r.status === 'verificado' && (!r.versao || !r.data || !r.fonte)) { avisar('Para marcar como verificado, preencha versão, data e fonte oficial HTTPS.'); return; }
    nova.requisitos = nova.requisitos.some(x => x.id === r.id) ? nova.requisitos.map(x => x.id === r.id ? r : x) : [...nova.requisitos, r]; guardar(nova, () => reapresentar('form-requisito'), 'g-referencia');
  });
  fr.addEventListener('reset', () => { fr.elements.id.value = ''; main.querySelector('#salvar-requisito').textContent = 'Adicionar referência'; });
  main.querySelector('#tela-cadastros').addEventListener('click', tratarClique);
  function tratarClique(e) {
    const b = e.target.closest('button'); const nova = copiaGestao();
    if (b?.dataset.editarPessoa) {
      const p = g.pessoas.find(p => p.id === b.dataset.editarPessoa);
      for (const [nome, valor] of Object.entries({ id: p.id, 'pessoa-nome': p.nome, funcao: p.funcao, especialidade: p.especialidade })) fp.elements[nome].value = valor;
      main.querySelector('#salvar-pessoa').textContent = 'Salvar pessoa'; fp.elements['pessoa-nome'].focus();
    } else if (b?.dataset.ativarPessoa) {
      nova.pessoas = nova.pessoas.map(p => p.id === b.dataset.ativarPessoa ? { ...p, ativo: !p.ativo } : p); guardar(nova, reapresentar, 'g-pessoa-nome'); return;
    } else if (b?.dataset.editarRequisito) {
      const r = g.requisitos.find(r => r.id === b.dataset.editarRequisito);
      for (const [nome, valor] of Object.entries(r)) fr.elements[nome].value = valor;
      main.querySelector('#salvar-requisito').textContent = 'Salvar referência'; fr.elements.referencia.focus();
    } else if (b?.dataset.removerRequisito) {
      if (confirm('Remover esta referência do cadastro?')) { nova.requisitos = nova.requisitos.filter(r => r.id !== b.dataset.removerRequisito); guardar(nova, () => reapresentar(fr.elements.id.value === b.dataset.removerRequisito ? 'form-requisito' : ''), 'g-referencia'); return; }
    }
  }
}
