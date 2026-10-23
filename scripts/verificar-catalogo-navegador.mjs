// Testa a interface com respostas fictícias. Permissões reais são verificadas no teste SQL.
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build, preview } from 'vite';
import { executarComRecursos } from './navegador.mjs';

const ferramenta = process.env.PCM_PLAYWRIGHT || new URL('../ferramentas/navegador/node_modules/playwright/index.mjs', import.meta.url).href;
const { chromium } = await import(ferramenta);
const raiz = fileURLToPath(new URL('../', import.meta.url));
const pasta = await mkdtemp(path.join(tmpdir(), 'pcm-catalogo-'));
const origem = 'https://catalogo-exemplo.supabase.co';
const autor = '10000000-0000-0000-0000-000000000001';
const moderador = '30000000-0000-0000-0000-000000000003';
const tituloPublico = 'Motor <img src=x onerror="window.injecao=true">';
const dados = titulo => ({ titulo, tipo_base: 'motor_eletrico', fabricante: 'Fabricante Exemplo', modelo: 'EX-1', descricao: 'Modelo fictício para conferência', caracteristicas: '', apelido: 'Colaborador', tarefas: [{ descricao: 'Inspeção de referência fictícia', periodicidade: 'Anual', especialidade: 'Elétrica', duracao_horas: 0.5, seguranca: true, origem: 'base genérica a validar com manual do fabricante', versao: '1', observacao: '' }] });
const registros = [{ id: '40000000-0000-0000-0000-000000000004', autor_id: autor, original_id: null, dados: dados(tituloPublico), situacao: 'aprovado', motivo: '', criado_em: '2026-10-01T00:00:00Z', atualizado_em: '2026-10-01T00:00:00Z' }];
const chamadas = [];
let atrasarConsulta = false;
const jwt = id => [Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url'), Buffer.from(JSON.stringify({ sub: id, role: 'authenticated', exp: Math.floor(Date.now() / 1000) + 3600 })).toString('base64url'), 'assinatura-ficticia'].join('.');

async function contexto(browser, identidade = null) {
  const c = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'block' });
  c.setDefaultTimeout(15000);
  if (identidade) {
    const user = { id: identidade, email: 'pessoa@example.invalid', aud: 'authenticated', role: 'authenticated', app_metadata: { provider: 'email' }, user_metadata: {}, created_at: '2026-10-01T00:00:00Z' };
    await c.addInitScript(({ user, token }) => {
      localStorage.setItem('sb-catalogo-exemplo-auth-token', JSON.stringify({ access_token: token, refresh_token: 'refresh-ficticio', expires_in: 3600, expires_at: Math.floor(Date.now() / 1000) + 3600, token_type: 'bearer', user }));
    }, { user, token: jwt(identidade) });
  }
  await c.route('**/*', async route => {
    const req = route.request(); const u = new URL(req.url());
    if (u.origin === 'http://127.0.0.1:4176') return route.continue();
    assert.equal(u.origin, origem, 'O teste tentou acessar um serviço não simulado');
    const corpo = req.postDataJSON(); chamadas.push({ caminho: u.pathname, corpo });
    let resposta = null;
    if (u.pathname === '/rest/v1/catalogo_modelos') {
      if (atrasarConsulta) await new Promise(resolve => setTimeout(resolve, 300));
      resposta = registros.filter(r => (!u.searchParams.has('situacao') || u.searchParams.get('situacao') === 'eq.' + r.situacao) && (!u.searchParams.has('autor_id') || u.searchParams.get('autor_id') === 'eq.' + r.autor_id));
    } else if (u.pathname === '/rest/v1/rpc/catalogo_e_moderador') resposta = identidade === moderador;
    else if (u.pathname === '/rest/v1/rpc/catalogo_salvar') {
      const id = corpo.p_id || '50000000-0000-0000-0000-000000000005';
      const anterior = registros.find(r => r.id === id);
      if (anterior) anterior.dados = corpo.p_dados;
      else registros.push({ id, autor_id: identidade, original_id: corpo.p_original_id, dados: corpo.p_dados, situacao: 'rascunho', motivo: '' });
      resposta = id;
    } else if (u.pathname === '/rest/v1/rpc/catalogo_enviar') registros.find(r => r.id === corpo.p_id).situacao = 'pendente';
    else if (u.pathname === '/rest/v1/rpc/catalogo_decidir') {
      const r = registros.find(r => r.id === corpo.p_id); r.situacao = corpo.p_aprovar ? 'aprovado' : 'rejeitado'; r.motivo = corpo.p_motivo;
    } else if (u.pathname === '/rest/v1/rpc/catalogo_retirar') registros.find(r => r.id === corpo.p_id).situacao = 'arquivado';
    else if (u.pathname === '/auth/v1/otp' || u.pathname === '/auth/v1/logout') resposta = {};
    else throw new Error('Endpoint não previsto no teste: ' + u.pathname);
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(resposta) });
  });
  return c;
}

const envAnterior = { url: process.env.VITE_SUPABASE_URL, chave: process.env.VITE_SUPABASE_ANON_KEY };
try {
  // Configuração pública fictícia usada apenas neste build temporário, nunca em dist/.
  process.env.VITE_SUPABASE_URL = origem;
  process.env.VITE_SUPABASE_ANON_KEY = 'sb_publishable_1234567890abcdefghijkl';
  await build({ root: raiz, build: { outDir: pasta, emptyOutDir: true }, logLevel: 'warn' });
  await executarComRecursos({
    criarServidor: () => preview({ root: raiz, build: { outDir: pasta }, preview: { host: '127.0.0.1', port: 4176, strictPort: true } }),
    criarNavegador: () => chromium.launch({ executablePath: process.env.PCM_CHROMIUM || undefined, args: process.env.PCM_SEM_SANDBOX === '1' ? ['--no-sandbox'] : [] }),
    executar: async ({ navegador }) => {
      const erros = [];
      const publico = await contexto(navegador); const p = await publico.newPage(); p.on('pageerror', e => erros.push(e.message));
      await p.goto('http://127.0.0.1:4176/#catalogo');
      await p.getByRole('heading', { name: tituloPublico, exact: true }).waitFor();
      assert.equal(await p.locator('article img').count(), 0, 'Conteúdo do modelo executado como HTML');
      assert.equal(await p.evaluate(() => window.injecao), undefined);
      assert.equal(await p.getByRole('button', { name: 'Criar modelo', exact: true }).count(), 0);
      await p.getByLabel('E-mail de acesso').fill('pessoa@example.invalid');
      await p.getByRole('button', { name: 'Enviar link de acesso', exact: true }).click();
      await p.waitForFunction(() => document.body.textContent.includes('Se o envio foi autorizado'));
      assert.ok(chamadas.some(c => c.caminho === '/auth/v1/otp' && c.corpo.email === 'pessoa@example.invalid'));
      const bibliotecaAntes = await p.evaluate(() => localStorage.getItem('pcm-direto:biblioteca:v1'));
      await p.getByRole('button', { name: 'Usar cadastro neste aparelho' }).click();
      await p.getByLabel('Setor (2 a 4 letras ou números)').fill('UTL');
      await p.getByRole('button', { name: 'Adicionar aos meus equipamentos' }).click();
      await p.waitForURL('**/#equipamentos');
      const armazenado = await p.evaluate(() => ({ biblioteca: localStorage.getItem('pcm-direto:biblioteca:v1'), dados: JSON.parse(localStorage.getItem('pcm-direto:rascunho:v1')) }));
      assert.equal(armazenado.biblioteca, bibliotecaAntes, 'Modelo remoto alterou biblioteca local');
      const ativo = armazenado.dados.equipamentos.find(e => e.descricao === tituloPublico);
      assert.ok(ativo?.id); assert.equal(ativo.tarefas, undefined);
      await publico.close();

      const usuario = await contexto(navegador, autor); const a = await usuario.newPage(); a.on('pageerror', e => erros.push(e.message));
      a.on('dialog', d => d.accept());
      await a.goto('http://127.0.0.1:4176/#catalogo');
      await a.getByRole('button', { name: 'Criar modelo', exact: true }).click();
      await a.getByLabel('Título público', { exact: true }).fill('Bomba fictícia contribuída');
      await a.getByLabel('Descrição pública', { exact: true }).fill('Conteúdo de demonstração autorizado');
      await a.getByRole('button', { name: 'Salvar rascunho online' }).click();
      await a.getByRole('heading', { name: 'Bomba fictícia contribuída', exact: true }).waitFor();
      assert.equal(registros.at(-1).situacao, 'rascunho');
      await a.getByRole('button', { name: 'Salvar e enviar para revisão' }).click();
      await a.waitForFunction(() => document.body.textContent.includes('Confirme a autorização'));
      assert.equal(registros.at(-1).situacao, 'rascunho', 'Enviou modelo sem consentimento');
      await a.locator('[name="consentimento"]').check();
      await a.getByRole('button', { name: 'Salvar e enviar para revisão' }).click();
      await a.waitForFunction(() => document.body.textContent.includes('Modelo enviado para revisão'));
      assert.equal(registros.at(-1).situacao, 'pendente');
      assert.equal(await a.getByRole('button', { name: 'Fila de revisão', exact: true }).count(), 0);
      await usuario.close();

      const revisao = await contexto(navegador, moderador); const m = await revisao.newPage(); m.on('pageerror', e => erros.push(e.message)); m.on('dialog', d => d.accept());
      await m.goto('http://127.0.0.1:4176/#catalogo');
      await m.getByRole('button', { name: 'Fila de revisão', exact: true }).click();
      await m.getByRole('heading', { name: 'Bomba fictícia contribuída', exact: true }).waitFor();
      await m.getByRole('button', { name: 'Aprovar publicação', exact: true }).click();
      await m.waitForFunction(() => document.body.textContent.includes('Modelo publicado após revisão'));
      assert.equal(registros.at(-1).situacao, 'aprovado');
      atrasarConsulta = true;
      await m.getByRole('button', { name: 'Catálogo público', exact: true }).click();
      await m.getByRole('link', { name: '1. Início', exact: true }).click();
      await m.getByRole('heading', { name: 'Plano de manutenção preventiva a partir da sua lista de equipamentos' }).waitFor();
      await m.waitForTimeout(500);
      assert.equal(await m.getByRole('heading', { name: 'Catálogo colaborativo de máquinas' }).count(), 0, 'Resposta assíncrona redesenhou outra tela');
      assert.deepEqual(erros, []);
      assert.ok(chamadas.filter(c => c.caminho.endsWith('/catalogo_salvar')).every(c => !Object.hasOwn(c.corpo.p_dados, 'gestao') && !Object.hasOwn(c.corpo.p_dados, 'autor_id')));
      await revisao.close();
      console.log('Catálogo no Chromium: público, escape de HTML, OTP simulado, cópia local segura, rascunho, consentimento, envio, revisão e navegação aprovados. Login real e autorização são conferidos separadamente.');
    },
  });
} finally {
  if (envAnterior.url === undefined) delete process.env.VITE_SUPABASE_URL; else process.env.VITE_SUPABASE_URL = envAnterior.url;
  if (envAnterior.chave === undefined) delete process.env.VITE_SUPABASE_ANON_KEY; else process.env.VITE_SUPABASE_ANON_KEY = envAnterior.chave;
  await rm(pasta, { recursive: true, force: true });
}
