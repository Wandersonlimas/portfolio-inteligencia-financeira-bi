"""Empacota dados, CSS e JS sem dependências externas em index.html."""
import json
from pathlib import Path
from pipeline import ROOT

def build(model):
    root=ROOT; web=root/'src'/'web'
    html=(web/'dashboard.html').read_text(encoding='utf-8')
    css=(web/'dashboard.css').read_text(encoding='utf-8').replace("@import url('');",'')
    js=(web/'dashboard.js').read_text(encoding='utf-8')
    data=json.dumps(model,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    html=html.replace('__CSS__',css).replace('__JS__',js).replace('__DATA__',data)
    (root/'index.html').write_text(html,encoding='utf-8')
    (root/'entregaveis'/'dashboard_offline.html').write_text(html,encoding='utf-8')
    print('index.html pronto:',(root/'index.html').stat().st_size,'bytes')
if __name__=='__main__':
    from gerar_dados import generate
    from pipeline import run
    generate();build(run())
