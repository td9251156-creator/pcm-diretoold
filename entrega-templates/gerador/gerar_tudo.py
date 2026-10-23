"""Gera todos os arquivos da entrega. Uso (na raiz do repositório):

    python3 entrega-templates/gerador/gerar_tudo.py

Requer Node.js 18+ (lógica do app, sem pacotes npm) e Python 3.10+ com openpyxl e python-docx
(versões em gerador/requirements.txt). Não acessa a internet.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gerar_contrato  # noqa: E402
import gerar_docx  # noqa: E402
import gerar_xlsx  # noqa: E402
from comum import BUILD, RAIZ_ENTREGA, SAIDA  # noqa: E402


def main():
    BUILD.mkdir(exist_ok=True)
    demo = BUILD / "demo.json"
    with open(demo, "w", encoding="utf-8") as f:
        subprocess.run(["node", str(RAIZ_ENTREGA / "gerador" / "dados-demo.mjs")], check=True, stdout=f)
    dados = json.loads(demo.read_text(encoding="utf-8"))

    gerar_xlsx.gerar(SAIDA / "PCM-Direto-Modelos.xlsx")
    gerar_xlsx.gerar(SAIDA / "PCM-Direto-Exemplo.xlsx", dados)
    print("XLSX gerados")

    valores, regioes = gerar_docx.valores_exemplo(dados)
    w1 = gerar_docx.manual_w1()
    w1.salvar(SAIDA / "PCMD-W1-Manual-Gestao-Ativos.docx")
    w2 = gerar_docx.manual_w2()
    w2.salvar(SAIDA / "PCMD-W2-Manual-Estrategia-Manutencao.docx")
    gerar_docx.manual_w1(valores, regioes).salvar(SAIDA / "PCMD-W1-Manual-Gestao-Ativos-Exemplo.docx")
    gerar_docx.manual_w2(valores, regioes).salvar(SAIDA / "PCMD-W2-Manual-Estrategia-Manutencao-Exemplo.docx")
    print("DOCX gerados")

    gerar_contrato.gerar(SAIDA / "CONTRATO-CAMPOS.json", SAIDA / "DICIONARIO-DE-DADOS.md", SAIDA / "PCM-Direto-Modelos.xlsx",
                         [("PCMD-W1-Manual-Gestao-Ativos.docx", w1), ("PCMD-W2-Manual-Estrategia-Manutencao.docx", w2)])
    print("Contrato e dicionário gerados")


if __name__ == "__main__":
    main()
