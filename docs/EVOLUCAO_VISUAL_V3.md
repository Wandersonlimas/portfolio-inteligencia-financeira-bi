# Evolução visual · V3 · Minimalismo terracota

## Objetivo

Aplicar à interface funcional do Case 03 o conceito aprovado em 08/11/2026. Esta implementação não utiliza a imagem conceitual como plano de fundo: todos os componentes são HTML/CSS/SVG/JavaScript nativos, alimentados pelos dados processados pelo pipeline em Python.

## Mudanças reais

- **Identidade própria:** terracota `#BF683D`, creme `#FCFAF7`, branco, areia e cinza neutro, sem reaproveitar o azul-petróleo e o verde dos primeiros cases.
- **Cabeçalho compacto**, menu por abas e filtros antes dos KPIs.
- **Cinco cards de KPI independentes**, com variação calculada contra o orçamento do mesmo recorte. Percentuais e pontos percentuais são identificados separadamente.
- **Gráfico SVG de receita + margem EBITDA:** valores do próprio modelo, eixo esquerdo em R$ mil e direito em %, com tooltip nos pontos e barras.
- **Gráfico de rosca por canal:** CSS conic-gradient com valores percentuais e monetários recalculados conforme os filtros.
- **Resumo gerencial da DRE** e demais análises seguem reativas aos filtros.
- **Responsividade** testada em desktop e dispositivo móvel.
- **Miniatura e PDF executivo** gerados com a mesma identidade e com dados do modelo.

## Integridade

Permanece a distinção entre realizado simulado (jan–out) e estimado (nov–dez), sem alterar regras ou fórmulas do pipeline. Os resultados são sintéticos e não representam resultados corporativos.

Para reconstruir o dashboard e o PDF: `python codigo/executar.py`. Para testes: `python -m unittest discover -s testes -v`.
