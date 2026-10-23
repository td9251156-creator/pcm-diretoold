// O formulário online é separado da gestão local: nenhum inventário é enviado ao catálogo.
import { estado, adicionar, armazenamento } from '../estado.js';
import { proximoNumero } from '../logica/tag.js';
import { novoId } from '../logica/entrada.js';
import { PERIODICIDADES } from '../logica/plano.js';
import { TIPOS_CATALOGO, modeloVazio, tarefaCatalogoVazia, validarModeloCatalogo, dadosEquipamentoDoModelo } from '../logica/catalogo.js';
import { configuracao, sessaoCatalogo, entrarCatalogo, sairCatalogo, listarCatalogo, moderadorCatalogo, salvarModelo, enviarModelo, retirarModelo, decidirModelo } from '../servicos/catalogo.js';
import { esc, avisar } from '../ui.js';

const SITUACOES = { rascunho: 'Rascunho privado', pendente: 'Aguardando revisão', aprovado: 'Publicado após revisão', rejeitado: 'Revisão solicitou ajustes', arquivado: 'Arquivado' };
const campo = (nome, rotulo, valor, atributos = '') => `<div><label for="c-${nome}">${rotulo}</label><input id="c-${nome}" name="${nome}" value="${esc(valor)}" ${atributos}></div>`;
const texto = (nome, rotulo, valor, atributos = '') => `<div><label for="c-${nome}">${rotulo}</label><textarea id="c-${nome}" name="${nome}" ${atributos}>${esc(valor)}</textarea></div>`;
const opcoes = (itens, atual) => itens.map(([id, nome]) => `<option value="${esc(id)}" ${id === atual ? 'selected' : ''}>${esc(nome)}</option>`).join('');

export function telaCatalogo(main, ir) {
  const raiz = document.createElement('div');
  main.replaceChildren(raiz);
  const vivo = () => raiz.isConnected && main.contains(raiz);
  raiz.innerHTML = `<section class="cartao"><h2>Catálogo colaborativo de máquinas</h2>
    <p>Consulte modelos reutilizáveis e contribua com novos cadastros. A publicação passa pela revisão do mantenedor.</p>
    <p>Seu inventário, TAGs, pessoas, execuções e falhas continuam neste aparelho. Somente os campos preenchidos no formulário de contribuição são enviados ao catálogo.</p>
    <p>Revisão editorial não certifica conformidade. Confirme tarefas e periodicidades com o manual do fabricante.</p>
    </section><div data-conta></div><div data-controles></div><div data-editor></div><div data-lista aria-live="polite"></div>`;
  const c = configuracao();
  if (!c.configurado) {
    raiz.querySelector('[data-conta]').innerHTML = `<section class="cartao"><h3>Catálogo online em configuração</h3><p>${esc(c.erro || 'O banco e o login ainda não foram conectados neste endereço. Os cadastros e os planos locais continuam disponíveis.')}</p><p><a href="#equipamentos">Continuar com meus equipamentos</a> · <a href="#inicio">Abrir gestão local</a></p></section>`;
    return;
  }
  let sessao = null; let moderador = false; let vista = 'publicos'; let pagina = 0; let busca = ''; let registros = []; let pedido = 0; let ocupado = false; let editor = null;
  const conta = raiz.querySelector('[data-conta]');
  const controles = raiz.querySelector('[data-controles]');
  const areaEditor = raiz.querySelector('[data-editor]');
  const lista = raiz.querySelector('[data-lista]');

  async function atuar(acao) {
    if (ocupado || !vivo()) return;
    ocupado = true;
    const botoes = [...raiz.querySelectorAll('button, input, select, textarea')].map(b => [b, b.disabled]);
    botoes.forEach(([b]) => { b.disabled = true; });
    try { await acao(); }
    catch (e) { if (vivo()) avisar(e.message || 'Não foi possível concluir a operação. Tente novamente.'); }
    finally { ocupado = false; botoes.forEach(([b, desativado]) => { b.disabled = desativado; }); }
  }

  function desenharConta() {
    conta.innerHTML = sessao ? `<section class="cartao"><h3>Sua conta</h3><p>Conectado como ${esc(sessao.user.email || 'colaborador')}. O e-mail não aparece no cadastro público.</p><button type="button" class="secundario" data-sair>Sair deste aparelho</button></section>` :
      `<section class="cartao"><h3>Entrar para contribuir</h3><p>A consulta pública dispensa conta. Para criar modelos, receba um link de acesso por e-mail e abra-o neste mesmo navegador.</p><form data-login>${campo('email', 'E-mail de acesso', '', 'type="email" autocomplete="email" required maxlength="254"')}<button type="submit">Enviar link de acesso</button></form></section>`;
    conta.querySelector('[data-login]')?.addEventListener('submit', e => {
      e.preventDefault(); const email = new FormData(e.currentTarget).get('email').trim();
      atuar(async () => { await entrarCatalogo(email); if (vivo()) avisar('Se o envio foi autorizado, o link chegará ao seu e-mail. Abra-o neste navegador. Confira também a pasta de spam.'); });
    });
    conta.querySelector('[data-sair]')?.addEventListener('click', () => {
      if (editor && !confirm('Sair e descartar os campos de contribuição ainda não salvos? Os modelos já salvos online serão mantidos.')) return;
      atuar(async () => { await sairCatalogo(); if (!vivo()) return; sessao = null; moderador = false; editor = null; vista = 'publicos'; pagina = 0; desenharConta(); desenharControles(); desenharEditor(); await atualizar(); avisar('Sessão encerrada neste aparelho. Seus planos locais foram mantidos.'); });
    });
  }

  function desenharControles() {
    controles.innerHTML = `<section class="cartao"><h3>Explorar modelos</h3><div class="acoes"><button type="button" data-vista="publicos" ${vista === 'publicos' ? 'aria-pressed="true"' : 'aria-pressed="false"'}>Catálogo público</button>${sessao ? `<button type="button" class="secundario" data-vista="meus" aria-pressed="${vista === 'meus'}">Meus modelos</button><button type="button" class="secundario" data-novo>Criar modelo</button>` : ''}${moderador ? `<button type="button" class="secundario" data-vista="moderacao" aria-pressed="${vista === 'moderacao'}">Fila de revisão</button>` : ''}</div>
      <form data-busca>${campo('busca', 'Buscar pelo título', busca, 'type="search" maxlength="120"')}<button type="submit">Buscar</button></form></section>`;
    controles.querySelectorAll('[data-vista]').forEach(b => b.addEventListener('click', () => {
      if (ocupado) return;
      vista = b.dataset.vista; pagina = 0; desenharControles(); atualizar();
    }));
    controles.querySelector('[data-novo]')?.addEventListener('click', () => abrirEditor(null));
    controles.querySelector('[data-busca]').addEventListener('submit', e => {
      e.preventDefault(); if (ocupado) return;
      busca = new FormData(e.currentTarget).get('busca').trim(); pagina = 0; atualizar();
    });
  }

  async function atualizar() {
    const idPedido = ++pedido;
    lista.innerHTML = '<section class="cartao"><p role="status">Consultando catálogo…</p></section>';
    try {
      const novos = await listarCatalogo({ busca, pagina, meus: vista === 'meus', moderacao: vista === 'moderacao', usuarioId: sessao?.user.id || '' });
      if (!vivo() || idPedido !== pedido) return;
      registros = novos;
      desenharLista();
    } catch (e) {
      if (!vivo() || idPedido !== pedido) return;
      lista.innerHTML = `<section class="cartao erro"><h3>Não foi possível consultar o catálogo</h3><p>${esc(e.message)}</p><button type="button" data-repetir>Tentar novamente</button><p><a href="#inicio">Continuar na gestão local</a></p></section>`;
      lista.querySelector('[data-repetir]').addEventListener('click', atualizar);
    }
  }

  function desenharLista() {
    lista.innerHTML = `<section class="cartao"><h3>${vista === 'meus' ? 'Seus modelos online' : vista === 'moderacao' ? 'Propostas aguardando revisão' : 'Modelos publicados'}</h3><p>Página ${pagina + 1}. Até 20 modelos por página.</p>${registros.length ? '' : '<p>Nenhum modelo encontrado nesta página.</p>'}</section>` + registros.map(r => {
      const d = r.dados; const proprio = sessao?.user.id === r.autor_id;
      if (validarModeloCatalogo(d).length) return '<section class="cartao erro"><p>Um modelo foi omitido porque contém campos inválidos. A gestão local não foi alterada.</p></section>';
      return `<article class="cartao"><h3>${esc(d.titulo)}</h3><p><strong>${esc(SITUACOES[r.situacao] || r.situacao)}</strong> · ${esc(TIPOS_CATALOGO[d.tipo_base])} · contribuição de ${esc(d.apelido || 'Colaborador')}</p>
        <p>${esc(d.fabricante)} ${esc(d.modelo)}</p><p>${esc(d.descricao)}</p>${d.caracteristicas ? `<p><strong>Características:</strong> ${esc(d.caracteristicas)}</p>` : ''}
        ${r.original_id ? '<p class="origem">Criado a partir de uma versão anterior; esta proposta tem revisão própria.</p>' : ''}
        ${r.motivo ? `<p><strong>Parecer:</strong> ${esc(r.motivo)}</p>` : ''}
        <details><summary>Tarefas de referência (${d.tarefas.length})</summary><p>Não são importadas para seu plano. A biblioteca local e suas proteções de segurança permanecem como fonte.</p>${d.tarefas.map(t => `<section><h4>${esc(t.descricao)}${t.seguranca ? ' — Segurança' : ''}</h4><p>${esc(t.periodicidade)} · ${esc(t.especialidade)} · ${esc(t.duracao_horas)} h</p><p>Origem: ${esc(t.origem)} · versão ${esc(t.versao)}</p><p>${esc(t.observacao)}</p></section>`).join('')}</details>
        <div class="acoes">${r.situacao === 'aprovado' ? `<button type="button" data-usar="${esc(r.id)}">Usar cadastro neste aparelho</button>${sessao ? `<button type="button" class="secundario" data-versao="${esc(r.id)}">Criar nova versão</button>` : ''}` : ''}
        ${proprio && ['rascunho', 'rejeitado'].includes(r.situacao) ? `<button type="button" data-editar="${esc(r.id)}">Editar e enviar para revisão</button>` : ''}
        ${proprio && r.situacao !== 'arquivado' ? `<button type="button" class="secundario" data-retirar="${esc(r.id)}">${r.situacao === 'pendente' ? 'Retirar da revisão' : 'Arquivar modelo'}</button>` : ''}
        ${proprio && r.situacao === 'arquivado' ? `<button type="button" class="secundario" data-versao="${esc(r.id)}">Criar nova versão</button>` : ''}</div>
        ${moderador && r.situacao === 'pendente' ? `<form data-parecer="${esc(r.id)}">${texto('parecer-' + r.id, 'Motivo da rejeição (obrigatório ao rejeitar)', '', 'maxlength="2000"')}<div class="acoes"><button type="submit" value="aprovar">Aprovar publicação</button><button type="submit" value="rejeitar" class="secundario">Solicitar ajustes</button></div></form>` : ''}
        <div data-importacao="${esc(r.id)}"></div></article>`;
    }).join('') + `<section class="cartao"><div class="acoes"><button type="button" class="secundario" data-anterior ${pagina === 0 ? 'disabled' : ''}>Página anterior</button><button type="button" class="secundario" data-proxima ${registros.length < 20 ? 'disabled' : ''}>Próxima página</button></div></section>`;
    const registro = id => registros.find(r => r.id === id);
    lista.querySelectorAll('[data-editar]').forEach(b => b.addEventListener('click', () => abrirEditor(registro(b.dataset.editar))));
    lista.querySelectorAll('[data-versao]').forEach(b => b.addEventListener('click', () => abrirEditor(registro(b.dataset.versao), true)));
    lista.querySelectorAll('[data-usar]').forEach(b => b.addEventListener('click', () => desenharImportacao(registro(b.dataset.usar))));
    lista.querySelectorAll('[data-retirar]').forEach(b => b.addEventListener('click', () => {
      if (!confirm('Retirar este modelo? A retirada não apaga cadastros já copiados para outros aparelhos.')) return;
      atuar(async () => { await retirarModelo(b.dataset.retirar); if (!vivo()) return; if (editor?.id === b.dataset.retirar) { editor = null; desenharEditor(); } await atualizar(); avisar('Situação do modelo atualizada.'); });
    }));
    lista.querySelectorAll('[data-parecer]').forEach(f => f.addEventListener('submit', e => {
      e.preventDefault(); const aprovar = e.submitter?.value === 'aprovar'; const motivo = new FormData(f).get('parecer-' + f.dataset.parecer).trim();
      if (!aprovar && !motivo) { avisar('Explique quais ajustes o autor deve fazer.'); f.querySelector('textarea').focus(); return; }
      if (aprovar && !confirm('Publicar este modelo para consulta pública após conferir conteúdo, origem, versão e ausência de dados privados? Isso não certifica conformidade.')) return;
      atuar(async () => { await decidirModelo(f.dataset.parecer, aprovar, motivo); if (!vivo()) return; await atualizar(); avisar(aprovar ? 'Modelo publicado após revisão.' : 'Proposta devolvida ao autor com o parecer.'); });
    }));
    lista.querySelector('[data-anterior]').addEventListener('click', () => { if (ocupado || !pagina) return; pagina--; atualizar(); });
    lista.querySelector('[data-proxima]').addEventListener('click', () => { if (ocupado) return; pagina++; atualizar(); });
  }

  function desenharImportacao(registro) {
    const area = [...lista.querySelectorAll('[data-importacao]')].find(el => el.dataset.importacao === registro.id);
    const tipo = estado.biblioteca.tipos.some(t => t.id === registro.dados.tipo_base) ? registro.dados.tipo_base : '';
    area.innerHTML = `<form data-copiar><h4>Novo equipamento local</h4><p>Serão copiados título, fabricante e modelo. Você escolhe o setor e o tipo da biblioteca local. As tarefas de referência não substituem o plano ou suas proteções de segurança.</p>
      ${campo('setor-' + registro.id, 'Setor (2 a 4 letras ou números)', '', 'required pattern="[A-Za-z0-9]{2,4}" maxlength="4"')}
      <div><label for="c-tipo-${esc(registro.id)}">Tipo da biblioteca local</label><select id="c-tipo-${esc(registro.id)}" name="tipo" required><option value="">Selecione</option>${opcoes(estado.biblioteca.tipos.map(t => [t.id, t.nome]), tipo)}</select></div><button type="submit">Adicionar aos meus equipamentos</button></form>`;
    area.querySelector('form').addEventListener('submit', e => {
      e.preventDefault(); if (ocupado) return;
      const dados = new FormData(e.currentTarget); const tipoLocal = dados.get('tipo');
      if (!estado.biblioteca.tipos.some(t => t.id === tipoLocal)) { avisar('Escolha um tipo existente na biblioteca local.'); return; }
      try {
        const campos = dadosEquipamentoDoModelo(registro.dados, dados.get('setor-' + registro.id).trim().toUpperCase(), tipoLocal);
        const numero = proximoNumero(estado.equipamentos, campos.setor, campos.tipo);
        if (numero === null) throw new Error('Todos os 999 números deste setor e tipo estão em uso. Escolha outro setor.');
        adicionar([{ ...campos, numero, id: novoId() }]);
        ir('equipamentos'); avisar(armazenamento.rascunho ? 'Cadastro adicionado neste aparelho. Confira a TAG e revise o plano da biblioteca local.' : 'Cadastro adicionado nesta sessão, mas o navegador não conseguiu salvar. Baixe um backup antes de sair.');
      } catch (e) { avisar(e.message); }
    });
    area.querySelector('input').focus();
  }

  function abrirEditor(registro, novaVersao = false) {
    if (ocupado || !sessao) return;
    if (editor && !confirm('Trocar o formulário? Campos ainda não salvos serão descartados.')) return;
    editor = { id: novaVersao ? null : registro?.id || null, originalId: novaVersao ? registro.id : null, dados: registro ? structuredClone(registro.dados) : modeloVazio() };
    desenharEditor(); areaEditor.querySelector('input')?.focus();
  }

  function lerEditor() {
    const form = areaEditor.querySelector('form'); if (!form || !editor) return;
    const fd = new FormData(form); const dados = editor.dados;
    for (const nome of ['titulo', 'tipo_base', 'fabricante', 'modelo', 'descricao', 'caracteristicas', 'apelido']) dados[nome] = fd.get(nome) ?? '';
    dados.tarefas = dados.tarefas.map((t, i) => ({ ...t,
      descricao: fd.get(`t${i}-descricao`) ?? '', periodicidade: fd.get(`t${i}-periodicidade`) ?? '', especialidade: fd.get(`t${i}-especialidade`) ?? '',
      duracao_horas: Number(fd.get(`t${i}-duracao_horas`)), seguranca: fd.has(`t${i}-seguranca`), origem: fd.get(`t${i}-origem`) ?? '', versao: fd.get(`t${i}-versao`) ?? '', observacao: fd.get(`t${i}-observacao`) ?? '',
    }));
  }

  function desenharEditor() {
    if (!editor) { areaEditor.replaceChildren(); return; }
    const d = editor.dados;
    areaEditor.innerHTML = `<section class="cartao"><h3>${editor.id ? 'Editar rascunho' : editor.originalId ? 'Nova versão para revisão' : 'Criar modelo reutilizável'}</h3><p>Este formulário é online. Não inclua TAGs, nomes de pessoas, dados de fábrica ou conteúdo sem autorização. Salvar rascunho guarda estes campos na sua conta; não publica o modelo.</p><p>Campos ainda não salvos serão perdidos ao sair desta tela.</p>
      <form data-modelo>${campo('titulo', 'Título público', d.titulo, 'required maxlength="120"')}
      <div><label for="c-tipo_base">Categoria da máquina</label><select id="c-tipo_base" name="tipo_base">${opcoes(Object.entries(TIPOS_CATALOGO), d.tipo_base)}</select></div>
      ${campo('fabricante', 'Fabricante (opcional)', d.fabricante, 'maxlength="120"')}${campo('modelo', 'Modelo do fabricante (opcional)', d.modelo, 'maxlength="120"')}
      ${texto('descricao', 'Descrição pública', d.descricao, 'required maxlength="2000"')}${texto('caracteristicas', 'Características técnicas (opcional)', d.caracteristicas, 'maxlength="4000"')}${campo('apelido', 'Apelido público (opcional; não use seu e-mail)', d.apelido, 'maxlength="60"')}
      <h4>Tarefas de referência opcionais</h4><p>Não alteram automaticamente os planos locais. Informe origem e versão de cada tarefa. Use “base genérica a validar com manual do fabricante” quando não houver fonte específica.</p>
      ${d.tarefas.map((t, i) => `<fieldset><legend>Tarefa ${i + 1}</legend>${texto(`t${i}-descricao`, 'Atividade', t.descricao, 'required maxlength="2000"')}
        <div><label for="c-t${i}-periodicidade">Periodicidade</label><select id="c-t${i}-periodicidade" name="t${i}-periodicidade">${opcoes(PERIODICIDADES.map(p => [p.nome, p.nome]), t.periodicidade)}</select></div>
        ${campo(`t${i}-especialidade`, 'Especialidade', t.especialidade, 'required maxlength="120"')}${campo(`t${i}-duracao_horas`, 'Duração (horas)', t.duracao_horas, 'type="number" required min="0.001" max="1000" step="any"')}
        <label><input type="checkbox" name="t${i}-seguranca" ${t.seguranca ? 'checked' : ''}> Tarefa de segurança</label>
        ${campo(`t${i}-origem`, 'Origem / fonte', t.origem, 'required maxlength="500"')}${campo(`t${i}-versao`, 'Versão da fonte ou base', t.versao, 'required maxlength="80"')}${texto(`t${i}-observacao`, 'Observação (opcional)', t.observacao, 'maxlength="2000"')}
        <button type="button" class="secundario" data-remover-tarefa="${i}">Remover esta tarefa de referência</button></fieldset>`).join('')}
      <div class="acoes"><button type="button" class="secundario" data-adicionar-tarefa ${d.tarefas.length >= 50 ? 'disabled' : ''}>Adicionar tarefa de referência</button></div>
      <p><label><input type="checkbox" name="consentimento"> Confirmo que posso compartilhar este conteúdo, retirei dados privados e aceito submetê-lo à revisão para publicação pública.</label></p>
      <div class="acoes"><button type="submit" value="salvar">Salvar rascunho online</button><button type="submit" value="enviar">Salvar e enviar para revisão</button><button type="button" class="secundario" data-fechar-editor>Fechar formulário</button></div></form></section>`;
    const form = areaEditor.querySelector('form');
    areaEditor.querySelector('[data-adicionar-tarefa]').addEventListener('click', () => {
      if (ocupado || editor.dados.tarefas.length >= 50) return;
      lerEditor(); editor.dados.tarefas.push(tarefaCatalogoVazia()); desenharEditor();
    });
    areaEditor.querySelectorAll('[data-remover-tarefa]').forEach(b => b.addEventListener('click', () => {
      if (ocupado) return; lerEditor(); editor.dados.tarefas.splice(Number(b.dataset.removerTarefa), 1); desenharEditor();
    }));
    areaEditor.querySelector('[data-fechar-editor]').addEventListener('click', () => {
      if (ocupado || !confirm('Fechar e descartar os campos ainda não salvos? Rascunhos já salvos online serão mantidos.')) return;
      editor = null; desenharEditor();
    });
    form.addEventListener('submit', e => {
      e.preventDefault(); if (ocupado) return;
      const enviar = e.submitter?.value === 'enviar'; lerEditor();
      const problemas = validarModeloCatalogo(editor.dados);
      if (problemas.length) { avisar(problemas.join(' ')); return; }
      if (enviar && !new FormData(form).has('consentimento')) { avisar('Confirme a autorização para compartilhar antes de enviar para revisão.'); form.elements.consentimento.focus(); return; }
      const atual = editor; const dados = structuredClone(editor.dados);
      atuar(async () => {
        const id = await salvarModelo(dados, atual.id, atual.originalId);
        atual.id = id;
        if (enviar) await enviarModelo(id);
        if (!vivo()) return;
        if (enviar) { editor = null; } else { editor = { ...atual, dados }; }
        vista = 'meus'; pagina = 0; desenharEditor(); desenharControles(); await atualizar();
        avisar(enviar ? 'Modelo enviado para revisão. Ainda não está publicado.' : 'Rascunho salvo na sua conta, sem publicação.');
      });
    });
  }

  conta.innerHTML = '<section class="cartao"><p role="status">Verificando sessão de acesso…</p></section>';
  async function iniciar() {
    try {
      sessao = await sessaoCatalogo();
      if (!vivo()) return;
      if (sessao) {
        try { moderador = await moderadorCatalogo(); }
        catch { if (vivo()) avisar('Não foi possível verificar o acesso à revisão. A consulta pública continua disponível.'); }
      }
      if (!vivo()) return;
      desenharConta(); desenharControles(); await atualizar();
    } catch (e) {
      if (!vivo()) return;
      conta.innerHTML = `<section class="cartao erro"><p>${esc(e.message)}</p><button type="button" data-reiniciar>Tentar conectar novamente</button></section>`;
      conta.querySelector('[data-reiniciar]').addEventListener('click', iniciar);
    }
  }
  iniciar();
}
