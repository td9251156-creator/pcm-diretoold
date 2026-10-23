"""Gera os manuais PCMD-W1 e PCMD-W2 (templates com marcadores e versões de exemplo).

Template e exemplo saem da mesma função: no template cada {{marcador}} fica visível, em um
único trecho de texto (run), para facilitar um preenchimento futuro; no exemplo o marcador é
substituído por um valor fictício e as regiões repetíveis recebem uma linha por registro.
"""
import datetime as dt
import json
import re

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import especificacao as E
from comum import AUTOR, AVISO, AVISO_FUNDO, AZUL, CONTATO, DATA_MODELO, DESTAQUE, FONTE, LICENCA, LOGO_PNG, RAIZ_REPO, SEGURANCA, VERSAO_MODELO

MARCADOR = re.compile(r"(\{\{[a-z0-9_.]+\}\})")


def _cor(hexa):
    return RGBColor.from_string(hexa)


def sombrear(celula, cor):
    tcPr = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    tcPr.append(shd)


def campo(paragrafo, instrucao, texto_padrao="1"):
    """Campo simples do Word (PAGE, NUMPAGES)."""
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), instrucao)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "16")
    rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = texto_padrao
    r.append(t)
    fld.append(r)
    paragrafo._p.append(fld)


def sumario(paragrafo):
    def fld(tipo):
        f = OxmlElement("w:fldChar")
        f.set(qn("w:fldCharType"), tipo)
        r = OxmlElement("w:r")
        r.append(f)
        return r
    paragrafo._p.append(fld("begin"))
    r = OxmlElement("w:r")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    r.append(instr)
    paragrafo._p.append(r)
    paragrafo._p.append(fld("separate"))
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = ("Sumário ainda não atualizado. No Word: clique aqui com o botão direito e escolha Atualizar campo. "
              "No LibreOffice: Ferramentas > Atualizar > Atualizar tudo.")
    r.append(t)
    paragrafo._p.append(r)
    paragrafo._p.append(fld("end"))


def repetir_cabecalho(linha):
    trPr = linha._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def nao_quebrar(linha):
    trPr = linha._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


class Manual:
    def __init__(self, codigo, titulo, valores=None, regioes=None):
        self.codigo, self.titulo = codigo, titulo
        self.valores = valores  # None = template
        self.regioes = regioes or {}
        self.doc = Document()
        self.marcadores_usados = []  # (marcador, local)
        self.regioes_usadas = []
        self._estilos()
        self._pagina(self.doc.sections[0])
        self._cabecalho_rodape(self.doc.sections[0])

    # ------------------------------------------------------------ estilos e página
    def _estilos(self):
        st = self.doc.styles
        normal = st["Normal"]
        normal.font.name = FONTE
        normal.font.size = Pt(10.5)
        rpr = normal.element.get_or_add_rPr()
        fontes = rpr.find(qn("w:rFonts"))
        if fontes is None:
            fontes = OxmlElement("w:rFonts")
            rpr.append(fontes)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            fontes.set(qn(a), FONTE)
        lang = OxmlElement("w:lang")
        lang.set(qn("w:val"), "pt-BR")
        rpr.append(lang)
        normal.paragraph_format.space_after = Pt(4)
        normal.paragraph_format.line_spacing = 1.1
        for nome, tam in (("Title", 20), ("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 11)):
            s = st[nome]
            s.font.name = FONTE
            s.font.size = Pt(tam)
            s.font.bold = True
            s.font.color.rgb = _cor(AZUL)
            s_rpr = s.element.get_or_add_rPr()
            f = s_rpr.find(qn("w:rFonts"))
            if f is None:
                f = OxmlElement("w:rFonts")
                s_rpr.append(f)
            for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                f.set(qn(a), FONTE)
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
                if f.get(qn(a)) is not None:
                    del f.attrib[qn(a)]
            s.paragraph_format.keep_with_next = True
            s.paragraph_format.space_before = Pt(12 if nome == "Heading 1" else 8)
        for nome in ("List Bullet", "List Number"):
            st[nome].font.name = FONTE
        if "Marcador PCMD" not in [s.name for s in st]:
            m = st.add_style("Marcador PCMD", WD_STYLE_TYPE.CHARACTER)
            m.font.color.rgb = _cor(DESTAQUE)
            m.font.bold = True
        av = st.add_style("Aviso PCMD", WD_STYLE_TYPE.PARAGRAPH)
        av.base_style = st["Normal"]
        av.font.size = Pt(8)
        av.paragraph_format.space_after = Pt(0)
        nt = st.add_style("Nota PCMD", WD_STYLE_TYPE.PARAGRAPH)
        nt.base_style = st["Normal"]
        nt.font.size = Pt(9)
        nt.font.italic = True
        nt.font.color.rgb = _cor("404040")
        tb = st.add_style("Tabela PCMD", WD_STYLE_TYPE.PARAGRAPH)
        tb.base_style = st["Normal"]
        tb.font.size = Pt(9)
        tb.paragraph_format.space_after = Pt(0)
        tb.paragraph_format.line_spacing = 1.0

    def _pagina(self, sec, paisagem=False):
        a4 = (Cm(21.0), Cm(29.7))
        if paisagem:
            sec.orientation = WD_ORIENT.LANDSCAPE
            sec.page_width, sec.page_height = a4[1], a4[0]
        else:
            sec.orientation = WD_ORIENT.PORTRAIT
            sec.page_width, sec.page_height = a4
        sec.left_margin = sec.right_margin = Cm(2.0)
        sec.top_margin = Cm(2.4)
        sec.bottom_margin = Cm(2.6)
        sec.header_distance = Cm(0.9)
        sec.footer_distance = Cm(0.8)

    def _cabecalho_rodape(self, sec):
        largura = sec.page_width - sec.left_margin - sec.right_margin
        cab = sec.header
        p = cab.paragraphs[0]
        p.paragraph_format.tab_stops.add_tab_stop(largura, WD_TAB_ALIGNMENT.RIGHT)
        if LOGO_PNG.exists():
            p.add_run().add_picture(str(LOGO_PNG), height=Cm(1.1))  # só a altura: preserva a proporção
        else:
            r = p.add_run("PCM Direto")
            r.bold = True
        r = p.add_run(f"\t{self.codigo} · {self.titulo}")
        r.font.size, r.bold, r.font.color.rgb = Pt(9), True, _cor(AZUL)
        p2 = cab.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        self._texto(p2, "{{organizacao.nome}}", "cabeçalho", tamanho=8)
        rod = sec.footer
        p = rod.paragraphs[0]
        p.style = self.doc.styles["Aviso PCMD"]
        p.add_run(AVISO).font.size = Pt(8)
        p = rod.add_paragraph(style="Aviso PCMD")
        p.paragraph_format.tab_stops.add_tab_stop(largura, WD_TAB_ALIGNMENT.RIGHT)
        r = p.add_run(f"{self.codigo} · Revisão ")
        r.font.size = Pt(8)
        self._texto(p, "{{documento.revisao}}", "rodapé", tamanho=8)
        r = p.add_run(f" · PCM Direto · Licença {LICENCA}\tPágina ")
        r.font.size = Pt(8)
        campo(p, "PAGE")
        p.add_run(" de ").font.size = Pt(8)
        campo(p, "NUMPAGES")

    # ------------------------------------------------------------ texto com marcadores
    def valor(self, marcador):
        chave = marcador.strip("{}")
        v = self.valores.get(chave)
        return "A definir" if v in (None, "") else str(v)

    def _texto(self, paragrafo, texto, local, tamanho=None, negrito=False):
        for parte in MARCADOR.split(texto):
            if not parte:
                continue
            if MARCADOR.fullmatch(parte):
                self.marcadores_usados.append((parte.strip("{}"), local))
                if self.valores is None:
                    r = paragrafo.add_run(parte, style="Marcador PCMD")
                else:
                    r = paragrafo.add_run(self.valor(parte))
            else:
                r = paragrafo.add_run(parte)
            if tamanho:
                r.font.size = Pt(tamanho)
            if negrito:
                r.bold = True
        return paragrafo

    def p(self, texto, estilo=None):
        return self._texto(self.doc.add_paragraph(style=estilo), texto, "parágrafo")

    def h1(self, texto):
        return self.doc.add_heading(texto, level=1)

    def h2(self, texto):
        return self.doc.add_heading(texto, level=2)

    def lista(self, itens, numerada=False):
        for i in itens:
            self.p(i, "List Number" if numerada else "List Bullet")

    def nota(self, texto):
        return self.p(texto, "Nota PCMD")

    # ------------------------------------------------------------ tabelas
    def _tabela(self, cabecalhos, larguras_cm):
        t = self.doc.add_table(rows=1, cols=len(cabecalhos))
        t.style = self.doc.styles["Table Grid"]
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        for i, w in enumerate(larguras_cm):
            t.columns[i].width = Cm(w)  # grade da tabela (tblGrid): respeitada por Word e LibreOffice
        tblPr = t._tbl.tblPr
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        linha = t.rows[0]
        repetir_cabecalho(linha)
        nao_quebrar(linha)
        for i, c in enumerate(cabecalhos):
            cel = linha.cells[i]
            cel.width = Cm(larguras_cm[i])
            sombrear(cel, AZUL)
            par = cel.paragraphs[0]
            par.style = self.doc.styles["Tabela PCMD"]
            r = par.add_run(c)
            r.bold = True
            r.font.color.rgb = _cor("FFFFFF")
        return t

    def _linha(self, t, textos, larguras_cm, local="célula de tabela", destaque=None):
        linha = t.add_row()
        nao_quebrar(linha)
        for i, tx in enumerate(textos):
            cel = linha.cells[i]
            cel.width = Cm(larguras_cm[i])
            par = cel.paragraphs[0]
            par.style = self.doc.styles["Tabela PCMD"]
            self._texto(par, tx, local)
            if destaque and destaque(i, tx):
                for r in par.runs:
                    r.bold = True
                    r.font.color.rgb = _cor(SEGURANCA)
        return linha

    def tabela(self, cabecalhos, linhas, larguras_cm, legenda=None):
        if legenda:
            self.legenda(legenda)
        t = self._tabela(cabecalhos, larguras_cm)
        for l in linhas:
            self._linha(t, l, larguras_cm)
        self.doc.add_paragraph()
        return t

    def legenda(self, texto):
        par = self.doc.add_paragraph(style="Nota PCMD")
        par.paragraph_format.keep_with_next = True
        par.add_run(texto)

    def regiao(self, rid, larguras_cm, legenda, destaque=None, cabecalhos=None):
        """Tabela repetível. Template: uma linha modelo com marcadores. Exemplo: uma linha por registro."""
        spec = E.REGIOES_DOC[rid]
        campos = [c for c, _ in spec["campos"]]
        cab = cabecalhos or [rot for _, rot in spec["campos"]]
        self.legenda(f"{legenda} · Região repetível «{rid}»: " +
                     ("repita a linha modelo para cada registro." if self.valores is None else "uma linha por registro."))
        t = self._tabela(cab, larguras_cm)
        indice = len(self.doc.tables) - 1
        if self.valores is None:
            self._linha(t, ["{{" + c + "}}" for c in campos], larguras_cm, local=f"célula de tabela (região {rid})")
        else:
            regs = self.regioes.get(rid, [])
            if not regs:
                self._linha(t, ["Nenhum registro"] + [""] * (len(campos) - 1), larguras_cm)
            for reg in regs:
                self._linha(t, [str(reg.get(c, "")) for c in campos], larguras_cm, destaque=destaque)
        self.regioes_usadas.append({"regiao": rid, "tabela_indice": indice, "linha_modelo": 1, "campos": campos})
        self.doc.add_paragraph()
        return t

    def identificacao(self):
        self.doc.add_paragraph(self.titulo, style="Title")
        p = self.doc.add_paragraph()
        r = p.add_run(f"{self.codigo} · Modelo documental do PCM Direto (versão do modelo {VERSAO_MODELO})")
        r.font.color.rgb = _cor(AZUL)
        linhas = [
            ("Código", self.codigo), ("Título", self.titulo), ("Organização", "{{organizacao.nome}}"),
            ("Revisão", "{{documento.revisao}}"), ("Data da revisão", "{{documento.data}}"),
            ("Elaborador", "{{documento.elaborador}}"), ("Aprovador", "{{documento.aprovador}}"),
            ("Próxima revisão", "{{documento.proxima_revisao}}"), ("Situação", "{{documento.situacao}}"),
            ("Referencial", "{{organizacao.referencial}}"), ("Origem dos dados", "{{origem.dados}}"), ("Data de emissão", "{{emissao.data}}"),
        ]
        t = self._tabela(["Identificação documental", "Valor"], [5.0, 12.0])
        for a, b in linhas:
            self._linha(t, [a, b], [5.0, 12.0], local="célula de tabela (identificação)")
        self.doc.add_paragraph()
        self.nota("Aprovador: preencha somente após a aprovação efetiva por quem tem essa atribuição. Este modelo não registra nem presume aprovação.")
        par = self.doc.add_paragraph()
        par.paragraph_format.space_before = Pt(6)
        r = par.add_run(f"AVISO: {AVISO}")
        r.bold = True
        r.font.size = Pt(9.5)
        pPr = par._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), AVISO_FUNDO)
        pPr.append(shd)
        self.nota(f"Modelo PCM Direto · Autor: {AUTOR} · Contato público: {CONTATO} · Licença {LICENCA} · "
                  f"versão {VERSAO_MODELO} de {dt.date.fromisoformat(DATA_MODELO):%d/%m/%Y}. Sem vínculos automáticos com planilhas ou bancos de dados.")
        self.doc.add_heading("Sumário", level=1)
        sumario(self.doc.add_paragraph())
        self.doc.add_page_break()

    def secao_paisagem(self):
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._pagina(sec, paisagem=True)
        # Cabeçalho e rodapé ficam vinculados à seção anterior: o aviso aparece também aqui.
        sec.header.is_linked_to_previous = True
        sec.footer.is_linked_to_previous = True
        return sec

    def checklist(self, itens):
        larg = [1.2, 11.3, 4.5]
        t = self._tabela(["Nº", "Item de conferência", "Conferido por / data"], larg)
        for i, item in enumerate(itens, start=1):
            self._linha(t, [str(i), item, ""], larg)
        self.doc.add_paragraph()

    def salvar(self, caminho):
        self.doc.core_properties.author = "PCM Direto (gerador de modelos)"
        self.doc.core_properties.title = f"{self.codigo} {self.titulo}"
        self.doc.core_properties.subject = AVISO
        self.doc.core_properties.created = dt.datetime(2026, 10, 23, 12, 0, 0)
        self.doc.core_properties.modified = dt.datetime(2026, 10, 23, 12, 0, 0)
        self.doc.core_properties.last_modified_by = "PCM Direto"
        self.doc.save(caminho)


# ------------------------------------------------------------ conteúdo comum
def termos_comuns(m):
    return [
        ("Ativo local", "Equipamento efetivo da organização, com ID técnico próprio, setor, TAG, plano, criticidade e histórico."),
        ("Modelo de máquina compartilhado", "Referência reutilizável do catálogo público do PCM Direto, sujeita a revisão. Não é o inventário da organização "
                                            "nem este documento. Usar um modelo cria um cadastro local; não há sincronização automática."),
        ("Template documental", "Arquivo Excel/Word preenchido com dados locais (este manual é um deles). Não consulta o catálogo nem envia dados."),
        ("ID técnico", "Identificador estável de ativo, tarefa, pessoa, execução ou falha. Não é substituído por TAG, nome ou número de linha."),
        ("TAG", "Rótulo legível do ativo no formato SETOR-SIGLA-NNN (ex.: UTL-CMP-001)."),
        ("Chave da tarefa", "Par ID do ativo|ID da tarefa."),
        ("Chave da ocorrência", "Chave da tarefa|data prevista no formato AAAA-MM-DD."),
        ("Tarefa de segurança", "Tarefa que não pode ser retirada do plano nem ter a frequência reduzida em relação à referência."),
        ("Pendente", "Resultado incompleto: falta informação para concluir (ex.: nota de criticidade ausente)."),
        ("A definir", "Valor que ainda não foi definido pelo responsável. Não é substituído por valor presumido."),
    ]


def referencias(m, rotulo):
    m.h1("Referências")
    m.p("Referencial adotado: {{organizacao.referencial}}. O referencial inicial do PCM Direto é GERAL (sem norma).")
    m.p("Cada referência começa como Não verificado. Só pode ser marcada como Verificado quando houver fonte oficial com endereço HTTPS, versão e data; "
        "essa marcação registra a conferência do responsável e não certifica conformidade. Referências sem fonte suficiente permanecem pendentes. "
        "Não cite número de norma sem fonte oficial, versão e data verificáveis.")
    m.regiao("requisitos", [5.2, 2.0, 2.3, 4.7, 2.8], f"Tabela · Referências do {rotulo} (cadastro M6)")


def responsabilidades(m, papeis):
    m.h1("Responsabilidades")
    m.tabela(["Papel", "Responsabilidade", "Pessoa"], papeis, [4.0, 9.0, 4.0], "Tabela · Papéis neste manual")
    m.regiao("pessoas", [4.0, 4.4, 3.4, 5.2], "Tabela · Pessoas e funções cadastradas (cadastro M3, somente pessoas ativas)")
    m.nota("Inclua apenas os dados pessoais necessários. Pessoas inativadas continuam associadas aos registros anteriores.")


def historico(m):
    m.h1("Histórico de revisão")
    m.regiao("revisoes", [2.0, 2.8, 8.2, 4.0], "Tabela · Histórico de revisão deste documento")


# ------------------------------------------------------------ W1
def manual_w1(valores=None, regioes=None):
    m = Manual("PCMD-W1", "Manual de Gestão de Ativos", valores, regioes)
    m.identificacao()

    m.h1("Objetivo e escopo")
    m.p("Este manual descreve como {{organizacao.nome}} cadastra, identifica, classifica e mantém o histórico dos seus ativos de manutenção, "
        "usando os registros do PCM Direto e os modelos PCMD.")
    m.p("Escopo: cadastro e hierarquia dos ativos, IDs e TAGs, setores, criticidade, responsáveis, conservação do histórico, requisitos e fontes, "
        "controle documental e distinção entre o cadastro local e o modelo público do catálogo.")
    m.p("Fora do escopo: procedimentos de execução de tarefas, cálculo de indicadores sem regra aprovada e qualquer declaração de conformidade legal.")

    m.h1("Termos e definições")
    m.tabela(["Termo", "Definição"], termos_comuns(m), [4.5, 12.5])

    referencias(m, "PCMD-W1")
    responsabilidades(m, [
        ("Elaborador", "Prepara e atualiza este manual e os cadastros de referência.", "{{documento.elaborador}}"),
        ("Aprovador", "Aprova o manual depois de revisado. O campo só é preenchido após aprovação efetiva.", "{{documento.aprovador}}"),
        ("Responsável pela criticidade", "Define o significado dos níveis 1, 2 e 3 de cada critério e confere as notas atribuídas.", "A definir"),
        ("Responsável por tarefa", "Pessoa associada a cada tarefa no plano mestre (PCMD-03).", "Ver PCMD-03"),
    ])

    m.h1("Cadastro e hierarquia dos ativos")
    m.p("A hierarquia usada pelos registros é: organização → setor → ativo → tarefas do plano. Cada ativo pertence a um setor e a um tipo de "
        "equipamento da biblioteca técnica.")
    m.h2("IDs e TAGs")
    m.lista([
        "Cada ativo tem um ID técnico estável, criado no cadastro. O ID não muda quando a descrição ou a TAG mudam.",
        "A TAG segue o formato SETOR-SIGLA-NNN: sigla do setor (2 a 4 letras ou números), sigla de 3 letras do tipo e número com 3 dígitos.",
        "TAG, nome de pessoa, número de linha ou título não substituem os IDs técnicos nos vínculos entre registros.",
        "Execuções e falhas guardam a TAG e a descrição vigentes no momento do registro; renomear o ativo não reescreve o histórico.",
    ])
    m.h2("Setores")
    m.regiao("setores", [3.0, 14.0], "Tabela · Setores cadastrados")
    m.h2("Registro dos ativos")
    m.p("A lista completa dos ativos, com notas e classe de criticidade, está no Anexo A deste manual e na planilha PCMD-02 Ativos.")

    m.h1("Criticidade")
    m.p("A criticidade usa cinco critérios, nesta ordem: Segurança (N1), Qualidade (N2), Produção (N3), Frequência de falha (N4) e "
        "Custo/tempo de reparo (N5). Cada nota é um número inteiro de 1 a 3. Nota ausente é ausência, não zero.")
    m.tabela(["Situação", "Resultado"], [
        ("Alguma nota ausente ou inválida", "Classe Pendente, sem soma parcial como resultado."),
        ("Cinco notas válidas e Segurança = 3", "Classe A."),
        ("Cinco notas válidas e soma ≥ limite A ({{criticidade.limite_a}})", "Classe A."),
        ("Cinco notas válidas e soma ≥ limite B ({{criticidade.limite_b}})", "Classe B."),
        ("Demais casos com cinco notas válidas", "Classe C."),
        ("Limites inválidos (fora de 5 ≤ B < A ≤ 15 ou não inteiros)", "Classe Pendente, com orientação para corrigir os limites."),
    ], [8.0, 9.0], "Tabela · Regra de classificação (a soma vai de 5 a 15)")
    m.p("Limites vigentes: A = {{criticidade.limite_a}} e B = {{criticidade.limite_b}}. Os limites iniciais do PCM Direto são A = 12 e B = 9.")
    m.tabela(["Critério", "Nível 1", "Nível 2", "Nível 3"], [
        (c, "A definir pelo mantenedor", "A definir pelo mantenedor", "A definir pelo mantenedor")
        for c in ("N1 Segurança", "N2 Qualidade", "N3 Produção", "N4 Frequência de falha", "N5 Custo/tempo de reparo")
    ], [4.4, 4.2, 4.2, 4.2], "Tabela · Significado dos níveis (definido pelo responsável; o PCM Direto não define)")
    m.p("A classe de criticidade não altera automaticamente frequências, tarefas nem proteções de segurança. Qualquer mudança no plano é decisão "
        "registrada do profissional responsável.")

    m.h1("Responsáveis pelas tarefas")
    m.p("Cada tarefa do plano mestre pode ter uma pessoa responsável, identificada pelo ID da pessoa. O nome exibido vem do cadastro de pessoas; "
        "alterar o nome não quebra o vínculo. Pessoas inativas permanecem nos registros anteriores.")

    m.h1("Conservação do histórico")
    m.lista([
        "Cada execução é um registro com ID próprio; pode haver vários registros para a mesma tarefa.",
        "Cancelar uma execução mantém o registro no histórico e o exclui da contagem do realizado.",
        "Marcações antigas migradas aparecem como legado sem vínculo e não multiplicam realizações.",
        "Remover um ativo não apaga o histórico de execuções e falhas; os registros preservam TAG e descrição.",
        "Horas de parada vazias significam não informado; não são convertidas em zero.",
    ])

    m.h1("Requisitos e fontes")
    m.p("Os requisitos aplicáveis são registrados na tabela de referências (seção Referências) com fonte, versão, data e status. "
        "Enquanto não houver fonte oficial verificável, o requisito permanece Não verificado.")

    m.h1("Controle documental")
    m.p("Os documentos do sistema usam o prefixo PCMD e estão relacionados na lista mestra (PCMD-01), com revisão, data, elaborador, aprovador, "
        "próxima revisão e situação. Cada revisão é registrada no histórico de revisão. A próxima revisão deste manual é {{documento.proxima_revisao}}.")
    m.tabela(["Código", "Documento"], [(c, t) for c, t, _ in E.DOCUMENTOS_PCMD], [3.0, 14.0], "Tabela · Documentos PCMD")

    m.h1("Cadastro local e modelo público")
    m.p("O catálogo colaborativo do PCM Direto reúne modelos de máquina compartilhados, sujeitos a revisão. Ao usar um modelo, cria-se um ativo local; "
        "as tarefas sugeridas na contribuição não substituem automaticamente a biblioteca validada nem suas proteções, e não há sincronização "
        "automática com o catálogo.")
    m.p("Pessoas, organização, falhas e execuções pertencem à gestão local e não devem ser publicadas no catálogo. Este manual e as planilhas não "
        "consultam o catálogo pela internet nem enviam dados.")

    m.h1("Indicadores")
    m.tabela(["Indicador", "Regra explícita", "Meta", "Situação"], [
        ("Ativos com criticidade concluída", "Ativos com classe A, B ou C ÷ ativos cadastrados (PCMD-02).", "A definir", "Regra definida; meta a definir"),
        ("Ativos com classe Pendente", "Contagem de ativos com classe Pendente (PCMD-02).", "A definir", "Regra definida; meta a definir"),
        ("Requisitos verificados", "Requisitos com status Verificado ÷ requisitos cadastrados.", "A definir", "Regra definida; meta a definir"),
        ("Disponibilidade", "Não calculada: regra técnica a definir pelo mantenedor.", "{{metas.disponibilidade}}", "A definir"),
        ("MTBF e MTTR", "Não calculados: regras técnicas a definir pelo mantenedor.", "A definir", "A definir"),
    ], [3.8, 6.4, 2.8, 4.0], "Tabela · Indicadores do manual")

    m.h1("Checklist de conferência")
    m.checklist([
        "Todos os ativos têm ID técnico, TAG, setor e tipo.",
        "As TAGs seguem o formato SETOR-SIGLA-NNN e não há IDs repetidos.",
        "O significado dos níveis 1, 2 e 3 de cada critério foi definido pelo responsável.",
        "Ativos com classe Pendente foram identificados e têm responsável pela avaliação.",
        "Limites A e B são inteiros e respeitam 5 ≤ B < A ≤ 15.",
        "Referências marcadas como Verificado têm fonte HTTPS, versão e data.",
        "Nenhum número de norma foi citado sem fonte oficial, versão e data.",
        "Histórico de execuções e falhas foi preservado após alterações no cadastro.",
        "Elaborador preenchido; aprovador preenchido somente após aprovação efetiva.",
        "Lista mestra e histórico de revisão atualizados.",
    ])
    historico(m)

    m.secao_paisagem()
    m.h1("Anexo A · Ativos e criticidade")
    m.p("Origem: PCMD-02 Ativos. Nota vazia = não avaliada; pontuação só aparece com as cinco notas válidas.")
    m.regiao("ativos", [2.6, 6.4, 1.4, 3.4, 1.1, 1.1, 1.1, 1.1, 1.1, 2.4, 2.0], "Tabela · Ativos e criticidade",
             destaque=lambda i, tx: i == 10 and tx == "Pendente")
    return m


# ------------------------------------------------------------ W2
def manual_w2(valores=None, regioes=None):
    m = Manual("PCMD-W2", "Manual de Estratégia de Manutenção", valores, regioes)
    m.identificacao()

    m.h1("Objetivo e escopo")
    m.p("Este manual descreve como {{organizacao.nome}} avalia as consequências das falhas, escolhe e revisa as estratégias de manutenção, "
        "registra a origem das tarefas, planeja, executa e trata falhas, usando os registros do PCM Direto e os modelos PCMD.")
    m.p("As estratégias, os prazos por classe e as metas são definidos pelo profissional responsável. Enquanto não forem definidos, aparecem como "
        "A definir; este manual não cria regras técnicas.")

    m.h1("Termos e definições")
    m.tabela(["Termo", "Definição"], termos_comuns(m) + [
        ("Ocorrência prevista", "Trio ativo + tarefa + data prevista gerado a partir do plano vigente."),
        ("Execução vinculada", "Registro de realização que informa a data prevista da ocorrência que atendeu."),
        ("Estratégia de manutenção", "Forma de atuação escolhida para um ativo ou tarefa pelo profissional responsável."),
    ], [4.5, 12.5])

    referencias(m, "PCMD-W2")
    responsabilidades(m, [
        ("Elaborador", "Prepara e atualiza este manual.", "{{documento.elaborador}}"),
        ("Aprovador", "Aprova o manual depois de revisado. O campo só é preenchido após aprovação efetiva.", "{{documento.aprovador}}"),
        ("Profissional responsável pela estratégia", "Avalia as consequências, escolhe e revisa as estratégias, define prazos por classe.", "{{estrategia.responsavel}}"),
        ("Responsável por tarefa", "Pessoa associada a cada tarefa no plano mestre (PCMD-03).", "Ver PCMD-03"),
    ])

    m.h1("Avaliação das consequências")
    m.p("A avaliação parte da criticidade registrada no Manual de Gestão de Ativos (PCMD-W1) e na planilha PCMD-02: cinco notas de 1 a 3 "
        "(Segurança, Qualidade, Produção, Frequência de falha e Custo/tempo de reparo) e a classe A, B, C ou Pendente.")
    m.lista([
        "Ativos com classe Pendente são avaliados antes de qualquer decisão de estratégia baseada na classe.",
        "O profissional responsável registra a justificativa de cada decisão no histórico de revisão ou em documento próprio.",
        "A classe não altera automaticamente a frequência de nenhuma tarefa.",
    ])

    m.h1("Escolha e revisão das estratégias")
    m.p("A escolha da estratégia é feita pelo profissional responsável ({{estrategia.responsavel}}). A tabela abaixo fica em A definir até que "
        "essa definição técnica seja registrada.")
    m.tabela(["Classe", "Estratégia predominante", "Prazo de atendimento", "Revisão do plano"], [
        (c.upper(), f"{{{{estrategia.classe_{c}.estrategia}}}}", f"{{{{estrategia.classe_{c}.prazo}}}}", f"{{{{estrategia.classe_{c}.revisao}}}}")
        for c in "abc"
    ] + [("Pendente", "Avaliar a criticidade antes de definir", "Não se aplica", "Não se aplica")],
        [2.2, 5.6, 4.6, 4.6], "Tabela · Estratégia por classe (definição do profissional responsável)")
    m.p("Periodicidade de revisão desta estratégia: {{estrategia.periodicidade_revisao}}.")

    m.h1("Origem das tarefas")
    m.lista([
        "As tarefas vêm da biblioteca técnica do PCM Direto, com origem e versão registradas em cada tarefa.",
        "Tarefa genérica traz a origem exata: base genérica a validar com manual do fabricante.",
        "Ao confirmar uma tarefa em manual do fabricante ou outra fonte, a origem e a versão da tarefa são atualizadas.",
        "Tarefa marcada como segurança não pode ser excluída, desmarcada nem ter intervalo ampliado em relação à referência; só é permitido manter "
        "ou aumentar a frequência.",
        "Validações e proteções de planilhas ajudam a evitar erros, mas podem ser contornadas por colagem ou edição externa; não substituem as travas do app.",
    ])

    m.h1("Planejamento")
    m.h2("Plano mestre e cronograma")
    m.lista([
        "O plano mestre (PCMD-03) é a fonte do cronograma: atividade, frequência vigente, especialidade, duração estimada e responsável.",
        "O cronograma do PCM Direto trabalha com 52 semanas a partir da data de início do ciclo, sem calendário ISO e sem redistribuir tarefas entre meses.",
        "Tarefa diária considera cinco dias úteis por semana, sem calendário de feriados; cada dia útil é uma ocorrência com a duração de um dia.",
        "Horas previstas são estimadas a partir da duração da tarefa. Não representam horas efetivamente trabalhadas.",
    ])

    m.h1("Execução e registro")
    m.h2("Vínculo entre execução e ocorrência prevista")
    m.lista([
        "Cada realização é registrada como uma execução, com data realizada, responsável e, quando houver, a data prevista da ocorrência atendida.",
        "O realizado é contado pelo vínculo explícito à ocorrência prevista, nunca pela coincidência da data real.",
        "Duas execuções da mesma ocorrência contam uma ocorrência concluída.",
        "Execuções canceladas permanecem no histórico e não contam. Execuções sem vínculo (incluindo legado) aparecem separadas.",
        "O mês considerado é o da data prevista, mesmo que a realização ocorra em outro mês.",
    ])

    m.h1("Tratamento de falhas")
    m.p("Cada falha é registrada na ficha PCMD-05 com ativo, data, sintoma, causa, ação, horas de parada (opcional), peça e responsável. "
        "A análise de causa e a definição de ações seguem o critério do profissional responsável; este manual não prescreve procedimentos técnicos.")
    m.lista([
        "Horas de parada vazias significam não informado e não são tratadas como zero.",
        "Falhas recorrentes são levadas à revisão da estratégia, conforme a periodicidade definida.",
        "Não são calculados MTBF, MTTR ou disponibilidade sem regras aprovadas.",
    ])

    m.h1("Indicadores")
    m.tabela(["Indicador", "Regra explícita", "Meta", "Situação"], [
        ("% realizado do plano (por ocorrência)", "Ocorrências concluídas distintas ÷ ocorrências previstas distintas no mês da data prevista. "
         "Mês sem previsão: Sem previsão.", "{{metas.aderencia}}", "Regra definida"),
        ("Falhas registradas", "Contagem de registros da PCMD-05 no período.", "A definir", "Regra definida; meta a definir"),
        ("Horas de parada informadas", "Soma das horas informadas na PCMD-05; registros vazios não entram como zero.", "A definir",
         "Regra definida; não é indicador de disponibilidade"),
        ("Disponibilidade, MTBF e MTTR", "Não calculados: regras técnicas a definir pelo mantenedor.", "{{metas.disponibilidade}}", "A definir"),
    ], [3.8, 6.6, 2.6, 4.0], "Tabela · Indicadores do manual")

    m.h1("Revisão do manual e da estratégia")
    m.p("A estratégia é revisada pelo profissional responsável na periodicidade {{estrategia.periodicidade_revisao}} e sempre que houver mudança "
        "relevante no ativo, na criticidade, no histórico de falhas ou nas referências. Cada revisão é registrada no histórico abaixo e na lista mestra (PCMD-01).")

    m.h1("Checklist de conferência")
    m.checklist([
        "Todos os ativos têm criticidade avaliada ou estão identificados como Pendente.",
        "A estratégia por classe foi definida pelo profissional responsável ou permanece A definir.",
        "Tarefas de segurança mantêm frequência igual ou maior que a referência e não foram retiradas.",
        "Toda tarefa tem origem e versão; tarefas genéricas trazem a origem exata da base genérica.",
        "Execuções informam a data prevista quando atendem uma ocorrência do cronograma.",
        "Execuções canceladas e sem vínculo não foram contadas no percentual.",
        "Falhas registradas com sintoma, data e ativo; horas de parada vazias não foram tratadas como zero.",
        "Metas e indicadores sem regra aprovada permanecem A definir.",
        "Elaborador preenchido; aprovador preenchido somente após aprovação efetiva.",
        "Histórico de revisão e lista mestra atualizados.",
    ])
    historico(m)

    m.secao_paisagem()
    m.h1("Anexo A · Plano mestre (resumo)")
    m.p("Origem: PCMD-03 Plano Mestre. Segurança = Sim indica tarefa que não pode ser retirada nem ter a frequência reduzida.")
    m.regiao("tarefas", [2.4, 1.7, 6.6, 2.2, 2.7, 2.0, 2.3, 3.4, 2.4], "Tabela · Tarefas do plano",
             destaque=lambda i, tx: i == 6 and tx == "Sim")
    return m


# ------------------------------------------------------------ dados do exemplo
def valores_exemplo(d):
    g = d["gestao"]
    pessoas = {p["id"]: p["nome"] for p in g["pessoas"]}
    org = g["organizacao"]
    v = {
        "organizacao.nome": org["nome"], "organizacao.referencial": org["referencial"],
        "documento.revisao": "00", "documento.data": "23/10/2026",
        "documento.elaborador": pessoas.get(org["elaborador"], ""),
        "documento.aprovador": pessoas.get(org["aprovador"], "") or "A definir (aprovação não registrada)",
        "documento.proxima_revisao": "", "documento.situacao": "Em elaboração",
        "emissao.data": "23/10/2026", "origem.dados": "Demonstração fictícia (não é exportação do app)",
        "criticidade.limite_a": g["criticidade"]["limites"]["a"], "criticidade.limite_b": g["criticidade"]["limites"]["b"],
        "metas.disponibilidade": "" if g["metas"]["disponibilidade"] is None else f"{g['metas']['disponibilidade']}%",
        "metas.aderencia": "" if g["metas"]["aderencia"] is None else f"{g['metas']['aderencia']}%",
    }
    with open(RAIZ_REPO / "src" / "dados" / "biblioteca.json", encoding="utf-8") as f:
        nomes_tipo = {t["id"]: t["nome"] for t in json.load(f)["tipos"]}
    status = {"verificado": "Verificado", "nao_verificado": "Não verificado"}
    reg = {
        "requisitos": [{"requisito.referencia": q["referencia"], "requisito.versao": q["versao"] or "A definir",
                        "requisito.data": q["data"] or "A definir", "requisito.fonte": q["fonte"] or "A definir",
                        "requisito.status": status[q["status"]]} for q in g["requisitos"]],
        "pessoas": [{"pessoa.nome": p["nome"], "pessoa.funcao": p["funcao"], "pessoa.especialidade": p["especialidade"],
                     "pessoa.responsabilidade": "A definir"} for p in g["pessoas"] if p["ativo"]],
        "setores": [{"setor.sigla": s, "setor.descricao": "A definir"} for s in org["setores"]],
        "revisoes": [{"revisao.numero": "00", "revisao.data": "23/10/2026", "revisao.descricao": "Emissão inicial (exemplo fictício)",
                      "revisao.responsavel": pessoas.get(org["elaborador"], "")}],
    }
    ativos = []
    for e in d["equipamentos"]:
        n = g["criticidade"]["notas"].get(e["id"], [None] * 5)
        c = d["criticidade"].get(e["id"], {"pontuacao": None, "classe": "Pendente"})
        ativos.append({"ativo.tag": e["tag"], "ativo.descricao": e["descricao"], "ativo.setor": e["setor"], "ativo.tipo_nome": nomes_tipo.get(e["tipo"], e["tipo"]),
                       "criticidade.nota_seguranca": n[0] or "", "criticidade.nota_qualidade": n[1] or "", "criticidade.nota_producao": n[2] or "",
                       "criticidade.nota_frequencia_falha": n[3] or "", "criticidade.nota_custo_reparo": n[4] or "",
                       "criticidade.pontuacao": c["pontuacao"] if c["pontuacao"] is not None else "", "criticidade.classe": c["classe"]})
    reg["ativos"] = ativos
    tarefas = []
    for l in sorted(d["plano"], key=lambda x: (x["tag"], x["tarefaId"])):
        resp = g["responsaveis"].get(f"{l['equipamentoId']}|{l['tarefaId']}", "")
        tarefas.append({"tarefa.tag": l["tag"], "tarefa.id": l["tarefaId"], "tarefa.atividade": l["descricao"], "tarefa.frequencia_vigente": l["periodicidade"],
                        "tarefa.especialidade": l["especialidade"], "tarefa.duracao_horas": f"{l['duracaoHoras']:.2f}".replace(".", ","),
                        "tarefa.seguranca": "Sim" if l["seguranca"] else "Não", "tarefa.origem_versao": f"{l['origem']} · {l['versao']}",
                        "tarefa.responsavel_nome": pessoas.get(resp, "")})
    reg["tarefas"] = tarefas
    return v, reg
