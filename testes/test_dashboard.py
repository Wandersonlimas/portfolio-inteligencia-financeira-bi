"""Testes estáticos da versão web distribuída, sem navegador ou rede."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class DashboardV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=(ROOT/'index.html').read_text(encoding='utf-8')
        cls.source=(ROOT/'src/web/dashboard.html').read_text(encoding='utf-8')
        cls.css=(ROOT/'src/web/dashboard.css').read_text(encoding='utf-8')

    def test_page_is_compiled(self):
        self.assertNotIn('__DATA__',self.page)
        self.assertNotIn('__CSS__',self.page)
        self.assertNotIn('__JS__',self.page)
        self.assertIn('id="model-data"',self.page)

    def test_minimalist_dashboard_with_four_views(self):
        self.assertNotIn('class="hero"',self.source)
        self.assertIn('class="executive-grid"',self.source)
        self.assertIn('id="channelDonut"',self.source)
        self.assertIn('id="dreSummary"',self.source)
        self.assertIn('--teal:#bf683d',self.css.lower())
        for tab in ['executiva','dre','cenarios','engenharia']:
            self.assertIn(f'data-tab="{tab}"',self.source)
            self.assertIn(f'id="tab-{tab}"',self.source)

    def test_filters_scenarios_and_csv(self):
        for element in ['period','channel','line','exportCsv','growth','eff']:
            self.assertIn(f'id="{element}"',self.source)
        self.assertIn('.kpis{display:grid;',self.css)
        self.assertIn('100% sintética',self.page)
        self.assertEqual((ROOT/'index.html').read_bytes(),(ROOT/'entregaveis/dashboard_offline.html').read_bytes())

if __name__=='__main__':unittest.main()
