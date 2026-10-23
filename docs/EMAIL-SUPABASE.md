# Envio de e-mail do PCM Direto

O app já pede o link por `signInWithOtp` do Supabase. O Supabase entrega esse e-mail pelo
SMTP configurado no projeto. A senha SMTP não deve entrar no JavaScript, nas Repository
Variables VITE ou no chat. Não é necessário criar um servidor de e-mail no app.

## Caminho mais simples: configurar no painel

1. Crie sua conta em https://resend.com e adicione um domínio que você controla.
   Copie para o DNS os registros solicitados e espere o domínio aparecer como verificado.
   Se não tiver domínio, use outro provedor SMTP que autorize seu remetente. O domínio
   `github.io` do site não é seu domínio de envio e não pode ser verificado por você.
2. No Resend, crie uma chave apropriada para envio e guarde-a em seu gerenciador de senhas.
   Confira os limites do plano escolhido; este roteiro não contrata serviço pago.
3. Abra https://supabase.com/dashboard/project/yzcjksiowgcncpxttoxt/auth/smtp
   (se o endereço mudar, procure Authentication → Email → SMTP Settings).
4. Habilite **Custom SMTP** e preencha:

| Campo | Valor |
|---|---|
| Sender email | Um endereço no seu domínio verificado, por exemplo `acesso@seu-dominio.com` |
| Sender name | `PCM Direto` |
| Host | `smtp.resend.com` |
| Port | `465` |
| Username | `resend` |
| Password | A chave de envio criada no Resend |

5. Salve. Confira limites de envio e proteção contra abuso no Supabase e no provedor.
   Não use o endereço de testes do provedor para liberar cadastro público.
6. Configure as URLs de retorno conforme [FINALIZAR-ATIVACAO.md](FINALIZAR-ATIVACAO.md).
   Quando a interface estiver publicada, peça um link no Catálogo e abra-o no mesmo navegador.
   Confira caixa de entrada e spam. Teste também um usuário externo autorizado para o teste.

**Sem domínio ou credenciais SMTP disponíveis, o envio público ainda não pode ser ativado.**
O remetente não pode ser inventado. O envio padrão Supabase continua restrito à equipe.
Testmail recebe mensagens de teste; não substitui o provedor de envio.

## Alternativa: aplicar a configuração por código

O script pronto usa a API administrativa oficial do Supabase. Este caminho exige um token
administrativo adicional; o painel acima é mais simples para a primeira configuração.
Requisitos: Node.js 24, credenciais SMTP válidas e acesso ao projeto Supabase.

1. Copie `scripts/configuracao-smtp.env.example` para `.env.smtp.local` na raiz.
2. Preencha os campos do seu provedor. O exemplo está preparado para Resend.
3. Valide sem alterar o projeto:

```sh
node --env-file=.env.smtp.local scripts/configurar-email-supabase.mjs
```

4. Para aplicar via código, obtenha um token pessoal em
   https://supabase.com/dashboard/account/tokens com acesso administrativo ao projeto.
   Preencha `SUPABASE_ACCESS_TOKEN` somente no arquivo privado e execute:

```sh
node --env-file=.env.smtp.local scripts/configurar-email-supabase.mjs --aplicar
```

Em ambientes que usam proxy de saída, acrescente `--use-env-proxy` ao comando Node.
Não envie o arquivo preenchido a ninguém nem o inclua em ZIPs. Revogue o token administrativo
temporário após configurar se ele não tiver outra finalidade.

O script altera somente os seis campos SMTP; não muda permissões, URLs ou outros provedores.
Não imprime a senha, token ou resposta administrativa. Sem `--aplicar`, não faz requisições.
Sucesso na API não prova entrega: o teste com link real continua obrigatório.

## Modelos de e-mail

Preserve os templates padrão do Supabase inicialmente. Eles já incluem o link gerado para cada
pedido. Não monte links manualmente nem coloque a chave SMTP ou a chave do projeto no HTML.
Depois de validar entrega e retorno, é possível personalizar assunto e apresentação em português.

Fontes: https://supabase.com/docs/guides/auth/auth-smtp · https://resend.com/docs/send-with-supabase-smtp
