-- Catálogo público de modelos. Os cadastros privados do PCM não são enviados a este banco.
-- Execute no SQL Editor do seu projeto Supabase como administrador.
begin;

create schema if not exists catalogo_privado;
revoke all on schema catalogo_privado from public, anon, authenticated;

create function catalogo_privado.texto_valido(p_valor jsonb, p_maximo integer, p_obrigatorio boolean default false)
returns boolean language sql immutable set search_path = '' as $$
  select coalesce(pg_catalog.jsonb_typeof(p_valor) = 'string'
    and pg_catalog.length(p_valor #>> '{}') <= p_maximo
    and (not p_obrigatorio or pg_catalog.length(pg_catalog.btrim(p_valor #>> '{}')) > 0), false);
$$;

create function catalogo_privado.dados_validos(p_dados jsonb)
returns boolean language plpgsql immutable set search_path = '' as $$
declare
  v_tarefa jsonb;
begin
  if pg_catalog.jsonb_typeof(p_dados) is distinct from 'object' then return false; end if;
  if not (p_dados ?& array['titulo','tipo_base','fabricante','modelo','descricao','caracteristicas','apelido','tarefas'])
    or (p_dados - array['titulo','tipo_base','fabricante','modelo','descricao','caracteristicas','apelido','tarefas']) <> '{}'::jsonb then return false; end if;
  if not catalogo_privado.texto_valido(p_dados->'titulo',120,true)
    or not catalogo_privado.texto_valido(p_dados->'tipo_base',80,true)
    or not (p_dados->>'tipo_base' = any(array['motor_eletrico','compressor_ar','bomba_centrifuga','ponte_rolante','outro']))
    or not catalogo_privado.texto_valido(p_dados->'fabricante',120)
    or not catalogo_privado.texto_valido(p_dados->'modelo',120)
    or not catalogo_privado.texto_valido(p_dados->'descricao',2000,true)
    or not catalogo_privado.texto_valido(p_dados->'caracteristicas',4000)
    or not catalogo_privado.texto_valido(p_dados->'apelido',60)
    or pg_catalog.jsonb_typeof(p_dados->'tarefas') is distinct from 'array' then return false; end if;
  if pg_catalog.jsonb_array_length(p_dados->'tarefas') > 50 then return false; end if;
  for v_tarefa in select value from pg_catalog.jsonb_array_elements(p_dados->'tarefas') loop
    if pg_catalog.jsonb_typeof(v_tarefa) is distinct from 'object' then return false; end if;
    if not (v_tarefa ?& array['descricao','periodicidade','especialidade','duracao_horas','seguranca','origem','versao','observacao'])
      or (v_tarefa - array['descricao','periodicidade','especialidade','duracao_horas','seguranca','origem','versao','observacao']) <> '{}'::jsonb then return false; end if;
    if not catalogo_privado.texto_valido(v_tarefa->'descricao',2000,true)
      or not catalogo_privado.texto_valido(v_tarefa->'periodicidade',80,true)
      or not (v_tarefa->>'periodicidade' = any(array['Diária','Semanal','Quinzenal','Mensal','Bimestral','Trimestral','Semestral','Anual']))
      or not catalogo_privado.texto_valido(v_tarefa->'especialidade',120,true)
      or pg_catalog.jsonb_typeof(v_tarefa->'duracao_horas') is distinct from 'number'
      or pg_catalog.jsonb_typeof(v_tarefa->'seguranca') is distinct from 'boolean'
      or not catalogo_privado.texto_valido(v_tarefa->'origem',500,true)
      or not catalogo_privado.texto_valido(v_tarefa->'versao',80,true)
      or not catalogo_privado.texto_valido(v_tarefa->'observacao',2000) then return false; end if;
    if (v_tarefa->>'duracao_horas')::numeric <= 0 or (v_tarefa->>'duracao_horas')::numeric > 1000 then return false; end if;
  end loop;
  return true;
exception when others then
  return false;
end;
$$;

create table public.catalogo_moderadores (
  user_id uuid primary key references auth.users(id) on delete cascade
);
create table public.catalogo_modelos (
  id uuid primary key default pg_catalog.gen_random_uuid(),
  autor_id uuid not null references auth.users(id),
  original_id uuid references public.catalogo_modelos(id),
  dados jsonb not null check (catalogo_privado.dados_validos(dados)),
  situacao text not null default 'rascunho' check (situacao in ('rascunho','pendente','aprovado','rejeitado','arquivado')),
  motivo text not null default '' check (pg_catalog.length(motivo) <= 2000),
  revisado_por uuid references auth.users(id),
  criado_em timestamptz not null default pg_catalog.now(),
  atualizado_em timestamptz not null default pg_catalog.now()
);
create index catalogo_modelos_publicos on public.catalogo_modelos (criado_em desc, id) where situacao = 'aprovado';
create index catalogo_modelos_autor on public.catalogo_modelos (autor_id, criado_em desc);
create index catalogo_modelos_pendentes on public.catalogo_modelos (criado_em, id) where situacao = 'pendente';

alter table public.catalogo_modelos enable row level security;
alter table public.catalogo_moderadores enable row level security;
revoke all on public.catalogo_modelos, public.catalogo_moderadores from public, anon, authenticated;
grant select on public.catalogo_modelos to anon, authenticated;
grant select on public.catalogo_moderadores to authenticated;
create policy moderador_consulta_propria on public.catalogo_moderadores for select to authenticated using (user_id = auth.uid());

create function public.catalogo_e_moderador()
returns boolean language sql stable security definer set search_path = '' as $$
  select exists(select 1 from public.catalogo_moderadores where user_id = auth.uid());
$$;
revoke all on function public.catalogo_e_moderador() from public;
grant execute on function public.catalogo_e_moderador() to anon, authenticated;
create policy modelos_consulta_publica on public.catalogo_modelos for select to anon using (situacao = 'aprovado');
create policy modelos_consulta_autenticada on public.catalogo_modelos for select to authenticated
  using (situacao = 'aprovado' or autor_id = auth.uid() or public.catalogo_e_moderador());

create function public.catalogo_salvar(p_dados jsonb, p_id uuid default null, p_original_id uuid default null)
returns uuid language plpgsql security definer set search_path = '' as $$
declare
  v_autor uuid := auth.uid();
  v_atual public.catalogo_modelos%rowtype;
  v_id uuid;
begin
  if v_autor is null then raise exception 'Entre na sua conta para contribuir.' using errcode='42501'; end if;
  if not catalogo_privado.dados_validos(p_dados) then raise exception 'Dados do modelo inválidos.' using errcode='22023'; end if;
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_autor::text,0));
  if p_id is not null then
    select * into v_atual from public.catalogo_modelos where id = p_id for update;
    if not found or v_atual.autor_id <> v_autor or v_atual.situacao not in ('rascunho','rejeitado') then
      raise exception 'Modelo indisponível para edição. Crie uma nova versão se ele já foi publicado.' using errcode='42501';
    end if;
    -- A origem de uma versão não pode ser trocada após sua criação.
    if p_original_id is not null and p_original_id is distinct from v_atual.original_id then
      raise exception 'A origem da versão não pode ser alterada.' using errcode='22023';
    end if;
    update public.catalogo_modelos set dados=p_dados, situacao='rascunho', motivo='', revisado_por=null,
      atualizado_em=pg_catalog.now() where id=p_id returning id into v_id;
  else
    if (select pg_catalog.count(*) from public.catalogo_modelos where autor_id=v_autor and situacao <> 'arquivado') >= 100 then
      raise exception 'Limite de 100 modelos ativos por conta. Arquive os que não utiliza.' using errcode='54000';
    end if;
    if p_original_id is not null and not exists(select 1 from public.catalogo_modelos where id=p_original_id
      and (situacao='aprovado' or (autor_id=v_autor and situacao='arquivado'))) then
      raise exception 'Modelo de origem indisponível.' using errcode='42501';
    end if;
    insert into public.catalogo_modelos(autor_id,original_id,dados) values(v_autor,p_original_id,p_dados) returning id into v_id;
  end if;
  return v_id;
end;
$$;

create function public.catalogo_enviar(p_id uuid)
returns void language plpgsql security definer set search_path = '' as $$
declare
  v_autor uuid := auth.uid();
  v_atual public.catalogo_modelos%rowtype;
begin
  if v_autor is null then raise exception 'Entre na sua conta para contribuir.' using errcode='42501'; end if;
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_autor::text,0));
  select * into v_atual from public.catalogo_modelos where id=p_id for update;
  if not found or v_atual.autor_id <> v_autor or v_atual.situacao not in ('rascunho','rejeitado') then
    raise exception 'Modelo indisponível para envio.' using errcode='42501';
  end if;
  if (select pg_catalog.count(*) from public.catalogo_modelos where autor_id=v_autor and situacao='pendente') >= 5 then
    raise exception 'Há cinco contribuições aguardando revisão. Aguarde antes de enviar outra.' using errcode='54000';
  end if;
  update public.catalogo_modelos set situacao='pendente',motivo='',revisado_por=null,atualizado_em=pg_catalog.now() where id=p_id;
end;
$$;

create function public.catalogo_decidir(p_id uuid, p_aprovar boolean, p_motivo text default '')
returns void language plpgsql security definer set search_path = '' as $$
declare
  v_atual public.catalogo_modelos%rowtype;
begin
  if auth.uid() is null or not public.catalogo_e_moderador() then
    raise exception 'Somente o responsável pela revisão pode decidir.' using errcode='42501';
  end if;
  if p_aprovar is null or p_motivo is null or pg_catalog.length(p_motivo)>2000 or
    (not p_aprovar and pg_catalog.length(pg_catalog.btrim(p_motivo))=0) then
    raise exception 'Informe uma justificativa de até 2000 caracteres para recusar.' using errcode='22023';
  end if;
  select * into v_atual from public.catalogo_modelos where id=p_id for update;
  if not found or v_atual.situacao <> 'pendente' then
    raise exception 'A contribuição não está mais aguardando revisão.' using errcode='22023';
  end if;
  update public.catalogo_modelos set situacao=case when p_aprovar then 'aprovado' else 'rejeitado' end,
    motivo=case when p_aprovar then '' else pg_catalog.btrim(p_motivo) end,
    revisado_por=auth.uid(),atualizado_em=pg_catalog.now() where id=p_id;
end;
$$;

create function public.catalogo_retirar(p_id uuid)
returns void language plpgsql security definer set search_path = '' as $$
declare
  v_autor uuid := auth.uid();
  v_atual public.catalogo_modelos%rowtype;
begin
  if v_autor is null then raise exception 'Entre na sua conta para continuar.' using errcode='42501'; end if;
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_autor::text,0));
  select * into v_atual from public.catalogo_modelos where id=p_id for update;
  if not found or v_atual.autor_id <> v_autor then raise exception 'Modelo indisponível.' using errcode='42501'; end if;
  update public.catalogo_modelos set situacao=case when v_atual.situacao='pendente' then 'rascunho' else 'arquivado' end,
    atualizado_em=pg_catalog.now() where id=p_id;
end;
$$;

revoke all on function public.catalogo_salvar(jsonb,uuid,uuid), public.catalogo_enviar(uuid),
  public.catalogo_decidir(uuid,boolean,text), public.catalogo_retirar(uuid) from public, anon;
grant execute on function public.catalogo_salvar(jsonb,uuid,uuid), public.catalogo_enviar(uuid),
  public.catalogo_decidir(uuid,boolean,text), public.catalogo_retirar(uuid) to authenticated;
revoke all on all functions in schema catalogo_privado from public, anon, authenticated;

commit;
