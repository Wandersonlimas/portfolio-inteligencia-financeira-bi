"""Recompila o estudo completo sem fontes externas."""
from gerar_dados import generate
from pipeline import run
from gerar_dashboard import build as build_dashboard
from gerar_relatorio import build as build_pdf

if __name__=='__main__':
    generate()
    model=run()
    build_dashboard(model)
    build_pdf(model)
    print('Case 03 recompilado: index.html + relatório executivo + dados auditáveis')
