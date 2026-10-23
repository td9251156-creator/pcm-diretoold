// Diagnóstico somente leitura: não cria conta, não envia e-mail e não altera o banco.
import { configuracaoCatalogo } from '../src/logica/catalogo.js';

const configuracao = configuracaoCatalogo(process.env);
if (!configuracao.configurado) {
  if (configuracao.erro) throw new Error(configuracao.erro);
  console.log('Catálogo não configurado: gestão local disponível; conexão online não verificada.');
} else {
  const consultar = async caminho => {
    const resposta = await fetch(configuracao.url + caminho, {
      headers: { apikey: configuracao.chave }, signal: AbortSignal.timeout(15000),
    });
    if (!resposta.ok) throw new Error(`Falha no diagnóstico do catálogo (HTTP ${resposta.status}). Confira o projeto, a chave pública e a migração SQL.`);
    return resposta.json();
  };
  const registros = await consultar('/rest/v1/catalogo_modelos?select=id&limit=0');
  if (!Array.isArray(registros) || registros.length !== 0) throw new Error('Resposta inesperada ao consultar o catálogo.');
  const moderador = await consultar('/rest/v1/rpc/catalogo_e_moderador');
  if (moderador !== false) throw new Error('Configuração insegura: visitante foi identificado como moderador.');
  const auth = await consultar('/auth/v1/settings');
  if (auth.external?.email !== true || auth.disable_signup === true) throw new Error('Habilite login por e-mail e cadastro de usuários no Supabase.');
  console.log('Aprovado: configuração pública, tabela acessível, visitante sem moderação e cadastro por e-mail habilitado. SMTP e retorno do link exigem teste de acesso real.');
}
