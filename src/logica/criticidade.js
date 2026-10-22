// Matriz inicial de criticidade: proposta de organização, a validar pelo responsável.
export const LIMITES_CRITICIDADE = Object.freeze({ a: 12, b: 9 });
export const ESTRATEGIAS_CRITICIDADE = Object.freeze({
  A: 'Priorizar a avaliação das consequências e revisar a estratégia com o responsável.',
  B: 'Revisar a estratégia conforme as consequências e o histórico do ativo.',
  C: 'Acompanhar as consequências e revisar a estratégia quando houver mudança.',
});

export function limitesCriticidadeValidos(limites) {
  return !!limites && Number.isInteger(limites.a) && Number.isInteger(limites.b) &&
    limites.b >= 5 && limites.b < limites.a && limites.a <= 15;
}

export function calcularCriticidade(notas, limites = LIMITES_CRITICIDADE) {
  const validas = Array.isArray(notas) && notas.length === 5 &&
    Array.from(notas).every(n => Number.isInteger(n) && n >= 1 && n <= 3);
  if (!validas) return { pontuacao: 'Pendente', classe: 'Pendente', estrategia: 'Preencha cinco notas inteiras de 1 a 3.' };
  const pontuacao = notas.reduce((total, n) => total + n, 0);
  if (!limitesCriticidadeValidos(limites)) return { pontuacao, classe: 'Pendente', estrategia: 'Corrija os limites na aba Cadastros.' };
  const classe = notas[0] === 3 || pontuacao >= limites.a ? 'A' : pontuacao >= limites.b ? 'B' : 'C';
  return { pontuacao, classe, estrategia: ESTRATEGIAS_CRITICIDADE[classe] };
}
