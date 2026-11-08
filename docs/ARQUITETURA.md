# Arquitetura técnica | Inteligência de Negócios e Gestão Financeira

## Pipeline

```text
gerar_dados.py
  ├── vendas.csv  (10 meses + 3 erros intencionais)
  ├── despesas_fixas.csv
  ├── orcamento_vendas.csv  (12 meses)
  └── orcamento_despesas.csv
         │
         ▼
pipeline.py
  ├── validação de esquemas e chaves
  ├── registro de rejeições
  ├── DRE em centavos inteiros
  ├── rateio mensal exato das despesas fixas
  ├── rolling avg Ago-Out + sazonalidade para Nov-Dez
  └── modelo.json + dre_mensal.csv + rejeicoes.csv
         │
         ├── gerar_dashboard.py -> index.html (HTML+CSS+JS+JSON autocontido)
         └── gerar_relatorio.py -> entregaveis/Relatorio_Executivo_Case03_Gestao_Financeira.pdf
```

## Contratos

- O código do Python não depende do JavaScript para cálculo de DRE, orçamento ou forecast-base.
- O JavaScript usa exclusivamente o JSON embutido para filtros, visão financeira, exportação e cenários. `model-data` tem todas as dimensões necessárias.
- O PDF usa o mesmo objeto `model` que gerou o HTML; indicadores-base não são digitados manualmente no script de layout.
- O arquivo `index.html` é autocontido e pronto para publicação por branch em GitHub Pages.
- A separação de período está em `tipo`: `realizado`, `projetado`, `orcamento`.
- `centavos` é a unidade monetária no cálculo; `R$` é somente camada de apresentação.

## Interfaces

Visões: `executiva`, `dre`, `cenarios`, `engenharia`. Filtros sincronizados: `period`, `channel`, `line`. As três dimensões de corte não comprometem somatório total porque despesas compartilhadas são rateadas com reconciliação de centavos.

## Teste e segurança

Execute `python -m unittest discover -s testes -v`. A versão pública não requer credenciais, banco de dados, CDNs, tokens, APIs ou Python. Não inserir `.env`, credenciais, informações contábeis reais, código proprietário ou nomes de empresas.
