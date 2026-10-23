-- Executar SOMENTE em Postgres descartável vazio: este arquivo cria um substituto de auth.users.
-- psql -v ON_ERROR_STOP=1 -f supabase/testes/catalogo.sql
\set ON_ERROR_STOP on

-- Recusa um banco que já possua usuários de autenticação (inclusive um projeto Supabase real).
do $$ begin
  if pg_catalog.to_regclass('auth.users') is not null then
    raise exception 'Teste recusado: use banco descartável vazio, nunca um projeto com auth.users.';
  end if;
end $$;
do $$ begin
  if not exists(select 1 from pg_catalog.pg_roles where rolname='anon') then create role anon nologin; end if;
  if not exists(select 1 from pg_catalog.pg_roles where rolname='authenticated') then create role authenticated nologin; end if;
end $$;
create schema auth;
create table auth.users(id uuid primary key);
create function auth.uid() returns uuid language sql stable as $$
  select nullif(pg_catalog.current_setting('request.jwt.claim.sub',true),'')::uuid;
$$;
grant usage on schema auth to anon,authenticated;
grant execute on function auth.uid() to anon,authenticated;
\ir ../migrations/202610230001_catalogo.sql

begin;
insert into auth.users(id) values('10000000-0000-0000-0000-000000000001'),('20000000-0000-0000-0000-000000000002'),('30000000-0000-0000-0000-000000000003');
insert into public.catalogo_moderadores(user_id) values('30000000-0000-0000-0000-000000000003');
select pg_catalog.set_config('teste.dados','{"titulo":"Motor fictício","tipo_base":"motor_eletrico","fabricante":"","modelo":"Exemplo","descricao":"Modelo fictício de teste","caracteristicas":"","apelido":"Colaborador","tarefas":[]}',false);

set role anon;
select pg_catalog.set_config('request.jwt.claim.sub','',false);
do $$ begin
  if (select count(*) from public.catalogo_modelos)<>0 or public.catalogo_e_moderador() then raise exception 'Anônimo obteve dados privados.'; end if;
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb); raise exception 'Anônimo criou modelo.'; exception when insufficient_privilege then null; end;
end $$;
reset role;

set role authenticated;
select pg_catalog.set_config('request.jwt.claim.sub','10000000-0000-0000-0000-000000000001',false);
select pg_catalog.set_config('teste.id',public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb)::text,false);
do $$ begin
  if (select count(*) from public.catalogo_modelos)<>1 then raise exception 'Autor não leu seu rascunho.'; end if;
  if public.catalogo_e_moderador() or (select count(*) from public.catalogo_moderadores)<>0 then raise exception 'Autor virou moderador.'; end if;
  begin insert into public.catalogo_moderadores values(auth.uid()); raise exception 'Autopromoção permitida.'; exception when insufficient_privilege then null; end;
  begin update public.catalogo_modelos set situacao='aprovado'; raise exception 'Escrita direta permitida.'; exception when insufficient_privilege then null; end;
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb||'{"autor_id":"30000000-0000-0000-0000-000000000003"}'::jsonb); raise exception 'Autor forjado aceito.'; exception when invalid_parameter_value then null; end;
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb||'{"situacao":"aprovado"}'::jsonb); raise exception 'Estado forjado aceito.'; exception when invalid_parameter_value then null; end;
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb||'{"tarefas":[{"descricao":"Inspeção fictícia","periodicidade":"Mensal","especialidade":"Elétrica","duracao_horas":0,"seguranca":true,"origem":"base genérica a validar com manual do fabricante","versao":"1","observacao":""}]}'::jsonb); raise exception 'Tarefa inválida aceita.'; exception when invalid_parameter_value then null; end;
end $$;
select public.catalogo_enviar(pg_catalog.current_setting('teste.id')::uuid);
do $$ begin
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb,pg_catalog.current_setting('teste.id')::uuid); raise exception 'Autor editou pendente.'; exception when insufficient_privilege then null; end;
  begin perform public.catalogo_decidir(pg_catalog.current_setting('teste.id')::uuid,true); raise exception 'Autor aprovou modelo.'; exception when insufficient_privilege then null; end;
end $$;

select pg_catalog.set_config('request.jwt.claim.sub','20000000-0000-0000-0000-000000000002',false);
do $$ begin
  if (select count(*) from public.catalogo_modelos)<>0 then raise exception 'Outro autor leu pendente.'; end if;
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb,pg_catalog.current_setting('teste.id')::uuid); raise exception 'Outro autor editou modelo.'; exception when insufficient_privilege then null; end;
  begin perform public.catalogo_enviar(pg_catalog.current_setting('teste.id')::uuid); raise exception 'Outro autor enviou modelo.'; exception when insufficient_privilege then null; end;
  begin perform public.catalogo_retirar(pg_catalog.current_setting('teste.id')::uuid); raise exception 'Outro autor retirou modelo.'; exception when insufficient_privilege then null; end;
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb,null,pg_catalog.current_setting('teste.id')::uuid); raise exception 'Outro autor acessou origem privada.'; exception when insufficient_privilege then null; end;
end $$;
reset role;
set role anon;
select pg_catalog.set_config('request.jwt.claim.sub','',false);
do $$ begin if (select count(*) from public.catalogo_modelos)<>0 then raise exception 'Anônimo leu pendente.'; end if; end $$;
reset role;

set role authenticated;
select pg_catalog.set_config('request.jwt.claim.sub','30000000-0000-0000-0000-000000000003',false);
do $$ begin
  if not public.catalogo_e_moderador() or (select count(*) from public.catalogo_modelos)<>1 then raise exception 'Moderador sem acesso de revisão.'; end if;
  begin perform public.catalogo_decidir(pg_catalog.current_setting('teste.id')::uuid,false,''); raise exception 'Recusa sem justificativa aceita.'; exception when invalid_parameter_value then null; end;
end $$;
select public.catalogo_decidir(pg_catalog.current_setting('teste.id')::uuid,false,'Conferir a origem da tarefa.');
select pg_catalog.set_config('request.jwt.claim.sub','10000000-0000-0000-0000-000000000001',false);
do $$ begin if (select motivo from public.catalogo_modelos where id=pg_catalog.current_setting('teste.id')::uuid)<>'Conferir a origem da tarefa.' then raise exception 'Autor não recebeu motivo.'; end if; end $$;
select public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb,pg_catalog.current_setting('teste.id')::uuid);
do $$ begin if exists(select 1 from public.catalogo_modelos where id=pg_catalog.current_setting('teste.id')::uuid and (situacao<>'rascunho' or motivo<>'' or revisado_por is not null)) then raise exception 'Edição não reiniciou revisão.'; end if; end $$;
select public.catalogo_enviar(pg_catalog.current_setting('teste.id')::uuid);
select pg_catalog.set_config('request.jwt.claim.sub','30000000-0000-0000-0000-000000000003',false);
select public.catalogo_decidir(pg_catalog.current_setting('teste.id')::uuid,true);
reset role;
set role anon;
select pg_catalog.set_config('request.jwt.claim.sub','',false);
do $$ begin if (select count(*) from public.catalogo_modelos)<>1 then raise exception 'Modelo aprovado não ficou público.'; end if; end $$;
reset role;

set role authenticated;
select pg_catalog.set_config('request.jwt.claim.sub','10000000-0000-0000-0000-000000000001',false);
do $$ begin
  begin perform public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb,pg_catalog.current_setting('teste.id')::uuid); raise exception 'Autor alterou versão pública.'; exception when insufficient_privilege then null; end;
end $$;
select pg_catalog.set_config('teste.versao',public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb,null,pg_catalog.current_setting('teste.id')::uuid)::text,false);
do $$ begin if (select original_id from public.catalogo_modelos where id=pg_catalog.current_setting('teste.versao')::uuid)<>pg_catalog.current_setting('teste.id')::uuid then raise exception 'Origem de versão perdida.'; end if; end $$;
select public.catalogo_retirar(pg_catalog.current_setting('teste.id')::uuid);
reset role;
set role anon;
select pg_catalog.set_config('request.jwt.claim.sub','',false);
do $$ begin if (select count(*) from public.catalogo_modelos)<>0 then raise exception 'Retirada não ocultou publicação.'; end if; end $$;
reset role;

-- Cinco envios simultaneamente pendentes por autor: o sexto é recusado.
set role authenticated;
select pg_catalog.set_config('request.jwt.claim.sub','20000000-0000-0000-0000-000000000002',false);
do $$ declare v_id uuid; begin
  for i in 1..5 loop v_id:=public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb); perform public.catalogo_enviar(v_id); end loop;
  v_id:=public.catalogo_salvar(pg_catalog.current_setting('teste.dados')::jsonb);
  begin perform public.catalogo_enviar(v_id); raise exception 'Sexto envio pendente aceito.'; exception when program_limit_exceeded then null; end;
end $$;
reset role;

-- Mesmo uma escrita administrativa incorreta precisa ser recusada pela constraint.
do $$ begin
  begin insert into public.catalogo_modelos(autor_id,dados) values('10000000-0000-0000-0000-000000000001','{}'); raise exception 'Constraint ausente.'; exception when check_violation then null; end;
end $$;
rollback;
\echo 'Aprovado: RLS, isolamento de autores, revisão, versões, retirada, limites e validação do catálogo.'
