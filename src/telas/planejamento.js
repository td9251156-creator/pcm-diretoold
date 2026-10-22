import { estado, dadosAtuais } from '../estado.js';
import { ocorrenciasPlanejadas, resumoMensal } from '../logica/gestao.js';
import { chaveAjuste } from '../logica/plano.js';
import { textoData } from '../logica/cronograma.js';
import { esc, num } from '../ui.js';
import { copiaGestao, guardar, pessoasOpcoes, tabela } from './gestao-ui.js';

export function telaPlano(main) {
  const dados = dadosAtuais(); const hoje = textoData(new Date());
  const previstas = ocorrenciasPlanejadas(dados);
  const concluidas = new Set(estado.gestao.historico.filter(h => !h.cancelada && h.dataPrevista).map(h => `${h.equipamentoId}|${h.tarefaId}|${h.dataPrevista}`));
  main.innerHTML = `<section class="cartao"><h2>Plano Mestre</h2><p>Uma linha por tarefa ativa, derivada da biblioteca e dos ajustes já revisados. A próxima data abaixo é uma ocorrência planejada, não uma nova regra de vencimento.</p><p><a href="#revisao">Editar frequências e capacidade na Revisão</a> · <a href="#mensal">Ver planejamento mensal</a> · <a href="#execucao">Registrar execução</a></p><label for="busca-plano">Buscar TAG, atividade ou especialidade</label><input id="busca-plano" type="search" placeholder="Ex.: UTL ou lubrificação"></section><section class="cartao"><div id="lista-plano"></div></section>`;
  const lista = main.querySelector('#lista-plano');
  function mostrar() {
    const busca = main.querySelector('#busca-plano').value.toLocaleLowerCase('pt-BR');
    lista.innerHTML = tabela(['Ativo / atividade', 'Frequência / horas', 'Especialidade', 'Responsável', 'Próxima ocorrência'], dados.plano.filter(l => l.ativa && `${l.tag} ${l.descricao} ${l.especialidade}`.toLocaleLowerCase('pt-BR').includes(busca)).map(l => {
      const chave = chaveAjuste(l.equipamentoId, l.tarefaId);
      const proxima = previstas.find(o => o.equipamentoId === l.equipamentoId && o.tarefaId === l.tarefaId && o.dataPrevista >= hoje && !concluidas.has(o.chave));
      return `<tr><td><strong>${esc(l.tag)}</strong> · ${esc(l.tarefaId)}<br>${esc(l.descricao)}${l.seguranca ? ' <span class="selo-seguranca">SEGURANÇA</span>' : ''}<div class="origem">${esc(l.origem)} · versão ${esc(l.versao)}</div></td><td>${esc(l.periodicidade)}<br>${num(l.duracaoHoras, 2)} h por execução</td><td>${esc(l.especialidade)}</td><td><label class="oculto" for="resp-${l.equipamentoId}-${l.tarefaId}">Responsável por ${esc(l.tag)} ${esc(l.tarefaId)}</label><select id="resp-${l.equipamentoId}-${l.tarefaId}" data-chave="${esc(chave)}">${pessoasOpcoes(estado.gestao.responsaveis[chave])}</select></td><td>${proxima?.dataPrevista || 'Sem ocorrência futura neste ciclo'}</td></tr>`;
    }), 'Nenhuma tarefa ativa com esses filtros.');
  }
  mostrar();
  main.querySelector('#busca-plano').addEventListener('input', mostrar);
  lista.addEventListener('change', e => {
    if (!e.target.dataset.chave) return;
    const nova = copiaGestao(); nova.responsaveis[e.target.dataset.chave] = e.target.value;
    const foco = e.target.id; guardar(nova, mostrar, foco);
  });
}

export function telaMensal(main) {
  const dados = dadosAtuais();
  main.innerHTML = `<section class="cartao"><h2>Planejamento mensal</h2><p>Janeiro a dezembro, somando as ocorrências do cronograma semanal atual. Não existe um segundo balanceamento mensal.</p><label for="ano-mensal">Ano de consulta</label><input id="ano-mensal" required type="number" min="1900" max="9999" step="1" value="${dados.inicio.getFullYear()}"><p><a href="#revisao">Revisar plano e capacidade</a> · <a href="#execucao">Vincular execuções a ocorrências previstas</a></p></section><section class="cartao" id="resumo-mensal"></section>`;
  const campoAno = main.querySelector('#ano-mensal');
  function mostrar() {
    if (!campoAno.reportValidity() || !Number.isInteger(Number(campoAno.value))) return;
    const r = resumoMensal(dados, estado.gestao, Number(campoAno.value));
    main.querySelector('#resumo-mensal').innerHTML = tabela(['Mês', 'Ocorrências previstas', 'Horas previstas', 'Realizadas com vínculo', '% realizado'], r.meses.map(m => `<tr><th scope="row">${new Date(Number(campoAno.value), m.mes - 1, 1).toLocaleDateString('pt-BR', { month: 'long' })}</th><td>${m.previstas}</td><td>${num(m.horas, 2)} h</td><td>${m.realizadas}</td><td>${m.percentual === null ? '—' : num(m.percentual) + '%'}</td></tr>`)) + `<p><strong>Fora do ano selecionado:</strong> ${r.foraDoAno.previstas} ocorrências · ${num(r.foraDoAno.horas, 2)} h do mesmo ciclo de 52 semanas.</p><p><strong>Execuções sem vínculo no ano:</strong> ${r.semVinculo}. Esses registros permanecem no histórico e não entram automaticamente no percentual.</p><p class="origem">Realizado = ocorrências com pelo menos uma execução válida e vinculada ÷ ocorrências previstas no mês. Uma ocorrência conta no máximo uma vez; cancelamentos não contam. Registros sem vínculo não provam a conclusão do previsto.</p>`;
  }
  mostrar(); campoAno.addEventListener('change', mostrar);
}
