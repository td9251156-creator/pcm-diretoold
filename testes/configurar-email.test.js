import { describe, it, expect, vi } from 'vitest';
import { configurarEmail } from '../scripts/configurar-email-supabase.mjs';

const exemplo = () => ({ SUPABASE_PROJECT_REF: 'abcdefghijklmnopqrst', SMTP_HOST: 'smtp.exemplo.com', SMTP_PORT: '465', SMTP_USER: 'exemplo', SMTP_PASS: 'senha-ficticia', SMTP_FROM_EMAIL: 'acesso@exemplo.com', SMTP_FROM_NAME: 'PCM Direto' });
describe('Configuração administrativa de e-mail', () => {
  it('simula sem token, rede ou vazamento de senha', async () => {
    const fetcher = vi.fn();
    const resultado = await configurarEmail(exemplo(), { fetcher });
    expect(fetcher).not.toHaveBeenCalled();
    expect(resultado).toContain('Simulação');
    expect(resultado).not.toContain('senha-ficticia');
  });
  it('recusa chave pública para administração antes de acessar a rede', async () => {
    const fetcher = vi.fn();
    await expect(configurarEmail({ ...exemplo(), SUPABASE_ACCESS_TOKEN: 'sb_publishable_ficticia' }, { aplicar: true, fetcher })).rejects.toThrow('publishable');
    expect(fetcher).not.toHaveBeenCalled();
  });
  it('envia somente campos SMTP e não altera outras opções de autenticação', async () => {
    const fetcher = vi.fn(async () => ({ ok: true }));
    await configurarEmail({ ...exemplo(), SUPABASE_ACCESS_TOKEN: 'sbp_TOKEN_FICTICIO' }, { aplicar: true, fetcher });
    const [url, opcoes] = fetcher.mock.calls[0];
    expect(url).toBe('https://api.supabase.com/v1/projects/abcdefghijklmnopqrst/config/auth');
    expect(opcoes.method).toBe('PATCH');
    expect(Object.keys(JSON.parse(opcoes.body)).sort()).toEqual(['smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_admin_email', 'smtp_sender_name'].sort());
  });
  it('oculta corpo de resposta administrativo e recusa configuração incompleta', async () => {
    const json = vi.fn();
    await expect(configurarEmail({ ...exemplo(), SUPABASE_ACCESS_TOKEN: 'sbp_TOKEN_FICTICIO' }, { aplicar: true, fetcher: async () => ({ ok: false, status: 403, json }) })).rejects.toThrow('HTTP 403');
    expect(json).not.toHaveBeenCalled();
    await expect(configurarEmail({ ...exemplo(), SMTP_PASS: '' })).rejects.toThrow('Preencha');
  });
});
