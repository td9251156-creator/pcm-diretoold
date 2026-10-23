// Monta os dados FICTÍCIOS da demonstração usando a lógica real do PCM Direto.
// Plano e cronograma: src/logica (main). Ocorrências e resumo mensal: cópia de referência
// de gestao.js (ramo interface/cadastros-operacao-sem-templates). Nada é enviado para fora.
// Uso: node gerador/dados-demo.mjs > build/demo.json
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { montarDados } from '../../src/logica/pacote.js';
import { atribuirTags } from '../../src/logica/tag.js';
import { siglasDaBiblioteca } from '../../src/logica/plano.js';
import { textoData } from '../../src/logica/cronograma.js';
import { criarGestao, validarGestao, ocorrenciasPlanejadas, resumoMensal, criticidadeAtivo } from './referencia/gestao-ramo-interface.js';

const raiz = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const biblioteca = JSON.parse(readFileSync(join(raiz, 'src', 'dados', 'biblioteca.json'), 'utf8'));

export const INICIO = '2025-11-03'; // segunda-feira; semana 1 do ciclo de 52 semanas
export const ANO = 2026; // ano consultado no resumo mensal

// Ativos fictícios (fabricantes e modelos inventados). IDs estáveis para os testes.
const equipamentos = atribuirTags([
  { id: 'eq-demo-001', setor: 'UTL', tipo: 'compressor_ar', descricao: 'Compressor de parafuso da central de ar', fabricante: 'Fabricante Fictício A', modelo: 'Modelo Fictício CP-30' },
  { id: 'eq-demo-002', setor: 'UTL', tipo: 'bomba_centrifuga', descricao: 'Bomba de água de resfriamento 1', fabricante: 'Fabricante Fictício B', modelo: 'Modelo Fictício BC-50' },
  { id: 'eq-demo-003', setor: 'PRD', tipo: 'motor_eletrico', descricao: 'Motor da esteira de alimentação', fabricante: 'Fabricante Fictício C', modelo: 'Modelo Fictício ME-7' },
  { id: 'eq-demo-004', setor: 'PRD', tipo: 'ponte_rolante', descricao: 'Ponte rolante do galpão de montagem (5 t)', fabricante: 'Fabricante Fictício D', modelo: 'Modelo Fictício PR-5' },
], siglasDaBiblioteca(biblioteca));

const dados = montarDados(equipamentos, biblioteca, {}, INICIO, {});
const ocorrencias = ocorrenciasPlanejadas(dados);
const primeira = (eq, tarefa, mes) => ocorrencias.find((o) => o.equipamentoId === eq && o.tarefaId === tarefa && o.dataPrevista.startsWith(mes));
const tagDe = (eq) => equipamentos.find((e) => e.id === eq)?.tag;
const descDe = (eq, tarefa) => dados.plano.find((l) => l.equipamentoId === eq && l.tarefaId === tarefa)?.descricao;

const gestao = criarGestao();
gestao.organizacao = { nome: 'Indústria Exemplo', setores: ['UTL', 'PRD', 'EXP'], elaborador: 'pes-a', aprovador: '', padraoCodigo: 'PCMD', referencial: 'GERAL (sem norma)' };
gestao.pessoas = [
  { id: 'pes-a', nome: 'Pessoa A', funcao: 'Planejamento de manutenção', especialidade: 'Mecânica', ativo: true },
  { id: 'pes-b', nome: 'Pessoa B', funcao: 'Técnico de manutenção', especialidade: 'Elétrica', ativo: true },
];
gestao.requisitos = [{ id: 'req-001', referencia: 'GERAL (sem norma)', versao: '', data: '', fonte: '', status: 'nao_verificado' }];
// Notas fictícias de demonstração: B, C, Pendente (nota ausente) e A por Segurança = 3.
gestao.criticidade.notas = {
  'eq-demo-001': [2, 2, 3, 2, 2],
  'eq-demo-002': [1, 1, 2, 1, 1],
  'eq-demo-003': [1, 2, null, 2, 2],
  'eq-demo-004': [3, 1, 1, 1, 1],
};
for (const l of dados.plano) {
  if (l.equipamentoId === 'eq-demo-004' || l.especialidade === 'Mecânica') gestao.responsaveis[`${l.equipamentoId}|${l.tarefaId}`] = 'pes-a';
  else if (l.especialidade === 'Elétrica') gestao.responsaveis[`${l.equipamentoId}|${l.tarefaId}`] = 'pes-b';
}

const historico = [];
function execucao(id, eq, tarefa, mesPrevisto, dataReal, extra = {}) {
  const o = mesPrevisto ? primeira(eq, tarefa, mesPrevisto) : null;
  historico.push({ id, equipamentoId: eq, tarefaId: tarefa, tag: tagDe(eq) ?? extra.tag, descricao: descDe(eq, tarefa) ?? extra.descricao,
    data: dataReal ?? o.dataPrevista, dataPrevista: o ? o.dataPrevista : '', observacao: extra.observacao ?? '',
    responsavelId: extra.responsavelId ?? 'pes-a', origem: extra.origem ?? 'app', cancelada: extra.cancelada ?? false });
}
execucao('ex-0001', 'eq-demo-001', 'CMP-01', '2026-01', null, { responsavelId: 'pes-b', observacao: 'Registro fictício de demonstração' });
execucao('ex-0002', 'eq-demo-001', 'CMP-01', '2026-01', null, { responsavelId: 'pes-b', observacao: 'Segundo registro da mesma ocorrência: conta uma vez' });
execucao('ex-0003', 'eq-demo-001', 'CMP-06', '2026-01', '2026-02-03', { observacao: 'Realizada em outro mês: conta no mês previsto' });
execucao('ex-0004', 'eq-demo-002', 'BCF-01', '2026-01', null, { cancelada: true, observacao: 'Registro cancelado: permanece no histórico e não conta' });
execucao('ex-0005', 'eq-demo-004', 'PRL-01', '2026-01', null, { observacao: '=SOMA(A1:A2) texto de teste, não é fórmula' });
execucao('ex-0006', 'eq-demo-004', 'PRL-02', '2026-01', null, { responsavelId: 'pes-b', observacao: '+ observação fictícia iniciada por sinal' });
execucao('ex-0007', 'eq-demo-004', 'PRL-03', '2026-01', null, { responsavelId: 'pes-b', observacao: '- observação fictícia iniciada por hífen' });
execucao('ex-0008', 'eq-demo-004', 'PRL-11', '2026-01', null, { observacao: '@ observação fictícia iniciada por arroba' });
execucao('ex-0009', 'eq-demo-003', 'MOT-01', null, '2026-01-20', { origem: 'legado', responsavelId: '', observacao: 'Marcação antiga migrada sem vínculo' });
execucao('ex-0010', 'eq-demo-002', 'BCF-02', '2026-02', null, {});
execucao('ex-0011', 'eq-demo-009', 'BCF-01', null, '2025-10-20', { tag: 'UTL-BCF-002', descricao: 'Verificar vazamento na vedação (selo mecânico ou gaxeta)', observacao: 'Ativo removido depois: histórico preservado' });
gestao.historico = historico;

gestao.falhas = [
  { id: 'fa-0001', equipamentoId: 'eq-demo-001', tag: 'UTL-CMP-001', data: '2026-02-10', sintoma: 'Sintoma fictício de demonstração', causa: 'A definir', acao: 'Ação fictícia de demonstração', horasParada: 1.5, peca: '', responsavelId: 'pes-b' },
  { id: 'fa-0002', equipamentoId: 'eq-demo-004', tag: 'PRD-PRL-001', data: '2026-03-05', sintoma: '@ sintoma fictício iniciado por arroba', causa: '', acao: '', horasParada: null, peca: '', responsavelId: '' },
  { id: 'fa-0003', equipamentoId: 'eq-demo-009', tag: 'UTL-BCF-002', data: '2025-10-15', sintoma: 'Registro fictício de ativo removido', causa: '', acao: '', horasParada: 0, peca: 'Peça fictícia', responsavelId: 'pes-a' },
];

if (!validarGestao(gestao)) throw new Error('A gestão de demonstração não passou em validarGestao().');

const resumo = resumoMensal(dados, gestao, ANO);
process.stdout.write(JSON.stringify({
  aviso: 'Dados fictícios gerados para demonstração; não são exportação do app.',
  inicio: INICIO, ano: ANO, biblioteca: dados.biblioteca, geradoEm: textoData(new Date()),
  equipamentos: dados.equipamentos, plano: dados.plano,
  cronograma: dados.cronograma.map(({ equipamentoId, tarefaId, semanas, vezesAno }) => ({ equipamentoId, tarefaId, semanas, vezesAno })),
  ocorrencias, gestao, resumoMensal: resumo,
  criticidade: Object.fromEntries(Object.entries(gestao.criticidade.notas).map(([k, n]) => [k, criticidadeAtivo(n, gestao.criticidade.limites)])),
}, null, 1));
