# Catálogo colaborativo de modelos de máquinas

## Decisões do mantenedor

O catálogo compartilha modelos reutilizáveis, não o inventário particular de uma fábrica.
Consulta pública; criar e compartilhar exige conta. A publicação depende da revisão do mantenedor.
A interface de gestão do PR #32 é a base desta proposta; ela não é integrada automaticamente.
Nenhum template Excel/Word novo é criado. Os modelos de documentos continuam a cargo do mantenedor.

## Arquitetura e dependência

Frontend Vite/JavaScript existente, hospedável no GitHub Pages. Banco PostgreSQL e login pelo
Supabase, com permissões RLS e operações autorizadas no banco, não somente botões escondidos.
Nova dependência: @supabase/supabase-js 2.118.0, MIT, para sessão, login e cliente de dados.
Nenhum serviço de IA é necessário. Começar com os recursos gratuitos disponíveis na conta do
mantenedor, sujeitos aos limites e condições do provedor; não há contratação ou recarga automática.
Código e testes podem ser preparados aqui; a ativação real exige um projeto Supabase do mantenedor.

## O que é compartilhado

Título, categoria base, fabricante/modelo, descrição, características, apelido público opcional e
lista opcional de tarefas com frequência, especialidade, duração, segurança, origem e versão.
Não enviar TAGs da fábrica, organização, pessoas, falhas, execução ou backup para o catálogo.
O formulário de contribuição é separado dos dados da gestão. Não publicar manuais de empresas,
dados pessoais ou conteúdo sem autorização. Não há upload de arquivos nesta primeira versão.

Ao usar um modelo público, o usuário escolhe seu setor e tipo local e cria um equipamento neste
aparelho. O plano continua usando a biblioteca local validada; tarefas da contribuição ficam
visíveis como referência e não substituem automaticamente tarefas ou proteções de segurança.
Uma revisão futura pode definir importação técnica de tarefas, com comparação e proteção explícita.

## Publicação e versões

1. Visitante consulta e busca modelos aprovados.
2. Conta autenticada cria e edita seus rascunhos online.
3. Autor envia para revisão; o conteúdo pendente não fica público.
4. Moderador aprova ou rejeita com motivo. O autor não pode se promover a moderador.
5. Conteúdo aprovado não pode ser editado diretamente; uma nova versão volta como rascunho.
6. Autor pode retirar a publicação ou a proposta. Arquivo local criado a partir do modelo não é apagado.

Nenhuma revisão certifica conformidade ou dispensa a verificação do manual do fabricante.
Informações de normas precisam de origem oficial, versão e data. Use base genérica a validar
com manual do fabricante quando essa for a origem efetiva, sem inventar requisitos técnicos.

## Permissões e verificação

Visitantes leem somente aprovados; contas leem também seus próprios registros; moderadores veem
a fila completa. Escritas são feitas por funções que conferem a identidade autenticada e o estado
da proposta. Autor, status e parecer não vêm de campos editáveis enviados pelo navegador.
Chave secret/service_role nunca pertence ao frontend, ao repositório ou ao chat.
Chave pública não substitui regras do banco: testar permissões antes de liberar o projeto.

Testes: validação dos campos, rascunho privado, autenticação, revisão e rejeição, retirada,
versionamento sem alterar aprovado, usuário não editar proposta alheia nem se promover,
malformações e manutenção dos fluxos locais/offline. Banco testado com dados fictícios em Postgres
isolado; login real e e-mail de acesso precisam de validação no projeto efetivamente conectado.


## Entrega e ativação

Consulte [ATIVACAO-STUDENT.md](ATIVACAO-STUDENT.md) para criar o projeto e conectar o app.
O código sem configuração mostra indisponibilidade online, sem simular cadastros públicos.
Os testes de navegador conectados interceptam um provedor fictício; não comprovam entrega real
de e-mails. As permissões usam testes separados no PostgreSQL real descartável.
Prompt para documentos externos: [PROMPT-CLAUDE-TEMPLATES.md](PROMPT-CLAUDE-TEMPLATES.md).
