# Banco do catálogo colaborativo

A migração cria somente o catálogo de modelos compartilháveis. Equipamentos específicos, TAGs,
registros de falhas, pessoas da fábrica e backups locais não entram neste banco.

## Aplicação

No SQL Editor do projeto Supabase, execute `migrations/202610230001_catalogo.sql` uma única vez.
Habilite a autenticação por e-mail no painel e configure os endereços de retorno do aplicativo.
Depois que o mantenedor criar sua conta, copie o UUID dela em Authentication → Users e execute,
como administrador, substituindo o UUID fictício:

```sql
insert into public.catalogo_moderadores(user_id)
values ('00000000-0000-0000-0000-000000000000');
```

Não conceda `service_role` ao navegador. As chaves públicas do Supabase não permitem escrita
direta: autores e moderadores usam as funções abaixo, com identidade conferida no banco.

## Contratos

- Tabela `catalogo_modelos`: `id`, `autor_id`, `original_id`, `dados`, `situacao`, `motivo`,
  `revisado_por`, `criado_em`, `atualizado_em`.
- `dados` contém exatamente `titulo`, `tipo_base`, `fabricante`, `modelo`, `descricao`,
  `caracteristicas`, `apelido` e `tarefas`. Textos opcionais são strings vazias; tarefas podem ser `[]`.
- `tipo_base`: `motor_eletrico`, `compressor_ar`, `bomba_centrifuga`, `ponte_rolante` ou `outro`.
- Cada tarefa contém exatamente `descricao`, `periodicidade`, `especialidade`, `duracao_horas`,
  `seguranca`, `origem`, `versao` e `observacao`.
- `catalogo_salvar(p_dados jsonb, p_id uuid = null, p_original_id uuid = null) → uuid`.
- `catalogo_enviar(p_id uuid) → void`.
- `catalogo_decidir(p_id uuid, p_aprovar boolean, p_motivo text = '') → void`.
- `catalogo_retirar(p_id uuid) → void`: pendente volta a rascunho; demais ficam arquivados.
- `catalogo_e_moderador() → boolean`: informa somente se a conta atual é moderadora.

Anônimos leem apenas aprovados. Autores leem também seus modelos. Moderadores veem a fila.
Modelos aprovados não podem ser editados: uma alteração cria nova versão e nova revisão.
Arquivar uma versão pública não altera as cópias locais que outras pessoas já fizeram.
Há limite de 100 modelos ativos e cinco envios pendentes por conta. Isso não é teto de custos
nem substitui limites de autenticação, monitoramento e configuração da conta do provedor.

## Teste em Postgres descartável

Com Node.js e Docker local disponíveis, execute na raiz do repositório:

```sh
docker pull postgres:17-alpine@sha256:eee6c6e1b0894fa4fe0075eb054af9fd1cf39a35321c2d4110626cfe506411fb
node scripts/verificar-catalogo-banco.mjs
```

O runner exige essa imagem previamente baixada, cria um container sem rede nem portas
publicadas, monta `supabase` somente para leitura e remove o container e seus volumes ao
terminar. A autenticação `trust` é exclusiva desse banco descartável, sem dados reais.
O comando termina com erro se Docker, inicialização, SQL ou limpeza falharem.

`testes/catalogo.sql` exige um banco vazio e recusa bancos com `auth.users`. Ele cria um substituto
mínimo da autenticação e carrega a migração. **Nunca executar esse teste em projeto Supabase real.**

```sh
psql -v ON_ERROR_STOP=1 -f supabase/testes/catalogo.sql
```

O teste usa três identidades fictícias, troca os papéis `anon`/`authenticated`, verifica RLS e
chama as funções reais. Os dados de teste são revertidos ao terminar. O esquema permanece
no banco descartável para inspeção. Validação de login por e-mail ainda exige projeto configurado.
