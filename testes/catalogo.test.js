import { describe, it, expect } from 'vitest';
import { modeloVazio, tarefaCatalogoVazia, validarModeloCatalogo, configuracaoCatalogo, dadosEquipamentoDoModelo } from '../src/logica/catalogo.js';

const modelo = () => ({ ...modeloVazio(), titulo: 'Motor Exemplo', descricao: 'Modelo fictício' });
const env = chave => ({ VITE_SUPABASE_URL: 'https://exemplo.supabase.co', VITE_SUPABASE_ANON_KEY: chave });
describe('Contrato público do catálogo', () => {
  it('aceita modelo sem tarefas e exige origem e versão das tarefas incluídas', () => {
    expect(validarModeloCatalogo(modelo())).toEqual([]);
    const m = modelo(); m.tarefas = [{ ...tarefaCatalogoVazia(), descricao: 'Inspeção fictícia', especialidade: 'Elétrica' }];
    expect(validarModeloCatalogo(m)).toEqual([]);
    m.tarefas[0].origem = '';
    expect(validarModeloCatalogo(m)).not.toEqual([]);
  });
  it('recusa dados da fábrica, identidade e situação forjadas', () => {
    for (const campo of ['tag', 'gestao', 'autor_id', 'situacao', 'execucoes']) {
      expect(validarModeloCatalogo({ ...modelo(), [campo]: 'não enviar' })).not.toEqual([]);
    }
  });
  it('recusa tarefas inválidas e limites excedidos', () => {
    for (const alteracao of [{ duracao_horas: 0 }, { duracao_horas: Infinity }, { seguranca: 'false' }, { periodicidade: 'Nunca' }, { versao: '' }, { tag: 'FAB' }]) {
      const t = { ...tarefaCatalogoVazia(), descricao: 'Inspeção fictícia', especialidade: 'Elétrica', ...alteracao };
      expect(validarModeloCatalogo({ ...modelo(), tarefas: [t] })).not.toEqual([]);
    }
    expect(validarModeloCatalogo({ ...modelo(), titulo: 'x'.repeat(121) })).not.toEqual([]);
    expect(validarModeloCatalogo({ ...modelo(), tarefas: Array(51).fill(tarefaCatalogoVazia()) })).not.toEqual([]);
  });
  it('copia somente cadastro para o ativo local, preservando tarefas e modelo original', () => {
    const m = modelo(); const antes = structuredClone(m);
    expect(dadosEquipamentoDoModelo(m, 'UTL', 'motor_eletrico')).toEqual({ setor: 'UTL', tipo: 'motor_eletrico', descricao: 'Motor Exemplo', fabricante: '', modelo: '' });
    expect(m).toEqual(antes);
    expect(() => dadosEquipamentoDoModelo(m, '<x>', 'motor_eletrico')).toThrow();
  });
});
describe('Configuração sem segredos no frontend', () => {
  it('permite trabalhar sem catálogo e aceita chave publishable', () => {
    expect(configuracaoCatalogo().configurado).toBe(false);
    expect(configuracaoCatalogo(env('sb_publishable_1234567890abcdefghijkl')).configurado).toBe(true);
  });
  it('aceita JWT anon e recusa service_role, secret, URL insegura e configuração parcial', () => {
    const jwt = role => 'cabecalho.' + btoa(JSON.stringify({ role })) + '.assinatura';
    expect(configuracaoCatalogo(env(jwt('anon'))).configurado).toBe(true);
    for (const chave of [jwt('service_role'), 'sb_secret_1234567890abcdefghijkl', 'invalida']) {
      const c = configuracaoCatalogo(env(chave));
      expect(c.configurado).toBe(false); expect(c.erro).not.toContain(chave);
    }
    for (const url of ['http://exemplo.com', 'https://usuario:senha@exemplo.com', 'https://exemplo.com/?chave=x']) {
      expect(configuracaoCatalogo({ ...env('sb_publishable_1234567890abcdefghijkl'), VITE_SUPABASE_URL: url }).configurado).toBe(false);
    }
    expect(configuracaoCatalogo({ VITE_SUPABASE_URL: 'https://exemplo.com' }).erro).not.toBe('');
  });
});
