# Finalizar a ativação — passos do mantenedor

Banco instalado e consulta pública confirmada em 22/10/2026. A checagem automática do Actions
confere a conexão usando as Repository Variables sem imprimir a chave ou dados do catálogo.
Ela não comprova entrega de e-mail, SMTP ou URLs de retorno, que não são públicos.

## 1. Permitir o retorno do login

Abra https://supabase.com/dashboard/project/yzcjksiowgcncpxttoxt/auth/url-configuration

- Site URL: `https://td9251156-creator.github.io/pcm-direto/`
- Redirect URLs: adicione `https://td9251156-creator.github.io/pcm-direto/` e
  `https://td9251156-creator.github.io/pcm-direto/#catalogo`.
- Para testar no ambiente local, adicione também o endereço exato informado pelo Vite,
  com e sem `#catalogo`. Não use um domínio genérico ou curinga de terceiros.

## 2. Configurar o envio de e-mail

Abra Authentication → Email/SMTP no painel do Supabase e configure seu provedor de envio.
O envio padrão permite apenas endereços autorizados da equipe, com limites baixos.
Não abra inscrições públicas dependendo desse envio padrão. As credenciais de SMTP ficam
somente no painel do Supabase; nunca nas variáveis VITE, repositório ou chat.
Para um primeiro teste restrito, use o e-mail autorizado da sua equipe no projeto.

## 3. Primeiro acesso e moderação

Após a interface ser integrada e publicada, abra `#catalogo`, peça o link de acesso e abra-o
no mesmo navegador. Em Authentication → Users, localize sua conta e copie seu User UID.
No SQL Editor, execute uma vez, substituindo o exemplo pelo UID da sua conta:

```sql
insert into public.catalogo_moderadores(user_id)
values ('COLE-AQUI-O-USER-UID')
on conflict (user_id) do nothing;
```

Somente contas de confiança devem receber essa permissão. Reabra a tela Catálogo para aparecer
a Fila de revisão. Não é necessário compartilhar seu UID, senha ou token de sessão no chat.

## 4. Conferência final

Crie um modelo fictício, salve rascunho, envie à revisão e aprove na fila. Em uma janela
sem login, confira que aparece somente o aprovado. Use o cadastro no plano local e confirme
que tarefas do catálogo não substituem a biblioteca. Depois arquive o modelo fictício.
Teste também uma segunda conta sem acesso de moderação e a saída da sessão.

Os PRs #32 (interface) e #33 (catálogo) permanecem em revisão, sem merge nesta etapa.
As Repository Variables entram no site somente após novo build/publicação. Não refaça a
migração em um banco já instalado. Sentry e resgate do Copilot são opcionais e não bloqueiam o catálogo.
