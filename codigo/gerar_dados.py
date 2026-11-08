"""Gerador de dados sintéticos reprodutíveis para o Case 03."""
import csv
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'dados'/'brutos'
CHANNELS=['Marketplace A','Marketplace B','Loja online']
LINES=['Essencial','Premium','Acessórios']
COSTS=['Pessoal','Marketing','Tecnologia','Administrativo']

def write_csv(name, fields, rows):
    RAW.mkdir(parents=True,exist_ok=True)
    with (RAW/name).open('w',encoding='utf-8',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

def generate():
    rng=random.Random(20261108)
    sales=[]; budget=[]; fixed=[]; budget_fixed=[]
    multipliers={'Marketplace A':1.22,'Marketplace B':0.98,'Loja online':0.83}
    line_multipliers={'Essencial':1.00,'Premium':1.28,'Acessórios':0.72}
    for month in range(1,13):
        seasonal=1 + (month-1)*0.016 + (0.13 if month==11 else 0.19 if month==12 else 0)
        for channel in CHANNELS:
            for line in LINES:
                gross_b=int(round(3000000*seasonal*multipliers[channel]*line_multipliers[line]))
                deduct_b=int(round(gross_b*.086))
                cogs_b=int(round(gross_b*({'Essencial':.40,'Premium':.35,'Acessórios':.47}[line])))
                fee_b=int(round(gross_b*({'Marketplace A':.107,'Marketplace B':.091,'Loja online':.044}[channel])))
                freight_b=int(round(gross_b*.052))
                budget.append({'mes':month,'canal':channel,'linha':line,'pedidos':max(1,round(gross_b/20800)),
                        'receita_bruta_centavos':gross_b,'deducoes_centavos':deduct_b,'cmv_centavos':cogs_b,
                        'taxas_centavos':fee_b,'frete_centavos':freight_b})
                if month<=10:
                    factor=rng.uniform(.91,1.115)
                    gross=max(1,int(gross_b*factor))
                    sales.append({'mes':month,'canal':channel,'linha':line,
                                  'pedidos':max(1,round(gross/20200+rng.uniform(-8,8))),
                                  'receita_bruta_centavos':gross,
                                  'deducoes_centavos':int(gross*rng.uniform(.079,.096)),
                                  'cmv_centavos':int(gross*({'Essencial':.398,'Premium':.352,'Acessórios':.473}[line])*rng.uniform(.97,1.04)),
                                  'taxas_centavos':int(gross*({'Marketplace A':.108,'Marketplace B':.092,'Loja online':.045}[channel])),
                                  'frete_centavos':int(gross*rng.uniform(.049,.064))})
        for k, cat in enumerate(COSTS):
            base=[5100000,2400000,1000000,1200000][k]
            base=int(base*(1+(month-1)*0.012))
            budget_fixed.append({'mes':month,'categoria':cat,'valor_centavos':base})
            if month<=10:
                fixed.append({'mes':month,'categoria':cat,'valor_centavos':int(base*rng.uniform(.94,1.10))})
    # Três registros propositalmente inválidos para testar rejeição/quarentena.
    sales.append({**sales[0]}) # duplicado
    sales.append({**sales[1],'receita_bruta_centavos':-100})
    sales.append({**sales[2],'mes':13})
    sf=['mes','canal','linha','pedidos','receita_bruta_centavos','deducoes_centavos','cmv_centavos','taxas_centavos','frete_centavos']
    ff=['mes','categoria','valor_centavos']
    write_csv('vendas.csv',sf,sales)
    write_csv('orcamento_vendas.csv',sf,budget)
    write_csv('despesas_fixas.csv',ff,fixed)
    write_csv('orcamento_despesas.csv',ff,budget_fixed)

if __name__=='__main__':
    generate(); print('Dados sintéticos criados em dados/brutos/')
