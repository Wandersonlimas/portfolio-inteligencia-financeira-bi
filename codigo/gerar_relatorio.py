"""Relatório executivo PDF vetorial (dados provenientes do mesmo pipeline do HTML)."""
from __future__ import annotations
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from pipeline import ROOT, aggregate

PAGE_W,PAGE_H=A4
NAVY='#774734'; INK='#272A30'; TEAL='#B65F38'; MINT='#F7EBE1'; GREY='#6A6D70'; PALE='#FCF7F2'; BORDER='#E9DED6'; RED='#B44F41'; AMBER='#BF673E'
FONT='/usr/share/fonts/truetype/lato'
pdfmetrics.registerFont(TTFont('Lato',FONT+'/Lato-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Lato-Bold',FONT+'/Lato-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Lato-Heavy',FONT+'/Lato-Heavy.ttf'))

def color(c):return HexColor(c)
def money(x):return ('-R$ ' if x<0 else 'R$ ')+f'{abs(x/100):,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def compact(x):return ('-' if x<0 else '')+f'{abs(x/100/1e6):,.2f}'.replace(',','X').replace('.',',').replace('X','.')+' mi'
def pct(n,d):return f'{(100*n/d):.1f}'.replace('.',',')+'%' if d else 'n/d'

def paragraph(c,txt,x,ytop,width,size=10,color_text=GREY,leading=None,bold=False):
    style=ParagraphStyle('t',fontName='Lato-Bold' if bold else 'Lato',fontSize=size,leading=leading or size*1.4,textColor=color(color_text),alignment=TA_LEFT,spaceAfter=0)
    p=Paragraph(txt,style)
    w,h=p.wrap(width,PAGE_H)
    p.drawOn(c,x,ytop-h)
    return ytop-h

def box(c,x,y,w,h,fill='#FFFFFF',border=BORDER,radius=10):
    c.setStrokeColor(color(border));c.setFillColor(color(fill));c.roundRect(x,y,w,h,radius,stroke=1,fill=1)

def label(c,x,y,t,size=9,cl=GREY,font='Lato-Bold'):
    c.setFillColor(color(cl));c.setFont(font,size);c.drawString(x,y,t)

def page_bg(c,page_num,section):
    c.setFillColor(color('#FFFFFF'));c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
    c.setFillColor(color(AMBER));c.rect(0,PAGE_H-5,PAGE_W,5,fill=1,stroke=0)
    label(c,42,PAGE_H-40,'WANDERSON LIMAS   /   PORTFÓLIO TÉCNICO   /   CASE 03',8,TEAL)
    c.setStrokeColor(color(BORDER));c.line(42,44,PAGE_W-42,44)
    label(c,42,28,'ESTUDO DEMONSTRATIVO · BASE 100% SINTÉTICA · 08/11/2026',7.5,GREY,'Lato')
    label(c,PAGE_W-112,28,f'{section}   /   {page_num:02}',7.5,GREY,'Lato')

def heading(c,title,subtitle):
    label(c,42,PAGE_H-92,title,21,INK,'Lato-Heavy')
    paragraph(c,subtitle,42,PAGE_H-109,PAGE_W-84,10,GREY)


def scenario(rows,g,e):
    x=[]
    for r in rows:
        if r['tipo']=='orcamento':continue
        if r['tipo']=='realizado':x.append(r);continue
        q=1+g/100; z=q*(1-e/100)
        gross=round(r['receita_bruta']*q);ded=round(r['deducoes']*q);net=gross-ded
        cogs=round(r['cmv']*z);fee=round(r['taxas']*z);fr=round(r['frete']*z)
        contrib=net-cogs-fee-fr
        x.append({**r,'receita_bruta':gross,'deducoes':ded,'receita_liquida':net,'cmv':cogs,'lucro_bruto':net-cogs,'taxas':fee,'frete':fr,'margem_contribuicao':contrib,'ebitda':contrib-r['despesas_fixas']})
    return aggregate(x)

def build(model):
    path=ROOT/'entregaveis'/'Relatorio_Executivo_Case03_Gestao_Financeira.pdf'
    rows=model['registros'];s=model['resumo'];act=s['realizado_jan_out'];bud=s['orcado_jan_out'];fy=s['fechamento_estimado_jan_dez'];fullbud=s['orcado_jan_dez']
    scenarios=[('Conservador',scenario(rows,-8,0),'-8% na receita futura'),('Base',scenario(rows,0,0),'Premissas originais'),('Otimista',scenario(rows,10,4),'+10% receita, +4% eficiência')]
    c=canvas.Canvas(str(path),pagesize=A4)
    c.setTitle('Case 03 | Relatório Executivo - Inteligência de Negócios e Gestão Financeira')
    c.setAuthor('Wanderson Limas | Portfólio Técnico')
    # CAPA: sistema visual minimalista alinhado ao dashboard aprovado
    c.setFillColor(color('#FCFAF7'));c.rect(0,0,PAGE_W,PAGE_H,stroke=0,fill=1)
    c.setFillColor(color(AMBER));c.rect(0,PAGE_H-6,PAGE_W,6,stroke=0,fill=1)
    box(c,48,PAGE_H-104,53,53,AMBER,AMBER,11)
    label(c,60,PAGE_H-86,'WL',23,'#FFFFFF','Lato-Heavy')
    label(c,118,PAGE_H-66,'INTELIGÊNCIA FINANCEIRA',15,INK,'Lato-Heavy')
    label(c,118,PAGE_H-84,'PLANEJAMENTO   /   BI   /   GESTÃO FINANCEIRA',8.5,GREY)
    c.setStrokeColor(color(BORDER));c.line(48,PAGE_H-128,PAGE_W-48,PAGE_H-128)
    label(c,48,PAGE_H-167,'PORTFÓLIO TÉCNICO     /     CASE 03',10,TEAL,'Lato-Bold')
    label(c,45,PAGE_H-230,'Inteligência de Negócios',25,INK,'Lato-Heavy')
    label(c,45,PAGE_H-266,'e Gestão Financeira',25,INK,'Lato-Heavy')
    paragraph(c,'DRE gerencial  |  Orçamento e desvios  |  Rentabilidade  |  Forecast e cenários',48,PAGE_H-294,PAGE_W-96,11,GREY,15)
    c.setFillColor(color(TEAL));c.roundRect(48,PAGE_H-319,90,4,2,stroke=0,fill=1)
    paragraph(c,'Estudo demonstrativo de integração, qualidade e análise de dados financeiros. O processamento em Python gera indicadores reproduzíveis para explorar decisões gerenciais.',48,PAGE_H-351,PAGE_W-96,10,INK,15)
    kpis=[('RECEITA LÍQUIDA',money(act['receita_liquida'])),('EBITDA GERENCIAL',money(act['ebitda'])),('MARGEM EBITDA',pct(act['ebitda'],act['receita_liquida']))]
    w=(PAGE_W-96-2*12)/3
    for i,(title,value) in enumerate(kpis):
        x=48+i*(w+12)
        box(c,x,277,w,102,'#FFFFFF',BORDER,12)
        box(c,x+12,345,25,23,'#FBF1E9','#FBF1E9',6)
        label(c,x+19,353,['1','2','3'][i],10,AMBER,'Lato-Bold')
        label(c,x+14,319,title,7.4,GREY)
        label(c,x+14,291,value,14,INK,'Lato-Heavy')
    label(c,48,246,'VISÃO DO PROJETO',10,TEAL,'Lato-Heavy')
    paragraph(c,'Pipeline automatizado, DRE, comparação entre orçamento e valores simulados, análises por canal e linha e simulação ajustável de cenários para novembro e dezembro de 2026.',48,229,PAGE_W-96,10,INK,15)
    box(c,48,92,PAGE_W-96,93,'#F7EEE5','#E8D6C6',10)
    label(c,63,160,'BASE 100% SINTÉTICA',9,TEAL,'Lato-Heavy')
    paragraph(c,'Os dados de janeiro a outubro são fictícios, representados como realizado simulado. Novembro e dezembro são projeções ilustrativas. Nenhum valor é resultado de uma empresa real.',63,146,PAGE_W-126,9,INK,14)
    label(c,48,59,'08 NOVEMBRO 2026   ·   PYTHON  /  BUSINESS INTELLIGENCE  /  FINANÇAS',8,GREY,'Lato')
    c.showPage()
    # PAGE 2
    page_bg(c,2,'VISÃO EXECUTIVA');heading(c,'Diagnóstico executivo','Recorte comparável: janeiro a outubro de 2026, exclusivamente com informações simuladas.')
    metrics=[('RECEITA LÍQUIDA',money(act['receita_liquida']),pct(act['receita_liquida']-bud['receita_liquida'],bud['receita_liquida'])+' vs plano'),('EBITDA GERENCIAL',money(act['ebitda']),pct(act['ebitda'],act['receita_liquida'])+' de margem'),('ORÇAMENTO EBITDA',money(bud['ebitda']),'Meta simulada, mesmo período')]
    gap=12;w=(PAGE_W-84-2*gap)/3
    for i,(title,value,note) in enumerate(metrics):
        x=42+i*(w+gap);y=PAGE_H-247;box(c,x,y,w,99,PALE,BORDER,10);label(c,x+14,y+71,title,8,GREY);label(c,x+14,y+38,value,15,INK,'Lato-Heavy');paragraph(c,note,x+14,y+25,w-28,8,TEAL)
    label(c,42,PAGE_H-288,'SINAIS DO MODELO',11,TEAL,'Lato-Heavy')
    delta=act['ebitda']-bud['ebitda'];revenue_delta=act['receita_liquida']-bud['receita_liquida']
    reads=[('01  Receita ligeiramente acima do orçamento',f'A receita líquida simulada supera o orçamento em {money(revenue_delta)}, ou {pct(revenue_delta,bud["receita_liquida"])}.'),('02  Rentabilidade aquém do planejamento',f'O EBITDA apurado no modelo ficou {money(abs(delta))} abaixo do orçamento. O crescimento de vendas não se converteu proporcionalmente em resultado.'),('03  Estrutura de custos exige monitoramento',f'CMV, taxas, frete e despesas fixas consomem {pct(act["cmv"]+act["taxas"]+act["frete"]+act["despesas_fixas"],act["receita_liquida"])} da receita líquida. Revisar o mix e a alocação antes de ampliar volume.')]
    y=PAGE_H-312
    for heading1,desc in reads:
        box(c,42,y-83,PAGE_W-84,75,'#FFFFFF',BORDER,9)
        label(c,58,y-25,heading1,10,INK,'Lato-Bold')
        paragraph(c,desc,58,y-35,PAGE_W-116,9,GREY,13)
        y-=95
    label(c,42,171,'INTERPRETAÇÃO GERENCIAL',11,TEAL,'Lato-Heavy')
    paragraph(c,'O caso evidencia um problema comum de gestão: receita acima do planejado não garante cumprimento da meta de rentabilidade. A investigação deve separar efeitos de preço, mix, custo variável e estrutura de despesas, respeitando a granularidade disponível.',42,154,PAGE_W-84,10,INK,15)
    paragraph(c,'Limite: o EBITDA usado é uma aproximação operacional para estudo, sem depreciação, provisões, tributos sobre lucro ou fluxo de caixa. Nenhuma economia ou ganho observado é real.',42,99,PAGE_W-84,8,RED,11)
    c.showPage()
    # PAGE 3
    page_bg(c,3,'DRE / ORÇAMENTO');heading(c,'DRE gerencial e orçamento','Valores em R$, calculados em centavos inteiros. Comparação Jan–Out/2026.')
    cols=[42,267,365,465];right=[352,451,553]
    c.setFillColor(color('#F9F0E7'));c.roundRect(42,PAGE_H-170,PAGE_W-84,30,5,fill=1,stroke=0)
    label(c,55,PAGE_H-159,'CONTA / INDICADOR',8,INK);label(c,287,PAGE_H-159,'SIMULADO',8,INK);label(c,386,PAGE_H-159,'ORÇADO',8,INK);label(c,490,PAGE_H-159,'DESVIO',8,INK)
    dre=[('Receita bruta','receita_bruta'),('Deduções','deducoes'),('Receita líquida','receita_liquida'),('CMV','cmv'),('Lucro bruto','lucro_bruto'),('Taxas de venda','taxas'),('Frete / logística','frete'),('Margem de contribuição','margem_contribuicao'),('Despesas fixas','despesas_fixas'),('EBITDA gerencial','ebitda')]
    y=PAGE_H-196
    for i,(name,key) in enumerate(dre):
        major=key in ('receita_liquida','lucro_bruto','margem_contribuicao','ebitda')
        if major:
            c.setFillColor(color('#FBF2EA' if key!='ebitda' else '#F7E6D9'));c.roundRect(42,y-10,PAGE_W-84,26,4,fill=1,stroke=0)
        label(c,54,y,name,9,INK,'Lato-Bold' if major else 'Lato')
        def shortmoney(x):return (('-' if x<0 else '')+f'{abs(x)/100:,.0f}').replace(',','.')
        for j,v in enumerate([act[key],bud[key],act[key]-bud[key]]):
            c.setFont('Lato-Bold' if major else 'Lato',9);c.setFillColor(color(RED if j==2 and key=='ebitda' and v<0 else INK));c.drawRightString(right[j],y,shortmoney(v))
        y-=34
    label(c,42,277,'COMPARATIVO DE RECEITA LÍQUIDA POR MÊS',10,TEAL,'Lato-Heavy')
    a_month=[sum(r['receita_liquida'] for r in rows if r['tipo']=='realizado' and r['mes']==m) for m in range(1,11)]
    b_month=[sum(r['receita_liquida'] for r in rows if r['tipo']=='orcamento' and r['mes']==m) for m in range(1,11)]
    mx=max(a_month+b_month)*1.13;start=42;chartw=PAGE_W-84;bw=chartw/10
    for i,(av,bv) in enumerate(zip(a_month,b_month)):
        height=av/mx*136;bh=bv/mx*136;x=start+bw*i+7
        c.setFillColor(color('#CAD2D5'));c.roundRect(x,116,12,bh,2,stroke=0,fill=1)
        c.setFillColor(color(TEAL));c.roundRect(x+14,116,17,height,2,stroke=0,fill=1)
        label(c,x+2,103,['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out'][i],7,GREY,'Lato')
    label(c,44,79,'Orçado',8,GREY,'Lato');c.setFillColor(color('#CAD2D5'));c.rect(90,79,10,7,fill=1,stroke=0)
    label(c,125,79,'Realizado simulado',8,GREY,'Lato');c.setFillColor(color(TEAL));c.rect(219,79,10,7,fill=1,stroke=0)
    c.showPage()
    # PAGE 4
    page_bg(c,4,'FORECAST / CENÁRIOS');heading(c,'Forecast e simulação de cenários','Fechamento anual: jan–out simulado + nov–dez projetado, sem misturar naturezas.')
    label(c,42,PAGE_H-155,'FECHAMENTO ESTIMADO / BASE',10,TEAL,'Lato-Heavy')
    box(c,42,PAGE_H-275,PAGE_W-84,100,PALE,BORDER,11)
    label(c,60,PAGE_H-207,'RECEITA LÍQUIDA',8,GREY)
    label(c,60,PAGE_H-242,money(fy['receita_liquida']),18,INK,'Lato-Heavy')
    label(c,315,PAGE_H-207,'EBITDA ESTIMADO',8,GREY)
    label(c,315,PAGE_H-242,money(fy['ebitda']),18,INK,'Lato-Heavy')
    label(c,42,PAGE_H-307,'COMPARATIVO DE SENSIBILIDADE',10,TEAL,'Lato-Heavy')
    yy=PAGE_H-328
    for name,data,condition in scenarios:
        box(c,42,yy-72,PAGE_W-84,66,'#FFFFFF',BORDER,8)
        label(c,56,yy-26,name,11,INK,'Lato-Bold')
        label(c,56,yy-43,condition,8,GREY,'Lato')
        label(c,235,yy-24,'RECEITA LÍQUIDA',7,GREY)
        label(c,235,yy-46,money(data['receita_liquida']),11,INK,'Lato-Bold')
        label(c,418,yy-24,'EBITDA',7,GREY)
        label(c,418,yy-46,money(data['ebitda']),11,TEAL if data['ebitda']>=0 else RED,'Lato-Bold')
        yy-=83
    label(c,42,235,'CÁLCULO DO FORECAST',10,TEAL,'Lato-Heavy')
    paragraph(c,'Para novembro e dezembro, cada combinação canal/linha utiliza a média aritmética de agosto, setembro e outubro, multiplicada por um fator sazonal fixo de 1,12 (novembro) ou 1,17 (dezembro). Despesas fixas são projetadas pela média das mesmas categorias no trimestre, com fatores 1,025 e 1,05.',42,216,PAGE_W-84,9,INK,13)
    label(c,42,153,'LIMITE DE INTERPRETAÇÃO',10,TEAL,'Lato-Heavy')
    paragraph(c,'Cenários são exercícios de sensibilidade, não previsões calibradas. Alterações na receita incidem somente em nov–dez. Custos variáveis escalam com o volume e têm redução proporcional conforme a eficiência assumida; despesas fixas permanecem constantes.',42,134,PAGE_W-84,9,INK,13)
    c.showPage()
    # PAGE 5
    page_bg(c,5,'MÉTODO / GOVERNANÇA');heading(c,'Arquitetura, qualidade e limites','O mesmo pipeline alimenta a interface web, os artefatos de auditoria e este relatório.')
    stages=[('01','FONTE','Vendas agregadas, orçamento e despesas fixas, gerados por Python com seed 20261108.'),('02','VALIDAÇÃO','Chaves mensais, categorias, sinais de custos e integridade; registros inválidos vão para quarentena.'),('03','DRE','Receita líquida, CMV, margem de contribuição e EBITDA operacional simplificado.'),('04','FORECAST','Separação explícita entre 10 meses fictícios observados e 2 meses estimados.'),('05','PUBLICAÇÃO','Dashboard HTML autocontido, código documentado, saída CSV e testes automatizados.')]
    y=PAGE_H-155
    for n,name,desc in stages:
        box(c,42,y-77,PAGE_W-84,68,'#FFFFFF',BORDER,8)
        label(c,58,y-35,n,18,TEAL,'Lato-Heavy')
        label(c,103,y-29,name,9,INK,'Lato-Bold')
        paragraph(c,desc,103,y-34,PAGE_W-165,9,GREY,13)
        y-=83
    y=245
    label(c,42,y,'QUALIDADE E REPRODUTIBILIDADE',10,TEAL,'Lato-Heavy')
    paragraph(c,f'{s["linhas_validas"]} registros mensais válidos no realizado; {s["linhas_rejeitadas"]} rejeições documentadas; {s["linhas_projetadas"]} registros mensais projetados; 108 registros de orçamento. Cálculos monetários armazenados em centavos inteiros. Validações automatizadas testam identidades da DRE, separação de períodos, orçamento comparável e integridade de rateio.',42,y-16,PAGE_W-84,9,INK,13)
    label(c,42,159,'RESTRIÇÕES IMPORTANTES',10,TEAL,'Lato-Heavy')
    paragraph(c,'Não contempla balanço patrimonial, impostos sobre lucro, provisões, juros, depreciação, capital de giro ou demonstrativo de fluxo de caixa. O rateio de despesas fixas por receita é apenas para cortes analíticos. Não representa auditoria contábil ou desempenho real de negócio. Não há integração com IA nesta versão.',42,145,PAGE_W-84,9,INK,13)
    c.showPage();c.save()
    print('PDF gerado:',path.name,path.stat().st_size,'bytes')
    return path

if __name__=='__main__':
    from gerar_dados import generate
    from pipeline import run
    generate();build(run())
