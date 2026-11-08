"""Consolidação de DRE, orçamento, forecast e cenários. Unidade: centavos inteiros."""
from __future__ import annotations
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'dados'/'brutos'
OUT=ROOT/'dados'/'processados'
SALES_FIELDS=('pedidos','receita_bruta_centavos','deducoes_centavos','cmv_centavos','taxas_centavos','frete_centavos')
MONEY_FIELDS=SALES_FIELDS[1:]
COMPONENTS=('receita_bruta','deducoes','receita_liquida','cmv','lucro_bruto','taxas','frete','margem_contribuicao','despesas_fixas','ebitda')
CHANNELS=['Marketplace A','Marketplace B','Loja online']
LINES=['Essencial','Premium','Acessórios']
COSTS=['Pessoal','Marketing','Tecnologia','Administrativo']

def read_csv(path):
    with (RAW/path).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def validate_sales(rows, expect_months):
    ok=[]; invalid=[]; seen=set()
    for idx,r in enumerate(rows,start=2):
        try:
            m=int(r['mes']); key=(m,r['canal'],r['linha'])
            if m not in expect_months: raise ValueError('mês fora do período')
            if r['canal'] not in CHANNELS or r['linha'] not in LINES: raise ValueError('dimensão inválida')
            item={k:int(r[k]) for k in SALES_FIELDS}
            if item['pedidos']<=0 or item['receita_bruta_centavos']<=0: raise ValueError('pedido/receita inválido')
            if any(item[k]<0 for k in MONEY_FIELDS if k!='receita_bruta_centavos'): raise ValueError('custo negativo')
            if item['deducoes_centavos']>=item['receita_bruta_centavos']: raise ValueError('deduções >= receita')
            if key in seen: raise ValueError('chave mensal duplicada')
            seen.add(key)
            ok.append({'mes':m,'canal':r['canal'],'linha':r['linha'],**item})
        except (ValueError,KeyError,TypeError) as e:
            invalid.append({'linha_origem':idx,'motivo':str(e),'registro':str(r)})
    return ok, invalid

def validate_fixed(rows, expect_months):
    out=[]; seen=set()
    for r in rows:
        m=int(r['mes']); val=int(r['valor_centavos']); cat=r['categoria']; key=(m,cat)
        if m not in expect_months or cat not in COSTS or key in seen or val<0:
            raise ValueError('Despesa fixa inválida: '+str(r))
        seen.add(key); out.append({'mes':m,'categoria':cat,'valor_centavos':val})
    if len(out)!=len(expect_months)*len(COSTS): raise ValueError('Despesas fixas incompletas')
    return out

def round_ratio(numerator,denominator,weight):
    return (weight*numerator)//denominator if denominator else 0

def allocate_fixed(rows, fixed_month):
    """Rateio exato de Opex por receita líquida para recortes. Saldo de centavos vai à última linha."""
    buckets=defaultdict(list)
    for r in rows:buckets[r['mes']].append(r)
    for month,items in buckets.items():
        items.sort(key=lambda z:(z['canal'],z['linha']))
        total=int(fixed_month.get(month,0))
        net_total=sum(x['receita_bruta_centavos']-x['deducoes_centavos'] for x in items)
        remaining=total
        for i,x in enumerate(items):
            if i==len(items)-1: alloc=remaining
            else:
                alloc=round_ratio(x['receita_bruta_centavos']-x['deducoes_centavos'],net_total,total)
            x['despesas_fixas_centavos']=alloc; remaining-=alloc
        assert sum(x['despesas_fixas_centavos'] for x in items)==total
    return rows

def fixed_dict(entries):
    d=defaultdict(int)
    for r in entries:d[r['mes']]+=r['valor_centavos']
    return d

def forecast_rows(actual, fixed):
    """Nov e dez: média Ago-Out do mesmo canal/linha; fator sazonal explícito."""
    keyed=defaultdict(list)
    for r in actual:
        if r['mes'] in (8,9,10):keyed[(r['canal'],r['linha'])].append(r)
    projected=[]
    for month, factor in ((11,1.12),(12,1.17)):
        for (channel,line),sample in keyed.items():
            if len(sample)!=3: raise ValueError('Histórico insuficiente para forecast')
            data={k:int(round((sum(x[k] for x in sample)/3)*factor)) for k in SALES_FIELDS}
            projected.append({'mes':month,'canal':channel,'linha':line,**data})
    proj_fixed={}
    grouped=defaultdict(list)
    for item in fixed:
        if item['mes'] in (8,9,10):grouped[item['categoria']].append(item['valor_centavos'])
    for month,factor in ((11,1.025),(12,1.05)):
        proj_fixed[month]=sum(int(round((sum(grouped[cat])/3)*factor)) for cat in COSTS)
    return projected,proj_fixed

def enrich(rows,kind):
    enriched=[]
    for r in rows:
        gross=r['receita_bruta_centavos']; deduct=r['deducoes_centavos']; net=gross-deduct
        cogs=r['cmv_centavos']; fees=r['taxas_centavos']; shipping=r['frete_centavos']; fixed=r['despesas_fixas_centavos']
        gross_profit=net-cogs; contribution=gross_profit-fees-shipping
        enriched.append({'mes':r['mes'],'canal':r['canal'],'linha':r['linha'],'tipo':kind,'pedidos':r['pedidos'],
              'receita_bruta':gross,'deducoes':deduct,'receita_liquida':net,'cmv':cogs,
              'lucro_bruto':gross_profit,'taxas':fees,'frete':shipping,'margem_contribuicao':contribution,
              'despesas_fixas':fixed,'ebitda':contribution-fixed})
    return enriched

def aggregate(rows):
    out={k:sum(r[k] for r in rows) for k in COMPONENTS}
    out['pedidos']=sum(r['pedidos'] for r in rows)
    return out

def run():
    a,bad=validate_sales(read_csv('vendas.csv'),set(range(1,11)))
    b, bad_budget=validate_sales(read_csv('orcamento_vendas.csv'),set(range(1,13)))
    if bad_budget:raise ValueError('Orçamento contém entradas inválidas')
    if len(a)!=90 or len(b)!=108:raise ValueError('Cobertura mensal incompleta')
    af=validate_fixed(read_csv('despesas_fixas.csv'),set(range(1,11)))
    bf=validate_fixed(read_csv('orcamento_despesas.csv'),set(range(1,13)))
    p,pf=forecast_rows(a,af)
    rows=enrich(allocate_fixed(a,fixed_dict(af)),'realizado') + enrich(allocate_fixed(p,pf),'projetado') + enrich(allocate_fixed(b,fixed_dict(bf)),'orcamento')
    valid=[r for r in rows if r['tipo']=='realizado']
    projected=[r for r in rows if r['tipo']=='projetado']
    budget=[r for r in rows if r['tipo']=='orcamento']
    ytd=aggregate(valid); plan_ytd=aggregate([r for r in budget if r['mes']<=10]); fy=aggregate(valid+projected)
    summary={'realizado_jan_out':ytd,'orcado_jan_out':plan_ytd,'fechamento_estimado_jan_dez':fy,
             'orcado_jan_dez':aggregate(budget),'linhas_validas':len(a),'linhas_rejeitadas':len(bad),
             'linhas_projetadas':len(p),'base_ate_mes':10}
    if summary['linhas_rejeitadas']!=3: raise AssertionError('Quarentena não rastreada')
    if sum(r['ebitda'] for r in valid)!=ytd['ebitda']:raise AssertionError('DRE não concilia')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'modelo.json').write_text(json.dumps({'meta':{'nome':'Case 03 | Inteligência de Negócios e Gestão Financeira','ano':2026,'atualizado_em':'2026-11-08','fontes':'Dados 100% sintéticos, sem dados reais de empresas','monetario':'centavos inteiros','forecast':'Nov-Dez simulados'},'registros':rows,'resumo':summary},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    with (OUT/'rejeicoes.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['linha_origem','motivo','registro']);writer.writeheader();writer.writerows(bad)
    with (OUT/'dre_mensal.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['mes','tipo','receita_liquida','cmv','taxas','frete','margem_contribuicao','despesas_fixas','ebitda']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for kind in ('realizado','projetado','orcamento'):
            for m in range(1,13):
                part=[r for r in rows if r['tipo']==kind and r['mes']==m]
                if part:
                    agg=aggregate(part);writer.writerow({'mes':m,'tipo':kind,**{k:agg[k] for k in fields[2:]}})
    return {'meta':{'ano':2026},'registros':rows,'resumo':summary}

if __name__=='__main__':
    from gerar_dados import generate
    generate(); print(json.dumps(run()['resumo'],ensure_ascii=False,indent=2))
