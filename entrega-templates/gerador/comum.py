"""Constantes compartilhadas pelos geradores dos modelos PCM Direto.

Cores conferidas com src/marca.js; aviso conferido com src/logica/pacote.js (AVISO).
"""
from pathlib import Path

RAIZ_ENTREGA = Path(__file__).resolve().parent.parent
RAIZ_REPO = RAIZ_ENTREGA.parent
SAIDA = RAIZ_ENTREGA  # os arquivos entregues ficam na raiz de entrega-templates/
BUILD = RAIZ_ENTREGA / "build"

VERSAO_MODELO = "1.0.0"
DATA_MODELO = "2026-10-23"

AVISO = (
    "O material apoia a organização do PCM e não substitui a avaliação de profissional habilitado "
    "nem o texto oficial das normas. As periodicidades são base genérica e devem ser confirmadas "
    "com o manual do fabricante."
)

AUTOR = "Thiago Oliveira Lima"
CONTATO = "pcmdireto@gmail.com"
LICENCA = "MIT"

# src/marca.js
AZUL = "0B3D63"
DESTAQUE = "B85C00"
AVISO_FUNDO = "FFF4C2"
AVISO_TEXTO = "5C4600"
SEGURANCA = "7A0019"
# Cores próprias do logo (public/icones/logo.svg); usadas apenas no próprio logo.
LOGO_AZUL = "13304A"
LOGO_LARANJA = "D97030"

CINZA_CALCULO = "EDEDED"
AZUL_CLARO = "DCE6EF"  # clarear(AZUL, 0.85) arredondado
BRANCO = "FFFFFF"

FONTE = "Arial"

LOGO_PNG = RAIZ_REPO / "public" / "icones" / "icone-512.png"
LOGO_SVG = RAIZ_REPO / "public" / "icones" / "logo.svg"

RAMO_GESTAO = "interface/cadastros-operacao-sem-templates (commit 81ec337), ainda não integrado na main"


def clarear(hex_cor: str, fracao: float = 0.85) -> str:
    """Mesma regra de src/marca.js."""
    partes = [int(hex_cor[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(v + (255 - v) * fracao):02X}" for v in partes)


def dividir_aviso() -> tuple[str, str]:
    """Divide o aviso em duas linhas na palavra mais próxima do meio, sem alterar o texto."""
    palavras = AVISO.split(" ")
    melhor = None
    for i in range(1, len(palavras)):
        a, b = " ".join(palavras[:i]), " ".join(palavras[i:])
        dif = abs(len(a) - len(b))
        if melhor is None or dif < melhor[0]:
            melhor = (dif, a, b)
    return melhor[1], melhor[2]
