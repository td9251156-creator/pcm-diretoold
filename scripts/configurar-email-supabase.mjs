// Ferramenta administrativa local. Nunca importar no app nem usar variáveis VITE.
import { pathToFileURL } from 'node:url';

export function configuracaoSMTP(env) {
  const obter = nome => typeof env[nome] === 'string' ? env[nome].trim() : '';
  const projeto = obter('SUPABASE_PROJECT_REF');
  const host = obter('SMTP_HOST');
  const porta = obter('SMTP_PORT');
  const email = obter('SMTP_FROM_EMAIL');
  const nome = obter('SMTP_FROM_NAME');
  const usuario = obter('SMTP_USER');
  const senha = env.SMTP_PASS;
  if (!/^[a-z0-9]{20}$/.test(projeto)) throw new Error('Confira SUPABASE_PROJECT_REF.');
  if (!/^(?=.{1,253}$)[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/i.test(host) || !host.includes('.')) throw new Error('Informe o host SMTP do provedor, sem protocolo ou caminho.');
  if (!['465', '587', '2525'].includes(porta)) throw new Error('Use uma porta SMTP segura suportada pelo provedor: 465, 587 ou 2525.');
  if (!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)) throw new Error('Informe o e-mail de remetente verificado no provedor.');
  if (!nome || nome.length > 100 || !usuario || usuario.length > 254 || typeof senha !== 'string' || !senha.trim() || /[\r\n]/.test(nome + usuario + senha)) throw new Error('Preencha nome, usuário e senha SMTP válidos no arquivo privado.');
  return {
    projeto,
    dados: { smtp_host: host, smtp_port: porta, smtp_user: usuario, smtp_pass: senha,
      smtp_admin_email: email, smtp_sender_name: nome },
  };
}

export async function configurarEmail(env, { aplicar = false, fetcher = fetch } = {}) {
  const { projeto, dados } = configuracaoSMTP(env);
  if (!aplicar) return 'Configuração SMTP válida. Simulação: nenhuma alteração ou envio de e-mail realizado.';
  const token = env.SUPABASE_ACCESS_TOKEN || '';
  if (!/^sbp_[A-Za-z0-9_-]+$/.test(token)) throw new Error('Para aplicar, configure SUPABASE_ACCESS_TOKEN privado. A chave publishable não serve para administração.');
  let resposta;
  try {
    resposta = await fetcher(`https://api.supabase.com/v1/projects/${projeto}/config/auth`, {
      method: 'PATCH', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(dados), signal: AbortSignal.timeout(20000),
    });
  } catch {
    throw new Error('Não foi possível acessar a administração do Supabase. Confira a conexão e tente novamente.');
  }
  // Não imprimir corpo da resposta: a configuração administrativa pode conter credenciais.
  if (!resposta.ok) throw new Error(`Supabase recusou a configuração SMTP (HTTP ${resposta.status}). Confira permissões do token e dados do provedor.`);
  return 'Configuração SMTP aplicada. Teste agora um link de acesso no app; este comando não envia e-mail nem comprova entrega.';
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  if (process.argv.slice(2).some(a => a !== '--aplicar')) {
    console.error('Uso: node --env-file=.env.smtp.local scripts/configurar-email-supabase.mjs [--aplicar]');
    process.exitCode = 1;
  } else {
    try { console.log(await configurarEmail(process.env, { aplicar: process.argv.includes('--aplicar') })); }
    catch (erro) { console.error(erro.message); process.exitCode = 1; }
  }
}
