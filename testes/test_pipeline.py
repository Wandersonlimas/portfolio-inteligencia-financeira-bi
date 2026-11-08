import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'codigo'))
from gerar_dados import generate
from pipeline import run, aggregate, COMPONENTS

class Case03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate(); cls.model=run()
    def test_coverage_and_quarantine(self):
        s=self.model['resumo']
        self.assertEqual(s['linhas_validas'],90)
        self.assertEqual(s['linhas_rejeitadas'],3)
        self.assertEqual(s['linhas_projetadas'],18)
    def test_forecast_not_mixed_with_realized(self):
        rows=self.model['registros']
        self.assertTrue(all(r['mes']<=10 for r in rows if r['tipo']=='realizado'))
        self.assertTrue(all(r['mes']>=11 for r in rows if r['tipo']=='projetado'))
    def test_accounting_identities(self):
        for r in self.model['registros']:
            self.assertEqual(r['receita_liquida'],r['receita_bruta']-r['deducoes'])
            self.assertEqual(r['lucro_bruto'],r['receita_liquida']-r['cmv'])
            self.assertEqual(r['margem_contribuicao'],r['lucro_bruto']-r['taxas']-r['frete'])
            self.assertEqual(r['ebitda'],r['margem_contribuicao']-r['despesas_fixas'])
    def test_budget_ytd_comparable(self):
        rows=self.model['registros']
        actual=aggregate([r for r in rows if r['tipo']=='realizado'])
        bud=aggregate([r for r in rows if r['tipo']=='orcamento' and r['mes']<=10])
        self.assertEqual(actual,self.model['resumo']['realizado_jan_out'])
        self.assertEqual(bud,self.model['resumo']['orcado_jan_out'])
    def test_fixed_allocation_exact(self):
        rows=self.model['registros']
        for typ in ('realizado','projetado','orcamento'):
            for m in range(1,13):
                part=[r for r in rows if r['tipo']==typ and r['mes']==m]
                if part:self.assertEqual(len(part),9)
    def test_all_periods_nonzero(self):
        self.assertGreater(self.model['resumo']['realizado_jan_out']['receita_liquida'],0)
        self.assertGreater(self.model['resumo']['realizado_jan_out']['ebitda'],0)

if __name__=='__main__':unittest.main()
