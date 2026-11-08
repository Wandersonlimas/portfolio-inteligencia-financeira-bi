Auditoria técnica automatizada.
Commit de origem: 3f6f4779d0b937ce2e23caa0f235bee9d8cb06d2
Python: success
Chromium: success

--- Logs dos testes Python ---
test_filters_scenarios_and_csv (test_dashboard.DashboardV3Tests.test_filters_scenarios_and_csv) ... FAIL
test_minimalist_dashboard_with_four_views (test_dashboard.DashboardV3Tests.test_minimalist_dashboard_with_four_views) ... ok
test_page_is_compiled (test_dashboard.DashboardV3Tests.test_page_is_compiled) ... ok
test_estrutura (test_dashboard_publicacao.TestDashboard.test_estrutura) ... ok
test_filtros_e_navegacao (test_dashboard_publicacao.TestDashboard.test_filtros_e_navegacao) ... ok
test_scripts_e_dados (test_dashboard_publicacao.TestDashboard.test_scripts_e_dados) ... ok
test_accounting_identities (test_pipeline.Case03Tests.test_accounting_identities) ... ok
test_all_periods_nonzero (test_pipeline.Case03Tests.test_all_periods_nonzero) ... ok
test_budget_ytd_comparable (test_pipeline.Case03Tests.test_budget_ytd_comparable) ... ok
test_coverage_and_quarantine (test_pipeline.Case03Tests.test_coverage_and_quarantine) ... ok
test_fixed_allocation_exact (test_pipeline.Case03Tests.test_fixed_allocation_exact) ... ok
test_forecast_not_mixed_with_realized (test_pipeline.Case03Tests.test_forecast_not_mixed_with_realized) ... ok

======================================================================
FAIL: test_filters_scenarios_and_csv (test_dashboard.DashboardV3Tests.test_filters_scenarios_and_csv)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/portfolio-inteligencia-financeira-bi/portfolio-inteligencia-financeira-bi/testes/test_dashboard.py", line 36, in test_filters_scenarios_and_csv
    self.assertEqual((ROOT/'index.html').read_bytes(),(ROOT/'entregaveis/dashboard_offline.html').read_bytes())
AssertionError: b'<!d[121927 chars]URL(url),500)});\nrefresh();\n})();\n</script></body></html>' != b'<!d[121927 chars]URL(url),500)});\nrefresh();\n})();\n</script></body></html>\n'

----------------------------------------------------------------------
Ran 12 tests in 2.275s

FAILED (failures=1)
--- Logs do navegador ---
OK: navegação, filtros e responsividade testados com Chromium
