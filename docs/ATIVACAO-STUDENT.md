# Ativação dos serviços e benefícios estudantis

Preparação autorizada em 22/10/2026. Não há projeto Supabase nem credenciais de Sentry
disponíveis neste ambiente. Nenhuma conta foi criada ou oferta resgatada automaticamente.
O resgate precisa acontecer na conta pessoal do mantenedor; não enviar senhas ou chaves secretas.

## Ordem de ativação

1. Abra https://education.github.com/pack com sua conta verificada. Resgate Copilot Student,
   Sentry e uma ferramenta de conferência visual (Polypane ou LambdaTest). Registre os vencimentos
   exibidos no resgate; benefícios e franquias podem mudar. Não habilite gasto excedente automático.
2. Crie um projeto Free em https://supabase.com/dashboard. Guarde a senha do banco em gerenciador
   de senhas. Escolha a região considerando os usuários e os termos de tratamento de dados.
3. Execute somente `supabase/migrations/202610230001_catalogo.sql` no SQL Editor.
   Nunca execute `supabase/testes/catalogo.sql` no projeto real: ele é exclusivo do banco descartável.
4. Em Authentication, habilite e-mail e configure Site URL como
   `https://td9251156-creator.github.io/pcm-direto/`. Autorize o retorno desse endereço e o endereço
   local de desenvolvimento. Configure SMTP próprio antes de abrir inscrições ao público.
   O envio padrão do Supabase é restrito à equipe e não atende cadastro público.
5. Em GitHub → Settings → Secrets and variables → Actions → Variables, informe
   `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY` (chave **publishable** ou **anon**).
   Essas duas configurações são públicas. Nunca usar `service_role`, `secret` ou senha.
   O build recusa configuração parcial, URL sem HTTPS e chaves privilegiadas.
6. Para desenvolvimento local, copie `.env.example` para `.env.local` e preencha as mesmas
   configurações públicas. Reinicie o Vite. Arquivos `.env*` particulares são ignorados pelo Git.
7. Entre no app e use o UUID da sua conta para cadastrar o moderador conforme `supabase/README.md`.
   Esse cadastro é feito no SQL Editor como administrador, nunca por botão no navegador.
8. Antes da liberação, teste com duas contas: criar rascunho, enviar, recusar, corrigir, aprovar,
   consultar sem login, criar nova versão e retirar. Confirme que a outra conta não acessa rascunhos.
   Confira também e-mail real, retorno do link, expiração e saída da sessão.

Sem configuração, os módulos locais continuam disponíveis; o catálogo informa que falta conexão.
Alterar Variables exige novo build/publicação para chegar ao site. Não confundir PR com publicação.
Supabase Free pode pausar por inatividade e não inclui backups automáticos: estabeleça exportações
do banco em local privado e teste restauração antes de depender dele para dados importantes.

## Benefícios complementares

- **Copilot Student:** habilitar no GitHub e no editor. Usar uma tarefa delimitada por PR com
  revisão e testes. Não disponibiliza crédito OpenAI nem execução ilimitada de agentes.
- **Sentry:** resgatar a oferta e criar projeto de navegador. A integração de código fica pendente
  do projeto/DSN e da revisão de privacidade: remover conteúdo de formulários, e-mails, identificadores
  pessoais e dados da fábrica. Não ativar replays ou captura de console por padrão. Não está integrado
  apenas por constar neste roteiro.
- **Testmail:** usar contas fictícias para testar os e-mails; não substitui SMTP de produção.
- **Polypane/LambdaTest:** validar teclado, telas pequenas e navegadores. Registrar versão e resultado.
- **Domínio:** opcional; conferir renovação e configurar HTTPS e URLs de retorno de autenticação.
- **Codespaces:** ambiente de desenvolvimento, não servidor permanente da aplicação.

Não adicionar Clerk, outro banco ou outro monitoramento junto sem uma necessidade concreta.
Supabase já fornece autenticação; duplicar fornecedores aumenta configuração e manutenção.

## Desenvolvimento contínuo sem prometer execução permanente

GitHub Actions mantém testes e publicação pelo fluxo existente. Dependabot propõe atualizações.
Codex/Copilot executam tarefas dentro das sessões e franquias disponíveis. O fluxo de IA pela API
continua pausado: não reativar agenda nem consumir o saldo OpenAI neste trabalho.
Uma tarefa bloqueada por conta, equipamento ou definição técnica não impede a próxima independente.
Não existe executor de implementação permanente ativado por este documento.

Fontes: https://education.github.com/pack · https://supabase.com/pricing ·
https://supabase.com/docs/guides/auth/auth-smtp


## Projeto criado e banco instalado

Em 22/10/2026, a consulta pública no projeto informado pelo mantenedor respondeu HTTP 200.
Tabela e função de moderação estão instaladas; visitante retorna `false` e chamadas anônimas
de salvar/aprovar foram recusadas com permissão negada, sem criar ou alterar registros.
Login por e-mail e cadastro aparecem habilitados nas configurações públicas. SMTP e URLs
de retorno não podem ser conferidos por essa chave. O build local conectado passou.
Consulte [FINALIZAR-ATIVACAO.md](FINALIZAR-ATIVACAO.md) para os poucos passos restantes.
A checagem no Actions confirma a configuração das Repository Variables sem imprimir seu valor.
