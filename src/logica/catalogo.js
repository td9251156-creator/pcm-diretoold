// Contrato dos modelos públicos. Não inclui nenhum dado da fábrica ou da sessão.
import { PERIODICIDADES } from './plano.js';
export const TIPOS_CATALOGO = Object.freeze({ motor_eletrico: 'Motor elétrico', compressor_ar: 'Compressor de ar', bomba_centrifuga: 'Bomba centrífuga', ponte_rolante: 'Ponte rolante', outro: 'Outro tipo' });
export const CAMPOS_MODELO = ['titulo', 'tipo_base', 'fabricante', 'modelo', 'descricao', 'caracteristicas', 'apelido', 'tarefas'];
const CAMPOS_TAREFA = ['descricao', 'periodicidade', 'especialidade', 'duracao_horas', 'seguranca', 'origem', 'versao', 'observacao'];
const objeto = o => o !== null && typeof o === 'object' && !Array.isArray(o);
const exatas = (o, chaves) => objeto(o) && Object.keys(o).length === chaves.length && chaves.every(c => Object.hasOwn(o, c));
const texto = (s, max, obrigatorio = false) => typeof s === 'string' && s.length <= max && (!obrigatorio || s.trim().length > 0);
export function modeloVazio() { return { titulo: '', tipo_base: 'motor_eletrico', fabricante: '', modelo: '', descricao: '', caracteristicas: '', apelido: 'Colaborador', tarefas: [] }; }
export function tarefaCatalogoVazia() { return { descricao: '', periodicidade: 'Mensal', especialidade: '', duracao_horas: 0.5, seguranca: false, origem: 'base genérica a validar com manual do fabricante', versao: '1', observacao: '' }; }
export function validarModeloCatalogo(dados) {
  const erros = [];
  if (!exatas(dados, CAMPOS_MODELO)) return ['O cadastro deve conter somente os campos do modelo, sem dados do plano ou da fábrica.'];
  if (!texto(dados.titulo, 120, true)) erros.push('Informe um título com até 120 caracteres.');
  if (!Object.hasOwn(TIPOS_CATALOGO, dados.tipo_base)) erros.push('Escolha uma categoria de máquina.');
  if (!texto(dados.descricao, 2000, true)) erros.push('Informe uma descrição com até 2000 caracteres.');
  for (const c of ['fabricante', 'modelo']) if (!texto(dados[c], 120)) erros.push(`Confira ${c}: até 120 caracteres.`);
  if (!texto(dados.caracteristicas, 4000) || !texto(dados.apelido, 60)) erros.push('Confira as características (até 4000) e o apelido público (até 60 caracteres).');
  if (!Array.isArray(dados.tarefas) || dados.tarefas.length > 50) return [...erros, 'Use no máximo 50 tarefas por modelo.'];
  dados.tarefas.forEach((t, i) => {
    if (!exatas(t, CAMPOS_TAREFA) || !texto(t.descricao, 2000, true) || !PERIODICIDADES.some(p => p.nome === t.periodicidade) ||
      !texto(t.especialidade, 120, true) || !Number.isFinite(t.duracao_horas) || t.duracao_horas <= 0 || t.duracao_horas > 1000 ||
      typeof t.seguranca !== 'boolean' || !texto(t.origem, 500, true) || !texto(t.versao, 80, true) || !texto(t.observacao, 2000)) erros.push(`Confira os campos, a origem e a versão da tarefa ${i + 1}.`);
  });
  return erros;
}

export function configuracaoCatalogo(env = {}) {
  const url = env.VITE_SUPABASE_URL || ''; const chave = env.VITE_SUPABASE_ANON_KEY || '';
  if (!url && !chave) return { configurado: false, erro: '' };
  try {
    const u = new URL(url);
    if (u.protocol !== 'https:' || u.username || u.password || u.pathname !== '/' || u.search || u.hash) throw new Error();
    const publicavel = /^sb_publishable_[A-Za-z0-9_-]{16,}$/.test(chave);
    let anon = false;
    if (chave.split('.').length === 3) {
      const trecho = chave.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      anon = JSON.parse(atob(trecho.padEnd(Math.ceil(trecho.length / 4) * 4, '='))).role === 'anon';
    }
    if (!publicavel && !anon) throw new Error();
    return { configurado: true, url: u.origin, chave, erro: '' };
  } catch { return { configurado: false, erro: 'O catálogo precisa de URL HTTPS e chave pública publishable/anon válidas. Nunca use secret ou service_role no app.' }; }
}

/** Preenche somente um novo ativo local; tarefas remotas nunca substituem a biblioteca. */
export function dadosEquipamentoDoModelo(modelo, setor, tipo) {
  const erros = validarModeloCatalogo(modelo);
  if (erros.length) throw new Error(erros[0]);
  if (!/^[A-Z0-9]{2,4}$/.test(setor)) throw new Error('Informe um setor com 2 a 4 letras ou números.');
  return { setor, tipo, descricao: modelo.titulo, fabricante: modelo.fabricante, modelo: modelo.modelo };
}
