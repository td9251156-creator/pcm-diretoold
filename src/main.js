// Ponto de entrada: carrega o rascunho, troca de tela pelo endereço (#inicio, #equipamentos...)
// e registra o service worker para funcionar como aplicativo e sem internet.
import { carregar, recuperacao } from './estado.js';
import { baixar, atualizarAvisoArmazenamento } from './ui.js';
import { telaInicio } from './telas/inicio.js';
import { telaEquipamentos } from './telas/equipamentos.js';
import { telaRevisao } from './telas/revisao.js';
import { telaEntrega } from './telas/entrega.js';
import { telaBiblioteca } from './telas/biblioteca.js';
import { telaImpressao } from './telas/impressao.js';
import { telaExecucao } from './telas/execucao.js';
import { telaCadastros } from './telas/cadastros.js';
import { telaCriticidade } from './telas/criticidade.js';
import { telaPlano, telaMensal } from './telas/planejamento.js';
import { telaFalhas } from './telas/falhas.js';

const TELAS = {
  inicio: { titulo: 'Início', desenhar: telaInicio },
  equipamentos: { titulo: 'Equipamentos', desenhar: telaEquipamentos },
  revisao: { titulo: 'Revisão', desenhar: telaRevisao },
  entrega: { titulo: 'Entrega', desenhar: telaEntrega },
  biblioteca: { titulo: 'Biblioteca técnica', desenhar: telaBiblioteca }, // fora das 4 etapas
  impressao: { titulo: 'Cronograma para imprimir', desenhar: telaImpressao },
  execucao: { titulo: 'Checklist de execução', desenhar: telaExecucao },
  cadastros: { titulo: 'Cadastros mestre', desenhar: telaCadastros },
  criticidade: { titulo: 'Criticidade', desenhar: telaCriticidade },
  plano: { titulo: 'Plano Mestre', desenhar: telaPlano },
  mensal: { titulo: 'Planejamento mensal', desenhar: telaMensal },
  falhas: { titulo: 'Registro de falhas', desenhar: telaFalhas },
};

const main = document.getElementById('conteudo');
document.querySelector('.pular').addEventListener('click', (e) => {
  e.preventDefault();
  main.focus();
  main.scrollIntoView();
});

/** Vai para outra tela. */
function ir(nome) {
  if (location.hash === '#' + nome) mostrar();
  else location.hash = nome;
}

/** Desenha a tela indicada no endereço. */
function mostrar() {
  const nome = location.hash.slice(1);
  const tela = TELAS[nome] ?? TELAS.inicio;
  const atual = TELAS[nome] ? nome : 'inicio';
  document.querySelectorAll('nav a[data-tela]').forEach((a) => {
    if (a.dataset.tela === atual) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  document.title = `${tela.titulo} · PCM Direto`;
  tela.desenhar(main, ir);
  // Leva o foco para o conteúdo novo (ajuda quem navega por teclado ou leitor de tela)
  main.focus();
  window.scrollTo(0, 0);
}

// Tema: automático (segue o aparelho) → claro → escuro
const TEMAS = ['', 'claro', 'escuro'];
const NOMES_TEMA = { '': 'automático', claro: 'claro', escuro: 'escuro' };
const botaoTema = document.getElementById('tema');
function mostrarTema() { botaoTema.textContent = `Tema: ${NOMES_TEMA[document.documentElement.dataset.tema ?? '']}`; }
botaoTema.addEventListener('click', () => {
  const atual = document.documentElement.dataset.tema ?? '';
  const novo = TEMAS[(TEMAS.indexOf(atual) + 1) % TEMAS.length];
  if (novo) document.documentElement.dataset.tema = novo;
  else delete document.documentElement.dataset.tema;
  try { if (novo) localStorage.setItem('pcm-direto:tema', novo); else localStorage.removeItem('pcm-direto:tema'); } catch { /* segue sem salvar */ }
  mostrarTema();
});
mostrarTema();

carregar();
atualizarAvisoArmazenamento();
if (recuperacao.length) {
  const aviso = document.createElement('section');
  aviso.className = 'cartao erro';
  aviso.setAttribute('role', 'alert');
  const texto = document.createElement('p');
  texto.textContent = 'Alguns dados salvos não puderam ser abertos. Os originais foram mantidos. Baixe uma cópia antes de continuar; a lista exibida pode estar vazia ou usar a biblioteca original.';
  const botao = document.createElement('button');
  botao.textContent = 'Baixar dados originais para recuperação';
  botao.addEventListener('click', () => baixar(JSON.stringify(recuperacao, null, 2), 'pcm-direto-recuperacao.json', 'application/json'));
  aviso.append(texto, botao);
  main.before(aviso);
}
window.addEventListener('hashchange', mostrar);
mostrar();

// Service worker só na versão publicada (no modo de desenvolvimento ele atrapalharia)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
}
