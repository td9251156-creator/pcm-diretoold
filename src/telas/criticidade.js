import { estado, dadosAtuais } from '../estado.js';
import { criticidadeAtivo } from '../logica/gestao.js';
import { esc } from '../ui.js';
import { campo, copiaGestao, guardar } from './gestao-ui.js';

const CRITERIOS = ['Segurança', 'Qualidade', 'Produção', 'Frequência de falha', 'Custo/tempo de reparo'];
export function telaCriticidade(main) {
  const g = estado.gestao; const equipamentos = dadosAtuais().equipamentos;
  main.innerHTML = `<section class="cartao"><h2>Criticidade dos ativos</h2><p>Avalie cinco critérios de 1 a 3. Defina o significado das notas com o responsável antes de avaliar. Sem todas as notas, o resultado fica Pendente.</p>
    <p>Segurança com nota 3 determina classe A. A classificação não muda as tarefas, as frequências ou as travas de segurança.</p>
    <form id="form-limites"><div class="grade duas">${campo('limite-a', 'Classe A a partir de', g.criticidade.limites.a, 'number', 'min="6" max="15" step="1" required')}${campo('limite-b', 'Classe B a partir de', g.criticidade.limites.b, 'number', 'min="5" max="14" step="1" required')}</div><p class="origem">Proposta inicial: A≥12, B≥9, C abaixo de 9. Os limites precisam respeitar 5≤B&lt;A≤15.</p><button id="salvar-limites">Salvar limites</button></form></section>
    <section><h3>Avaliação por equipamento</h3>${equipamentos.map(eq => {
      const notas = g.criticidade.notas[eq.id] || Array(5).fill(null); const r = criticidadeAtivo(notas, g.criticidade.limites);
      return `<form class="cartao avaliacao" data-equipamento="${eq.id}"><h3>${esc(eq.tag)} · ${esc(eq.descricao)}</h3><div class="grade tres">${CRITERIOS.map((c, i) => `<div><label for="nota-${eq.id}-${i}">${c}</label><select id="nota-${eq.id}-${i}" name="nota-${i}"><option value="">Não avaliado</option>${[1, 2, 3].map(n => `<option ${notas[i] === n ? 'selected' : ''}>${n}</option>`).join('')}</select></div>`).join('')}</div><p>Pontuação: <strong>${r.pontuacao ?? 'Pendente'}</strong> · Classe: <strong>${r.classe}</strong></p><button id="salvar-notas-${eq.id}">Salvar avaliação de ${esc(eq.tag)}</button></form>`;
    }).join('') || '<p>Nenhum ativo válido. <a href="#equipamentos">Cadastre ou corrija os equipamentos.</a></p>'}</section>`;
  main.querySelector('#form-limites').addEventListener('submit', e => {
    e.preventDefault(); const nova = copiaGestao();
    nova.criticidade.limites = { a: Number(e.target.elements['limite-a'].value), b: Number(e.target.elements['limite-b'].value) };
    guardar(nova, () => telaCriticidade(main), 'salvar-limites');
  });
  main.querySelectorAll('.avaliacao').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault(); const nova = copiaGestao();
    nova.criticidade.notas[f.dataset.equipamento] = CRITERIOS.map((_, i) => f.elements[`nota-${i}`].value === '' ? null : Number(f.elements[`nota-${i}`].value));
    guardar(nova, () => telaCriticidade(main), `salvar-notas-${f.dataset.equipamento}`);
  }));
}
