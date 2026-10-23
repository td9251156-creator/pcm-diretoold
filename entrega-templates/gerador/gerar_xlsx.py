"""Gera PCM-Direto-Modelos.xlsx (em branco) e PCM-Direto-Exemplo.xlsx (dados fictícios).

As duas pastas usam a mesma função de montagem; o exemplo apenas recebe dados.
Fórmulas são gravadas em inglês (padrão OOXML); o Excel em português mostra SE, ÍNDICE, CORRESP...
"""
import datetime as dt
import json

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter as letra
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.pagebreak import Break

import especificacao as E
from comum import (AUTOR, AVISO, AVISO_FUNDO, AVISO_TEXTO, AZUL, AZUL_CLARO, BRANCO, CINZA_CALCULO, CONTATO,
                   DATA_MODELO, DESTAQUE, FONTE, LICENCA, LOGO_PNG, RAIZ_REPO, SEGURANCA, VERSAO_MODELO, clarear, dividir_aviso)

FINO = Side(style="thin", color="A6A6A6")
BORDA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
F_NORMAL = Font(name=FONTE, size=10)
F_CALC = Font(name=FONTE, size=10, color="333333")
F_FUTURO = Font(name=FONTE, size=10, italic=True, color="595959")
F_CAB = Font(name=FONTE, size=10, bold=True, color=BRANCO)
F_TITULO = Font(name=FONTE, size=14, bold=True, color=AZUL)
F_SUB = Font(name=FONTE, size=11, bold=True, color=AZUL)
F_AVISO = Font(name=FONTE, size=10, bold=True, color=AVISO_TEXTO)
F_NEGRITO = Font(name=FONTE, size=10, bold=True)
F_PEQ = Font(name=FONTE, size=9, color="404040")

def preench(cor):
    return PatternFill("solid", fgColor=cor)

P_CAB = preench(AZUL)
P_AVISO = preench(AVISO_FUNDO)
P_CALC = preench(CINZA_CALCULO)
P_ENTRADA = preench(BRANCO)
P_REF = preench(clarear(DESTAQUE, 0.9))
P_FUTURO = preench("F5F5F5")
P_TIPO = {"id": preench(AZUL_CLARO), "entrada": preench(AZUL_CLARO), "referencia": preench(clarear(DESTAQUE, 0.8)),
          "calculo": preench("D0D0D0"), "manual": preench(AZUL_CLARO), "futuro": preench("E7E6E6")}
QUEBRA = Alignment(wrap_text=True, vertical="top")
QUEBRA_C = Alignment(wrap_text=True, vertical="center")

FORMATO_TEXTO = "@"

AVISO_L1, AVISO_L2 = dividir_aviso()


def texto(cell, valor):
    """Grava texto como texto, mesmo que comece com =, +, - ou @ (não vira fórmula)."""
    cell.value = valor
    if isinstance(valor, str):
        cell.data_type = "s"
        if valor[:1] in "=+-@":
            cell.quotePrefix = True


def nome(wb, nome_def, ref):
    wb.defined_names[nome_def] = DefinedName(nome_def, attr_text=ref)


def ref_abs(aba, col, l1, l2=None):
    c = letra(col) if isinstance(col, int) else col
    return f"'{aba}'!${c}${l1}" + (f":${c}${l2}" if l2 else "")


def configurar_impressao(ws, paisagem, ultima_col, ultima_linha, titulos="5:6", largura=1, colunas=None):
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "landscape" if paisagem else "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = largura
    ws.page_setup.pageOrder = "overThenDown"  # partes esquerda e direita da mesma linha em sequência
    ws.page_setup.fitToHeight = 0  # quantas páginas forem necessárias na altura
    ws.page_margins.left = ws.page_margins.right = 0.5
    ws.page_margins.top = 0.75
    ws.page_margins.bottom = 0.85
    ws.page_margins.header = 0.3
    ws.page_margins.footer = 0.3
    ws.print_options.horizontalCentered = False
    if titulos:
        ws.print_title_rows = titulos
    if colunas:
        ws.print_title_cols = colunas
    ws.print_area = f"A1:{letra(ultima_col)}{ultima_linha}"
    # Rodapé: só o aviso completo (233 caracteres com os códigos, abaixo do limite de 255).
    ws.oddFooter.left.text = f"{AVISO_L1}\n{AVISO_L2}"
    ws.oddFooter.left.size = 7
    ws.oddFooter.left.font = "Arial,Regular"
    ws.oddHeader.left.text = "PCM Direto · &A"
    ws.oddHeader.left.size = 8
    ws.oddHeader.left.font = "Arial,Bold"
    ws.oddHeader.right.text = "Página &P de &N"
    ws.oddHeader.right.size = 8
    ws.oddHeader.right.font = "Arial,Regular"


def topo(ws, titulo, instrucao, ncols, capacidade_txt=None):
    """Linhas 1 a 4: título, aviso, instrução, origem/emissão/capacidade."""
    ws["A1"].value = titulo
    ws["A1"].font = F_TITULO
    ws.row_dimensions[1].height = 22
    ultima = letra(max(ncols, 2))
    ws.merge_cells(f"A2:{ultima}2")
    texto(ws["A2"], f"AVISO: {AVISO}")
    ws["A2"].font = F_AVISO
    ws["A2"].fill = P_AVISO
    ws["A2"].alignment = QUEBRA_C
    ws.row_dimensions[2].height = 42 if ncols >= 8 else 70
    ws.merge_cells(f"A3:{ultima}3")
    texto(ws["A3"], instrucao)
    ws["A3"].font = F_PEQ
    ws["A3"].alignment = QUEBRA_C
    ws.row_dimensions[3].height = 30 if ncols >= 8 else 56
    o_fim = max(3, ncols // 2) if ncols >= 6 else 2
    ws["A4"].value = "Origem:"
    ws["A4"].font = F_NEGRITO
    if o_fim > 2:
        ws.merge_cells(start_row=4, start_column=2, end_row=4, end_column=o_fim)
    c = ws.cell(4, 2, '=IF(pcmd_origem="","Não informada (preencha no Leia-me)",pcmd_origem)')
    c.font = F_NORMAL
    c.alignment = Alignment(wrap_text=True, vertical="center")
    c = ws.cell(4, o_fim + 1, "Emissão:")
    c.font = F_NEGRITO
    c.alignment = Alignment(horizontal="right")
    c = ws.cell(4, o_fim + 2, '=IF(ISNUMBER(pcmd_emissao),pcmd_emissao,"Não informada")')
    c.number_format = "dd/mm/yyyy"
    c.font = F_NORMAL
    c.alignment = Alignment(horizontal="left")
    if capacidade_txt and o_fim + 3 <= ncols:
        if o_fim + 3 < ncols:
            ws.merge_cells(start_row=4, start_column=o_fim + 3, end_row=4, end_column=ncols)
        c = ws.cell(4, o_fim + 3, capacidade_txt)
        c.font = F_PEQ
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[4].height = 30


def estilo_dado(cell, col):
    if col.papel == "calculo":
        cell.fill, cell.font = P_CALC, F_CALC
    elif col.papel == "referencia":
        cell.fill, cell.font = P_REF, F_NORMAL
    elif col.papel == "futuro":
        cell.fill, cell.font = P_FUTURO, F_FUTURO
    else:
        cell.fill, cell.font = P_ENTRADA, F_NORMAL
    cell.border = BORDA
    cell.alignment = Alignment(vertical="top", wrap_text=col.largura >= 20)
    if col.numero:
        cell.number_format = col.numero
    elif col.papel != "calculo" and col.tipo in ("texto", "lista", "sim_nao"):
        cell.number_format = FORMATO_TEXTO
    if col.papel in ("entrada", "manual", "futuro") or (col.papel == "id" and col.id.startswith(("execucao", "falha", "pessoa", "requisito", "ocorrencia", "ativo"))):
        cell.protection = Protection(locked=False)


def escrever_valor(cell, col, valor):
    if valor is None or valor == "":
        return
    if col.tipo == "data":
        if isinstance(valor, str):
            valor = dt.date.fromisoformat(valor)
        cell.value = valor
    elif col.tipo in ("numero_horas", "inteiro", "percentual"):
        cell.value = valor
    else:
        texto(cell, str(valor))


def cabecalho_tabela(ws, colunas, linha_tipo, linha_cab, col0=1):
    for i, col in enumerate(colunas):
        c = ws.cell(linha_tipo, col0 + i, E.PAPEIS[col.papel][0])
        c.font = Font(name=FONTE, size=8, bold=True, color="262626")
        c.fill = P_TIPO[col.papel]
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDA
        c = ws.cell(linha_cab, col0 + i, col.cabecalho)
        c.font, c.fill, c.border = F_CAB, P_CAB, BORDA
        c.alignment = QUEBRA_C
        nota = f"{E.PAPEIS[col.papel][1]}\nOrigem: {col.origem}\nVazio: {col.vazio}"
        if col.validacao != "—":
            nota += f"\nValidação: {col.validacao}"
        if col.obs:
            nota += f"\n{col.obs}"
        c.comment = Comment(nota[:1500], "PCM Direto")
        c.comment.width, c.comment.height = 320, 160
        ws.column_dimensions[letra(col0 + i)].width = col.largura
    ws.row_dimensions[linha_tipo].height = 24
    ws.row_dimensions[linha_cab].height = 48


def aplicar_validacoes(ws, colunas, l1, l2, col0=1):
    for i, col in enumerate(colunas):
        if not col.dv:
            continue
        L = letra(col0 + i)
        d = dict(col.dv)
        f1 = d.pop("formula1").replace("{c}", f"{L}{l1}")
        f2 = d.pop("formula2", None)
        erro, prompt = d.pop("error"), d.pop("prompt")
        dv = DataValidation(formula1=f1, formula2=f2, allow_blank=True, showErrorMessage=True, showInputMessage=True,
                            errorTitle="Valor não aceito", error=erro[:255], promptTitle=col.cabecalho[:32], prompt=prompt[:255], **d)
        dv.add(f"{L}{l1}:{L}{l2}")
        ws.add_data_validation(dv)


def formatacao_condicional(ws, ncols, l1, l2, colunas, col0=1):
    area = f"{letra(col0)}{l1}:{letra(col0 + ncols - 1)}{l2}"
    for i, col in enumerate(colunas):
        L = letra(col0 + i)
        alvo = f"{L}{l1}:{L}{l2}"
        if col.papel == "calculo" and col.tipo == "texto":
            ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'LEFT({L}{l1},4)="ERRO"'], stopIfTrue=True,
                                                            fill=preench(AVISO_FUNDO), font=Font(name=FONTE, bold=True, color=SEGURANCA)))
            ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'OR(LEFT({L}{l1},8)="Pendente",LEFT({L}{l1},9)="Verificar",LEFT({L}{l1},9)="Duplicada",LEFT({L}{l1},7)="Tarefa ",LEFT({L}{l1},5)="Ativo")'],
                                                            fill=preench(AVISO_FUNDO), font=Font(name=FONTE, color=AVISO_TEXTO)))
        if col.id in ("tarefa.seguranca",):
            ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'{L}{l1}="Sim"'], font=Font(name=FONTE, bold=True, color=SEGURANCA)))
    _ = area


def montar_aba_tabela(wb, aba, linhas, versao_exemplo):
    ws = wb.create_sheet(aba.nome)
    n = len(aba.colunas)
    l1, l2 = E.PRIMEIRA, E.PRIMEIRA + aba.capacidade - 1
    cap_txt = (f'=IF(COUNTA(A{l2 + 1}:A{l2 + 2000})>0,"ATENÇÃO: há dados abaixo da linha {l2}: estenda fórmulas, validações e nomes (ver Leia-me)",'
               f'"Capacidade: {aba.capacidade} linhas (7 a {l2}); preenchidas: "&COUNTA(A{l1}:A{l2}))')
    topo(ws, aba.titulo, aba.instrucao, n, cap_txt)
    cabecalho_tabela(ws, aba.colunas, E.LINHA_TIPO, E.LINHA_CAB)
    for r in range(l1, l2 + 1):
        dado = linhas[r - l1] if r - l1 < len(linhas) else None
        for i, col in enumerate(aba.colunas):
            cell = ws.cell(r, i + 1)
            estilo_dado(cell, col)
            if col.formula:
                cell.value = col.formula.replace("{r}", str(r))
            elif dado is not None:
                escrever_valor(cell, col, dado.get(col.id))
    for i, col in enumerate(aba.colunas):
        if col.nome:
            nome(wb, col.nome, ref_abs(aba.nome, i + 1, l1, l2))
    aplicar_validacoes(ws, aba.colunas, l1, l2)
    formatacao_condicional(ws, n, l1, l2, aba.colunas)
    ws.freeze_panes = ws.cell(l1, aba.congelar_col + 1)
    ws.auto_filter.ref = f"A{E.LINHA_CAB}:{letra(n)}{l2}"
    usadas = len(linhas) if versao_exemplo else aba.linhas_impressao_modelo
    configurar_impressao(ws, aba.paisagem, n, l1 + max(usadas, 1) - 1, largura=aba.paginas_largura, colunas=aba.colunas_repetidas)
    if aba.protegida:
        ws.protection.sheet = True
        ws.protection.autoFilter = False
        ws.protection.sort = False
        ws.protection.formatColumns = False
        ws.protection.formatRows = False
        ws.protection.selectLockedCells = False
        ws.protection.selectUnlockedCells = False
    return ws


def bloco_titulo(ws, linha, titulo, ncols=7):
    c = ws.cell(linha, 1, titulo)
    c.font = F_SUB
    for i in range(1, ncols + 1):
        ws.cell(linha, i).border = Border(bottom=Side(style="medium", color=AZUL))


def montar_cadastros(wb, dados):
    ws = wb.create_sheet("Cadastros")
    topo(ws, "Cadastros · Organização, limites, metas, setores, pessoas e requisitos",
         "Preencha uma vez. Pessoas e requisitos ficam neste arquivo local; não publique. "
         "Metas vazias permanecem A definir. Requisitos começam Não verificado.", 7)
    for i, w in enumerate([30, 26, 26, 26, 22, 18, 34], start=1):
        ws.column_dimensions[letra(i)].width = w
    g = dados.get("gestao") if dados else None

    def cab(linha, titulos):
        for i, t in enumerate(titulos, start=1):
            c = ws.cell(linha, i, t)
            c.font, c.fill, c.border, c.alignment = F_CAB, P_CAB, BORDA, QUEBRA_C
        ws.row_dimensions[linha].height = 32

    def entrada(cell, valor=None, fmt=None, calc=False):
        cell.border = BORDA
        cell.fill = P_CALC if calc else P_ENTRADA
        cell.font = F_CALC if calc else F_NORMAL
        cell.alignment = QUEBRA
        if fmt:
            cell.number_format = fmt
        if valor not in (None, ""):
            if isinstance(valor, str) and not valor.startswith("=IF") and not valor.startswith("=AND"):
                texto(cell, valor)
            else:
                cell.value = valor

    # Bloco 1: organização
    bloco_titulo(ws, 6, "Bloco 1 · Organização (M1)")
    cab(7, ["Campo", "Valor (ENTRADA)", "Nome / resultado (CÁLCULO)", "Observação"])
    org = g["organizacao"] if g else {"nome": "", "referencial": "GERAL (sem norma)", "padraoCodigo": "PCMD", "elaborador": "", "aprovador": ""}
    linhas = [
        ("Nome da organização", org["nome"], None, "Opcional. Ex.: Indústria Exemplo."),
        ("Referencial", org["referencial"], None, "Padrão GERAL (sem norma). Não citar norma sem fonte oficial, versão e data."),
        ("Prefixo dos documentos", org["padraoCodigo"], None, "Padrão PCMD."),
        ("Elaborador padrão (ID da pessoa)", org["elaborador"], '=IF(B11="","",IFERROR(INDEX(cad_pessoa_nome,MATCH(B11,cad_pessoa_id,0)),"Pessoa não cadastrada"))', "ID do bloco Pessoas."),
        ("Aprovador padrão (ID da pessoa)", org["aprovador"], '=IF(B12="","A definir (aprovação não registrada)",IFERROR(INDEX(cad_pessoa_nome,MATCH(B12,cad_pessoa_id,0)),"Pessoa não cadastrada"))', "Só informe após aprovação efetiva."),
    ]
    for k, (rot, val, form, obs) in enumerate(linhas):
        r = 8 + k
        ws.cell(r, 1, rot).font = F_NEGRITO
        entrada(ws.cell(r, 2), val, FORMATO_TEXTO)
        ws.cell(r, 2).protection = Protection(locked=False)
        entrada(ws.cell(r, 3), form, calc=True)
        texto(ws.cell(r, 4), obs)
        ws.cell(r, 4).font = F_PEQ
        ws.cell(r, 4).alignment = QUEBRA
    nome(wb, "cad_org_nome", "'Cadastros'!$B$8")
    nome(wb, "cad_referencial", "'Cadastros'!$B$9")
    nome(wb, "cad_prefixo", "'Cadastros'!$B$10")
    for celula in ("B11", "B12"):
        dv = DataValidation(type="list", formula1="=cad_pessoa_id", allow_blank=True, showErrorMessage=True,
                            error="Use um ID do bloco Pessoas.", errorTitle="Valor não aceito")
        dv.add(celula)
        ws.add_data_validation(dv)

    # Bloco 2: limites
    bloco_titulo(ws, 14, "Bloco 2 · Limites de criticidade (PCMD-02)")
    cab(15, ["Campo", "Valor (ENTRADA)", "Resultado (CÁLCULO)", "Regra"])
    lim = g["criticidade"]["limites"] if g else {"a": 12, "b": 9}
    for r, rot, val in ((16, "Limite A (soma mínima)", lim["a"]), (17, "Limite B (soma mínima)", lim["b"])):
        ws.cell(r, 1, rot).font = F_NEGRITO
        entrada(ws.cell(r, 2), val, "0")
        ws.cell(r, 2).protection = Protection(locked=False)
    ws.cell(18, 1, "Limites válidos?").font = F_NEGRITO
    entrada(ws.cell(18, 2), "=IF(AND(ISNUMBER(B16),ISNUMBER(B17)),AND(B16=INT(B16),B17=INT(B17),B17>=5,B17<B16,B16<=15),FALSE)", calc=True)
    entrada(ws.cell(18, 3), '=IF(B18,"Válidos","Inválidos: use inteiros com 5 ≤ B < A ≤ 15; classes ficam Pendente")', calc=True)
    texto(ws.cell(16, 4), "Inteiros, com 5 ≤ B < A ≤ 15. Padrão inicial: A = 12 e B = 9.")
    texto(ws.cell(17, 4), "Segurança = 3 resulta em A, qualquer que seja a soma.")
    texto(ws.cell(19, 1), "Regra: com as cinco notas válidas, Segurança = 3 → A; senão soma ≥ A → A; senão soma ≥ B → B; senão C. Faltando nota ou com limites inválidos → Pendente. A classe não altera frequências nem proteções de segurança.")
    ws.merge_cells("A19:G19")
    ws["A19"].alignment = QUEBRA
    ws["A19"].font = F_PEQ
    ws.row_dimensions[19].height = 30
    for r in (16, 17):
        ws.cell(r, 4).font = F_PEQ
    nome(wb, "cad_limite_a", "'Cadastros'!$B$16")
    nome(wb, "cad_limite_b", "'Cadastros'!$B$17")
    nome(wb, "cad_limites_ok", "'Cadastros'!$B$18")
    dv = DataValidation(type="whole", operator="between", formula1="5", formula2="15", allow_blank=False, showErrorMessage=True,
                        errorTitle="Limite não aceito", error="Use inteiro entre 5 e 15, com B menor que A.")
    dv.add("B16:B17")
    ws.add_data_validation(dv)

    # Bloco 3: níveis das notas
    bloco_titulo(ws, 21, "Bloco 3 · Significado dos níveis das notas (definição do mantenedor)")
    texto(ws.cell(22, 1), "O PCM Direto não define o significado técnico de cada nível. Preencha conforme o critério aprovado pelo profissional responsável.")
    ws.merge_cells("A22:G22")
    ws["A22"].font = F_PEQ
    ws["A22"].alignment = QUEBRA
    cab(23, ["Critério", "Nível 1 (MANUAL)", "Nível 2 (MANUAL)", "Nível 3 (MANUAL)", "Situação (CÁLCULO)"])
    for k, crit in enumerate(["N1 Segurança", "N2 Qualidade", "N3 Produção", "N4 Frequência de falha", "N5 Custo/tempo de reparo"]):
        r = 24 + k
        ws.cell(r, 1, crit).font = F_NEGRITO
        for c in (2, 3, 4):
            entrada(ws.cell(r, c), None, FORMATO_TEXTO)
            ws.cell(r, c).protection = Protection(locked=False)
        entrada(ws.cell(r, 5), f'=IF(COUNTA(B{r}:D{r})<3,"A definir pelo mantenedor","Definido")', calc=True)

    # Bloco 4: metas
    bloco_titulo(ws, 30, "Bloco 4 · Metas (M5)")
    cab(31, ["Meta", "Valor % (ENTRADA)", "Exibição (CÁLCULO)", "Observação"])
    metas = g["metas"] if g else {"disponibilidade": None, "aderencia": None}
    for r, rot, chave in ((32, "Meta de disponibilidade (%)", "disponibilidade"), (33, "Meta de aderência preventiva (%)", "aderencia")):
        ws.cell(r, 1, rot).font = F_NEGRITO
        v = metas[chave]
        entrada(ws.cell(r, 2), None if v is None else v / 100, "0.0%")
        ws.cell(r, 2).protection = Protection(locked=False)
        entrada(ws.cell(r, 3), f'=IF(B{r}="","A definir",B{r})', "0.0%", calc=True)
    texto(ws.cell(32, 4), "Disponibilidade, MTBF e MTTR não são calculados: regras técnicas pendentes.")
    texto(ws.cell(33, 4), "Comparação com o % realizado só depois de a meta ser definida.")
    for r in (32, 33):
        ws.cell(r, 4).font = F_PEQ
        ws.cell(r, 4).alignment = QUEBRA
    nome(wb, "cad_meta_disponibilidade", "'Cadastros'!$B$32")
    nome(wb, "cad_meta_aderencia", "'Cadastros'!$B$33")
    dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="1", allow_blank=True, showErrorMessage=True,
                        errorTitle="Meta não aceita", error="Informe um percentual entre 0% e 100%. Vazio = A definir.")
    dv.add("B32:B33")
    ws.add_data_validation(dv)

    # Blocos de tabela
    def bloco_tabela(titulo, linha_tit, linha_cab, cap, colunas, registros):
        bloco_titulo(ws, linha_tit, titulo)
        cabecalho_tabela(ws, colunas, linha_cab - 1, linha_cab)
        l1, l2 = linha_cab + 1, linha_cab + cap
        for r in range(l1, l2 + 1):
            dado = registros[r - l1] if r - l1 < len(registros) else None
            for i, col in enumerate(colunas):
                cell = ws.cell(r, i + 1)
                estilo_dado(cell, col)
                if col.formula:
                    cell.value = col.formula.replace("{r}", str(r))
                elif dado:
                    escrever_valor(cell, col, dado.get(col.id))
        for i, col in enumerate(colunas):
            if col.nome:
                nome(wb, col.nome, ref_abs("Cadastros", i + 1, l1, l2))
        aplicar_validacoes(ws, colunas, l1, l2)
        formatacao_condicional(ws, len(colunas), l1, l2, colunas)
        # nas linhas de tipo, a largura já foi definida pelo primeiro bloco; mantemos as larguras fixas
        for i, w in enumerate([30, 26, 26, 26, 22, 18, 34], start=1):
            ws.column_dimensions[letra(i)].width = w

    setores = [{"setor.sigla": s, "setor.descricao": ""} for s in (g["organizacao"]["setores"] if g else [])]
    pessoas = [{"pessoa.id": p["id"], "pessoa.nome": p["nome"], "pessoa.funcao": p["funcao"], "pessoa.especialidade": p["especialidade"],
                "pessoa.ativo": "Sim" if p["ativo"] else "Não"} for p in (g["pessoas"] if g else [])]
    reqs = [{"requisito.id": q["id"], "requisito.referencia": q["referencia"], "requisito.versao": q["versao"], "requisito.data": q["data"],
             "requisito.fonte": q["fonte"], "requisito.status": "Verificado" if q["status"] == "verificado" else "Não verificado"}
            for q in (g["requisitos"] if g else [])]
    C = E.CAD
    bloco_tabela("Bloco 5 · Setores", C["setores_cab"] - 2, C["setores_cab"], C["setores_cap"], E.COLUNAS_SETORES, setores)
    bloco_tabela("Bloco 6 · Pessoas e funções (M3)", C["pessoas_cab"] - 2, C["pessoas_cab"], C["pessoas_cap"], E.COLUNAS_PESSOAS, pessoas)
    bloco_tabela("Bloco 7 · Requisitos e referências (M6)", C["req_cab"] - 2, C["req_cab"], C["req_cap"], E.COLUNAS_REQUISITOS, reqs)
    ws.row_breaks.append(Break(id=C["pessoas_cab"] - 3))
    ws.row_breaks.append(Break(id=C["req_cab"] - 3))
    ws.freeze_panes = "A5"
    fim = C["req_cab"] + (max(len(reqs), 1) + 2 if dados else 15)
    configurar_impressao(ws, True, 7, fim, titulos=None)
    return ws


def montar_listas(wb, biblioteca):
    ws = wb.create_sheet("Listas")
    topo(ws, "Listas · Valores aceitos nas validações",
         "Fonte: src/logica/plano.js (frequências) e src/dados/biblioteca.json (tipos e especialidades). "
         "Ao acrescentar itens, mantenha-os dentro dos intervalos nomeados (ver Leia-me).", 21)
    blocos = [
        (1, ["Frequência", "Execuções no ciclo de 52 semanas", "Observação"], [list(f) for f in E.FREQUENCIAS], [("lst_frequencias", 0, 8), ("lst_frequencias_vezes", 1, 8)], [12, 12, 30]),
        (5, ["Especialidade"], [[e] for e in especialidades(biblioteca)], [("lst_especialidades", 0, 30)], [16]),
        (7, ["Tipo (ID)", "Tipo (nome)", "Sigla"], [[t["id"], t["nome"], t["sigla"]] for t in biblioteca["tipos"]],
         [("lst_tipo_id", 0, 30), ("lst_tipo_nome", 1, 30), ("lst_tipo_sigla", 2, 30)], [18, 18, 7]),
        (11, ["Sim/Não"], [["Sim"], ["Não"]], [("lst_sim_nao", 0, 2)], [8]),
        (13, ["Origem da execução"], [["app"], ["legado"]], [("lst_origem_execucao", 0, 2)], [11]),
        (15, ["Status de requisito"], [["Não verificado"], ["Verificado"]], [("lst_status_requisito", 0, 2)], [15]),
        (17, ["Situação do documento (proposta)"], [[s] for s in E.SITUACOES_DOCUMENTO], [("lst_situacao_documento", 0, 10)], [16]),
        (19, ["Tipo de documento"], [[t] for t in E.TIPOS_DOCUMENTO], [("lst_tipo_documento", 0, 10)], [15]),
        (21, ["Tipos de tarefa (consulta; sem campo no app)"], [[t] for t in E.TIPOS_TAREFA_REFERENCIA], [], [18]),
    ]
    for col0, titulos, valores, nomes, larguras in blocos:
        for i, t in enumerate(titulos):
            c = ws.cell(E.LINHA_TIPO, col0 + i, "REFERÊNCIA")
            c.font = Font(name=FONTE, size=8, bold=True)
            c.fill = P_TIPO["referencia"]
            c.border = BORDA
            c = ws.cell(E.LINHA_CAB, col0 + i, t)
            c.font, c.fill, c.border, c.alignment = F_CAB, P_CAB, BORDA, QUEBRA_C
            ws.column_dimensions[letra(col0 + i)].width = larguras[i]
        altura = max([n[2] for n in nomes] + [len(valores)])
        for k in range(altura):
            for i in range(len(titulos)):
                cell = ws.cell(E.PRIMEIRA + k, col0 + i)
                cell.border = BORDA
                cell.font = F_NORMAL
                cell.fill = P_REF
                if k < len(valores):
                    v = valores[k][i]
                    if isinstance(v, str):
                        texto(cell, v)
                    else:
                        cell.value = v
        for nm, desloc, tam in nomes:
            nome(wb, nm, ref_abs("Listas", col0 + desloc, E.PRIMEIRA, E.PRIMEIRA + tam - 1))
    for c in (4, 6, 10, 12, 14, 16, 18, 20):
        ws.column_dimensions[letra(c)].width = 2
    ws.row_dimensions[E.LINHA_CAB].height = 48
    ws.freeze_panes = "A7"
    configurar_impressao(ws, True, 21, E.PRIMEIRA + 30 - 1)


def especialidades(biblioteca):
    vistas = []
    for t in biblioteca["tipos"]:
        for tarefa in t["tarefas"]:
            if tarefa["especialidade"] not in vistas:
                vistas.append(tarefa["especialidade"])
    return vistas


def montar_cronograma(wb, dados):
    ws = wb.create_sheet("PCMD-04 Cronograma", 4)
    topo(ws, "PCMD-04 · Cronograma: resumo mensal por ocorrência prevista",
         "Informe o ano consultado. O mês é o da data PREVISTA. % realizado = ocorrências concluídas distintas ÷ previstas distintas. "
         "Horas são estimadas a partir da duração da tarefa; não são horas trabalhadas.", 7)
    for i, w in enumerate([10, 30, 16, 16, 14, 16, 30], start=1):
        ws.column_dimensions[letra(i)].width = w
    bloco_titulo(ws, 6, "Parâmetros")
    par = [
        (7, "Ano consultado (ENTRADA)", dados["ano"] if dados else None, "0", True),
        (8, "Início do ciclo (ENTRADA, informativo)", dt.date.fromisoformat(dados["inicio"]) if dados else None, "dd/mm/yyyy", True),
        (9, "Fonte das ocorrências (ENTRADA)", ("Cronograma do PCM Direto: 52 semanas a partir de 03/11/2025, calculado pela lógica do app para demonstração fictícia"
                                              if dados else None), FORMATO_TEXTO, True),
        (10, "Conferência do ano (CÁLCULO)", '=IF(ISNUMBER(crono_ano),IF(AND(crono_ano=INT(crono_ano),crono_ano>=1900,crono_ano<=9999),"OK","ERRO: ano inválido"),"Informe o ano consultado")', None, False),
        (11, "Meta de aderência (Cadastros)", '=IF(cad_meta_aderencia="","A definir",cad_meta_aderencia)', "0.0%", False),
    ]
    for r, rot, val, fmt, ent in par:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.cell(r, 1, rot).font = F_NEGRITO
        c = ws.cell(r, 3)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7 if r == 9 else 4)
        c.border = BORDA
        c.fill = P_ENTRADA if ent else P_CALC
        c.font = F_NORMAL if ent else F_CALC
        c.alignment = QUEBRA
        if fmt:
            c.number_format = fmt
        if ent:
            c.protection = Protection(locked=False)
        if isinstance(val, str) and not val.startswith("=IF"):
            texto(c, val)
        elif val is not None:
            c.value = val
    ws.row_dimensions[9].height = 30
    nome(wb, "crono_ano", "'PCMD-04 Cronograma'!$C$7")
    nome(wb, "crono_inicio", "'PCMD-04 Cronograma'!$C$8")
    dv = DataValidation(type="whole", operator="between", formula1="1900", formula2="9999", allow_blank=True, showErrorMessage=True,
                        errorTitle="Ano não aceito", error="Informe o ano com quatro dígitos.")
    dv.add("C7")
    ws.add_data_validation(dv)
    dv = DataValidation(type="date", operator="between", formula1="1", formula2="2958465", allow_blank=True, showErrorMessage=True,
                        errorTitle="Data não aceita", error="Informe uma data válida.")
    dv.add("C8")
    ws.add_data_validation(dv)

    def cab(linha, titulos):
        for i, t in enumerate(titulos, start=1):
            c = ws.cell(linha, i, t)
            c.font, c.fill, c.border, c.alignment = F_CAB, P_CAB, BORDA, QUEBRA_C
        ws.row_dimensions[linha].height = 44

    def calc(r, c, formula, fmt=None):
        cell = ws.cell(r, c, formula)
        cell.fill, cell.font, cell.border = P_CALC, F_CALC, BORDA
        if fmt:
            cell.number_format = fmt
        return cell

    cr = E.CRONO
    bloco_titulo(ws, cr["cab_mes"] - 1, "Resumo mensal do ano consultado (CÁLCULO)")
    cab(cr["cab_mes"], ["Mês (nº)", "Mês", "Ocorrências previstas (distintas)", "Ocorrências concluídas (distintas)", "% realizado",
                        "Horas estimadas previstas (h)", "Observação"])
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    for k, m in enumerate(meses):
        r = cr["jan"] + k
        calc(r, 1, k + 1, "0")
        calc(r, 2, m)
        calc(r, 3, f'=IF(NOT(ISNUMBER(crono_ano)),"",SUMIFS(oc_conta,oc_ano,crono_ano,oc_mes,A{r}))', "0")
        calc(r, 4, f'=IF(C{r}="","",SUMIFS(oc_concluida,oc_ano,crono_ano,oc_mes,A{r}))', "0")
        calc(r, 5, f'=IF(C{r}="","",IF(C{r}=0,"Sem previsão",D{r}/C{r}))', "0.0%")
        calc(r, 6, f'=IF(C{r}="","",SUMIFS(oc_horas,oc_conta,1,oc_ano,crono_ano,oc_mes,A{r}))', "0.00")
        calc(r, 7, f'=IF(C{r}="","",IF(C{r}=0,"Mês sem previsão: sem divisão por zero",""))')
    t = cr["total"]
    calc(t, 1, "")
    calc(t, 2, "Total do ano").font = Font(name=FONTE, bold=True)
    j, d = cr["jan"], cr["jan"] + 11
    calc(t, 3, f'=IF(NOT(ISNUMBER(crono_ano)),"",SUM(C{j}:C{d}))', "0")
    calc(t, 4, f'=IF(C{t}="","",SUM(D{j}:D{d}))', "0")
    calc(t, 5, f'=IF(C{t}="","",IF(C{t}=0,"Sem previsão",D{t}/C{t}))', "0.0%")
    calc(t, 6, f'=IF(C{t}="","",SUM(F{j}:F{d}))', "0.00")
    calc(t, 7, "")

    f0 = cr["fora_cab"]
    bloco_titulo(ws, f0 - 1, "Fora do ano consultado (separado, não descartado)")
    cab(f0, ["", "Posição", "Ocorrências previstas (distintas)", "Ocorrências concluídas (distintas)", "% realizado", "Horas estimadas previstas (h)", ""])
    for k, pos in enumerate(["Antes do ano", "Depois do ano"]):
        r = f0 + 1 + k
        calc(r, 1, "")
        calc(r, 2, pos)
        calc(r, 3, f'=IF(NOT(ISNUMBER(crono_ano)),"",SUMIFS(oc_conta,oc_posicao,B{r}))', "0")
        calc(r, 4, f'=IF(C{r}="","",SUMIFS(oc_concluida,oc_posicao,B{r}))', "0")
        calc(r, 5, f'=IF(C{r}="","",IF(C{r}=0,"Sem previsão",D{r}/C{r}))', "0.0%")
        calc(r, 6, f'=IF(C{r}="","",SUMIFS(oc_horas,oc_conta,1,oc_posicao,B{r}))', "0.00")
        calc(r, 7, "")

    s0 = cr["semv_cab"]
    bloco_titulo(ws, s0 - 1, "Execuções que não entram no percentual (ano da data realizada = ano consultado)")
    cab(s0, ["", "Situação", "Registros", "", "", "", "Observação"])
    linhas_s = [
        ("Sem vínculo (legado ou sem data prevista)", f'=IF(NOT(ISNUMBER(crono_ano)),"",COUNTIFS(ex_vinculo,"Sem vínculo",ex_cancelada,"<>Sim",ex_ano,crono_ano))', "Não aumentam o percentual."),
        ("Data prevista sem ocorrência no cronograma", f'=IF(NOT(ISNUMBER(crono_ano)),"",COUNTIFS(ex_vinculo,"Previsão não encontrada",ex_cancelada,"<>Sim",ex_ano,crono_ano))', "Conferir a data prevista informada."),
        ("Canceladas (preservadas no histórico)", f'=IF(NOT(ISNUMBER(crono_ano)),"",COUNTIFS(ex_cancelada,"Sim",ex_ano,crono_ano))', "Não contam."),
    ]
    for k, (rot, form, obs) in enumerate(linhas_s):
        r = s0 + 1 + k
        calc(r, 1, "")
        calc(r, 2, rot)
        calc(r, 3, form, "0")
        for c in (4, 5, 6):
            calc(r, c, "")
        calc(r, 7, obs)

    c0 = cr["conf_cab"]
    bloco_titulo(ws, c0 - 1, "Conferências")
    cab(c0, ["", "Verificação", "Resultado", "", "", "", "Como corrigir"])
    oc = E.OCORRENCIAS
    l2 = E.PRIMEIRA + oc.capacidade - 1
    linhas_c = [
        ("Ocorrências com ERRO", '=COUNTIF(oc_conferencia,"ERRO*")', "Ver coluna Conferência em PCMD-04 Ocorrências."),
        ("Linhas de ocorrência duplicadas (contadas uma vez)", '=COUNTIF(oc_conferencia,"Duplicada*")', "Remova a linha repetida."),
        ("Dados além da capacidade de PCMD-04 Ocorrências",
         f"=IF(COUNTA('PCMD-04 Ocorrências'!A{l2 + 1}:A{l2 + 5000})>0,\"ATENÇÃO: há linhas fora das fórmulas\",\"OK\")", "Estenda as fórmulas e os nomes (Leia-me)."),
        ("Dados além da capacidade de Execuções",
         f"=IF(COUNTA('Execuções'!A{E.PRIMEIRA + E.EXECUCOES.capacidade}:A{E.PRIMEIRA + E.EXECUCOES.capacidade + 5000})>0,\"ATENÇÃO: há linhas fora das fórmulas\",\"OK\")", "Estenda as fórmulas e os nomes (Leia-me)."),
    ]
    for k, (rot, form, obs) in enumerate(linhas_c):
        r = c0 + 1 + k
        calc(r, 1, "")
        calc(r, 2, rot)
        calc(r, 3, form, "0")
        for c in (4, 5, 6):
            calc(r, c, "")
        calc(r, 7, obs)
    for r in range(cr["jan"], c0 + 6):
        for c in (2, 7):
            ws.cell(r, c).alignment = QUEBRA
    ws.conditional_formatting.add(f"C{c0 + 1}:C{c0 + 4}", FormulaRule(formula=[f'LEFT(C{c0 + 1},8)="ATENÇÃO"'], fill=preench(AVISO_FUNDO),
                                                                     font=Font(name=FONTE, bold=True, color=SEGURANCA)))
    nota = c0 + 6
    ws.merge_cells(start_row=nota, start_column=1, end_row=nota, end_column=7)
    texto(ws.cell(nota, 1), "Notas: cada linha de PCMD-04 Ocorrências é um trio ativo + tarefa + data prevista. Concluída = existe ao menos uma execução não cancelada "
                            "vinculada a esse trio; duas execuções da mesma ocorrência contam uma vez. Diária = uma ocorrência por dia útil (segunda a sexta), sem feriados. "
                            "Não há campo de horas realizadas: o histórico atual não informa duração real.")
    ws.cell(nota, 1).alignment = QUEBRA
    ws.cell(nota, 1).font = F_PEQ
    ws.row_dimensions[nota].height = 54
    ws.freeze_panes = "A5"
    configurar_impressao(ws, False, 7, nota, titulos=None)


def montar_leiame(wb, dados, biblioteca):
    ws = wb.active
    ws.title = "Leia-me"
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 100
    ws["A1"].value = "PCM Direto · Modelos documentais (PCMD)"
    ws["A1"].font = F_TITULO
    ws.column_dimensions["C"].width = 12
    if LOGO_PNG.exists():  # logo original, quadrado: largura = altura preserva a proporção
        from openpyxl.drawing.image import Image as Imagem
        logo = Imagem(str(LOGO_PNG))
        logo.width = logo.height = 72
        ws.add_image(logo, "C1")
    ws.merge_cells("A2:B2")
    texto(ws["A2"], f"AVISO: {AVISO}")
    ws["A2"].font, ws["A2"].fill, ws["A2"].alignment = F_AVISO, P_AVISO, QUEBRA_C
    ws.row_dimensions[2].height = 34
    ws.merge_cells("A3:B3")
    texto(ws["A3"], f"Modelo versão {VERSAO_MODELO} ({dt.date.fromisoformat(DATA_MODELO):%d/%m/%Y}) · Autor: {AUTOR} · Contato público: {CONTATO} · Licença {LICENCA}. "
                    "Sem macros, sem vínculos externos, sem conexões de dados e sem envio de dados.")
    ws["A3"].font = F_PEQ
    ws["A3"].alignment = QUEBRA_C
    ws.row_dimensions[3].height = 28
    ws["A4"].value = "Origem dos dados:"
    ws["A4"].font = F_NEGRITO
    ws["B4"].value = '=IF(pcmd_origem="","Não informada (preencha a linha 7)",pcmd_origem)&"   ·   Emissão: "&IF(ISNUMBER(pcmd_emissao),DAY(pcmd_emissao)&"/"&MONTH(pcmd_emissao)&"/"&YEAR(pcmd_emissao),"não informada")'
    ws["B4"].font = F_NORMAL
    ws["B4"].alignment = QUEBRA

    linha = [6]

    def secao(titulo):
        r = linha[0]
        ws.cell(r, 1, titulo).font = F_SUB
        ws.cell(r, 1).border = Border(bottom=Side(style="medium", color=AZUL))
        ws.cell(r, 2).border = Border(bottom=Side(style="medium", color=AZUL))
        linha[0] += 1

    def item(rotulo, conteudo, altura=None, fill=None, negrito=False):
        r = linha[0]
        c = ws.cell(r, 1)
        texto(c, rotulo)
        c.font = F_NEGRITO
        c.alignment = QUEBRA
        if fill:
            c.fill = fill
            c.border = BORDA
        c = ws.cell(r, 2)
        texto(c, conteudo)
        c.font = F_NEGRITO if negrito else F_NORMAL
        c.alignment = QUEBRA
        linhas_txt = max(1, sum(1 + len(p) // 105 for p in conteudo.split("\n")))
        ws.row_dimensions[r].height = altura or max(15, 13.5 * linhas_txt)
        linha[0] += 1
        return r

    secao("Identificação desta emissão")
    r = item("Origem dos dados (ENTRADA)", "")
    c = ws.cell(r, 2)
    c.border, c.fill = BORDA, P_ENTRADA
    c.number_format = FORMATO_TEXTO
    c.protection = Protection(locked=False)
    if dados:
        texto(c, "Demonstração fictícia gerada com a lógica do PCM Direto (não é exportação do app)")
    nome(wb, "pcmd_origem", f"'Leia-me'!$B${r}")
    r = item("Data de emissão (ENTRADA)", "")
    c = ws.cell(r, 2)
    c.border, c.fill = BORDA, P_ENTRADA
    c.number_format = "dd/mm/yyyy"
    c.alignment = Alignment(horizontal="left")
    c.protection = Protection(locked=False)
    if dados:
        c.value = dt.date(2026, 10, 23)
    nome(wb, "pcmd_emissao", f"'Leia-me'!$B${r}")
    dv = DataValidation(type="date", operator="between", formula1="1", formula2="2958465", allow_blank=True, showErrorMessage=True,
                        errorTitle="Data não aceita", error="Informe uma data válida (dd/mm/aaaa).")
    dv.add(f"B{r}")
    ws.add_data_validation(dv)
    r = item("Organização (CÁLCULO)", "")
    ws.cell(r, 2).value = '=IF(cad_org_nome="","A definir (preencha em Cadastros)",cad_org_nome)'
    ws.cell(r, 2).fill, ws.cell(r, 2).font, ws.cell(r, 2).border = P_CALC, F_CALC, BORDA
    item("Biblioteca de referência", f"{biblioteca['nome']} versão {biblioteca['versao']} ({biblioteca['data']}), src/dados/biblioteca.json.")
    linha[0] += 1

    secao("Objetivo")
    item("Para que serve", "Organizar o Planejamento e Controle de Manutenção (PCM) de uma organização: lista de documentos, ativos e criticidade, "
                           "plano mestre, cronograma com acompanhamento mensal, execuções e falhas. É um modelo documental para uso local.")
    item("Três coisas diferentes", "1) Modelo de máquina compartilhado: referência reutilizável do catálogo público, sujeita a revisão; não é este arquivo.\n"
                                   "2) Ativo local: equipamento efetivo da organização, com ID próprio, setor, TAG, plano, criticidade e histórico.\n"
                                   "3) Template documental: esta pasta e os manuais Word, preenchidos com dados locais. Não consultam o catálogo nem enviam dados.")
    item("Integração", "O PCM Direto ainda não preenche este arquivo. O mapa proposto para um futuro adaptador está em CONTRATO-CAMPOS.json; "
                       "ele ainda será implementado e testado. Pessoas, falhas e execuções pertencem à gestão local e não devem ser publicadas.")
    linha[0] += 1

    secao("Sequência de preenchimento")
    passos = [
        ("1. Leia-me", "Informe origem dos dados e data de emissão (linhas acima)."),
        ("2. Cadastros", "Organização, limites A/B, significado dos níveis (manual), metas (vazio = A definir), setores, pessoas e requisitos."),
        ("3. PCMD-02 Ativos", "Um ativo por linha, com ID técnico e as cinco notas de criticidade."),
        ("4. PCMD-03 Plano Mestre", "Tarefas copiadas da biblioteca (colunas REFERÊNCIA). A aba é protegida sem senha: para incluir tarefas, use "
                                    "Revisão > Desproteger Planilha, cole as referências e proteja de novo."),
        ("5. PCMD-04 Ocorrências", "Uma linha por ativo + tarefa + data prevista, com a fonte da data. Depois informe o ano em PCMD-04 Cronograma."),
        ("6. Execuções", "Um registro por realização. Informe a data prevista para vincular à ocorrência; cancele marcando Sim."),
        ("7. PCMD-05 Ficha de Falha", "Um registro por falha; horas de parada são opcionais."),
        ("8. PCMD-01 e Revisões", "Atualize a lista mestra e o histórico de revisão dos documentos."),
    ]
    for a, b in passos:
        item(a, b)
    linha[0] += 1

    secao("Legenda (texto e cor)")
    legenda = [
        ("ENTRADA", "Célula para digitar (fundo branco). A linha 5 de cada tabela indica o papel de cada coluna.", P_ENTRADA),
        ("ID TÉCNICO", "Identificador estável. Não substitua por TAG, nome ou número de linha. Renomear ativo ou pessoa não muda o ID.", P_TIPO["id"]),
        ("REFERÊNCIA", "Conteúdo técnico da biblioteca/plano (fundo laranja-claro). No Plano Mestre fica protegido contra edição acidental.", P_REF),
        ("CÁLCULO", "Fórmula (fundo cinza). Não digite: o resultado se refaz ao recalcular.", P_CALC),
        ("MANUAL", "Preenchimento documental que o app não fornece (ex.: próxima revisão, significado dos níveis).", P_TIPO["manual"]),
        ("FUTURO", "Campo reservado, não integrado. Manter vazio.", P_FUTURO),
        ("Pendente / Verificar", "Resultado incompleto ou que precisa de conferência (texto + fundo amarelo).", preench(AVISO_FUNDO)),
        ("ERRO:", "Inconsistência que precisa de correção (texto + destaque).", preench(AVISO_FUNDO)),
        ("Segurança = Sim", "Tarefa de segurança: não pode ser retirada nem ter a frequência reduzida (texto Sim + destaque).", None),
    ]
    for a, b, f in legenda:
        item(a, b, fill=f)
    linha[0] += 1

    secao("Regras principais")
    item("IDs e chaves", "Chave da tarefa = ID do ativo|ID da tarefa. Chave da ocorrência = chave da tarefa|AAAA-MM-DD (data prevista). "
                         "Cada execução e cada falha tem ID próprio, pois pode haver vários registros para a mesma tarefa. "
                         "TAG e descrição das execuções e falhas ficam preservadas como foram registradas; um ativo removido não apaga o histórico.")
    item("Criticidade", "Cinco critérios, nesta ordem: Segurança, Qualidade, Produção, Frequência de falha e Custo/tempo de reparo. Notas inteiras de 1 a 3; "
                        "vazio é ausência, não zero. Faltando nota (ou com nota inválida ou limites inválidos) → Pendente. Com cinco notas: Segurança = 3 → A; "
                        "senão soma ≥ limite A → A; senão soma ≥ limite B → B; senão C. Limites iniciais A = 12 e B = 9 (inteiros, 5 ≤ B < A ≤ 15). "
                        "O significado de cada nível é definido pelo mantenedor (Cadastros). A classe nunca altera frequências.")
    item("Cronograma e percentual", "O plano vigente é a fonte. O app trabalha com 52 semanas a partir da data de início (sem calendário ISO e sem redistribuir tarefas). "
                                    "Diária = cinco dias úteis por semana, sem feriados; cada dia é uma ocorrência com a duração de um dia. "
                                    "Conta como concluída a ocorrência com pelo menos uma execução não cancelada vinculada; duas execuções contam uma vez; "
                                    "canceladas e execuções sem vínculo não contam (aparecem separadas). O mês é o da data prevista. "
                                    "% = concluídas distintas ÷ previstas distintas; mês sem previsão mostra Sem previsão. Previsões fora do ano ficam em quadro separado.")
    item("Datas, horas e vazios", "Datas são datas reais do Excel (dd/mm/aaaa). Horas são números decimais (1,5 = uma hora e meia), não horário do dia. "
                                  "Vazio significa não informado: horas de parada vazias não viram zero. Percentuais são frações com formato % (0,5 = 50%). "
                                  "Colunas de texto têm formato Texto: conteúdos que começam com =, +, - ou @ continuam texto.")
    item("Segurança das tarefas", "Tarefa marcada como segurança não pode ser excluída, desmarcada nem ter intervalo ampliado em relação à referência. "
                                  "A coluna Conferência mostra ERRO quando isso acontece. Validações e proteção do Excel evitam erro acidental, mas podem ser "
                                  "contornadas por colagem ou edição externa: não substituem as travas do app nem representam segurança de acesso.")
    item("Metas, requisitos e indicadores", "Referencial inicial GERAL (sem norma). Requisitos começam Não verificado; Verificado exige versão, data e fonte HTTPS "
                                            "e não certifica conformidade. Metas vazias ficam A definir. Não há cálculo de MTBF, MTTR, disponibilidade, vida útil, "
                                            "intervalos por criticidade ou prazos de parada sem regras aprovadas pelo mantenedor.")
    linha[0] += 1

    secao("Recálculo e fórmulas")
    item("Recálculo", "O arquivo pede recálculo completo ao abrir. Se aparecerem células vazias onde deveria haver resultado: Excel, Ctrl+Alt+F9; "
                      "LibreOffice Calc, Dados > Calcular > Recalcular incondicionalmente (Ctrl+Shift+F9). Visualizadores que não calculam fórmulas "
                      "(prévias de e-mail ou de celular) podem mostrar cálculos em branco.")
    item("Compatibilidade", "Feito para Excel 2010 ou posterior, com funções clássicas: sem PROCX, FILTRO, ÚNICO, CLASSIFICAR, SEQUÊNCIA, LET, LAMBDA, "
                            "matrizes dinâmicas, macros, VBA, Power Query, conexões ou vínculos externos. Testes executados estão em RELATORIO-DE-TESTES.md.")
    item("Nomes das funções", "O arquivo grava as fórmulas no padrão do formato (inglês); o Excel em português mostra automaticamente: IF = SE, AND = E, OR = OU, "
                              "NOT = NÃO, ISNUMBER = ÉNÚM, ISERROR = ÉERROS, IFERROR = SEERRO, COUNTIF = CONT.SE, COUNTIFS = CONT.SES, COUNTA = CONT.VALORES, "
                              "SUM = SOMA, SUMIFS = SOMASES, INDEX = ÍNDICE, MATCH = CORRESP, YEAR = ANO, MONTH = MÊS, DAY = DIA, LEFT = ESQUERDA, "
                              "RIGHT = DIREITA, LEN = NÚM.CARACT, FIND = PROCURAR, INT = INT, MAX = MÁXIMO, N = N.")
    caps = "; ".join(f"{a.nome}: {a.capacidade} linhas" for a in E.ABAS_TABELA) + \
        f"; Cadastros: {E.CAD['setores_cap']} setores, {E.CAD['pessoas_cap']} pessoas, {E.CAD['req_cap']} requisitos."
    item("Capacidade de linhas", f"Fórmulas, formatos e validações vão da linha 7 até: {caps} Cada tabela mostra na linha 4 a capacidade e um alerta "
                                 "ATENÇÃO quando há dados abaixo dela; PCMD-04 Cronograma também confere Ocorrências e Execuções.")
    item("Como ampliar", "1) Selecione a última linha da tabela inteira (todas as colunas) e copie. 2) Selecione as linhas abaixo e cole: fórmulas, formatos e "
                         "validações acompanham. 3) Em Fórmulas > Gerenciador de Nomes, estenda até a nova última linha os nomes da aba (ex.: at_id, pl_chave, "
                         "oc_chave, oc_conta, ex_chave_oc, ex_cancelada). 4) Ajuste a área de impressão (Layout da Página > Área de Impressão). "
                         "No Plano Mestre, desproteja a aba antes e proteja depois.")
    item("Impressão", "A4, orientação definida por aba, ajuste à largura de uma página e quantas páginas forem necessárias na altura. Cabeçalhos da tabela "
                      "se repetem em cada página. O aviso completo fica no rodapé de cada página e na linha 2 de cada aba. No modelo em branco, a área de impressão "
                      "cobre as primeiras linhas; amplie-a ao preencher.")
    linha[0] += 1
    secao("Dados e privacidade")
    item("Privacidade", "Nomes de pessoas, falhas, execuções e dados da organização são locais. Não publique este arquivo no catálogo público. "
                        "Exemplos usam apenas dados fictícios (Indústria Exemplo, Pessoa A, Pessoa B, fabricantes e modelos fictícios).")
    item("Responsabilidade", "Não há promessa de conformidade, aprovação em auditoria ou ganhos. Conteúdo técnico deve ser confirmado por profissional habilitado "
                             "e pelo manual do fabricante.")
    configurar_impressao(ws, False, 3, linha[0], titulos=None)
    ws.freeze_panes = "A5"


def gerar(destino, dados=None):
    with open(RAIZ_REPO / "src" / "dados" / "biblioteca.json", encoding="utf-8") as f:
        biblioteca = json.load(f)
    wb = Workbook()
    montar_leiame(wb, dados, biblioteca)
    linhas = linhas_dados(dados) if dados else {}
    montar_aba_tabela(wb, E.LISTA_MESTRA, linhas.get("lista", [{"documento.codigo": c, "documento.titulo": t, "documento.tipo": tp}
                                                              for c, t, tp in E.DOCUMENTOS_PCMD]), True)
    montar_aba_tabela(wb, E.ATIVOS, linhas.get("ativos", []), bool(dados))
    montar_aba_tabela(wb, E.PLANO, linhas.get("plano", []), bool(dados))
    montar_cronograma(wb, dados)
    montar_aba_tabela(wb, E.OCORRENCIAS, linhas.get("ocorrencias", []), bool(dados))
    montar_aba_tabela(wb, E.FALHAS, linhas.get("falhas", []), bool(dados))
    montar_aba_tabela(wb, E.EXECUCOES, linhas.get("execucoes", []), bool(dados))
    montar_cadastros(wb, dados)
    montar_listas(wb, biblioteca)
    montar_aba_tabela(wb, E.REVISOES, linhas.get("revisoes", []), bool(dados))
    # Ordem pedida: Leia-me, 01, 02, 03, 04, 05, Execuções, Cadastros, Listas, Revisões
    ordem = ["Leia-me", "PCMD-01 Lista Mestra", "PCMD-02 Ativos", "PCMD-03 Plano Mestre", "PCMD-04 Cronograma", "PCMD-04 Ocorrências",
             "PCMD-05 Ficha de Falha", "Execuções", "Cadastros", "Listas", "Revisões"]
    wb._sheets = [wb[n] for n in ordem]
    wb.active = 0
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.calcMode = "auto"
    wb.properties.creator = "PCM Direto (gerador de modelos)"
    wb.properties.title = "PCM Direto · Modelos documentais PCMD"
    wb.properties.subject = AVISO
    wb.properties.keywords = f"PCM Direto; modelo {VERSAO_MODELO}; licença MIT"
    wb.properties.created = wb.properties.modified = dt.datetime(2026, 10, 23, 12, 0, 0)
    wb.save(destino)
    corrigir_quebra_rodape(destino)


def corrigir_quebra_rodape(caminho):
    """O openpyxl grava a quebra de linha do rodapé como _x000a_; gravamos o caractere de nova linha real."""
    import shutil
    import zipfile
    temp = str(caminho) + ".tmp"
    with zipfile.ZipFile(caminho) as zin, zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            dados = zin.read(item.filename)
            if item.filename.startswith("xl/worksheets/sheet"):
                texto_xml = dados.decode("utf-8")
                if "<oddFooter>" in texto_xml:
                    ini = texto_xml.index("<oddFooter>")
                    fim = texto_xml.index("</oddFooter>")
                    texto_xml = texto_xml[:ini] + texto_xml[ini:fim].replace("_x000a_", "\n") + texto_xml[fim:]
                    dados = texto_xml.encode("utf-8")
            zout.writestr(item, dados)
    shutil.move(temp, caminho)


def linhas_dados(d):
    g = d["gestao"]
    nomes_tipo = {}
    ativos = []
    for e in d["equipamentos"]:
        notas = g["criticidade"]["notas"].get(e["id"], [None] * 5)
        ativos.append({"ativo.id": e["id"], "ativo.tag": e["tag"], "ativo.descricao": e["descricao"], "ativo.tipo_id": e["tipo"],
                       "ativo.fabricante": e.get("fabricante", ""), "ativo.modelo": e.get("modelo", ""), "ativo.setor": e["setor"],
                       "ativo.numero": e["numero"], "criticidade.nota_seguranca": notas[0], "criticidade.nota_qualidade": notas[1],
                       "criticidade.nota_producao": notas[2], "criticidade.nota_frequencia_falha": notas[3], "criticidade.nota_custo_reparo": notas[4]})
    _ = nomes_tipo
    plano = []
    for l in sorted(d["plano"], key=lambda x: (x["tag"], x["tarefaId"])):
        plano.append({"tarefa.ativo_id": l["equipamentoId"], "tarefa.id": l["tarefaId"], "tarefa.atividade": l["descricao"], "tarefa.origem": l["origem"],
                      "tarefa.versao": l["versao"], "tarefa.frequencia_referencia": l["periodicidadeOriginal"],
                      "tarefa.seguranca": "Sim" if l["seguranca"] else "Não", "tarefa.frequencia_vigente": l["periodicidade"],
                      "tarefa.especialidade": l["especialidade"], "tarefa.duracao_horas": l["duracaoHoras"], "tarefa.ativa": "Sim" if l["ativa"] else "Não",
                      "tarefa.responsavel_id": g["responsaveis"].get(f"{l['equipamentoId']}|{l['tarefaId']}", ""), "tarefa.observacao": l["observacao"]})
    fonte = "Cronograma do PCM Direto (52 semanas a partir de 03/11/2025), demonstração"
    ocorrencias = [{"ocorrencia.ativo_id": o["equipamentoId"], "ocorrencia.tarefa_id": o["tarefaId"], "ocorrencia.data_prevista": o["dataPrevista"],
                    "ocorrencia.fonte": fonte} for o in d["ocorrencias"]]
    execucoes = [{"execucao.id": h["id"], "execucao.ativo_id": h["equipamentoId"], "execucao.tarefa_id": h["tarefaId"], "execucao.tag": h["tag"],
                  "execucao.descricao": h["descricao"], "execucao.data_prevista": h["dataPrevista"], "execucao.data": h["data"],
                  "execucao.observacao": h["observacao"], "execucao.responsavel_id": h["responsavelId"], "execucao.origem": h["origem"],
                  "execucao.cancelada": "Sim" if h["cancelada"] else "Não"} for h in g["historico"]]
    falhas = [{"falha.id": f["id"], "falha.ativo_id": f["equipamentoId"], "falha.data": f["data"], "falha.tag": f["tag"], "falha.sintoma": f["sintoma"],
               "falha.causa": f["causa"], "falha.acao": f["acao"], "falha.horas_parada": f["horasParada"], "falha.peca": f["peca"],
               "falha.responsavel_id": f["responsavelId"]} for f in g["falhas"]]
    lista = [{"documento.codigo": c, "documento.titulo": t, "documento.tipo": tp, "documento.revisao": "00", "documento.data": "2026-10-23",
              "documento.elaborador": "Pessoa A", "documento.situacao": "Em elaboração", "documento.observacao": "Exemplo fictício"}
             for c, t, tp in E.DOCUMENTOS_PCMD]
    revisoes = [{"revisao.documento": c, "revisao.numero": "00", "revisao.data": "2026-10-23", "revisao.descricao": "Emissão inicial (exemplo fictício)",
                 "revisao.responsavel": "Pessoa A"} for c, _, _ in E.DOCUMENTOS_PCMD]
    return {"ativos": ativos, "plano": plano, "ocorrencias": ocorrencias, "execucoes": execucoes, "falhas": falhas, "lista": lista, "revisoes": revisoes}
