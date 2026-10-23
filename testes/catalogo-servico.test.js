import { beforeEach, describe, expect, it, vi } from 'vitest';

const mock = vi.hoisted(() => ({ cliente: null, criar: vi.fn() }));
vi.mock('@supabase/supabase-js', () => ({ createClient: (...args) => { mock.criar(...args); return mock.cliente; } }));
beforeEach(() => {
  vi.resetModules(); vi.clearAllMocks();
  vi.stubEnv('VITE_SUPABASE_URL', 'https://exemplo.supabase.co');
  vi.stubEnv('VITE_SUPABASE_ANON_KEY', 'sb_publishable_1234567890abcdefghijkl');
});
describe('Cliente do catálogo e permissões solicitadas', () => {
  it('consulta somente aprovados por padrão e pagina sem escrever dados locais', async () => {
    const q = {}; for (const m of ['select', 'order', 'eq', 'ilike']) q[m] = vi.fn(() => q);
    q.range = vi.fn(async () => ({ data: [], error: null }));
    mock.cliente = { from: vi.fn(() => q) };
    const { listarCatalogo } = await import('../src/servicos/catalogo.js');
    await listarCatalogo({ pagina: 2, busca: 'Motor' });
    expect(mock.cliente.from).toHaveBeenCalledWith('catalogo_modelos');
    expect(q.eq).toHaveBeenCalledWith('situacao', 'aprovado');
    expect(q.range).toHaveBeenCalledWith(40, 59);
  });
  it('usa a função de moderador real e exige conta para filtrar modelos próprios', async () => {
    mock.cliente = { rpc: vi.fn(async () => ({ data: true, error: null })), from: vi.fn(() => ({ select: () => ({ order: () => ({}) }) })) };
    const { moderadorCatalogo, listarCatalogo } = await import('../src/servicos/catalogo.js');
    expect(await moderadorCatalogo()).toBe(true);
    expect(mock.cliente.rpc).toHaveBeenCalledWith('catalogo_e_moderador');
    await expect(listarCatalogo({ meus: true })).rejects.toThrow('Entre na sua conta');
  });
  it('não recebe autor ou situação no salvamento e usa saída local da sessão', async () => {
    mock.cliente = { rpc: vi.fn(async () => ({ data: 'id-ficticio', error: null })), auth: { signOut: vi.fn(async () => ({ error: null })) } };
    const { salvarModelo, sairCatalogo } = await import('../src/servicos/catalogo.js');
    const { modeloVazio } = await import('../src/logica/catalogo.js');
    const dados = { ...modeloVazio(), titulo: 'Exemplo', descricao: 'Fictício' };
    await salvarModelo(dados);
    expect(mock.cliente.rpc).toHaveBeenCalledWith('catalogo_salvar', { p_dados: dados, p_id: null, p_original_id: null });
    await sairCatalogo();
    expect(mock.cliente.auth.signOut).toHaveBeenCalledWith({ scope: 'local' });
  });
  it('não expõe detalhes internos de erro do provedor', async () => {
    mock.cliente = { rpc: vi.fn(async () => ({ error: { code: 'XX000', message: 'detalhe interno' } })) };
    const { moderadorCatalogo } = await import('../src/servicos/catalogo.js');
    await expect(moderadorCatalogo()).rejects.toThrow('Não foi possível');
    await expect(moderadorCatalogo()).rejects.not.toThrow('detalhe interno');
  });
});
