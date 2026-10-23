"""Gera CONTRATO-CAMPOS.json e DICIONARIO-DE-DADOS.md a partir da especificação e dos arquivos gerados."""
import json
from collections import OrderedDict

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter as letra

import especificacao as E
from comum import AVISO, DATA_MODELO, RAMO_GESTAO, VERSAO_MODELO

TIPOS = {
    "texto": "texto", "lista": "texto de lista fechada", "sim_nao": "texto 'Sim' ou 'Não'", "data": "data do Excel (número de série)",
    "numero_horas": "número decimal de horas", "inteiro": "número inteiro", "percentual": "fração 0–1 com formato %", "booleano": "VERDADEIRO/FALSO",
}


def campo_coluna(col, aba, indice, l1, l2):
    L = letra(indice)
    return OrderedDict([
        ("id", col.id), ("rotulo", col.cabecalho), ("tipo", TIPOS.get(col.tipo, col.tipo)), ("obrigatorio", col.obrigatorio),
        ("formato_unidade", col.formato if col.formato != "texto" else ("texto (célula com formato Texto)" if col.papel != "calculo" else "texto")),
        ("papel", col.papel), ("entrada_ou_calculo", "cálculo" if col.papel == "calculo" else "entrada"),
        ("origem_proposta", col.origem), ("situacao_origem", col.origem_status),
        ("destino", {"arquivo_aba": aba, "coluna": L, "cabecalho_linha": E.LINHA_CAB, "intervalo_dados": f"{L}{l1}:{L}{l2}",
                     "intervalo_nomeado": col.nome}),
        ("regra_vazio", col.vazio), ("validacao", col.validacao if col.validacao != "—" else (col.dv["type"] if col.dv else "—")),
        ("validacao_excel", None if not col.dv else {k: v for k, v in col.dv.items() if k in ("type", "operator", "formula1", "formula2")}),
        ("formula_modelo", col.formula), ("privacidade", col.privacidade), ("observacoes", col.obs),
    ])


def gerar(destino_json, destino_md, xlsx_modelo, docs):
    wb = load_workbook(xlsx_modelo)
    nomes = [{"nome": n, "referencia": d.attr_text} for n, d in sorted(wb.defined_names.items())]
    abas = []
    campos_todos = OrderedDict()

    def registrar(c):
        campos_todos.setdefault(c["id"], []).append(c["destino"])

    for aba in E.ABAS_TABELA:
        l1, l2 = E.PRIMEIRA, E.PRIMEIRA + aba.capacidade - 1
        cols = [campo_coluna(c, aba.nome, i + 1, l1, l2) for i, c in enumerate(aba.colunas)]
        for c in cols:
            registrar(c)
        abas.append(OrderedDict([("nome", aba.nome), ("codigo", aba.codigo or None), ("tipo_regiao", "tabela de linhas repetíveis"),
                                 ("linha_papel", E.LINHA_TIPO), ("linha_cabecalho", E.LINHA_CAB), ("primeira_linha", l1),
                                 ("ultima_linha_com_formulas", l2), ("capacidade_linhas", aba.capacidade), ("protegida_sem_senha", aba.protegida),
                                 ("colunas", cols)]))
    C = E.CAD
    blocos = []
    for titulo, cab, cap, colunas in (("Setores", C["setores_cab"], C["setores_cap"], E.COLUNAS_SETORES),
                                      ("Pessoas", C["pessoas_cab"], C["pessoas_cap"], E.COLUNAS_PESSOAS),
                                      ("Requisitos", C["req_cab"], C["req_cap"], E.COLUNAS_REQUISITOS)):
        l1, l2 = cab + 1, cab + cap
        cols = []
        for i, c in enumerate(colunas):
            d = campo_coluna(c, "Cadastros", i + 1, l1, l2)
            d["destino"]["cabecalho_linha"] = cab
            cols.append(d)
            registrar(d)
        blocos.append(OrderedDict([("bloco", titulo), ("linha_cabecalho", cab), ("primeira_linha", l1), ("ultima_linha_com_formulas", l2),
                                   ("capacidade_linhas", cap), ("colunas", cols)]))
    celulas = []
    for (cid, rot, cel, papel, tipo, origem, sit, vazio, val, priv, obs) in E.CAMPOS_CADASTROS:
        d = OrderedDict([("id", cid), ("rotulo", rot), ("tipo", TIPOS.get(tipo, tipo)), ("papel", papel),
                         ("entrada_ou_calculo", "cálculo" if papel == "calculo" else "entrada"), ("origem_proposta", origem),
                         ("situacao_origem", sit), ("destino", {"arquivo_aba": "Cadastros", "celula": cel}), ("regra_vazio", vazio),
                         ("validacao", val), ("privacidade", priv), ("observacoes", obs)])
        celulas.append(d)
        registrar(d)
    extras = [
        ("emissao.origem_dados", "Origem dos dados", "Leia-me", "B7", "entrada", "texto", "Texto curto do adaptador ou de quem preenche", E.FUTURO, "pcmd_origem"),
        ("emissao.data", "Data de emissão", "Leia-me", "B8", "entrada", "data", "Data em que o arquivo é gerado/preenchido", E.FUTURO, "pcmd_emissao"),
        ("cronograma.ano", "Ano consultado", "PCMD-04 Cronograma", E.CRONO["ano"], "entrada", "inteiro", "Escolha do usuário (resumoMensal(dados, gestao, ano))", E.RAMO, "crono_ano"),
        ("cronograma.inicio", "Início do ciclo (semana 1)", "PCMD-04 Cronograma", E.CRONO["inicio"], "entrada", "data", "estado.inicio (AAAA-MM-DD, main)", E.MAIN, "crono_inicio"),
        ("cronograma.fonte", "Fonte das ocorrências", "PCMD-04 Cronograma", E.CRONO["fonte"], "entrada", "texto", "Texto do adaptador", E.FUTURO, None),
    ]
    for cid, rot, aba, cel, papel, tipo, origem, sit, nm in extras:
        d = OrderedDict([("id", cid), ("rotulo", rot), ("tipo", TIPOS.get(tipo, tipo)), ("papel", papel), ("entrada_ou_calculo", "entrada"),
                         ("origem_proposta", origem), ("situacao_origem", sit), ("destino", {"arquivo_aba": aba, "celula": cel, "intervalo_nomeado": nm}),
                         ("regra_vazio", "Vazio = não informado."), ("privacidade", E.PRIV_NENHUM)])
        celulas.append(d)
        registrar(d)
    cr = E.CRONO
    resumo = OrderedDict([
        ("descricao", "Resumo mensal por ocorrência (equivale a resumoMensal do ramo de gestão). Somente cálculo; o adaptador não escreve aqui."),
        ("meses", f"linhas {cr['jan']} a {cr['jan'] + 11}; total na linha {cr['total']}"),
        ("colunas", {"C": "previstas distintas = SUMIFS(oc_conta, oc_ano, crono_ano, oc_mes, mês)",
                     "D": "concluídas distintas = SUMIFS(oc_concluida, oc_ano, crono_ano, oc_mes, mês)",
                     "E": "% = D/C; 'Sem previsão' quando C = 0 (app: percentual null; app usa escala 0–100, aqui fração 0–1)",
                     "F": "horas estimadas = SUMIFS(oc_horas, oc_conta, 1, oc_ano, crono_ano, oc_mes, mês)"}),
        ("fora_do_ano", f"linhas {cr['fora_cab'] + 1} (Antes do ano) e {cr['fora_cab'] + 2} (Depois do ano)"),
        ("sem_vinculo", f"linhas {cr['semv_cab'] + 1} a {cr['semv_cab'] + 3}: sem vínculo, previsão não encontrada, canceladas"),
        ("conferencias", f"linhas {cr['conf_cab'] + 1} a {cr['conf_cab'] + 4}"),
    ])
    arquivos_docx = []
    marcadores_doc = {m[0]: m for m in E.MARCADORES_DOC}
    for nome_arq, manual in docs:
        locais = OrderedDict()
        for mk, local in manual.marcadores_usados:
            locais.setdefault(mk, set()).add(local)
        simples = []
        for mk, ls in locais.items():
            if mk in marcadores_doc:
                _, desc, tipo, origem, sit, vazio = marcadores_doc[mk]
                simples.append(OrderedDict([("marcador", "{{" + mk + "}}"), ("id", mk), ("descricao", desc), ("tipo", TIPOS.get(tipo, tipo)),
                                            ("locais", sorted(ls)), ("origem_proposta", origem), ("situacao_origem", sit), ("regra_vazio", vazio)]))
        regioes = []
        for r in manual.regioes_usadas:
            spec = E.REGIOES_DOC[r["regiao"]]
            regioes.append(OrderedDict([("regiao", r["regiao"]), ("descricao", spec["descricao"]), ("tabela_indice_no_corpo", r["tabela_indice"]),
                                        ("linha_cabecalho", 0), ("linha_modelo", r["linha_modelo"]),
                                        ("marcadores_da_linha", ["{{" + c + "}}" for c in r["campos"]]),
                                        ("origem_proposta", spec["origem"]), ("situacao_origem", spec["situacao"]),
                                        ("regra", "Repetir a linha modelo uma vez por registro; sem registros, escrever 'Nenhum registro' na primeira célula.")]))
        arquivos_docx.append(OrderedDict([("arquivo", nome_arq), ("codigo", manual.codigo), ("titulo", manual.titulo),
                                          ("marcadores", simples), ("regioes_repetiveis", regioes)]))
        for s in simples:
            campos_todos.setdefault("docx:" + s["id"], []).append({"arquivo": nome_arq, "locais": s["locais"]})
    contrato = OrderedDict([
        ("$comentario", "Mapa PROPOSTO para um adaptador futuro. Não é formato de backup nem API aceita pelo PCM Direto. Não contém dados reais."),
        ("contrato", "PCM Direto · Contrato de campos dos modelos PCMD"),
        ("versao", 1), ("versao_modelo", VERSAO_MODELO), ("data", DATA_MODELO),
        ("situacao", "proposto, ainda não validado por adaptador ou pelo app"),
        ("aviso", AVISO),
        ("fontes_consultadas", [
            "AGENTS.md, BIBLIOTECA.md, src/marca.js (main, commit 6f09c92)",
            "src/logica/plano.js, src/logica/cronograma.js, src/logica/tag.js, src/logica/pacote.js, src/estado.js, src/dados/biblioteca.json (main)",
            f"src/logica/gestao.js, src/estado.js e src/telas/cadastros.js do ramo {RAMO_GESTAO}",
            "docs/INTERFACE-E-MODELOS.md (pasta de contexto do projeto; mesmo texto do ramo acima)",
        ]),
        ("limites", [
            "dadosAtuais() (montarDados) não inclui estado.gestao; o adaptador precisará ler estado.gestao separadamente.",
            "O exportador atual (src/saida/xlsx.js e docx.js) não escreve estes modelos.",
            "estado.gestao existe apenas no ramo indicado; se o ramo mudar antes da integração, revalidar este contrato.",
            "Este contrato não autoriza upload de backup nem envio de dados; o preenchimento deve ocorrer localmente.",
        ]),
        ("convencoes", OrderedDict([
            ("chave_tarefa", "equipamentoId|tarefaId"), ("chave_ocorrencia", "equipamentoId|tarefaId|AAAA-MM-DD (data prevista)"),
            ("ids", "IDs técnicos são texto [A-Za-z0-9_-]; nunca substituir por TAG, nome ou número de linha."),
            ("datas", "App usa texto AAAA-MM-DD; no XLSX gravar data real do Excel com formato dd/mm/aaaa. '' no app → célula vazia."),
            ("horas", "Número decimal (0.5 = meia hora). null no app → célula vazia (não zero)."),
            ("percentuais", "App guarda metas e percentuais em 0–100; no XLSX gravar fração 0–1 com formato %. Percentual do resumo é cálculo."),
            ("booleanos", "true/false no app → 'Sim'/'Não' no XLSX."),
            ("textos", "Gravar como texto (tipo string); conteúdo iniciado por =, +, - ou @ nunca vira fórmula."),
            ("formulas", "Gravadas em inglês/OOXML; o adaptador não deve sobrescrever colunas de cálculo nem nomes definidos."),
            ("capacidade", "Se os dados excederem a capacidade, estender fórmulas, validações e intervalos nomeados antes de escrever (ver COMO-USAR.md)."),
        ])),
        ("situacoes_origem", E.SITUACAO_ORIGEM),
        ("papeis", {k: v[1] for k, v in E.PAPEIS.items()}),
        ("ids_tecnicos", [
            {"id": "ativo.id", "onde": "PCMD-02 A; PCMD-03 A; PCMD-04 Ocorrências A; Execuções B; PCMD-05 B", "origem": "estado.equipamentos[].id"},
            {"id": "tarefa.id", "onde": "PCMD-03 B; PCMD-04 Ocorrências B; Execuções C", "origem": "biblioteca.tipos[].tarefas[].id"},
            {"id": "pessoa.id", "onde": "Cadastros (Pessoas) A; PCMD-03 P; Execuções K; PCMD-05 J; Cadastros B11/B12", "origem": "gestao.pessoas[].id"},
            {"id": "execucao.id", "onde": "Execuções A", "origem": "gestao.historico[].id"},
            {"id": "falha.id", "onde": "PCMD-05 A", "origem": "gestao.falhas[].id"},
            {"id": "requisito.id", "onde": "Cadastros (Requisitos) A", "origem": "gestao.requisitos[].id"},
        ]),
        ("arquivos", [
            OrderedDict([("arquivo", "PCM-Direto-Modelos.xlsx"), ("versao", "em branco"), ("mesma_estrutura_que", "PCM-Direto-Exemplo.xlsx"),
                         ("abas_tabela", abas), ("cadastros_blocos", blocos), ("celulas_unicas", celulas),
                         ("cronograma_resumo", resumo), ("intervalos_nomeados", nomes),
                         ("listas", {"lst_frequencias": [f[0] for f in E.FREQUENCIAS], "lst_situacao_documento": E.SITUACOES_DOCUMENTO,
                                     "lst_tipo_documento": E.TIPOS_DOCUMENTO, "lst_sim_nao": ["Sim", "Não"], "lst_origem_execucao": ["app", "legado"],
                                     "lst_status_requisito": ["Não verificado", "Verificado"]})]),
        ] + arquivos_docx),
        ("indice_campos", campos_todos),
    ])
    with open(destino_json, "w", encoding="utf-8") as f:
        json.dump(contrato, f, ensure_ascii=False, indent=2)
        f.write("\n")
    escrever_dicionario(destino_md, abas, blocos, celulas, arquivos_docx, nomes)


def _esc(t):
    return str(t if t is not None else "").replace("|", "\\|").replace("\n", " ")


def escrever_dicionario(destino, abas, blocos, celulas, docx, nomes):
    rot_sit = {E.MAIN: "app (main)", E.RAMO: "app (ramo de gestão, não integrado)", E.MANUAL: "manual", E.FUTURO: "futuro", E.CALCULO: "cálculo"}
    L = ["# Dicionário de dados dos modelos PCMD", "",
         f"Modelo versão {VERSAO_MODELO} · gerado a partir de `gerador/especificacao.py` (mesma fonte do `CONTRATO-CAMPOS.json`).", "",
         f"> **Aviso:** {AVISO}", "",
         "**Situação do mapeamento: proposto, ainda não validado.** A coluna Origem indica de onde o futuro adaptador poderia ler cada dado. "
         f"Campos marcados como *ramo de gestão* existem apenas no ramo `{RAMO_GESTAO}`. O app ainda não preenche estes arquivos.", "",
         "Legenda de papel: ENTRADA, ID TÉCNICO, REFERÊNCIA (protegida no Plano Mestre), CÁLCULO (não escrever), MANUAL (documental), FUTURO (manter vazio).", ""]
    for a in abas:
        L += [f"## {a['nome']}", "",
              f"Cabeçalho na linha {a['linha_cabecalho']}; dados de {a['primeira_linha']} a {a['ultima_linha_com_formulas']} "
              f"(capacidade {a['capacidade_linhas']} linhas){'; aba protegida sem senha' if a['protegida_sem_senha'] else ''}.", "",
              "| Col. | Campo | Cabeçalho | Papel | Tipo / formato | Obrig. | Origem proposta | Situação | Vazio | Validação |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for c in a["colunas"]:
            L.append(f"| {c['destino']['coluna']} | `{c['id']}` | {_esc(c['rotulo'])} | {E.PAPEIS[c['papel']][0]} | {_esc(c['formato_unidade'])} | "
                     f"{c['obrigatorio']} | {_esc(c['origem_proposta'])} | {rot_sit[c['situacao_origem']]} | {_esc(c['regra_vazio'])} | {_esc(c['validacao'])} |")
        L.append("")
    L += ["## Cadastros", "", "### Células únicas", "", "| Célula | Campo | Rótulo | Papel | Origem proposta | Situação | Vazio | Validação |", "|---|---|---|---|---|---|---|---|"]
    for c in celulas:
        L.append(f"| {c['destino']['arquivo_aba']}!{c['destino']['celula']} | `{c['id']}` | {_esc(c['rotulo'])} | {E.PAPEIS[c['papel']][0]} | "
                 f"{_esc(c['origem_proposta'])} | {rot_sit[c['situacao_origem']]} | {_esc(c['regra_vazio'])} | {_esc(c.get('validacao', '—'))} |")
    L.append("")
    for b in blocos:
        L += [f"### Bloco {b['bloco']}", "", f"Cabeçalho na linha {b['linha_cabecalho']}; dados de {b['primeira_linha']} a {b['ultima_linha_com_formulas']}.", "",
              "| Col. | Campo | Cabeçalho | Papel | Origem proposta | Situação | Vazio |", "|---|---|---|---|---|---|---|"]
        for c in b["colunas"]:
            L.append(f"| {c['destino']['coluna']} | `{c['id']}` | {_esc(c['rotulo'])} | {E.PAPEIS[c['papel']][0]} | {_esc(c['origem_proposta'])} | "
                     f"{rot_sit[c['situacao_origem']]} | {_esc(c['regra_vazio'])} |")
        L.append("")
    L += ["## Intervalos nomeados", "", "| Nome | Referência |", "|---|---|"] + [f"| `{n['nome']}` | `{n['referencia']}` |" for n in nomes] + [""]
    for d in docx:
        L += [f"## {d['arquivo']}", "", "### Marcadores", "", "| Marcador | Descrição | Locais | Origem proposta | Situação | Vazio |", "|---|---|---|---|---|---|"]
        for mk in d["marcadores"]:
            L.append(f"| `{mk['marcador']}` | {_esc(mk['descricao'])} | {', '.join(mk['locais'])} | {_esc(mk['origem_proposta'])} | "
                     f"{rot_sit[mk['situacao_origem']]} | {_esc(mk['regra_vazio'])} |")
        L += ["", "### Regiões repetíveis", "", "| Região | Tabela nº (corpo, a partir de 0) | Linha modelo | Marcadores da linha |", "|---|---|---|---|"]
        for r in d["regioes_repetiveis"]:
            L.append(f"| `{r['regiao']}` | {r['tabela_indice_no_corpo']} | {r['linha_modelo']} | {' '.join('`' + x + '`' for x in r['marcadores_da_linha'])} |")
        L.append("")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
