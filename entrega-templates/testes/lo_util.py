"""Abre arquivos no LibreOffice (headless, via UNO), recalcula e exporta.

Uso em testes: recalcular(entrada.xlsx, saida.xlsx) e pdf(entrada, saida.pdf).
O recálculo é feito explicitamente com calculateAll(); não usamos valores em cache do gerador.
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue

_PROC = None
_DESKTOP = None


def _prop(nome, valor):
    p = PropertyValue()
    p.Name, p.Value = nome, valor
    return p


def iniciar():
    global _PROC, _DESKTOP
    if _DESKTOP is not None:
        return _DESKTOP
    perfil = Path(tempfile.mkdtemp(prefix="lo-perfil-"))
    porta = 2002 + (os.getpid() % 1000)
    _PROC = subprocess.Popen(["soffice", "--headless", "--invisible", "--nologo", "--norestore", "--nodefault",
                              f"-env:UserInstallation=file://{perfil}",
                              f"--accept=socket,host=127.0.0.1,port={porta};urp;StarOffice.ComponentContext"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    local = uno.getComponentContext()
    resolvedor = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(120):
        try:
            ctx = resolvedor.resolve(f"uno:socket,host=127.0.0.1,port={porta};urp;StarOffice.ComponentContext")
            _DESKTOP = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
            return _DESKTOP
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("LibreOffice não respondeu")


def encerrar():
    global _PROC, _DESKTOP
    try:
        if _DESKTOP is not None:
            _DESKTOP.terminate()
    except Exception:
        pass
    if _PROC:
        try:
            _PROC.wait(timeout=20)
        except Exception:
            _PROC.kill()
    _PROC = _DESKTOP = None


def abrir(caminho):
    desk = iniciar()
    url = uno.systemPathToFileUrl(str(Path(caminho).resolve()))
    doc = desk.loadComponentFromURL(url, "_blank", 0, (_prop("Hidden", True), _prop("RepairPackage", False)))
    if doc is None:
        raise RuntimeError(f"LibreOffice não abriu {caminho}")
    return doc


def recalcular(entrada, saida):
    doc = abrir(entrada)
    try:
        doc.calculateAll()
        url = uno.systemPathToFileUrl(str(Path(saida).resolve()))
        doc.storeToURL(url, (_prop("FilterName", "Calc MS Excel 2007 XML"),))
    finally:
        doc.close(True)


def pdf(entrada, saida, recalcular_antes=True):
    doc = abrir(entrada)
    try:
        if recalcular_antes and hasattr(doc, "calculateAll"):
            doc.calculateAll()
        if hasattr(doc, "getDocumentIndexes"):  # Writer: atualiza sumário e campos
            idx = doc.getDocumentIndexes()
            for i in range(idx.getCount()):
                idx.getByIndex(i).update()
            doc.getTextFields().refresh()
        filtro = "calc_pdf_Export" if hasattr(doc, "calculateAll") else "writer_pdf_Export"
        url = uno.systemPathToFileUrl(str(Path(saida).resolve()))
        doc.storeToURL(url, (_prop("FilterName", filtro),))
    finally:
        doc.close(True)


def versao():
    r = subprocess.run(["soffice", "--version"], capture_output=True, text=True)
    return r.stdout.strip()
