"""Gera os quatro arquivos XLSX dos modelos PCMD, cada um em branco e com exemplo fictício.

Cada arquivo é independente: nenhuma fórmula depende de outro arquivo. Modelo e exemplo saem da
mesma função de montagem; o exemplo apenas recebe dados. Fórmulas são gravadas em inglês (padrão
OOXML); o Excel em português mostra SE, ÍNDICE, CORRESP...
"""
import datetime as dt
import json
import math

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter as letra
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.pagebreak import Break

import especificacao as E
from comum import (AUTOR, AVISO, AVISO_FUNDO, AVISO_TEXTO, AZUL, CONTATO, DATA_MODELO, DESTAQUE, FONTE, LICENCA, LOGO_PNG,
                   RAIZ_REPO, SEGURANCA, VERSAO_MODELO, dividir_aviso)

# ------------------------------------------------------------------ paleta (marca + neutros)
TINTA = "1F2A37"        # texto principal
CINZA = "5B6875"        # texto secundário e cálculos
LINHA = "D5DDE5"        # linhas finas
ZEBRA = "F4F7FA"
CALC_FUNDO = "EBEFF3"
OK_TXT = "1E7B34"
ERRO_FUNDO = "FBE7EA"
AZUL_SUAVE = "E3ECF4"
COR_PAPEL = {"id": AZUL, "entrada": AZUL, "manual": AZUL, "referencia": DESTAQUE, "calculo": "4F6273", "futuro": "8C96A0"}


def preench(cor):
    return PatternFill("solid", fgColor=cor)


def fonte(tam=9.5, cor=TINTA, negrito=False, italico=False, sublinhado=None):
    return Font(name=FONTE, size=tam, color=cor, bold=negrito, italic=italico, underline=sublinhado)


FINO = Side(style="thin", color=LINHA)
B_LINHA = Border(bottom=FINO)
B_CAIXA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
B_CAB = Border(left=Side(style="thin", color="FFFFFF"), right=Side(style="thin", color="FFFFFF"),
               bottom=Side(style="medium", color=DESTAQUE))
B_SECAO = Border(bottom=Side(style="medium", color=DESTAQUE))
CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)
ESQ = Alignment(vertical="center", wrap_text=True, indent=1)
FORMATO_TEXTO = "@"
AVISO_L1, AVISO_L2 = dividir_aviso()


# ------------------------------------------------------------------ utilitários
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


def largura_total(ws, c1, c2):
    return sum(ws.column_dimensions[letra(c)].width or 9 for c in range(c1, c2 + 1))


def altura_texto(txt, largura, tam=9.5, minimo=15):
    """Altura aproximada de um texto com quebra em células mescladas (o Excel não ajusta mescladas)."""
    por_linha = max(8, largura * 1.15 * 10 / tam)
    linhas = sum(max(1, math.ceil(len(p) / por_linha)) for p in str(txt).split("\n"))
    return max(minimo, linhas * tam * 1.45 + 6)


def mesclar(ws, linha, c1, c2):
    if c2 > c1:
        ws.merge_cells(start_row=linha, start_column=c1, end_row=linha, end_column=c2)


def configurar_impressao(ws, paisagem, ultima_col, ultima_linha, codigo, titulos="6:6", largura=1, colunas=None):
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "landscape" if paisagem else "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = largura
    ws.page_setup.pageOrder = "overThenDown"  # partes esquerda e direita da mesma linha em sequência
    ws.page_setup.fitToHeight = 0
    ws.page_margins.left = ws.page_margins.right = 0.45
    ws.page_margins.top = 0.7
    ws.page_margins.bottom = 0.85
    ws.page_margins.header = 0.3
    ws.page_margins.footer = 0.3
    if titulos:
        ws.print_title_rows = titulos
    if colunas:
        ws.print_title_cols = colunas
    ws.print_area = f"A1:{letra(ultima_col)}{ultima_linha}"
    # Rodapé: o aviso completo em duas linhas (cerca de 235 caracteres com os códigos, abaixo do limite de 255).
    ws.oddFooter.left.text = f"{AVISO_L1}\n{AVISO_L2}"
    ws.oddFooter.left.size = 7
    ws.oddFooter.left.font = "Arial,Regular"
    ws.oddHeader.left.text = f"PCM Direto · {codigo} · &A"
    ws.oddHeader.left.size = 8
    ws.oddHeader.left.font = "Arial,Bold"
    ws.oddHeader.right.text = "Página &P de &N"
    ws.oddHeader.right.size = 8
    ws.oddHeader.right.font = "Arial,Regular"


def aviso_rico():
    return CellRichText(TextBlock(InlineFont(rFont=FONTE, sz=8, b=True, color=AVISO_TEXTO), "AVISO  "),
                        TextBlock(InlineFont(rFont=FONTE, sz=8, color=AVISO_TEXTO), AVISO))


def faixa_titulo(ws, codigo, titulo, ncols, c_ini=1):
    """Linha 1: selo com o código e faixa azul com o título."""
    c = ws.cell(1, 1, codigo)
    c.font, c.fill, c.alignment = fonte(10, "FFFFFF", True), preench(DESTAQUE), CENTRO
    t0 = max(2, c_ini)
    mesclar(ws, 1, t0, ncols)
    c = ws.cell(1, t0, titulo)
    c.font, c.fill, c.alignment = fonte(15, "FFFFFF", True), preench(AZUL), ESQ
    for i in range(2, ncols + 1):
        ws.cell(1, i).fill = preench(AZUL)
    ws.row_dimensions[1].height = 32


def coluna_meia_largura(ws, ncols):
    """Última coluna que cabe na primeira página de uma impressão em duas páginas de largura."""
    total, soma = largura_total(ws, 1, ncols), 0
    for c in range(1, ncols + 1):
        soma += ws.column_dimensions[letra(c)].width or 9
        if soma > total * 0.48:
            return max(c - 1, 2)
    return ncols


def linha_instrucao(ws, linha, txt, ncols, c_ini=1):
    mesclar(ws, linha, c_ini, ncols)
    c = ws.cell(linha, c_ini)
    texto(c, txt)
    c.font, c.alignment = fonte(9.5, CINZA), Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[linha].height = altura_texto(txt, largura_total(ws, c_ini, ncols), 9.5, 20)


def linha_aviso(ws, linha, ncols, c_ini=1):
    mesclar(ws, linha, c_ini, ncols)
    c = ws.cell(linha, c_ini)
    c.value = aviso_rico()
    c.fill, c.alignment = preench(AVISO_FUNDO), Alignment(vertical="center", wrap_text=True, indent=1)
    for i in range(c_ini + 1, ncols + 1):
        ws.cell(linha, i).fill = preench(AVISO_FUNDO)
    ws.row_dimensions[linha].height = altura_texto("AVISO  " + AVISO, largura_total(ws, c_ini, ncols) - 2, 8, 18)


ORIGEM = ('="Origem: "&IF(pcmd_origem="","não informada",pcmd_origem)&"   ·   Emissão: "&IF(ISNUMBER(pcmd_emissao),'
          'RIGHT("0"&DAY(pcmd_emissao),2)&"/"&RIGHT("0"&MONTH(pcmd_emissao),2)&"/"&YEAR(pcmd_emissao),"não informada")')


def topo(ws, codigo, titulo, instrucao, ncols, inicio_direita=None, c_ini=1):
    """Linhas 1 a 4: faixa de título, instrução curta, aviso e linha de origem/emissão.

    c_ini > 1 nas abas impressas em duas páginas de largura: os textos começam depois das colunas
    repetidas, para não aparecerem cortados na segunda página.
    """
    faixa_titulo(ws, codigo, titulo, ncols, c_ini)
    fim_txt = coluna_meia_largura(ws, ncols) if c_ini > 1 else ncols  # texto inteiro na 1ª página da largura
    linha_instrucao(ws, 2, instrucao, fim_txt, c_ini)
    linha_aviso(ws, 3, fim_txt, c_ini)
    fim = min((inicio_direita - 1) if inicio_direita else ncols, fim_txt)
    mesclar(ws, 4, c_ini, fim)
    c = ws.cell(4, c_ini, ORIGEM)
    c.font, c.alignment = fonte(8.5, CINZA), Alignment(vertical="center")
    ws.row_dimensions[4].height = 20


def secao(ws, linha, titulo, c1, c2):
    c = ws.cell(linha, c1, titulo)
    c.font = fonte(11, AZUL, True)
    c.alignment = Alignment(vertical="bottom")
    for i in range(c1, c2 + 1):
        ws.cell(linha, i).border = B_SECAO
    ws.row_dimensions[linha].height = 22


def cabecalho(ws, linha, titulos_cores, col0=1, chips=True):
    """Linha de papéis (rótulo curto colorido) e cabeçalho com a cor do papel da coluna."""
    altura = 30
    for i, (titulo, papel) in enumerate(titulos_cores):
        cor = COR_PAPEL.get(papel, AZUL)
        if chips and papel:
            c = ws.cell(linha - 1, col0 + i, E.PAPEIS[papel][0])
            c.font, c.alignment = fonte(7, cor, True), Alignment(horizontal="center", vertical="bottom")
        c = ws.cell(linha, col0 + i, titulo)
        c.font, c.fill, c.alignment, c.border = fonte(9, "FFFFFF", True), preench(cor), CENTRO, B_CAB
        larg = ws.column_dimensions[letra(col0 + i)].width or 9
        altura = max(altura, altura_texto(titulo, larg, 9, 30))
    ws.row_dimensions[linha].height = min(altura, 64)
    if chips:
        ws.row_dimensions[linha - 1].height = 14


# ------------------------------------------------------------------ tabelas
def estilo_dado(cell, col):
    cell.font = fonte(9.5, CINZA if col.papel == "calculo" else ("8C96A0" if col.papel == "futuro" else TINTA), italico=col.papel == "futuro")
    cell.border = B_LINHA
    cell.alignment = Alignment(vertical="center", wrap_text=col.largura >= 28)
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


AMBAR = ("Pendente", "Verificar", "Duplicada", "Tarefa ", "Fora do plano", "Previsão", "Sem vínculo", "Não verificado", "Não informado", "Informe")


COLUNAS_STATUS = ("conferencia", "orientacao", "vinculo", "situacao_plano", "parada_situacao", "tag_conferencia")


def regra_status(ws, alvo, L, l1):
    """ERRO em vermelho, situações a conferir em âmbar e OK em verde (texto + cor)."""
    ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'LEFT({L}{l1},4)="ERRO"'], stopIfTrue=True,
                                                    fill=preench(ERRO_FUNDO), font=Font(bold=True, color=SEGURANCA)))
    cond = ",".join(f'LEFT({L}{l1},{len(p)})="{p}"' for p in AMBAR)
    ws.conditional_formatting.add(alvo, FormulaRule(formula=[f"OR({cond})"], stopIfTrue=True, fill=preench(AVISO_FUNDO), font=Font(color=AVISO_TEXTO)))
    ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'OR(LEFT({L}{l1},2)="OK",LEFT({L}{l1},10)="Verificado",{L}{l1}="Vinculada",'
                                                             f'{L}{l1}="No plano atual",{L}{l1}="Informado")'],
                                                    stopIfTrue=True, font=Font(bold=True, color=OK_TXT)))


def formatacao_condicional(ws, colunas, l1, l2, col0=1):
    n = len(colunas)
    chave = f"${letra(col0)}{l1}"
    for i, col in enumerate(colunas):
        L = letra(col0 + i)
        alvo = f"{L}{l1}:{L}{l2}"
        if col.id == "criticidade.classe":
            for valor, fundo, cor in (("A", SEGURANCA, "FFFFFF"), ("B", DESTAQUE, "FFFFFF"), ("C", AZUL_SUAVE, AZUL), ("Pendente", AVISO_FUNDO, AVISO_TEXTO)):
                ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'{L}{l1}="{valor}"'], stopIfTrue=True, fill=preench(fundo),
                                                                font=Font(bold=True, color=cor)))
        elif col.id.rsplit(".", 1)[1] in COLUNAS_STATUS:
            regra_status(ws, alvo, L, l1)
        if col.id.startswith("criticidade.nota_"):
            ws.conditional_formatting.add(alvo, ColorScaleRule(start_type="num", start_value=1, start_color="E3F0E6",
                                                               mid_type="num", mid_value=2, mid_color="FFF0C7",
                                                               end_type="num", end_value=3, end_color="F6CDD3"))
        if col.id == "tarefa.seguranca":
            ws.conditional_formatting.add(alvo, FormulaRule(formula=[f'{L}{l1}="Sim"'], font=Font(bold=True, color=SEGURANCA)))
        if col.id in ("tarefa.ativa", "execucao.cancelada", "pessoa.ativo"):
            alvo_txt = "Não" if col.id != "execucao.cancelada" else "Sim"
            ws.conditional_formatting.add(f"{letra(col0)}{l1}:{letra(col0 + n - 1)}{l2}",
                                          FormulaRule(formula=[f'${L}{l1}="{alvo_txt}"'], font=Font(color="8C96A0", strike=col.id == "execucao.cancelada")))
    # Linhas preenchidas: fundo dos cálculos e zebra (o modelo em branco fica limpo).
    for i, col in enumerate(colunas):
        if col.papel == "calculo":
            L = letra(col0 + i)
            ws.conditional_formatting.add(f"{L}{l1}:{L}{l2}", FormulaRule(formula=[f'{chave}<>""'], fill=preench(CALC_FUNDO)))
    ws.conditional_formatting.add(f"{letra(col0)}{l1}:{letra(col0 + n - 1)}{l2}",
                                  FormulaRule(formula=[f'AND({chave}<>"",MOD(ROW(),2)=0)'], fill=preench(ZEBRA)))


def texto_capacidade(aba, l1, l2):
    erros = ""
    conf = [i for i, c in enumerate(aba.colunas, start=1) if c.id.endswith(".conferencia")]
    if conf:
        L = letra(conf[0])
        erros = f'&IF(COUNTIF({L}{l1}:{L}{l2},"ERRO*")>0,"   ·   "&COUNTIF({L}{l1}:{L}{l2},"ERRO*")&" com ERRO","")'
    return (f'=IF(COUNTA(A{l2 + 1}:A{l2 + 2000})>0,"ATENÇÃO: dados além da linha {l2}",'
            f'"Linhas: "&COUNTA(A{l1}:A{l2})&" de {aba.capacidade}"{erros})')


def montar_aba_tabela(wb, aba, linhas, versao_exemplo):
    ws = wb.create_sheet(aba.nome)
    ws.sheet_view.showGridLines = False
    n = len(aba.colunas)
    l1, l2 = E.PRIMEIRA, E.PRIMEIRA + aba.capacidade - 1
    for i, col in enumerate(aba.colunas, start=1):
        ws.column_dimensions[letra(i)].width = col.largura
    chips_ativos = aba.nome == E.ATIVOS.nome
    if aba.colunas_repetidas:  # capacidade sob as colunas repetidas: aparece em todas as páginas da largura
        c_ini = ord(aba.colunas_repetidas.split(":")[1]) - ord("A") + 2
        cap_ini, cap_fim, alinhar = 1, c_ini - 1, "left"
    else:
        c_ini = 1
        cap_ini = max(2, n - max(1, n // 3) + 1)
        cap_fim, alinhar = n, "right"
    topo(ws, aba.codigo, aba.titulo, aba.instrucao, n, inicio_direita=11 if chips_ativos else (None if c_ini > 1 else cap_ini), c_ini=c_ini)
    mesclar(ws, 4, cap_ini, cap_fim)
    c = ws.cell(4, cap_ini, texto_capacidade(aba, l1, l2))
    c.font, c.alignment = fonte(8.5, CINZA, True), Alignment(horizontal=alinhar, vertical="center", wrap_text=True)
    ws.conditional_formatting.add(f"{letra(cap_ini)}4", FormulaRule(formula=[f'LEFT({letra(cap_ini)}4,7)="ATENÇÃO"'], fill=preench(ERRO_FUNDO),
                                                                    font=Font(bold=True, color=SEGURANCA)))
    if chips_ativos:  # contagem por classe em selos coloridos
        R = letra(next(i for i, c in enumerate(aba.colunas, start=1) if c.id == "criticidade.classe"))
        for k, (cl, fundo, cor) in enumerate((("A", SEGURANCA, "FFFFFF"), ("B", DESTAQUE, "FFFFFF"), ("C", AZUL_SUAVE, AZUL), ("Pendente", AVISO_FUNDO, AVISO_TEXTO))):
            c = ws.cell(4, 11 + k, f'="{cl}  "&COUNTIF({R}{l1}:{R}{l2},"{cl}")')
            c.font, c.fill, c.alignment = fonte(8.5, cor, True), preench(fundo), CENTRO
            c.border = Border(left=Side(style="thick", color="FFFFFF"), right=Side(style="thick", color="FFFFFF"))
    cabecalho(ws, E.LINHA_CAB, [(c.cabecalho, c.papel) for c in aba.colunas])
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
    formatacao_condicional(ws, aba.colunas, l1, l2)
    ws.freeze_panes = ws.cell(l1, aba.congelar_col + 1)
    ws.auto_filter.ref = f"A{E.LINHA_CAB}:{letra(n)}{l2}"
    usadas = len(linhas) if versao_exemplo else aba.linhas_impressao_modelo
    configurar_impressao(ws, aba.paisagem, n, l1 + max(usadas, 1) - 1, aba.codigo, largura=aba.paginas_largura, colunas=aba.colunas_repetidas)
    if aba.protegida:
        ws.protection.sheet = True
        ws.protection.autoFilter = False
        ws.protection.sort = False
        ws.protection.formatColumns = False
        ws.protection.formatRows = False
        ws.protection.selectLockedCells = False
        ws.protection.selectUnlockedCells = False
    return ws


# ------------------------------------------------------------------ formulários (células únicas)
def campo_entrada(cell, valor=None, fmt=FORMATO_TEXTO):
    cell.border, cell.font, cell.alignment = B_CAIXA, fonte(10), Alignment(vertical="center", wrap_text=True)
    cell.number_format = fmt
    cell.protection = Protection(locked=False)
    if valor not in (None, ""):
        if isinstance(valor, str):
            texto(cell, valor)
        else:
            cell.value = valor


def campo_calculo(cell, formula, fmt=None):
    cell.value = formula
    cell.fill, cell.font, cell.border = preench(CALC_FUNDO), fonte(9.5, CINZA), B_LINHA
    cell.alignment = Alignment(vertical="center", wrap_text=True)
    if fmt:
        cell.number_format = fmt


def rotulo(ws, r, c, txt):
    cell = ws.cell(r, c)
    texto(cell, txt)
    cell.font, cell.alignment, cell.border = fonte(9.5, TINTA, True), Alignment(vertical="center", wrap_text=True), B_LINHA


def nota_curta(ws, r, c, txt):
    cell = ws.cell(r, c)
    texto(cell, txt)
    cell.font, cell.alignment, cell.border = fonte(8.5, CINZA), Alignment(vertical="center", wrap_text=True), B_LINHA


def montar_organizacao(wb, dados):
    ws = wb.create_sheet("Organização")
    ws.sheet_view.showGridLines = False
    for i, w in enumerate([25, 27, 26, 32], start=1):
        ws.column_dimensions[letra(i)].width = w
    topo(ws, "PCMD-01", "Organização", "Preencha uma vez. Elaborador e aprovador usam o ID da aba Pessoas; a meta vazia fica A definir.", 4)
    cabecalho(ws, 6, [("Campo", "entrada"), ("Valor", "entrada"), ("Resultado", "calculo"), ("Observação", "entrada")], chips=False)
    g = dados.get("gestao") if dados else None
    org = g["organizacao"] if g else {"nome": "", "referencial": "GERAL (sem norma)", "padraoCodigo": "PCMD", "elaborador": "", "aprovador": ""}
    pessoa = 'IFERROR(INDEX(cad_pessoa_nome,MATCH(B{r},cad_pessoa_id,0)),"Pessoa não cadastrada")'
    linhas = [
        ("Nome da organização", org["nome"], None, "Ex.: Indústria Exemplo."),
        ("Referencial", org["referencial"], None, "Padrão GERAL (sem norma). Não cite norma sem fonte oficial, versão e data."),
        ("Prefixo dos documentos", org["padraoCodigo"], None, "Padrão PCMD."),
        ("Elaborador padrão (ID)", org["elaborador"], '=IF(B10="","",' + pessoa.format(r=10) + ")", "ID da aba Pessoas."),
        ("Aprovador padrão (ID)", org["aprovador"], '=IF(B11="","A definir (aprovação não registrada)",' + pessoa.format(r=11) + ")",
         "Só informe após aprovação efetiva."),
    ]
    for k, (rot, val, form, obs) in enumerate(linhas):
        r = 7 + k
        rotulo(ws, r, 1, rot)
        campo_entrada(ws.cell(r, 2), val)
        campo_calculo(ws.cell(r, 3), form)
        nota_curta(ws, r, 4, obs)
        ws.row_dimensions[r].height = 22
    rotulo(ws, 12, 1, "Meta de disponibilidade (%)")
    v = g["metas"]["disponibilidade"] if g else None
    campo_entrada(ws.cell(12, 2), None if v is None else v / 100, "0.0%")
    campo_calculo(ws.cell(12, 3), '=IF(B12="","A definir",B12)', "0.0%")
    nota_curta(ws, 12, 4, "Disponibilidade, MTBF e MTTR não são calculados: regras técnicas pendentes.")
    ws.row_dimensions[12].height = 22
    for nm, cel in (("cad_org_nome", "B7"), ("cad_referencial", "B8"), ("cad_prefixo", "B9"), ("cad_meta_disponibilidade", "B12")):
        nome(wb, nm, f"'Organização'!${cel[0]}${cel[1:]}")
    for celula in ("B10", "B11"):
        dv = DataValidation(type="list", formula1="=cad_pessoa_id", allow_blank=True, showErrorMessage=True,
                            error="Use um ID da aba Pessoas.", errorTitle="Valor não aceito")
        dv.add(celula)
        ws.add_data_validation(dv)
    dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="1", allow_blank=True, showErrorMessage=True,
                        errorTitle="Meta não aceita", error="Informe um percentual entre 0% e 100%. Vazio = A definir.")
    dv.add("B12")
    ws.add_data_validation(dv)
    ws.freeze_panes = "A5"
    configurar_impressao(ws, False, 4, 12, "PCMD-01", titulos=None)


def montar_criterios(wb, dados):
    ws = wb.create_sheet("Critérios")
    ws.sheet_view.showGridLines = False
    for i, w in enumerate([26, 22, 22, 22, 26], start=1):
        ws.column_dimensions[letra(i)].width = w
    topo(ws, "PCMD-02", "Critérios de criticidade",
         "Segurança = 3 → A; senão soma ≥ A → A; soma ≥ B → B; senão C. Nota ausente ou limite inválido → Pendente.", 5)
    cabecalho(ws, 6, [("Campo", "entrada"), ("Valor", "entrada"), ("Resultado", "calculo"), ("Regra", "entrada")], chips=False)
    g = dados.get("gestao") if dados else None
    lim = g["criticidade"]["limites"] if g else {"a": 12, "b": 9}
    for r, rot, val, regra in ((7, "Limite A (soma mínima)", lim["a"], "Inteiros com 5 ≤ B < A ≤ 15."), (8, "Limite B (soma mínima)", lim["b"], "Padrão inicial: A = 12 e B = 9.")):
        rotulo(ws, r, 1, rot)
        campo_entrada(ws.cell(r, 2), val, "0")
        nota_curta(ws, r, 4, regra)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        ws.cell(r, 3).border = B_LINHA
        ws.row_dimensions[r].height = 22
    rotulo(ws, 9, 1, "Limites válidos?")
    campo_calculo(ws.cell(9, 2), "=IF(AND(ISNUMBER(B7),ISNUMBER(B8)),AND(B7=INT(B7),B8=INT(B8),B8>=5,B8<B7,B7<=15),FALSE)")
    campo_calculo(ws.cell(9, 3), '=IF(B9,"OK: limites válidos","ERRO: Inválidos; use inteiros com 5 ≤ B < A ≤ 15 (classes ficam Pendente)")')
    ws.merge_cells("C9:E9")
    ws.row_dimensions[9].height = 22
    regra_status(ws, "C9", "C", 9)
    nome(wb, "cad_limite_a", "'Critérios'!$B$7")
    nome(wb, "cad_limite_b", "'Critérios'!$B$8")
    nome(wb, "cad_limites_ok", "'Critérios'!$B$9")
    dv = DataValidation(type="whole", operator="between", formula1="5", formula2="15", allow_blank=False, showErrorMessage=True,
                        errorTitle="Limite não aceito", error="Use inteiro entre 5 e 15, com B menor que A.")
    dv.add("B7:B8")
    ws.add_data_validation(dv)
    secao(ws, 11, "Significado dos níveis (definido pelo mantenedor; o PCM Direto não define)", 1, 5)
    cabecalho(ws, 12, [("Critério", "entrada"), ("Nível 1", "manual"), ("Nível 2", "manual"), ("Nível 3", "manual"), ("Situação", "calculo")], chips=False)
    for k, crit in enumerate(["N1 Segurança", "N2 Qualidade", "N3 Produção", "N4 Frequência de falha", "N5 Custo/tempo de reparo"]):
        r = 13 + k
        rotulo(ws, r, 1, crit)
        for c in (2, 3, 4):
            campo_entrada(ws.cell(r, c))
        campo_calculo(ws.cell(r, 5), f'=IF(COUNTA(B{r}:D{r})<3,"Pendente: a definir pelo mantenedor","OK: definido")')
        ws.row_dimensions[r].height = 30
    regra_status(ws, "E13:E17", "E", 13)
    ws.merge_cells("A19:E19")
    texto(ws["A19"], "A classe não altera frequências, tarefas nem proteções de segurança. Qualquer mudança no plano é decisão registrada do profissional responsável.")
    ws["A19"].font, ws["A19"].alignment = fonte(8.5, CINZA, italico=True), Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[19].height = 26
    ws.freeze_panes = "A5"
    configurar_impressao(ws, False, 5, 19, "PCMD-02", titulos=None)


# ------------------------------------------------------------------ listas
def especialidades(biblioteca):
    vistas = []
    for t in biblioteca["tipos"]:
        for tarefa in t["tarefas"]:
            if tarefa["especialidade"] not in vistas:
                vistas.append(tarefa["especialidade"])
    return vistas


def blocos_listas(biblioteca):
    return {
        "frequencias": (["Frequência", "Execuções em 52 semanas", "Observação"], [list(f) for f in E.FREQUENCIAS],
                        [("lst_frequencias", 0, 8), ("lst_frequencias_vezes", 1, 8)], [12, 12, 30]),
        "especialidades": (["Especialidade"], [[e] for e in especialidades(biblioteca)], [("lst_especialidades", 0, 30)], [16]),
        "tipos": (["Tipo (ID)", "Tipo (nome)", "Sigla"], [[t["id"], t["nome"], t["sigla"]] for t in biblioteca["tipos"]],
                  [("lst_tipo_id", 0, 30), ("lst_tipo_nome", 1, 30), ("lst_tipo_sigla", 2, 30)], [20, 22, 8]),
        "sim_nao": (["Sim/Não"], [["Sim"], ["Não"]], [("lst_sim_nao", 0, 2)], [9]),
        "origem_execucao": (["Origem da execução"], [["app"], ["legado"]], [("lst_origem_execucao", 0, 2)], [12]),
        "status_requisito": (["Status de requisito"], [["Não verificado"], ["Verificado"]], [("lst_status_requisito", 0, 2)], [15]),
        "situacao_documento": (["Situação do documento"], [[s] for s in E.SITUACOES_DOCUMENTO], [("lst_situacao_documento", 0, 10)], [16]),
        "tipo_documento": (["Tipo de documento"], [[t] for t in E.TIPOS_DOCUMENTO], [("lst_tipo_documento", 0, 10)], [15]),
        "tipos_tarefa": (["Tipos de tarefa (consulta)"], [[t] for t in E.TIPOS_TAREFA_REFERENCIA], [], [18]),
    }


def montar_listas(wb, biblioteca, chaves, codigo):
    ws = wb.create_sheet("Listas")
    ws.sheet_view.showGridLines = False
    todos = blocos_listas(biblioteca)
    col0, ultima, altura_max = 1, 1, 1
    posicoes = []
    for k in chaves:
        titulos, valores, nomes, larguras = todos[k]
        for i, w in enumerate(larguras):
            ws.column_dimensions[letra(col0 + i)].width = w
        posicoes.append((col0, k))
        ultima = col0 + len(titulos) - 1
        col0 = ultima + 2
        if col0 - 1 > ultima:
            ws.column_dimensions[letra(col0 - 1)].width = 2
    topo(ws, codigo, "Listas", "Valores aceitos nas listas suspensas. Ao acrescentar itens, mantenha-os dentro dos intervalos nomeados.", ultima)
    for col0, k in posicoes:
        titulos, valores, nomes, larguras = todos[k]
        cabecalho(ws, E.LINHA_CAB, [(t, "referencia") for t in titulos], col0=col0)
        altura = max([n[2] for n in nomes] + [len(valores)])
        altura_max = max(altura_max, altura)
        for kk in range(altura):
            for i in range(len(titulos)):
                cell = ws.cell(E.PRIMEIRA + kk, col0 + i)
                cell.border, cell.font = B_LINHA, fonte(9.5)
                if kk < len(valores):
                    v = valores[kk][i]
                    if isinstance(v, str):
                        texto(cell, v)
                    else:
                        cell.value = v
        for nm, desloc, tam in nomes:
            nome(wb, nm, ref_abs("Listas", col0 + desloc, E.PRIMEIRA, E.PRIMEIRA + tam - 1))
    ws.freeze_panes = "A7"
    configurar_impressao(ws, ultima > 8, ultima, E.PRIMEIRA + min(altura_max, 30) - 1, codigo)


# ------------------------------------------------------------------ cronograma (painel)
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def montar_cronograma(wb, dados):
    ws = wb.create_sheet("Cronograma")
    ws.sheet_view.showGridLines = False
    for i, w in enumerate([9, 22, 15, 15, 13, 15, 30], start=1):
        ws.column_dimensions[letra(i)].width = w
    topo(ws, "PCMD-04", "Cronograma · painel do ano",
         "O mês é o da data PREVISTA. % realizado = ocorrências concluídas ÷ previstas (distintas). Horas são estimadas, não trabalhadas.", 7)
    secao(ws, 6, "Parâmetros", 1, 7)
    meta = (dados["gestao"]["metas"]["aderencia"] if dados else None)
    par = [
        (7, "Ano consultado", dados["ano"] if dados else None, "0", True),
        (8, "Início do ciclo (informativo)", dt.date.fromisoformat(dados["inicio"]) if dados else None, "dd/mm/yyyy", True),
        (9, "Fonte das ocorrências", ("Cronograma do PCM Direto: 52 semanas a partir de 03/11/2025, calculado pela lógica do app para demonstração fictícia"
                                      if dados else None), FORMATO_TEXTO, True),
        (10, "Conferência do ano", '=IF(ISNUMBER(crono_ano),IF(AND(crono_ano=INT(crono_ano),crono_ano>=1900,crono_ano<=9999),"OK","ERRO: ano inválido"),"Informe o ano consultado")', None, False),
        (11, "Meta de aderência (%)", None if meta is None else meta / 100, "0.0%", True),
    ]
    for r, rot, val, fmt, ent in par:
        mesclar(ws, r, 1, 2)
        rotulo(ws, r, 1, rot)
        ws.cell(r, 2).border = B_LINHA
        mesclar(ws, r, 3, 7 if r == 9 else 4)
        c = ws.cell(r, 3)
        if ent:
            campo_entrada(c, val, fmt)
            for i in range(4, (7 if r == 9 else 4) + 1):
                ws.cell(r, i).border = B_CAIXA
        else:
            campo_calculo(c, val, fmt)
        ws.row_dimensions[r].height = 30 if r == 9 else 20
    regra_status(ws, "C10", "C", 10)
    nome(wb, "crono_ano", "'Cronograma'!$C$7")
    nome(wb, "crono_inicio", "'Cronograma'!$C$8")
    nome(wb, "crono_meta_aderencia", "'Cronograma'!$C$11")
    for celula, tipo, f1, f2, erro in (("C7", "whole", "1900", "9999", "Informe o ano com quatro dígitos."),
                                       ("C8", "date", "1", "2958465", "Informe uma data válida."),
                                       ("C11", "decimal", "0", "1", "Informe um percentual entre 0% e 100%. Vazio = A definir.")):
        dv = DataValidation(type=tipo, operator="between", formula1=f1, formula2=f2, allow_blank=True, showErrorMessage=True,
                            errorTitle="Valor não aceito", error=erro)
        dv.add(celula)
        ws.add_data_validation(dv)

    cr = E.CRONO
    j, d, t = cr["jan"], cr["jan"] + 11, cr["total"]
    # Cartões
    cartoes = [
        (1, 2, "Previstas no ano", f"=IF(C{t}=\"\",\"—\",C{t})", "0"),
        (3, 3, "Concluídas", f"=IF(D{t}=\"\",\"—\",D{t})", "0"),
        (4, 4, "% realizado", f"=IF(E{t}=\"\",\"—\",E{t})", "0.0%"),
        (5, 6, "Meta de aderência", '=IF(crono_meta_aderencia="","A definir",crono_meta_aderencia)', "0.0%"),
        (7, 7, "Situação frente à meta", f'=IF(OR(NOT(ISNUMBER(E{t})),NOT(ISNUMBER(crono_meta_aderencia))),"Sem comparação",IF(E{t}>=crono_meta_aderencia,"OK: na meta","Verificar: abaixo da meta"))', None),
    ]
    rr, rv = cr["cartao_rot"], cr["cartao"]
    for c1, c2, rot, form, fmt in cartoes:
        mesclar(ws, rr, c1, c2)
        mesclar(ws, rv, c1, c2)
        c = ws.cell(rr, c1, rot)
        c.font, c.alignment = fonte(8, CINZA, True), Alignment(horizontal="center", vertical="bottom")
        c = ws.cell(rv, c1, form)
        c.font, c.alignment = fonte(16 if c1 < 7 else 11, AZUL, True), CENTRO
        if fmt:
            c.number_format = fmt
        for i in range(c1, c2 + 1):
            ws.cell(rr, i).fill = preench(AZUL_SUAVE)
            ws.cell(rv, i).fill = preench(AZUL_SUAVE)
            ws.cell(rr, i).border = Border(top=Side(style="thick", color=DESTAQUE if c1 == 4 else AZUL), left=Side(style="thick", color="FFFFFF") if i == c1 else None)
            ws.cell(rv, i).border = Border(left=Side(style="thick", color="FFFFFF") if i == c1 else None)
    ws.row_dimensions[rr].height = 18
    ws.row_dimensions[rv].height = 36
    regra_status(ws, f"G{rv}", "G", rv)

    def calc(r, c, formula, fmt=None, negrito=False):
        cell = ws.cell(r, c, formula)
        cell.font, cell.border = fonte(9.5, TINTA if c <= 2 else CINZA, negrito), B_LINHA
        cell.alignment = Alignment(vertical="center", wrap_text=c in (2, 7))
        if fmt:
            cell.number_format = fmt
        return cell

    secao(ws, cr["cab_mes"] - 1, "Resumo mensal", 1, 7)
    cabecalho(ws, cr["cab_mes"], [(x, "calculo") for x in ("Mês (nº)", "Mês", "Previstas (distintas)", "Concluídas (distintas)", "% realizado",
                                                            "Horas estimadas (h)", "Observação")], chips=False)
    for k, m in enumerate(MESES):
        r = j + k
        calc(r, 1, k + 1, "0")
        calc(r, 2, m)
        calc(r, 3, f'=IF(NOT(ISNUMBER(crono_ano)),"",SUMIFS(oc_conta,oc_ano,crono_ano,oc_mes,A{r}))', "0")
        calc(r, 4, f'=IF(C{r}="","",SUMIFS(oc_concluida,oc_ano,crono_ano,oc_mes,A{r}))', "0")
        calc(r, 5, f'=IF(C{r}="","",IF(C{r}=0,"Sem previsão",D{r}/C{r}))', "0.0%")
        calc(r, 6, f'=IF(C{r}="","",SUMIFS(oc_horas,oc_conta,1,oc_ano,crono_ano,oc_mes,A{r}))', "0.00")
        calc(r, 7, f'=IF(C{r}="","",IF(C{r}=0,"Mês sem previsão",""))')
    for c in range(1, 8):
        ws.conditional_formatting.add(f"{letra(c)}{j}:{letra(c)}{d}", FormulaRule(formula=[f"MOD(ROW(),2)=0"], fill=preench(ZEBRA)))
    calc(t, 1, "")
    calc(t, 2, "Total do ano", negrito=True)
    calc(t, 3, f'=IF(NOT(ISNUMBER(crono_ano)),"",SUM(C{j}:C{d}))', "0", True)
    calc(t, 4, f'=IF(C{t}="","",SUM(D{j}:D{d}))', "0", True)
    calc(t, 5, f'=IF(C{t}="","",IF(C{t}=0,"Sem previsão",D{t}/C{t}))', "0.0%", True)
    calc(t, 6, f'=IF(C{t}="","",SUM(F{j}:F{d}))', "0.00", True)
    calc(t, 7, "")
    for c in range(1, 8):
        ws.cell(t, c).fill = preench(AZUL_SUAVE)
        ws.cell(t, c).border = Border(top=Side(style="medium", color=AZUL))
    ws.conditional_formatting.add(f"E{j}:E{d}", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="5B8DB8", showValue=True))
    ws.conditional_formatting.add(f"E{j}:E{d}", FormulaRule(formula=[f'AND(ISNUMBER(E{j}),ISNUMBER(crono_meta_aderencia),E{j}<crono_meta_aderencia)'],
                                                          font=Font(bold=True, color=AVISO_TEXTO)))
    ws.conditional_formatting.add(f"E{j}:E{d}", FormulaRule(formula=[f'E{j}="Sem previsão"'], font=Font(italic=True, color="8C96A0")))

    graf = BarChart()
    graf.type = "col"
    graf.grouping = "clustered"
    graf.overlap = -10
    graf.gapWidth = 60
    graf.y_axis.title = None
    graf.y_axis.majorGridlines = None
    graf.y_axis.delete = False
    graf.x_axis.delete = False
    graf.legend.position = "b"
    dados_ref = Reference(ws, min_col=3, max_col=4, min_row=cr["cab_mes"], max_row=d)
    graf.add_data(dados_ref, titles_from_data=True)
    graf.set_categories(Reference(ws, min_col=2, min_row=j, max_row=d))
    for serie, cor in zip(graf.series, (AZUL, DESTAQUE)):
        serie.graphicalProperties.solidFill = cor
        serie.graphicalProperties.line.solidFill = cor
    graf.height, graf.width = 8.2, 17.6
    secao(ws, cr["grafico"] - 1, "Previstas × concluídas por mês", 1, 7)
    ws.add_chart(graf, f"A{cr['grafico']}")

    f0 = cr["fora_cab"]
    secao(ws, f0 - 1, "Fora do ano consultado (separado, não descartado)", 1, 7)
    cabecalho(ws, f0, [(x, "calculo") for x in ("", "Posição", "Previstas (distintas)", "Concluídas (distintas)", "% realizado", "Horas estimadas (h)", "")], chips=False)
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
    secao(ws, s0 - 1, "Execuções fora do percentual (no ano da data realizada)", 1, 7)
    cabecalho(ws, s0, [(x, "calculo") for x in ("", "Situação", "Registros", "", "", "", "Observação")], chips=False)
    linhas_s = [
        ("Sem vínculo (legado ou sem data prevista)", 'COUNTIFS(ex_vinculo,"Sem vínculo",ex_cancelada,"<>Sim",ex_ano,crono_ano)', "Não aumentam o percentual."),
        ("Data prevista sem ocorrência", 'COUNTIFS(ex_vinculo,"Previsão não encontrada",ex_cancelada,"<>Sim",ex_ano,crono_ano)', "Conferir a data prevista informada."),
        ("Canceladas (preservadas)", 'COUNTIFS(ex_cancelada,"Sim",ex_ano,crono_ano)', "Não contam."),
    ]
    for k, (rot, form, obs) in enumerate(linhas_s):
        r = s0 + 1 + k
        calc(r, 1, "")
        calc(r, 2, rot)
        calc(r, 3, f'=IF(NOT(ISNUMBER(crono_ano)),"",{form})', "0")
        for c in (4, 5, 6):
            calc(r, c, "")
        calc(r, 7, obs)

    c0 = cr["conf_cab"]
    secao(ws, c0 - 1, "Conferências", 1, 7)
    cabecalho(ws, c0, [(x, "calculo") for x in ("", "Verificação", "Resultado", "", "", "", "Como corrigir")], chips=False)
    l2o = E.PRIMEIRA + E.OCORRENCIAS.capacidade - 1
    l2x = E.PRIMEIRA + E.EXECUCOES.capacidade - 1
    linhas_c = [
        ("Ocorrências com ERRO", '=COUNTIF(oc_conferencia,"ERRO*")', "Ver a coluna Conferência em Ocorrências."),
        ("Ocorrências duplicadas (contadas uma vez)", '=COUNTIF(oc_conferencia,"Duplicada*")', "Remova a linha repetida."),
        ("Dados além da capacidade de Ocorrências", f"=IF(COUNTA('Ocorrências'!A{l2o + 1}:A{l2o + 5000})>0,\"ATENÇÃO: há linhas fora das fórmulas\",\"OK\")",
         "Estenda fórmulas e nomes (COMO-USAR)."),
        ("Dados além da capacidade de Execuções", f"=IF(COUNTA('Execuções'!A{l2x + 1}:A{l2x + 5000})>0,\"ATENÇÃO: há linhas fora das fórmulas\",\"OK\")",
         "Estenda fórmulas e nomes (COMO-USAR)."),
    ]
    for k, (rot, form, obs) in enumerate(linhas_c):
        r = c0 + 1 + k
        calc(r, 1, "")
        calc(r, 2, rot)
        calc(r, 3, form, "0")
        for c in (4, 5, 6):
            calc(r, c, "")
        calc(r, 7, obs)
    ws.conditional_formatting.add(f"C{c0 + 1}:C{c0 + 4}", FormulaRule(formula=[f'LEFT(C{c0 + 1},8)="ATENÇÃO"'], fill=preench(ERRO_FUNDO),
                                                                     font=Font(bold=True, color=SEGURANCA)))
    ws.conditional_formatting.add(f"C{c0 + 1}:C{c0 + 4}", FormulaRule(formula=[f'C{c0 + 1}="OK"'], font=Font(bold=True, color=OK_TXT)))
    nota = c0 + 6
    mesclar(ws, nota, 1, 7)
    texto(ws.cell(nota, 1), "Cada linha de Ocorrências é um trio ativo + tarefa + data prevista. Concluída = ao menos uma execução não cancelada vinculada; "
                            "duas execuções da mesma ocorrência contam uma vez. Diária = uma ocorrência por dia útil, sem feriados.")
    ws.cell(nota, 1).font, ws.cell(nota, 1).alignment = fonte(8.5, CINZA, italico=True), Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[nota].height = 30
    ws.freeze_panes = "A5"
    configurar_impressao(ws, False, 7, nota, "PCMD-04", titulos=None)
    ws.row_breaks.append(Break(id=f0 - 3))


# ------------------------------------------------------------------ início
LEGENDA = [
    ("PREENCHER", "entrada", "Cabeçalho azul: digite aqui (texto, número ou data)."),
    ("ID", "id", "Identificador técnico estável. Não troque por TAG, nome ou número de linha."),
    ("REFERÊNCIA", "referencia", "Cabeçalho laranja: conteúdo da biblioteca técnica."),
    ("AUTOMÁTICO", "calculo", "Cabeçalho cinza: fórmula. Não digite; recalcula sozinho."),
    ("FUTURO", "futuro", "Reservado, não integrado. Deixe vazio."),
]


def montar_inicio(wb, arq, dados):
    ws = wb.active
    ws.title = "Início"
    ws.sheet_view.showGridLines = False
    for col, w in (("A", 5), ("B", 26), ("C", 66), ("D", 12)):
        ws.column_dimensions[col].width = w
    for c in range(1, 5):
        ws.cell(1, c).fill = preench(AZUL)
    ws.cell(1, 1, "").fill = preench(DESTAQUE)
    mesclar(ws, 1, 2, 3)
    c = ws.cell(1, 2, arq.titulo)
    c.font, c.alignment = fonte(20, "FFFFFF", True), Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 48
    if LOGO_PNG.exists():  # logo original, quadrado: largura = altura preserva a proporção
        from openpyxl.drawing.image import Image as Imagem
        logo = Imagem(str(LOGO_PNG))
        logo.width = logo.height = 52
        ws.add_image(logo, "D1")
    mesclar(ws, 2, 1, 4)
    c = ws.cell(2, 1)
    texto(c, f"{arq.codigo}  ·  {arq.resumo}")
    c.font, c.alignment = fonte(10, CINZA), Alignment(vertical="center", indent=1)
    ws.row_dimensions[2].height = 24
    linha_aviso(ws, 3, 4)

    r = 5
    secao(ws, r, "Neste arquivo", 2, 4)
    r += 1
    for aba, uso in arq.abas:
        c = ws.cell(r, 2, aba)
        c.hyperlink = Hyperlink(ref=c.coordinate, location=f"'{aba}'!A1", display=aba)  # vínculo interno, sem relação externa
        c.font, c.alignment, c.border = fonte(10, AZUL, True, sublinhado="single"), Alignment(vertical="center"), B_LINHA
        c = ws.cell(r, 3)
        texto(c, uso)
        c.font, c.alignment, c.border = fonte(9.5), Alignment(vertical="center", wrap_text=True), B_LINHA
        ws.cell(r, 4).border = B_LINHA
        ws.row_dimensions[r].height = 20
        r += 1
    r += 1
    secao(ws, r, "Como preencher", 2, 4)
    r += 1
    for k, passo in enumerate(arq.passos, start=1):
        c = ws.cell(r, 1, k)
        c.font, c.fill, c.alignment = fonte(10, "FFFFFF", True), preench(DESTAQUE), CENTRO
        mesclar(ws, r, 2, 4)
        c = ws.cell(r, 2)
        texto(c, passo)
        c.font, c.alignment = fonte(10), Alignment(vertical="center", wrap_text=True, indent=1)
        ws.row_dimensions[r].height = 22
        r += 1
    r += 1
    secao(ws, r, "Legenda", 2, 4)
    r += 1
    papeis = {c.papel for a in arq.tabelas for c in a.colunas}
    for rot, papel, expl in LEGENDA:
        if papel not in papeis and papel not in ("entrada", "calculo"):
            continue
        c = ws.cell(r, 2, rot)
        c.font, c.fill, c.alignment = fonte(8.5, "FFFFFF", True), preench(COR_PAPEL[papel]), CENTRO
        c = ws.cell(r, 3)
        texto(c, expl)
        c.font, c.alignment = fonte(9.5), Alignment(vertical="center", indent=1)
        ws.row_dimensions[r].height = 19
        r += 1
    for rot, fundo, cor, expl in (("ERRO", ERRO_FUNDO, SEGURANCA, "Inconsistência a corrigir."),
                                  ("Pendente · Verificar", AVISO_FUNDO, AVISO_TEXTO, "Falta informação ou precisa de conferência."),
                                  ("OK", "FFFFFF", OK_TXT, "Conferência sem problema.")):
        c = ws.cell(r, 2, rot)
        c.font, c.fill, c.alignment, c.border = fonte(8.5, cor, True), preench(fundo), CENTRO, B_CAIXA
        c = ws.cell(r, 3)
        texto(c, expl)
        c.font, c.alignment = fonte(9.5), Alignment(vertical="center", indent=1)
        ws.row_dimensions[r].height = 19
        r += 1
    r += 1
    secao(ws, r, "Esta emissão", 2, 4)
    r += 1
    rotulo(ws, r, 2, "Origem dos dados")
    campo_entrada(ws.cell(r, 3), "Demonstração fictícia gerada com a lógica do PCM Direto (não é exportação do app)" if dados else None)
    ws.row_dimensions[r].height = 22
    nome(wb, "pcmd_origem", f"'Início'!$C${r}")
    r += 1
    rotulo(ws, r, 2, "Data de emissão")
    campo_entrada(ws.cell(r, 3), dt.date(2026, 10, 23) if dados else None, "dd/mm/yyyy")
    ws.cell(r, 3).alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[r].height = 22
    nome(wb, "pcmd_emissao", f"'Início'!$C${r}")
    dv = DataValidation(type="date", operator="between", formula1="1", formula2="2958465", allow_blank=True, showErrorMessage=True,
                        errorTitle="Data não aceita", error="Informe uma data válida (dd/mm/aaaa).")
    dv.add(f"C{r}")
    ws.add_data_validation(dv)
    r += 2
    mesclar(ws, r, 2, 4)
    c = ws.cell(r, 2)
    texto(c, f"Modelo {VERSAO_MODELO} · {dt.date.fromisoformat(DATA_MODELO):%d/%m/%Y} · {AUTOR} · {CONTATO} · Licença {LICENCA}. "
             "Sem macros, vínculos externos ou envio de dados. Regras completas, recálculo e como ampliar: COMO-USAR.md.")
    c.font, c.alignment = fonte(8, "8C96A0"), Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 26
    configurar_impressao(ws, False, 4, r, arq.codigo, titulos=None)


# ------------------------------------------------------------------ montagem
def gerar(arq, destino, dados=None):
    with open(RAIZ_REPO / "src" / "dados" / "biblioteca.json", encoding="utf-8") as f:
        biblioteca = json.load(f)
    wb = Workbook()
    montar_inicio(wb, arq, dados)
    linhas = linhas_dados(dados) if dados else {}
    if arq.chave == "01":
        montar_aba_tabela(wb, E.LISTA_MESTRA, linhas.get("lista", [{"documento.codigo": c, "documento.titulo": t, "documento.tipo": tp}
                                                                  for c, t, tp in E.DOCUMENTOS_PCMD]), True)
        montar_aba_tabela(wb, E.REVISOES, linhas.get("revisoes", []), bool(dados))
        montar_organizacao(wb, dados)
        montar_aba_tabela(wb, E.PESSOAS, linhas.get("pessoas", []), bool(dados))
        montar_aba_tabela(wb, E.REQUISITOS, linhas.get("requisitos", []), bool(dados))
    elif arq.chave == "02":
        montar_aba_tabela(wb, E.ATIVOS, linhas.get("ativos", []), bool(dados))
        montar_criterios(wb, dados)
        montar_aba_tabela(wb, E.SETORES, linhas.get("setores", []), bool(dados))
    elif arq.chave == "03":
        montar_aba_tabela(wb, E.PLANO, linhas.get("plano", []), bool(dados))
        montar_cronograma(wb, dados)
        montar_aba_tabela(wb, E.OCORRENCIAS, linhas.get("ocorrencias", []), bool(dados))
        montar_aba_tabela(wb, E.EXECUCOES, linhas.get("execucoes", []), bool(dados))
    elif arq.chave == "05":
        montar_aba_tabela(wb, E.FALHAS, linhas.get("falhas", []), bool(dados))
    if arq.listas:
        montar_listas(wb, biblioteca, arq.listas, arq.codigo)
    ordem = ["Início"] + [a for a, _ in arq.abas]
    assert sorted(ordem) == sorted(wb.sheetnames), (ordem, wb.sheetnames)
    wb._sheets = [wb[n] for n in ordem]
    wb.active = 0
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.calcMode = "auto"
    wb.properties.creator = "PCM Direto (gerador de modelos)"
    wb.properties.title = f"PCM Direto · {arq.codigo} {arq.titulo}"
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
    pessoas = {p["id"]: p["nome"] for p in g["pessoas"]}
    ativos = []
    for e in d["equipamentos"]:
        notas = g["criticidade"]["notas"].get(e["id"], [None] * 5)
        ativos.append({"ativo.id": e["id"], "ativo.tag": e["tag"], "ativo.descricao": e["descricao"], "ativo.tipo_id": e["tipo"],
                       "ativo.fabricante": e.get("fabricante", ""), "ativo.modelo": e.get("modelo", ""), "ativo.setor": e["setor"],
                       "ativo.numero": e["numero"], "criticidade.nota_seguranca": notas[0], "criticidade.nota_qualidade": notas[1],
                       "criticidade.nota_producao": notas[2], "criticidade.nota_frequencia_falha": notas[3], "criticidade.nota_custo_reparo": notas[4]})
    plano = []
    for l in sorted(d["plano"], key=lambda x: (x["tag"], x["tarefaId"])):
        resp = g["responsaveis"].get(f"{l['equipamentoId']}|{l['tarefaId']}", "")
        plano.append({"tarefa.ativo_id": l["equipamentoId"], "tarefa.id": l["tarefaId"], "tarefa.tag": l["tag"], "tarefa.atividade": l["descricao"],
                      "tarefa.origem": l["origem"], "tarefa.versao": l["versao"], "tarefa.frequencia_referencia": l["periodicidadeOriginal"],
                      "tarefa.seguranca": "Sim" if l["seguranca"] else "Não", "tarefa.frequencia_vigente": l["periodicidade"],
                      "tarefa.especialidade": l["especialidade"], "tarefa.duracao_horas": l["duracaoHoras"], "tarefa.ativa": "Sim" if l["ativa"] else "Não",
                      "tarefa.responsavel_id": resp, "tarefa.responsavel_nome": pessoas.get(resp, ""), "tarefa.observacao": l["observacao"]})
    fonte_oc = "Cronograma do PCM Direto (52 semanas a partir de 03/11/2025), demonstração"
    ocorrencias = [{"ocorrencia.ativo_id": o["equipamentoId"], "ocorrencia.tarefa_id": o["tarefaId"], "ocorrencia.data_prevista": o["dataPrevista"],
                    "ocorrencia.fonte": fonte_oc} for o in d["ocorrencias"]]
    execucoes = [{"execucao.id": h["id"], "execucao.ativo_id": h["equipamentoId"], "execucao.tarefa_id": h["tarefaId"], "execucao.tag": h["tag"],
                  "execucao.descricao": h["descricao"], "execucao.data_prevista": h["dataPrevista"], "execucao.data": h["data"],
                  "execucao.observacao": h["observacao"], "execucao.responsavel_id": h["responsavelId"],
                  "execucao.responsavel_nome": pessoas.get(h["responsavelId"], ""), "execucao.origem": h["origem"],
                  "execucao.cancelada": "Sim" if h["cancelada"] else "Não"} for h in g["historico"]]
    falhas = [{"falha.id": f["id"], "falha.ativo_id": f["equipamentoId"], "falha.data": f["data"], "falha.tag": f["tag"], "falha.sintoma": f["sintoma"],
               "falha.causa": f["causa"], "falha.acao": f["acao"], "falha.horas_parada": f["horasParada"], "falha.peca": f["peca"],
               "falha.responsavel_id": f["responsavelId"], "falha.responsavel_nome": pessoas.get(f["responsavelId"], "")} for f in g["falhas"]]
    lista = [{"documento.codigo": c, "documento.titulo": t, "documento.tipo": tp, "documento.revisao": "00", "documento.data": "2026-10-23",
              "documento.elaborador": "Pessoa A", "documento.situacao": "Em elaboração", "documento.observacao": "Exemplo fictício"}
             for c, t, tp in E.DOCUMENTOS_PCMD]
    revisoes = [{"revisao.documento": c, "revisao.numero": "00", "revisao.data": "2026-10-23", "revisao.descricao": "Emissão inicial (exemplo fictício)",
                 "revisao.responsavel": "Pessoa A"} for c, _, _ in E.DOCUMENTOS_PCMD]
    setores = [{"setor.sigla": s, "setor.descricao": ""} for s in g["organizacao"]["setores"]]
    pessoas_l = [{"pessoa.id": p["id"], "pessoa.nome": p["nome"], "pessoa.funcao": p["funcao"], "pessoa.especialidade": p["especialidade"],
                  "pessoa.ativo": "Sim" if p["ativo"] else "Não"} for p in g["pessoas"]]
    reqs = [{"requisito.id": q["id"], "requisito.referencia": q["referencia"], "requisito.versao": q["versao"], "requisito.data": q["data"],
             "requisito.fonte": q["fonte"], "requisito.status": "Verificado" if q["status"] == "verificado" else "Não verificado"}
            for q in g["requisitos"]]
    return {"ativos": ativos, "plano": plano, "ocorrencias": ocorrencias, "execucoes": execucoes, "falhas": falhas, "lista": lista,
            "revisoes": revisoes, "setores": setores, "pessoas": pessoas_l, "requisitos": reqs}
