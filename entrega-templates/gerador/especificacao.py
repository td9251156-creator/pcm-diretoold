"""Especificação única das abas, colunas, marcadores e regiões.

Os geradores XLSX/DOCX e o CONTRATO-CAMPOS.json leem esta especificação, para que o
contrato descreva exatamente o que foi gerado. O mapeamento de origem é PROPOSTO:
o adaptador de integração ainda será implementado e testado depois.
"""
from dataclasses import dataclass, field

from comum import RAMO_GESTAO

# Padrão visual PCM Direto: linhas 1-2 = bloco de cabeçalho (logo, título, revisão), linha 3 = aviso,
# linha 4 = respiro, linha 5 = faixa azul (grupos de colunas), linha 6 = cabeçalho da tabela.
LINHA_TIPO = 5      # faixa azul com os grupos de colunas
LINHA_CAB = 6       # cabeçalho da tabela
PRIMEIRA = 7        # primeira linha de dados

MAIN = "main"
RAMO = "ramo"
MANUAL = "manual"
FUTURO = "futuro"
CALCULO = "calculo"

SITUACAO_ORIGEM = {
    MAIN: "Existe no app (main): src/estado.js, src/logica/plano.js, src/logica/cronograma.js ou src/dados/biblioteca.json.",
    RAMO: f"Existe apenas no ramo {RAMO_GESTAO}: estado.gestao.",
    MANUAL: "Preenchimento manual/documental: o app não possui este dado.",
    FUTURO: "Campo futuro reservado: não existe no app nem é integrado; deixar vazio.",
    CALCULO: "Calculado por fórmula no modelo; o adaptador não deve escrever nesta célula.",
}

PAPEIS = {  # rótulo curto exibido acima do cabeçalho, descrição usada no contrato
    "id": ("ID", "Identificador técnico estável; não substituir por TAG, nome ou número de linha."),
    "entrada": ("PREENCHER", "Célula de entrada."),
    "referencia": ("REFERÊNCIA", "Referência técnica da biblioteca/plano; protegida contra edição acidental."),
    "calculo": ("AUTOMÁTICO", "Resultado de fórmula; não digitar."),
    "manual": ("PREENCHER", "Preenchimento manual documental; o app não fornece."),
    "futuro": ("FUTURO", "Reservado para uso futuro; não integrado; deixar vazio."),
}

PRIV_NENHUM = "sem dado pessoal"
PRIV_NOME = "dado pessoal mínimo (nome de pessoa); manter local"
PRIV_LIVRE = "texto livre: pode conter dado pessoal ou da organização; manter local, não publicar"
PRIV_ORG = "dado da organização; manter local, não publicar no catálogo"


@dataclass
class Coluna:
    id: str
    cabecalho: str
    papel: str
    tipo: str
    origem: str
    origem_status: str
    obrigatorio: str = "opcional"
    formato: str = "texto"
    vazio: str = "Vazio = não informado."
    validacao: str = "—"
    formula: str | None = None
    largura: float = 14
    privacidade: str = PRIV_NENHUM
    obs: str = ""
    nome: str | None = None  # intervalo nomeado da coluna
    dv: dict | None = None   # validação de dados do Excel
    numero: str | None = None  # formato numérico do Excel
    oculta: bool = False       # coluna técnica: continua calculando, mas fica oculta na tela e na impressão


@dataclass
class Aba:
    nome: str
    codigo: str
    titulo: str
    instrucao: str  # uma frase curta exibida na linha 2
    colunas: list
    capacidade: int
    paisagem: bool = True
    congelar_col: int = 0
    protegida: bool = False
    linhas_impressao_modelo: int = 30
    paginas_largura: int = 1          # páginas na largura da impressão
    colunas_repetidas: str | None = None  # colunas repetidas em cada página (ex.: "A:B")
    extra: dict = field(default_factory=dict)


def _r(texto: str) -> str:
    return f"{texto} — ramo {RAMO_GESTAO}"


DATA_DV = {"type": "date", "operator": "between", "formula1": "1", "formula2": "2958465",
           "error": "Informe uma data válida (dd/mm/aaaa).", "prompt": "Data real do Excel, exibida em dd/mm/aaaa."}
HORAS_DV = {"type": "decimal", "operator": "greaterThanOrEqual", "formula1": "0",
            "error": "Informe horas como número decimal maior ou igual a zero (ex.: 1,5).",
            "prompt": "Horas em número decimal (1,5 = uma hora e meia). Vazio = não informado."}
SIMNAO_DV = {"type": "list", "formula1": "=lst_sim_nao", "error": "Use Sim ou Não.", "prompt": "Escolha Sim ou Não."}
ID_DV = {"type": "custom", "formula1": "AND(LEN({c})<=120,ISERROR(FIND(\"|\",{c})),ISERROR(FIND(\" \",{c})))",
         "error": "ID técnico: sem espaços e sem o caractere |.", "prompt": "ID técnico estável (letras sem acento, números, hífen ou sublinhado)."}

NOTA_DV = {"type": "whole", "operator": "between", "formula1": "1", "formula2": "3",
           "error": "A nota deve ser um número inteiro de 1 a 3. Deixe vazio se ainda não avaliou.",
           "prompt": "Inteiro de 1 a 3. Vazio = não avaliado (classe Pendente)."}


def responsavel(prefixo, origem_id):
    """ID e nome do responsável. Cada arquivo é independente: o nome é gravado ao lado do ID, sem consulta a outro arquivo."""
    return [
        Coluna(f"{prefixo}.responsavel_id", "Responsável (ID)", "entrada", "texto", _r(origem_id), RAMO, largura=11, dv=ID_DV,
               obs="ID de gestao.pessoas[] (cadastro em PCMD-01, aba Pessoas)."),
        Coluna(f"{prefixo}.responsavel_nome", "Responsável (nome)", "entrada", "texto",
               _r(f"nome de gestao.pessoas[] com id = {origem_id}"), RAMO, largura=16, privacidade=PRIV_NOME,
               obs="Nome exibido; o vínculo é feito pelo ID."),
    ]


def chave_data(col_chave, col_data):
    """Chave textual AAAA-MM-DD sem TEXT(), que depende do idioma do Excel."""
    return (f'=IF(OR({col_chave}{{r}}="",NOT(ISNUMBER({col_data}{{r}}))),"",{col_chave}{{r}}&"|"&YEAR({col_data}{{r}})&"-"&'
            f'RIGHT("0"&MONTH({col_data}{{r}}),2)&"-"&RIGHT("0"&DAY({col_data}{{r}}),2))')


def nota_valida(c):
    return f"IF(ISNUMBER({c}{{r}}),AND({c}{{r}}=INT({c}{{r}}),{c}{{r}}>=1,{c}{{r}}<=3),FALSE)"


# ---------------------------------------------------------------- PCMD-01
LISTA_MESTRA = Aba(
    nome="Lista Mestra", codigo="PCMD-01", titulo="Lista mestra de documentos",
    instrucao="Uma linha por documento. Informe o aprovador só depois da aprovação efetiva.",
    capacidade=50, linhas_impressao_modelo=12,
    colunas=[
        Coluna("documento.codigo", "Código", "entrada", "texto", "Código PCMD do modelo (documental)", MANUAL, "obrigatório",
               largura=12, validacao="Texto; código PCMD-xx ou PCMD-Wx.", obs="Linhas dos documentos PCMD já vêm preenchidas."),
        Coluna("documento.titulo", "Título", "entrada", "texto", "Título do documento (documental)", MANUAL, "obrigatório", largura=34),
        Coluna("documento.tipo", "Tipo", "entrada", "lista", "Documental", MANUAL, largura=16,
               dv={"type": "list", "formula1": "=lst_tipo_documento", "error": "Escolha um tipo da aba Listas.", "prompt": "Tipo do documento."},
               validacao="Lista lst_tipo_documento."),
        Coluna("documento.revisao", "Revisão", "manual", "texto", "Documental", MANUAL, largura=10, validacao="Texto (ex.: 00, 01)."),
        Coluna("documento.data", "Data da revisão (dd/mm/aaaa)", "manual", "data", "Documental", MANUAL, formato="data dd/mm/aaaa",
               largura=14, dv=DATA_DV, numero="dd/mm/yyyy", validacao="Data válida."),
        Coluna("documento.elaborador", "Elaborador (nome)", "manual", "texto",
               _r("Sugestão: nome de gestao.pessoas[] cujo id = gestao.organizacao.elaborador"), RAMO, largura=18, privacidade=PRIV_NOME,
               obs="No app o elaborador padrão é um ID de pessoa; aqui fica o nome exibido no documento."),
        Coluna("documento.aprovador", "Aprovador (nome)", "manual", "texto",
               _r("Sugestão: nome de gestao.pessoas[] cujo id = gestao.organizacao.aprovador"), RAMO, largura=18, privacidade=PRIV_NOME,
               obs="Preencher somente após aprovação efetiva. Não declarar aprovação inexistente."),
        Coluna("documento.proxima_revisao", "Próxima revisão (dd/mm/aaaa)", "manual", "data", "Documental: não existe no app", MANUAL,
               formato="data dd/mm/aaaa", largura=14, dv=DATA_DV, numero="dd/mm/yyyy", vazio="Vazio = a definir."),
        Coluna("documento.situacao", "Situação", "manual", "lista", "Documental", MANUAL, largura=15,
               dv={"type": "list", "formula1": "=lst_situacao_documento", "error": "Escolha uma situação da aba Listas.", "prompt": "Situação do documento."},
               validacao="Lista lst_situacao_documento (proposta, editável)."),
        Coluna("documento.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=30,
               formula='=IF(A{r}="","",IF(AND(ISNUMBER(E{r}),ISNUMBER(H{r}),H{r}<E{r}),"Verificar: próxima revisão anterior à data",'
                       'IF(AND(G{r}<>"",I{r}<>"Aprovado"),"Verificar: aprovador sem situação Aprovado",IF(AND(I{r}="Aprovado",G{r}=""),"Verificar: Aprovado sem aprovador","OK"))))'),
        Coluna("documento.observacao", "Observação", "manual", "texto", "Documental", MANUAL, largura=24, privacidade=PRIV_LIVRE),
    ],
)

DOCUMENTOS_PCMD = [
    ("PCMD-01", "Lista mestra de documentos", "Planilha (XLSX)"),
    ("PCMD-02", "Ativos e criticidade", "Planilha (XLSX)"),
    ("PCMD-03", "Plano mestre de manutenção", "Planilha (XLSX)"),
    ("PCMD-04", "Cronograma e acompanhamento mensal", "Planilha (XLSX)"),
    ("PCMD-05", "Ficha de falha", "Planilha (XLSX)"),
    ("PCMD-W1", "Manual de Gestão de Ativos", "Manual (DOCX)"),
    ("PCMD-W2", "Manual de Estratégia de Manutenção", "Manual (DOCX)"),
]

# ---------------------------------------------------------------- PCMD-02
ATIVOS = Aba(
    nome="Ativos", codigo="PCMD-02", titulo="Ativos e criticidade",
    instrucao="Uma linha por ativo. Notas inteiras de 1 a 3; nota vazia deixa a classe Pendente. Limites A/B na aba Critérios.",
    capacidade=300, congelar_col=2, paginas_largura=2, colunas_repetidas="A:B",
    colunas=[
        Coluna("ativo.id", "ID do ativo", "id", "texto", "estado.equipamentos[].id", MAIN, "obrigatório", largura=13,
               dv=ID_DV, nome="at_id", validacao="Único; sem espaços e sem |.", obs="TAG não substitui o ID."),
        Coluna("ativo.tag", "TAG", "entrada", "texto", "estado.equipamentos[].tag (SETOR-SIGLA-NNN, src/logica/tag.js)", MAIN, "obrigatório",
               largura=14, nome="at_tag"),
        Coluna("ativo.descricao", "Descrição do equipamento", "entrada", "texto", "estado.equipamentos[].descricao", MAIN, "obrigatório",
               largura=30, nome="at_descricao", privacidade=PRIV_ORG),
        Coluna("ativo.tipo_id", "Tipo (ID)", "entrada", "lista", "estado.equipamentos[].tipo (id do tipo na biblioteca)", MAIN, "obrigatório",
               largura=17, dv={"type": "list", "formula1": "=lst_tipo_id", "error": "Use um tipo da aba Listas.", "prompt": "ID do tipo de equipamento da biblioteca."},
               validacao="Lista lst_tipo_id."),
        Coluna("ativo.tipo_nome", "Tipo (nome)", "calculo", "texto", "Fórmula a partir de Listas (biblioteca.tipos[].nome)", CALCULO, largura=16,
               formula='=IF(D{r}="","",IFERROR(INDEX(lst_tipo_nome,MATCH(D{r},lst_tipo_id,0)),"Tipo não cadastrado em Listas"))'),
        Coluna("ativo.fabricante", "Fabricante", "entrada", "texto", "estado.equipamentos[].fabricante", MAIN, largura=20, privacidade=PRIV_ORG),
        Coluna("ativo.modelo", "Modelo", "entrada", "texto", "estado.equipamentos[].modelo", MAIN, largura=20, privacidade=PRIV_ORG),
        Coluna("ativo.setor", "Setor (sigla)", "entrada", "lista", "estado.equipamentos[].setor", MAIN, "obrigatório", largura=9,
               dv={"type": "list", "formula1": "=cad_setor", "error": "Cadastre o setor em Cadastros (bloco Setores).", "prompt": "Sigla do setor (2 a 4 letras/números)."},
               validacao="Lista cad_setor."),
        Coluna("ativo.numero", "Número", "entrada", "inteiro", "estado.equipamentos[].numero", MAIN, "obrigatório", formato="inteiro 1–999", largura=8,
               dv={"type": "whole", "operator": "between", "formula1": "1", "formula2": "999", "error": "Número inteiro de 1 a 999.", "prompt": "Número do ativo no setor e tipo (1 a 999)."},
               numero="0"),
        Coluna("ativo.tag_conferencia", "Conferência da TAG", "calculo", "texto", "Fórmula: SETOR-SIGLA-NNN", CALCULO, largura=16,
               formula='=IF(OR(B{r}="",D{r}="",H{r}="",I{r}=""),"",IF(B{r}=H{r}&"-"&IFERROR(INDEX(lst_tipo_sigla,MATCH(D{r},lst_tipo_id,0)),"???")&"-"&RIGHT("00"&I{r},3),"OK","Verificar: TAG difere de setor-sigla-número"))'),
        Coluna("criticidade.nota_seguranca", "N1 Segurança (1–3)", "entrada", "inteiro", _r("gestao.criticidade.notas[ativo.id][0]"), RAMO,
               "condicional", formato="inteiro 1–3", largura=10, dv=NOTA_DV, numero="0", vazio="Vazio = não avaliado (nunca zero).", validacao="Inteiro de 1 a 3."),
        Coluna("criticidade.nota_qualidade", "N2 Qualidade (1–3)", "entrada", "inteiro", _r("gestao.criticidade.notas[ativo.id][1]"), RAMO,
               "condicional", formato="inteiro 1–3", largura=10, dv=NOTA_DV, numero="0", vazio="Vazio = não avaliado (nunca zero).", validacao="Inteiro de 1 a 3."),
        Coluna("criticidade.nota_producao", "N3 Produção (1–3)", "entrada", "inteiro", _r("gestao.criticidade.notas[ativo.id][2]"), RAMO,
               "condicional", formato="inteiro 1–3", largura=10, dv=NOTA_DV, numero="0", vazio="Vazio = não avaliado (nunca zero).", validacao="Inteiro de 1 a 3."),
        Coluna("criticidade.nota_frequencia_falha", "N4 Frequência de falha (1–3)", "entrada", "inteiro", _r("gestao.criticidade.notas[ativo.id][3]"), RAMO,
               "condicional", formato="inteiro 1–3", largura=11, dv=NOTA_DV, numero="0", vazio="Vazio = não avaliado (nunca zero).", validacao="Inteiro de 1 a 3."),
        Coluna("criticidade.nota_custo_reparo", "N5 Custo/tempo de reparo (1–3)", "entrada", "inteiro", _r("gestao.criticidade.notas[ativo.id][4]"), RAMO,
               "condicional", formato="inteiro 1–3", largura=11, dv=NOTA_DV, numero="0", vazio="Vazio = não avaliado (nunca zero).", validacao="Inteiro de 1 a 3."),
        Coluna("criticidade.notas_validas", "Notas válidas (de 5)", "calculo", "inteiro", "Fórmula", CALCULO, largura=9,
               formula="=IF(COUNTA(A{r}:D{r})+COUNTA(F{r}:I{r})+COUNTA(K{r}:O{r})=0,\"\"," + "+".join(nota_valida(c) for c in "KLMNO") + ")"),
        Coluna("criticidade.pontuacao", "Pontuação (5–15)", "calculo", "inteiro", "Fórmula (equivale a criticidadeAtivo().pontuacao)", CALCULO, largura=10,
               formula='=IF(P{r}=5,SUM(K{r}:O{r}),"")', vazio="Vazio enquanto houver nota ausente ou inválida."),
        Coluna("criticidade.classe", "Classe", "calculo", "texto", "Fórmula (equivale a criticidadeAtivo().classe)", CALCULO, largura=10,
               formula='=IF(P{r}="","",IF(P{r}<5,"Pendente",IF(NOT(cad_limites_ok),"Pendente",IF(K{r}=3,"A",IF(Q{r}>=cad_limite_a,"A",IF(Q{r}>=cad_limite_b,"B","C"))))))',
               validacao="A, B, C ou Pendente."),
        Coluna("criticidade.orientacao", "Orientação", "calculo", "texto", "Fórmula", CALCULO, largura=30,
               formula='=IF(P{r}="","",IF(A{r}="","Pendente: falta o ID do ativo",IF(COUNTIF(at_id,A{r})>1,"ERRO: ID do ativo duplicado",'
                       'IF(COUNTA(K{r}:O{r})>P{r},"Pendente: nota inválida (use inteiro de 1 a 3)",IF(P{r}<5,"Pendente: falta(m) "&(5-P{r})&" nota(s)",'
                       'IF(NOT(cad_limites_ok),"Pendente: corrija os limites A/B em Critérios",IF(K{r}=3,"A por Segurança = 3","Classe pela soma e limites")))))))'),
    ],
)

# ---------------------------------------------------------------- PCMD-03
PLANO = Aba(
    nome="Plano Mestre", codigo="PCMD-03", titulo="Plano mestre",
    instrucao="Uma linha por tarefa. REFERÊNCIA fica protegida (sem senha). Tarefa de segurança: só manter ou aumentar a frequência.",
    capacidade=2000, congelar_col=4, protegida=True, paginas_largura=2, colunas_repetidas="A:D",
    colunas=[
        Coluna("tarefa.ativo_id", "ID do ativo", "id", "texto", "plano[].equipamentoId (gerarPlano, src/logica/plano.js)", MAIN, "obrigatório",
               largura=13, dv=ID_DV),
        Coluna("tarefa.id", "ID da tarefa", "id", "texto", "plano[].tarefaId (biblioteca.tipos[].tarefas[].id)", MAIN, "obrigatório", largura=10, dv=ID_DV),
        Coluna("tarefa.chave", "Chave da tarefa (ativo|tarefa)", "calculo", "texto", "Fórmula: equipamentoId|tarefaId (chaveAjuste)", CALCULO, largura=22,
               formula='=IF(OR(A{r}="",B{r}=""),"",A{r}&"|"&B{r})', nome="pl_chave"),
        Coluna("tarefa.tag", "TAG", "referencia", "texto", "plano[].tag (TAG vigente do ativo)", MAIN, "obrigatório", largura=13, nome="pl_tag",
               obs="Copiada do cadastro do ativo; este arquivo não consulta o PCMD-02."),
        Coluna("tarefa.atividade", "Atividade", "referencia", "texto", "plano[].descricao", MAIN, "obrigatório", largura=40, nome="pl_atividade"),
        Coluna("tarefa.origem", "Origem", "referencia", "texto", "plano[].origem", MAIN, "obrigatório", largura=22,
               obs="Tarefa genérica usa exatamente: base genérica a validar com manual do fabricante."),
        Coluna("tarefa.versao", "Versão", "referencia", "texto", "plano[].versao", MAIN, "obrigatório", largura=8),
        Coluna("tarefa.frequencia_referencia", "Frequência de referência", "referencia", "lista", "plano[].periodicidadeOriginal", MAIN, "obrigatório", largura=12,
               dv={"type": "list", "formula1": "=lst_frequencias", "error": "Use uma frequência da aba Listas.", "prompt": "Frequência da biblioteca (referência)."},
               validacao="Lista lst_frequencias."),
        Coluna("tarefa.seguranca", "Segurança (referência)", "referencia", "sim_nao", "plano[].seguranca (true → Sim)", MAIN, "obrigatório", largura=10,
               dv=SIMNAO_DV, nome="pl_seguranca", validacao="Sim ou Não."),
        Coluna("tarefa.frequencia_vigente", "Frequência vigente", "entrada", "lista", "plano[].periodicidade (após ajustes válidos)", MAIN, "obrigatório", largura=12,
               dv={"type": "list", "formula1": "=lst_frequencias", "error": "Use uma frequência da aba Listas.", "prompt": "Tarefa de segurança: igual ou mais frequente que a referência."},
               validacao="Lista lst_frequencias; segurança não pode ser menos frequente."),
        Coluna("tarefa.vezes_ano", "Execuções no ciclo de 52 semanas", "calculo", "inteiro", "Fórmula (vezesPorAno)", CALCULO, largura=11,
               formula='=IF(J{r}="","",IFERROR(INDEX(lst_frequencias_vezes,MATCH(J{r},lst_frequencias,0)),"Frequência não aceita"))', nome="pl_vezes"),
        Coluna("tarefa.especialidade", "Especialidade", "referencia", "lista", "plano[].especialidade", MAIN, "obrigatório", largura=13, nome="pl_especialidade",
               dv={"type": "list", "formula1": "=lst_especialidades", "error": "Use uma especialidade da aba Listas.", "prompt": "Especialidade da tarefa."}),
        Coluna("tarefa.duracao_horas", "Duração estimada por execução (h)", "referencia", "numero_horas", "plano[].duracaoHoras (biblioteca duracao_horas)", MAIN,
               "obrigatório", formato="número decimal de horas", largura=11, dv=HORAS_DV, numero="0.00", nome="pl_duracao"),
        Coluna("tarefa.horas_ciclo", "Horas estimadas no ciclo (h)", "calculo", "numero_horas", "Fórmula: duração × execuções no ciclo", CALCULO,
               formato="número decimal de horas", largura=11, numero="0.00",
               formula='=IF(AND(ISNUMBER(K{r}),ISNUMBER(M{r})),K{r}*M{r},"")', obs="Estimativa; não são horas trabalhadas."),
        Coluna("tarefa.ativa", "Ativa no plano", "entrada", "sim_nao", "plano[].ativa (true → Sim)", MAIN, "obrigatório", largura=9, dv=SIMNAO_DV, nome="pl_ativa"),
        *responsavel("tarefa", "gestao.responsaveis['equipamentoId|tarefaId']"),
        Coluna("tarefa.conferencia", "Conferência de segurança e frequência", "calculo", "texto", "Fórmula (equivale a podeAlterar)", CALCULO, largura=34,
               formula='=IF(C{r}="","",IF(COUNTIF(pl_chave,C{r})>1,"ERRO: chave de tarefa duplicada",IF(I{r}="Sim",'
                       'IF(O{r}="Não","ERRO: tarefa de segurança retirada do plano",IF(NOT(ISNUMBER(K{r})),"ERRO: frequência vigente inválida",'
                       'IF(ISERROR(MATCH(H{r},lst_frequencias,0)),"ERRO: frequência de referência ausente",'
                       'IF(K{r}<INDEX(lst_frequencias_vezes,MATCH(H{r},lst_frequencias,0)),"ERRO: intervalo ampliado em tarefa de segurança (referência "&H{r}&")","OK: segurança mantida")))),'
                       'IF(NOT(ISNUMBER(K{r})),"Verificar: frequência vigente","OK"))))'),
        Coluna("tarefa.observacao", "Observação técnica", "referencia", "texto", "plano[].observacao", MAIN, largura=28, privacidade=PRIV_LIVRE),
    ],
)

# ---------------------------------------------------------------- PCMD-04 Ocorrências
OCORRENCIAS = Aba(
    nome="Ocorrências", codigo="PCMD-04", titulo="Ocorrências previstas",
    instrucao="Uma linha por ativo + tarefa + data prevista, com a fonte da data. Diária = uma linha por dia útil.",
    capacidade=5000, congelar_col=3, paginas_largura=2, colunas_repetidas="A:C",
    colunas=[
        Coluna("ocorrencia.ativo_id", "ID do ativo", "id", "texto", _r("ocorrenciasPlanejadas(dados)[].equipamentoId"), RAMO, "obrigatório", largura=13, dv=ID_DV),
        Coluna("ocorrencia.tarefa_id", "ID da tarefa", "id", "texto", _r("ocorrenciasPlanejadas(dados)[].tarefaId"), RAMO, "obrigatório", largura=10, dv=ID_DV),
        Coluna("ocorrencia.data_prevista", "Data prevista (dd/mm/aaaa)", "entrada", "data", _r("ocorrenciasPlanejadas(dados)[].dataPrevista (AAAA-MM-DD → data Excel)"), RAMO,
               "obrigatório", formato="data dd/mm/aaaa", largura=12, dv=DATA_DV, numero="dd/mm/yyyy"),
        Coluna("ocorrencia.fonte", "Fonte da data prevista", "entrada", "texto", "Texto do adaptador ou de quem digitou", MANUAL, "obrigatório", largura=26,
               obs="Ex.: cronograma do PCM Direto (52 semanas a partir de dd/mm/aaaa)."),
        Coluna("ocorrencia.chave_tarefa", "Chave da tarefa", "calculo", "texto", "Fórmula", CALCULO, largura=20, formula='=IF(OR(A{r}="",B{r}=""),"",A{r}&"|"&B{r})'),
        Coluna("ocorrencia.chave", "Chave da ocorrência (ativo|tarefa|AAAA-MM-DD)", "calculo", "texto", "Fórmula (equivale a ocorrencia.chave do app)", CALCULO,
               largura=30, formula=chave_data("E", "C"), nome="oc_chave"),
        Coluna("ocorrencia.linha_plano", "Linha no plano (técnico)", "calculo", "inteiro", "Fórmula: posição da chave no Plano Mestre", CALCULO, largura=8,
               formula='=IF(E{r}="","",IFERROR(MATCH(E{r},pl_chave,0),0))', obs="0 = tarefa não encontrada no plano."),
        Coluna("ocorrencia.tag", "TAG", "calculo", "texto", "Fórmula a partir do Plano Mestre", CALCULO, largura=13,
               formula='=IF(G{r}="","",IF(G{r}=0,"Tarefa fora do plano",INDEX(pl_tag,G{r})))'),
        Coluna("ocorrencia.atividade", "Atividade", "calculo", "texto", "Fórmula a partir do Plano Mestre", CALCULO, largura=34,
               formula='=IF(N(G{r})=0,"",INDEX(pl_atividade,G{r}))'),
        Coluna("ocorrencia.especialidade", "Especialidade", "calculo", "texto", "Fórmula a partir do Plano Mestre", CALCULO, largura=12,
               formula='=IF(N(G{r})=0,"",INDEX(pl_especialidade,G{r}))'),
        Coluna("ocorrencia.horas_estimadas", "Horas estimadas (h)", "calculo", "numero_horas", "Fórmula: duração por execução do Plano Mestre", CALCULO,
               formato="número decimal de horas", largura=9, numero="0.00", nome="oc_horas",
               formula='=IF(N(G{r})=0,"",INDEX(pl_duracao,G{r}))', obs="Diária: duração de um dia; a soma da semana não é multiplicada outra vez."),
        Coluna("ocorrencia.ano", "Ano previsto", "calculo", "inteiro", "Fórmula", CALCULO, largura=7, numero="0", nome="oc_ano",
               formula='=IF(ISNUMBER(C{r}),YEAR(C{r}),"")'),
        Coluna("ocorrencia.mes", "Mês previsto", "calculo", "inteiro", "Fórmula", CALCULO, largura=7, numero="0", nome="oc_mes",
               formula='=IF(ISNUMBER(C{r}),MONTH(C{r}),"")'),
        Coluna("ocorrencia.posicao", "Posição em relação ao ano consultado", "calculo", "texto", "Fórmula", CALCULO, largura=13, nome="oc_posicao",
               formula='=IF(L{r}="","",IF(NOT(ISNUMBER(crono_ano)),"Informe o ano",IF(L{r}<crono_ano,"Antes do ano",IF(L{r}>crono_ano,"Depois do ano","No ano"))))'),
        Coluna("ocorrencia.primeira", "Primeira linha da chave (1/0)", "calculo", "inteiro", "Fórmula", CALCULO, largura=8, numero="0",
               formula='=IF(F{r}="","",IF(COUNTIF(F$7:F{r},F{r})=1,1,0))'),
        Coluna("ocorrencia.conta", "Prevista válida (1/0)", "calculo", "inteiro", "Fórmula", CALCULO, largura=8, numero="0", nome="oc_conta",
               formula='=IF(A{r}&B{r}&C{r}="","",IF(AND(O{r}=1,N(G{r})>0),IF(INDEX(pl_ativa,MAX(1,N(G{r})))="Sim",1,0),0))'),
        Coluna("ocorrencia.execucoes_ativas", "Execuções ativas vinculadas", "calculo", "inteiro", "Fórmula: CONT.SES em Execuções", CALCULO, largura=9, numero="0",
               formula='=IF(F{r}="","",COUNTIFS(ex_chave_oc,F{r},ex_cancelada,"<>Sim"))'),
        Coluna("ocorrencia.concluida", "Concluída (1/0)", "calculo", "inteiro", "Fórmula: 1 se prevista válida com execução ativa", CALCULO, largura=8,
               numero="0", nome="oc_concluida", formula='=IF(P{r}="","",IF(AND(P{r}=1,N(Q{r})>0),1,0))'),
        Coluna("ocorrencia.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=28, nome="oc_conferencia",
               formula='=IF(P{r}="","",IF(F{r}="","ERRO: data prevista ausente ou inválida",IF(O{r}=0,"Duplicada: contada uma vez",'
                       'IF(N(G{r})=0,"ERRO: tarefa fora do Plano Mestre",IF(P{r}=0,"Tarefa retirada do plano: não conta","OK")))))'),
    ],
)

# ---------------------------------------------------------------- Execuções
EXECUCOES = Aba(
    nome="Execuções", codigo="PCMD-04", titulo="Execuções realizadas",
    instrucao="Um registro por realização. A data prevista vincula à ocorrência. Cancelar = Sim (o registro continua no histórico).",
    capacidade=3000, congelar_col=1, paginas_largura=2, colunas_repetidas="A:C",
    colunas=[
        Coluna("execucao.id", "ID do registro", "id", "texto", _r("gestao.historico[].id"), RAMO, "obrigatório", largura=12, dv=ID_DV, nome="ex_id"),
        Coluna("execucao.ativo_id", "ID do ativo", "id", "texto", _r("gestao.historico[].equipamentoId"), RAMO, "obrigatório", largura=13, dv=ID_DV),
        Coluna("execucao.tarefa_id", "ID da tarefa", "id", "texto", _r("gestao.historico[].tarefaId"), RAMO, "obrigatório", largura=10, dv=ID_DV),
        Coluna("execucao.chave_tarefa", "Chave da tarefa", "calculo", "texto", "Fórmula", CALCULO, largura=20, formula='=IF(OR(B{r}="",C{r}=""),"",B{r}&"|"&C{r})'),
        Coluna("execucao.tag", "TAG preservada", "entrada", "texto", _r("gestao.historico[].tag"), RAMO, "obrigatório", largura=13,
               obs="Texto gravado no momento do registro; não muda se o ativo for renomeado."),
        Coluna("execucao.descricao", "Descrição preservada", "entrada", "texto", _r("gestao.historico[].descricao"), RAMO, largura=30),
        Coluna("execucao.data_prevista", "Data prevista (opcional, dd/mm/aaaa)", "entrada", "data", _r("gestao.historico[].dataPrevista ('' → vazio)"), RAMO,
               formato="data dd/mm/aaaa", largura=12, dv=DATA_DV, numero="dd/mm/yyyy", vazio="Vazio = execução sem vínculo (não entra no percentual)."),
        Coluna("execucao.data", "Data realizada (dd/mm/aaaa)", "entrada", "data", _r("gestao.historico[].data"), RAMO, "obrigatório",
               formato="data dd/mm/aaaa", largura=12, dv=DATA_DV, numero="dd/mm/yyyy"),
        Coluna("execucao.chave_ocorrencia", "Chave da ocorrência vinculada", "calculo", "texto", "Fórmula", CALCULO, largura=30,
               formula=chave_data("D", "G"), nome="ex_chave_oc"),
        Coluna("execucao.observacao", "Observação", "entrada", "texto", _r("gestao.historico[].observacao"), RAMO, largura=30, privacidade=PRIV_LIVRE),
        *responsavel("execucao", "gestao.historico[].responsavelId"),
        Coluna("execucao.origem", "Origem do registro", "entrada", "lista", _r("gestao.historico[].origem (app | legado)"), RAMO, "obrigatório", largura=9,
               dv={"type": "list", "formula1": "=lst_origem_execucao", "error": "Use app ou legado.", "prompt": "app = registrado no app; legado = marcação antiga migrada."}),
        Coluna("execucao.cancelada", "Cancelada", "entrada", "sim_nao", _r("gestao.historico[].cancelada (true → Sim)"), RAMO, "obrigatório", largura=9,
               dv=SIMNAO_DV, nome="ex_cancelada", vazio="Vazio é tratado como Não (ativa)."),
        Coluna("execucao.vinculo", "Vínculo", "calculo", "texto", "Fórmula", CALCULO, largura=16, nome="ex_vinculo",
               formula='=IF(A{r}&B{r}&C{r}="","",IF(I{r}="","Sem vínculo",IF(COUNTIF(oc_chave,I{r})>0,"Vinculada","Previsão não encontrada")))'),
        Coluna("execucao.ano", "Ano realizado", "calculo", "inteiro", "Fórmula", CALCULO, largura=7, numero="0", nome="ex_ano",
               formula='=IF(ISNUMBER(H{r}),YEAR(H{r}),"")'),
        Coluna("execucao.situacao_plano", "Tarefa no plano atual?", "calculo", "texto", "Fórmula: chave da tarefa no Plano Mestre", CALCULO, largura=18,
               formula='=IF(D{r}="","",IF(COUNTIF(pl_chave,D{r})>0,"No plano atual","Fora do plano: histórico preservado"))',
               obs="Ativo ou tarefa removidos não apagam o histórico."),
        Coluna("execucao.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=26,
               formula='=IF(A{r}&B{r}&C{r}="","",IF(A{r}="","ERRO: falta ID do registro",IF(COUNTIF(ex_id,A{r})>1,"ERRO: ID do registro duplicado",'
                       'IF(NOT(ISNUMBER(H{r})),"ERRO: data realizada ausente ou inválida",IF(AND(ISNUMBER(pcmd_emissao),N(H{r})>N(pcmd_emissao)),"Verificar: realizada após a emissão","OK")))))'),
        Coluna("execucao.duracao_real_horas", "Duração real (h) — FUTURO, não integrado", "futuro", "numero_horas",
               "Não existe no histórico atual do app", FUTURO, formato="número decimal de horas", largura=12, dv=HORAS_DV, numero="0.00",
               vazio="Manter vazio. Não é somado em nenhuma fórmula.", obs="Horas estimadas do plano não são horas trabalhadas."),
    ],
)

# ---------------------------------------------------------------- PCMD-05
FALHAS = Aba(
    nome="Ficha de Falha", codigo="PCMD-05", titulo="Ficha de falha",
    instrucao="Um registro por falha. Horas de parada vazias = não informado (não é zero). Sem cálculo de MTBF, MTTR ou disponibilidade.",
    capacidade=1000, congelar_col=1, paginas_largura=2, colunas_repetidas="A:B",
    colunas=[
        Coluna("falha.id", "ID do registro", "id", "texto", _r("gestao.falhas[].id"), RAMO, "obrigatório", largura=12, dv=ID_DV, nome="fa_id"),
        Coluna("falha.ativo_id", "ID do ativo", "id", "texto", _r("gestao.falhas[].equipamentoId"), RAMO, "obrigatório", largura=13, dv=ID_DV),
        Coluna("falha.data", "Data da falha (dd/mm/aaaa)", "entrada", "data", _r("gestao.falhas[].data"), RAMO, "obrigatório",
               formato="data dd/mm/aaaa", largura=12, dv=DATA_DV, numero="dd/mm/yyyy"),
        Coluna("falha.tag", "TAG preservada", "entrada", "texto", _r("gestao.falhas[].tag"), RAMO, "obrigatório", largura=13),
        Coluna("falha.sintoma", "Sintoma", "entrada", "texto", _r("gestao.falhas[].sintoma"), RAMO, "obrigatório", largura=30, privacidade=PRIV_LIVRE),
        Coluna("falha.causa", "Causa", "entrada", "texto", _r("gestao.falhas[].causa"), RAMO, largura=26, privacidade=PRIV_LIVRE),
        Coluna("falha.acao", "Ação", "entrada", "texto", _r("gestao.falhas[].acao"), RAMO, largura=26, privacidade=PRIV_LIVRE),
        Coluna("falha.horas_parada", "Horas de parada (h, opcional)", "entrada", "numero_horas", _r("gestao.falhas[].horasParada (null → vazio)"), RAMO,
               formato="número decimal de horas", largura=11, dv=HORAS_DV, numero="0.00", vazio="Vazio = não informado; nunca converter em zero."),
        Coluna("falha.peca", "Peça", "entrada", "texto", _r("gestao.falhas[].peca"), RAMO, largura=16),
        *responsavel("falha", "gestao.falhas[].responsavelId"),
        Coluna("falha.parada_situacao", "Parada informada?", "calculo", "texto", "Fórmula", CALCULO, largura=14, nome="fa_parada",
               formula='=IF(A{r}&B{r}="","",IF(H{r}="","Não informado",IF(ISNUMBER(H{r}),"Informado","ERRO: horas devem ser número")))'),
        Coluna("falha.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=24,
               formula='=IF(A{r}&B{r}="","",IF(A{r}="","ERRO: falta ID do registro",IF(COUNTIF(fa_id,A{r})>1,"ERRO: ID duplicado",'
                       'IF(NOT(ISNUMBER(C{r})),"ERRO: data ausente ou inválida",IF(E{r}="","ERRO: falta o sintoma","OK")))))'),
    ],
)

# ---------------------------------------------------------------- Revisões
REVISOES = Aba(
    nome="Revisões", codigo="PCMD-01", titulo="Histórico de revisões",
    instrucao="Uma linha por revisão documental: documento, revisão, data, mudança e responsável.",
    capacidade=100, paisagem=False, linhas_impressao_modelo=20,
    colunas=[
        Coluna("revisao.documento", "Documento (código)", "manual", "texto", "Documental", MANUAL, "obrigatório", largura=16),
        Coluna("revisao.numero", "Revisão", "manual", "texto", "Documental", MANUAL, "obrigatório", largura=9),
        Coluna("revisao.data", "Data (dd/mm/aaaa)", "manual", "data", "Documental", MANUAL, "obrigatório", formato="data dd/mm/aaaa", largura=12,
               dv=DATA_DV, numero="dd/mm/yyyy"),
        Coluna("revisao.descricao", "Descrição da mudança", "manual", "texto", "Documental", MANUAL, "obrigatório", largura=40, privacidade=PRIV_LIVRE),
        Coluna("revisao.responsavel", "Responsável (nome)", "manual", "texto", "Documental", MANUAL, "obrigatório", largura=22, privacidade=PRIV_NOME),
    ],
)

# Revisões do próprio arquivo (padrão PCM Direto): PCMD-02, PCMD-03/04 e PCMD-05. No PCMD-01 a revisão vem da Lista Mestra.
REVISOES_ARQ = Aba(
    nome="Revisões", codigo="", titulo="Histórico de revisões",
    instrucao="Uma linha por revisão deste arquivo. A última linha preenchida aparece no cabeçalho de todas as abas.",
    capacidade=30, paisagem=False, linhas_impressao_modelo=15,
    colunas=[
        Coluna("arquivo.revisao", "Revisão", "manual", "texto", "Documental", MANUAL, "obrigatório", largura=10, nome="rv_revisao"),
        Coluna("arquivo.data", "Data", "manual", "data", "Documental", MANUAL, "obrigatório", formato="data dd/mm/aaaa", largura=13,
               dv=DATA_DV, numero="dd/mm/yyyy", nome="rv_data"),
        Coluna("arquivo.descricao", "Descrição da alteração", "manual", "texto", "Documental", MANUAL, "obrigatório", largura=50, privacidade=PRIV_LIVRE),
        Coluna("arquivo.revisado_por", "Revisado por", "manual", "texto", "Documental", MANUAL, largura=18, privacidade=PRIV_NOME),
        Coluna("arquivo.aprovado_por", "Aprovado por", "manual", "texto", "Documental", MANUAL, largura=18, privacidade=PRIV_NOME,
               vazio="Vazio = aprovação não registrada; nunca presumir."),
    ],
)

# ---------------------------------------------------------------- Cadastros em tabela
SETORES = Aba(
    nome="Setores", codigo="PCMD-02", titulo="Setores",
    instrucao="Siglas de 2 a 4 letras ou números usadas na TAG (SETOR-SIGLA-NNN).",
    capacidade=30, paisagem=False, linhas_impressao_modelo=12,
    colunas=[
        Coluna("setor.sigla", "Sigla do setor", "entrada", "texto", _r("gestao.organizacao.setores[]") + "; também estado.equipamentos[].setor (main)", RAMO,
               "obrigatório", largura=24, nome="cad_setor", validacao="2 a 4 letras maiúsculas/números (normalizarSetor)."),
        Coluna("setor.descricao", "Descrição do setor", "manual", "texto", "Não existe no app (o app guarda só a sigla)", MANUAL, largura=30, privacidade=PRIV_ORG),
        Coluna("setor.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=28,
               formula='=IF(A{r}="","",IF(OR(LEN(A{r})<2,LEN(A{r})>4),"ERRO: use 2 a 4 caracteres",IF(COUNTIF(cad_setor,A{r})>1,"ERRO: sigla repetida","OK")))'),
    ],
)
PESSOAS = Aba(
    nome="Pessoas", codigo="PCMD-01", titulo="Pessoas e funções",
    instrucao="Dado pessoal mínimo, só neste arquivo local. Pessoa inativa continua nos registros anteriores.",
    capacidade=60, paisagem=False, linhas_impressao_modelo=15,
    colunas=[
        Coluna("pessoa.id", "ID da pessoa", "id", "texto", _r("gestao.pessoas[].id"), RAMO, "obrigatório", largura=12, dv=ID_DV, nome="cad_pessoa_id"),
        Coluna("pessoa.nome", "Nome", "entrada", "texto", _r("gestao.pessoas[].nome"), RAMO, "obrigatório", largura=22, nome="cad_pessoa_nome", privacidade=PRIV_NOME),
        Coluna("pessoa.funcao", "Função", "entrada", "texto", _r("gestao.pessoas[].funcao"), RAMO, largura=22, privacidade=PRIV_NOME),
        Coluna("pessoa.especialidade", "Especialidade", "entrada", "texto", _r("gestao.pessoas[].especialidade"), RAMO, largura=14),
        Coluna("pessoa.ativo", "Ativa", "entrada", "sim_nao", _r("gestao.pessoas[].ativo (true → Sim)"), RAMO, "obrigatório", largura=8, dv=SIMNAO_DV,
               obs="Pessoa inativa continua nos registros anteriores."),
        Coluna("pessoa.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=18,
               formula='=IF(A{r}&B{r}="","",IF(A{r}="","ERRO: falta ID",IF(COUNTIF(cad_pessoa_id,A{r})>1,"ERRO: ID repetido",IF(B{r}="","ERRO: falta nome","OK"))))'),
    ],
)
REQUISITOS = Aba(
    nome="Requisitos", codigo="PCMD-01", titulo="Requisitos e referências",
    instrucao="Tudo começa Não verificado. Verificado exige versão, data e fonte HTTPS e não certifica conformidade.",
    capacidade=60, linhas_impressao_modelo=12,
    colunas=[
        Coluna("requisito.id", "ID do requisito", "id", "texto", _r("gestao.requisitos[].id"), RAMO, "obrigatório", largura=12, dv=ID_DV),
        Coluna("requisito.referencia", "Referência ou título", "entrada", "texto", _r("gestao.requisitos[].referencia"), RAMO, "obrigatório", largura=34,
               obs="Não citar número de norma sem fonte oficial, versão e data."),
        Coluna("requisito.versao", "Versão", "entrada", "texto", _r("gestao.requisitos[].versao"), RAMO, largura=10, vazio="Vazio = A definir."),
        Coluna("requisito.data", "Data da referência (dd/mm/aaaa)", "entrada", "data", _r("gestao.requisitos[].data ('' → vazio)"), RAMO,
               formato="data dd/mm/aaaa", largura=12, dv=DATA_DV, numero="dd/mm/yyyy", vazio="Vazio = A definir."),
        Coluna("requisito.fonte", "Fonte oficial (link HTTPS)", "entrada", "texto", _r("gestao.requisitos[].fonte"), RAMO, largura=30,
               dv={"type": "custom", "formula1": 'OR({c}="",LEFT({c},8)="https://")', "error": "Use um link que comece com https://", "prompt": "Link HTTPS da fonte oficial (texto, sem hiperlink automático)."},
               validacao="Vazio ou começa com https://."),
        Coluna("requisito.status", "Status de verificação", "entrada", "lista", _r("gestao.requisitos[].status (nao_verificado | verificado)"), RAMO, "obrigatório",
               largura=14, dv={"type": "list", "formula1": "=lst_status_requisito", "error": "Use Não verificado ou Verificado.", "prompt": "Verificado exige versão, data e fonte HTTPS; não certifica conformidade."}),
        Coluna("requisito.conferencia", "Conferência", "calculo", "texto", "Fórmula", CALCULO, largura=32,
               formula='=IF(A{r}&B{r}="","",IF(F{r}="Verificado",IF(OR(C{r}="",NOT(ISNUMBER(D{r})),LEFT(E{r},8)<>"https://"),'
                       '"ERRO: Verificado exige versão, data e fonte HTTPS","Verificado pelo responsável (não certifica conformidade)"),"Não verificado: verificar na fonte oficial"))'),
    ],
)

ABAS_TABELA = [LISTA_MESTRA, REVISOES, PESSOAS, REQUISITOS, ATIVOS, SETORES, PLANO, OCORRENCIAS, EXECUCOES, FALHAS, REVISOES_ARQ]

# ---------------------------------------------------------------- Apresentação
# Cabeçalhos curtos (o significado completo fica no contrato e no dicionário) e colunas técnicas ocultas.
CABECALHOS = {
    "documento.data": "Data da revisão", "documento.elaborador": "Elaborador", "documento.aprovador": "Aprovador",
    "documento.proxima_revisao": "Próxima revisão",
    "ativo.descricao": "Descrição", "ativo.tipo_id": "Tipo", "ativo.setor": "Setor", "ativo.tag_conferencia": "Conferência TAG",
    "criticidade.nota_seguranca": "N1 Segurança", "criticidade.nota_qualidade": "N2 Qualidade", "criticidade.nota_producao": "N3 Produção",
    "criticidade.nota_frequencia_falha": "N4 Freq. de falha", "criticidade.nota_custo_reparo": "N5 Custo/tempo reparo",
    "criticidade.pontuacao": "Pontuação",
    "tarefa.frequencia_referencia": "Frequência referência", "tarefa.seguranca": "Segurança", "tarefa.vezes_ano": "Vezes/ano",
    "tarefa.duracao_horas": "Duração (h)", "tarefa.horas_ciclo": "Horas/ano", "tarefa.ativa": "Ativa", "tarefa.conferencia": "Conferência",
    "tarefa.observacao": "Observação", "tarefa.responsavel_nome": "Responsável",
    "ocorrencia.data_prevista": "Data prevista", "ocorrencia.fonte": "Fonte da data", "ocorrencia.horas_estimadas": "Horas (h)",
    "ocorrencia.concluida": "Concluída",
    "execucao.tag": "TAG", "execucao.descricao": "Descrição", "execucao.data_prevista": "Data prevista", "execucao.data": "Data realizada",
    "execucao.origem": "Origem", "execucao.situacao_plano": "No plano?", "execucao.responsavel_nome": "Responsável",
    "falha.data": "Data", "falha.tag": "TAG", "falha.horas_parada": "Parada (h)", "falha.responsavel_nome": "Responsável",
    "revisao.documento": "Documento", "revisao.data": "Data", "revisao.responsavel": "Responsável",
    "requisito.referencia": "Referência", "requisito.data": "Data", "requisito.fonte": "Fonte oficial (HTTPS)", "requisito.status": "Status",
    "setor.sigla": "Sigla", "setor.descricao": "Descrição",
}
OCULTAS = {
    "ativo.tipo_nome", "criticidade.notas_validas",
    "tarefa.chave", "tarefa.responsavel_id",
    "ocorrencia.chave_tarefa", "ocorrencia.chave", "ocorrencia.linha_plano", "ocorrencia.ano", "ocorrencia.mes", "ocorrencia.posicao",
    "ocorrencia.primeira", "ocorrencia.conta", "ocorrencia.execucoes_ativas",
    "execucao.chave_tarefa", "execucao.chave_ocorrencia", "execucao.ano", "execucao.duracao_real_horas", "execucao.responsavel_id",
    "falha.responsavel_id", "falha.parada_situacao",
}
for _aba in ABAS_TABELA:
    for _c in _aba.colunas:
        _c.cabecalho = CABECALHOS.get(_c.id, _c.cabecalho)
        _c.oculta = _c.id in OCULTAS
        if _c.id == "ocorrencia.concluida":
            _c.numero = '"Sim";"Sim";"Não"'  # valor 1/0 (usado nas somas), exibido como Sim/Não
            _c.largura = 11
    _visivel = sum(_c.largura for _c in _aba.colunas if not _c.oculta)
    if _aba.paginas_largura == 2 and _visivel <= 200:
        _aba.paginas_largura, _aba.colunas_repetidas = 1, None
# Larguras mais justas: a tabela inteira cabe na largura de uma página (ou de duas, nas abas largas).
LARGURAS = {
    "documento.titulo": 30, "documento.elaborador": 15, "documento.aprovador": 15, "documento.conferencia": 24, "documento.observacao": 20,
    "falha.sintoma": 26, "falha.causa": 22, "falha.acao": 22,
    "ocorrencia.fonte": 22, "tarefa.origem": 26,
}
for _aba in ABAS_TABELA:
    for _c in _aba.colunas:
        _c.largura = LARGURAS.get(_c.id, _c.largura)

# Faixa azul (linha 5): grupos de colunas, como no modelo padrão. Cada grupo começa na coluna indicada.
# Nas abas largas, a segunda página da impressão começa no grupo marcado em QUEBRA.
GRUPOS = {
    "Lista Mestra": [("Documento", "documento.codigo"), ("Revisão", "documento.revisao"), ("Situação", "documento.situacao")],
    "Revisões": [("Histórico de revisões", None)],
    "Pessoas": [("Pessoas", None)],
    "Requisitos": [("Referência", "requisito.id"), ("Verificação", "requisito.status")],
    "Ativos": [("Identificação", "ativo.id"), ("Cadastro do ativo", "ativo.descricao"), ("Criticidade", "criticidade.nota_seguranca")],
    "Setores": [("Setores", None)],
    "Plano Mestre": [("Identificação", "tarefa.ativo_id"), ("Tarefa", "tarefa.atividade"), ("Frequência", "tarefa.frequencia_referencia"), ("Execução", "tarefa.especialidade"),
                     ("Conferência", "tarefa.conferencia")],
    "Ocorrências": [("Ocorrência prevista", "ocorrencia.ativo_id"), ("Tarefa", "ocorrencia.tag"), ("Situação", "ocorrencia.concluida")],
    "Execuções": [("Identificação", "execucao.id"), ("Registro", "execucao.chave_tarefa"), ("Execução", "execucao.data_prevista"), ("Situação", "execucao.responsavel_id")],
    "Ficha de Falha": [("Registro", "falha.id"), ("Análise", "falha.sintoma"), ("Parada e responsável", "falha.horas_parada")],
}
QUEBRA = {"Ativos": "criticidade.nota_seguranca", "Plano Mestre": "tarefa.especialidade", "Execuções": "execucao.responsavel_id"}
PLANO.colunas_repetidas = "A:D"
EXECUCOES.colunas_repetidas = "A:C"

# ---------------------------------------------------------------- Células únicas (formulários)
# Abas Organização (PCMD-01) e Critérios (PCMD-02): cabeçalho na linha 6, campos a partir da linha 7.
CAMPOS_CELULAS = [
    # id, rótulo, aba, célula, papel, tipo, origem, situação, vazio, validação, privacidade, obs
    ("organizacao.nome", "Nome da organização", "Organização", "B7", "entrada", "texto", _r("gestao.organizacao.nome"), RAMO, "Vazio = não informado.", "Até 120 caracteres.", PRIV_ORG, "Intervalo cad_org_nome."),
    ("organizacao.referencial", "Referencial", "Organização", "B8", "entrada", "texto", _r("gestao.organizacao.referencial"), RAMO, "Padrão: GERAL (sem norma).", "Até 120 caracteres; não citar norma sem fonte.", PRIV_NENHUM, "Intervalo cad_referencial."),
    ("organizacao.prefixo", "Prefixo dos documentos", "Organização", "B9", "entrada", "texto", _r("gestao.organizacao.padraoCodigo"), RAMO, "Padrão: PCMD.", "Até 40 caracteres.", PRIV_NENHUM, "Intervalo cad_prefixo."),
    ("organizacao.elaborador_id", "Elaborador padrão (ID)", "Organização", "B10", "entrada", "lista", _r("gestao.organizacao.elaborador"), RAMO, "Vazio = não informado.", "Lista cad_pessoa_id.", PRIV_NENHUM, "Nome em C10 (cálculo, aba Pessoas)."),
    ("organizacao.aprovador_id", "Aprovador padrão (ID)", "Organização", "B11", "entrada", "lista", _r("gestao.organizacao.aprovador"), RAMO, "Vazio = não informado; não presumir aprovação.", "Lista cad_pessoa_id.", PRIV_NENHUM, "Nome em C11 (cálculo, aba Pessoas)."),
    ("metas.disponibilidade", "Meta de disponibilidade (%)", "Organização", "B12", "entrada", "percentual", _r("gestao.metas.disponibilidade (0–100 no app → dividir por 100)"), RAMO, "Vazio = A definir (null no app).", "0% a 100%.", PRIV_ORG, "Intervalo cad_meta_disponibilidade. Disponibilidade não é calculada."),
    ("criticidade.limite_a", "Limite A", "Critérios", "B7", "entrada", "inteiro", _r("gestao.criticidade.limites.a"), RAMO, "Padrão 12.", "Inteiro; 5 ≤ B < A ≤ 15.", PRIV_NENHUM, "Intervalo cad_limite_a."),
    ("criticidade.limite_b", "Limite B", "Critérios", "B8", "entrada", "inteiro", _r("gestao.criticidade.limites.b"), RAMO, "Padrão 9.", "Inteiro; 5 ≤ B < A ≤ 15.", PRIV_NENHUM, "Intervalo cad_limite_b."),
    ("criticidade.limites_ok", "Limites válidos?", "Critérios", "B9", "calculo", "booleano", "Fórmula", CALCULO, "—", "VERDADEIRO/FALSO.", PRIV_NENHUM, "Intervalo cad_limites_ok; texto explicativo em C9."),
    ("criticidade.niveis", "Significado dos níveis 1/2/3 por critério", "Critérios", "B13:D17", "manual", "texto", "Definição do mantenedor; não existe no app", MANUAL, "Vazio = A definir pelo mantenedor.", "Texto livre.", PRIV_NENHUM, "Situação em E13:E17 (cálculo)."),
]

# ---------------------------------------------------------------- Listas
FREQUENCIAS = [  # src/logica/plano.js PERIODICIDADES
    ("Diária", 260, "5 dias úteis × 52 semanas; sem calendário de feriados"),
    ("Semanal", 52, ""), ("Quinzenal", 26, ""), ("Mensal", 12, ""), ("Bimestral", 6, ""),
    ("Trimestral", 4, ""), ("Semestral", 2, ""), ("Anual", 1, ""),
]
SITUACOES_DOCUMENTO = ["Em elaboração", "Em revisão", "Aprovado", "Obsoleto"]
TIPOS_DOCUMENTO = ["Planilha (XLSX)", "Manual (DOCX)", "Outro"]
TIPOS_TAREFA_REFERENCIA = ["Preventiva", "Preditiva", "Lubrificação", "Inspeção", "Autônoma"]

# ---------------------------------------------------------------- Cronograma (painel)
# Parâmetros em C7:C11 (situação da meta em E11); resumo mensal; gráfico; quadros separados.
CRONO = {"ano": "C7", "inicio": "C8", "fonte": "C9", "conf_ano": "C10", "meta": "C11", "card_meta": "E11",
         "cab_mes": 14, "jan": 15, "total": 27, "grafico": 30, "fora_cab": 47, "semv_cab": 52, "conf_cab": 58}

CAMPOS_CELULAS += [
    ("cronograma.ano", "Ano consultado", "Cronograma", CRONO["ano"], "entrada", "inteiro", _r("escolha do usuário (resumoMensal(dados, gestao, ano))"), RAMO, "Vazio = resumo em branco.", "Inteiro de 1900 a 9999.", PRIV_NENHUM, "Intervalo crono_ano."),
    ("cronograma.inicio", "Início do ciclo (semana 1)", "Cronograma", CRONO["inicio"], "entrada", "data", "estado.inicio (AAAA-MM-DD, main)", MAIN, "Vazio = não informado.", "Data válida.", PRIV_NENHUM, "Intervalo crono_inicio. Informativo."),
    ("cronograma.fonte", "Fonte das ocorrências", "Cronograma", CRONO["fonte"], "entrada", "texto", "Texto do adaptador ou de quem preenche", FUTURO, "Vazio = não informado.", "Texto.", PRIV_NENHUM, ""),
    ("metas.aderencia", "Meta de aderência preventiva (%)", "Cronograma", CRONO["meta"], "entrada", "percentual", _r("gestao.metas.aderencia (0–100 no app → dividir por 100)"), RAMO, "Vazio = A definir (null no app).", "0% a 100%.", PRIV_ORG, "Intervalo crono_meta_aderencia."),
]

# ---------------------------------------------------------------- Arquivos XLSX
# Cada arquivo é independente (sem fórmula que dependa de outro arquivo). A aba Config de cada um guarda
# elaborado/aprovado (cfg_elaborado, cfg_aprovado), a revisão atual (cfg_revisao, cfg_data_revisao) e a emissão (pcmd_origem, pcmd_emissao).
@dataclass
class Arquivo:
    chave: str
    nome: str            # nome do arquivo sem extensão e sem "-Exemplo"
    codigo: str
    titulo: str
    resumo: str
    abas: list           # (nome da aba, para que serve)
    passos: list
    tabelas: list        # objetos Aba deste arquivo
    listas: list = field(default_factory=list)  # chaves de listas deste arquivo


ARQUIVOS = [
    Arquivo("01", "PCMD-01-Controle-Documental", "PCMD-01", "Controle documental",
            "Lista mestra, histórico de revisões, organização, pessoas e requisitos.",
            [("Lista Mestra", "Um documento por linha: revisão, datas, elaborador, aprovador e situação."),
             ("Revisões", "Uma linha por revisão de cada documento."),
             ("Organização", "Nome, referencial, prefixo, elaborador/aprovador padrão e meta de disponibilidade."),
             ("Pessoas", "Pessoas e funções (dado pessoal mínimo, local)."),
             ("Requisitos", "Tudo começa Não verificado; Verificado exige versão, data e fonte HTTPS."),
             ("Config", "Elaborado, aprovado, origem e data de emissão; conferências do arquivo."),
             ("Listas", "Valores aceitos nas listas suspensas.")],
            ["Preencha a aba Organização e cadastre as Pessoas.",
             "Registre as referências em Requisitos (começam Não verificado).",
             "Mantenha a Lista Mestra e as Revisões a cada mudança. A revisão do PCMD-01 na Lista Mestra aparece no cabeçalho."],
            [LISTA_MESTRA, REVISOES, PESSOAS, REQUISITOS],
            ["tipo_documento", "situacao_documento", "sim_nao", "status_requisito"]),
    Arquivo("02", "PCMD-02-Ativos-Criticidade", "PCMD-02", "Ativos e criticidade",
            "Inventário de ativos com TAG e classificação de criticidade A, B, C ou Pendente.",
            [("Ativos", "Um ativo por linha. Notas inteiras de 1 a 3; nota vazia deixa a classe Pendente."),
             ("Critérios", "Limites A/B e significado dos níveis 1, 2 e 3 de cada critério."),
             ("Setores", "Siglas de setor usadas na TAG."),
             ("Revisões", "Uma linha por revisão deste arquivo."),
             ("Config", "Elaborado, aprovado, origem e data de emissão; conferências do arquivo."),
             ("Listas", "Tipos de equipamento da biblioteca.")],
            ["Cadastre os Setores e confira os limites em Critérios.",
             "Lance um ativo por linha em Ativos, com ID e TAG, e dê as cinco notas de 1 a 3.",
             "Registre cada revisão em Revisões: a última aparece no cabeçalho."],
            [ATIVOS, SETORES, REVISOES_ARQ],
            ["tipos"]),
    Arquivo("03", "PCMD-03-04-Plano-Cronograma", "PCMD-03/04", "Plano mestre e cronograma",
            "Plano mestre, ocorrências previstas, execuções e resumo mensal de % realizado.",
            [("Plano Mestre", "Uma linha por tarefa. Referência protegida (sem senha); segurança só mantém ou aumenta a frequência."),
             ("Cronograma", "Informe o ano: resumo mensal, gráfico e conferências."),
             ("Ocorrências", "Uma linha por ativo + tarefa + data prevista. Diária = uma linha por dia útil."),
             ("Execuções", "Cada realização informa a data prevista que atendeu; canceladas ficam no histórico."),
             ("Revisões", "Uma linha por revisão deste arquivo."),
             ("Config", "Elaborado, aprovado, origem e data de emissão; conferências do arquivo."),
             ("Listas", "Frequências, especialidades e valores aceitos.")],
            ["Lance as tarefas no Plano Mestre e as datas previstas em Ocorrências.",
             "Registre cada realização em Execuções, com a data prevista.",
             "Informe o ano no Cronograma. Registre cada revisão em Revisões."],
            [PLANO, OCORRENCIAS, EXECUCOES, REVISOES_ARQ],
            ["frequencias", "especialidades", "sim_nao", "origem_execucao", "tipos_tarefa"]),
    Arquivo("05", "PCMD-05-Ficha-Falha", "PCMD-05", "Ficha de falha",
            "Registro de falhas com sintoma, causa, ação, horas de parada e responsável.",
            [("Ficha de Falha", "Um registro por falha. Horas de parada vazias = não informadas (não viram zero)."),
             ("Revisões", "Uma linha por revisão deste arquivo."),
             ("Config", "Elaborado, aprovado, origem e data de emissão; conferências do arquivo.")],
            ["Registre cada falha com ID, ativo, data e sintoma.",
             "Complete causa, ação, peça e responsável quando souber.",
             "Registre cada revisão em Revisões: a última aparece no cabeçalho."],
            [FALHAS, REVISOES_ARQ]),
]

# ---------------------------------------------------------------- Word
MARCADORES_DOC = [
    # id, descrição, tipo, origem, situação, vazio
    ("organizacao.nome", "Nome da organização", "texto", _r("gestao.organizacao.nome"), RAMO, "Vazio → 'A definir'."),
    ("organizacao.referencial", "Referencial adotado", "texto", _r("gestao.organizacao.referencial"), RAMO, "Padrão 'GERAL (sem norma)'."),
    ("documento.revisao", "Revisão do documento", "texto", "PCMD-01, aba Lista Mestra (manual)", MANUAL, "Vazio → 'A definir'."),
    ("documento.data", "Data da revisão (dd/mm/aaaa)", "data", "PCMD-01, aba Lista Mestra (manual)", MANUAL, "Vazio → 'A definir'."),
    ("documento.elaborador", "Nome do elaborador", "texto", _r("nome de gestao.pessoas[] com id = gestao.organizacao.elaborador"), RAMO, "Vazio → 'A definir'."),
    ("documento.aprovador", "Nome do aprovador", "texto", _r("nome de gestao.pessoas[] com id = gestao.organizacao.aprovador"), RAMO,
     "Vazio → 'A definir (aprovação não registrada)'. Nunca presumir aprovação."),
    ("documento.proxima_revisao", "Próxima revisão (dd/mm/aaaa)", "data", "PCMD-01, aba Lista Mestra (manual)", MANUAL, "Vazio → 'A definir'."),
    ("documento.situacao", "Situação do documento", "texto", "PCMD-01, aba Lista Mestra (manual)", MANUAL, "Vazio → 'Em elaboração'."),
    ("emissao.data", "Data de emissão do arquivo (dd/mm/aaaa)", "data", "Data em que o adaptador gera o arquivo", FUTURO, "Vazio → 'A definir'."),
    ("origem.dados", "Origem dos dados", "texto", "Texto curto do adaptador (ex.: PCM Direto, backup local de dd/mm/aaaa)", FUTURO, "Vazio → 'Não informada'."),
    ("criticidade.limite_a", "Limite A da criticidade", "inteiro", _r("gestao.criticidade.limites.a"), RAMO, "Vazio → 'A definir'."),
    ("criticidade.limite_b", "Limite B da criticidade", "inteiro", _r("gestao.criticidade.limites.b"), RAMO, "Vazio → 'A definir'."),
    ("metas.disponibilidade", "Meta de disponibilidade", "percentual", _r("gestao.metas.disponibilidade"), RAMO, "null → 'A definir'."),
    ("metas.aderencia", "Meta de aderência preventiva", "percentual", _r("gestao.metas.aderencia"), RAMO, "null → 'A definir'."),
    ("estrategia.responsavel", "Profissional responsável pela estratégia", "texto", "Manual: não existe no app", MANUAL, "Vazio → 'A definir'."),
    ("estrategia.periodicidade_revisao", "Periodicidade de revisão da estratégia", "texto", "Manual: definição do mantenedor", MANUAL, "Vazio → 'A definir'."),
]
for _c in "abc":
    MARCADORES_DOC += [
        (f"estrategia.classe_{_c}.estrategia", f"Estratégia predominante para a classe {_c.upper()}", "texto", "Manual: definição do profissional responsável", MANUAL, "Vazio → 'A definir'."),
        (f"estrategia.classe_{_c}.prazo", f"Prazo de atendimento para a classe {_c.upper()}", "texto", "Manual: definição do profissional responsável", MANUAL, "Vazio → 'A definir'."),
        (f"estrategia.classe_{_c}.revisao", f"Revisão do plano para a classe {_c.upper()}", "texto", "Manual: definição do profissional responsável", MANUAL, "Vazio → 'A definir'."),
    ]

REGIOES_DOC = {
    "requisitos": {"descricao": "Requisitos e referências", "origem": _r("gestao.requisitos[]"), "situacao": RAMO,
                   "campos": [("requisito.referencia", "Referência"), ("requisito.versao", "Versão"), ("requisito.data", "Data"),
                              ("requisito.fonte", "Fonte (HTTPS)"), ("requisito.status", "Status")]},
    "pessoas": {"descricao": "Pessoas e funções", "origem": _r("gestao.pessoas[] (somente ativo = true)"), "situacao": RAMO,
                "campos": [("pessoa.nome", "Nome"), ("pessoa.funcao", "Função"), ("pessoa.especialidade", "Especialidade"),
                           ("pessoa.responsabilidade", "Responsabilidade neste manual (manual)")]},
    "setores": {"descricao": "Setores", "origem": _r("gestao.organizacao.setores[]"), "situacao": RAMO,
                "campos": [("setor.sigla", "Sigla"), ("setor.descricao", "Descrição (manual)")]},
    "ativos": {"descricao": "Ativos e criticidade", "origem": "estado.equipamentos[] (main) + " + _r("gestao.criticidade"), "situacao": RAMO,
               "campos": [("ativo.tag", "TAG"), ("ativo.descricao", "Descrição"), ("ativo.setor", "Setor"), ("ativo.tipo_nome", "Tipo"),
                          ("criticidade.nota_seguranca", "N1"), ("criticidade.nota_qualidade", "N2"), ("criticidade.nota_producao", "N3"),
                          ("criticidade.nota_frequencia_falha", "N4"), ("criticidade.nota_custo_reparo", "N5"),
                          ("criticidade.pontuacao", "Pontuação"), ("criticidade.classe", "Classe")]},
    "tarefas": {"descricao": "Plano mestre (resumo)", "origem": "plano[] (gerarPlano, main) + " + _r("gestao.responsaveis"), "situacao": RAMO,
                "campos": [("tarefa.tag", "TAG"), ("tarefa.id", "ID tarefa"), ("tarefa.atividade", "Atividade"), ("tarefa.frequencia_vigente", "Frequência"),
                           ("tarefa.especialidade", "Especialidade"), ("tarefa.duracao_horas", "Duração (h)"), ("tarefa.seguranca", "Segurança"),
                           ("tarefa.origem_versao", "Origem / versão"), ("tarefa.responsavel_nome", "Responsável")]},
    "revisoes": {"descricao": "Histórico de revisão do documento", "origem": "PCMD-01, aba Revisões (manual)", "situacao": MANUAL,
                 "campos": [("revisao.numero", "Revisão"), ("revisao.data", "Data"), ("revisao.descricao", "Descrição da mudança"),
                            ("revisao.responsavel", "Responsável")]},
}
