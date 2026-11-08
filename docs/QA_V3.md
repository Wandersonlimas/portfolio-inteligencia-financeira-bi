# Verificação funcional · Case 03 V3

## Testes executados em 08/11/2026

- `python -m unittest discover -s testes -v`: **9 testes aprovados**.
- Navegador Chromium (Playwright): interface renderizada nos tamanhos de 1600, 1440, 1280 e 390 pixels de largura, sem erro de JavaScript e sem rolagem horizontal extra.
- Cinco KPIs e gráficos reativos conferidos contra o modelo sintético.
- Abas Visão executiva, DRE e rentabilidade, Forecast e cenários, Engenharia e auditoria: visibilidade e navegação conferidas.
- Filtros de período, canal e linha de negócio: seleção, recálculo e limpeza conferidos.
- Cenários base/otimista: mudança do valor de EBITDA comprovada (R$ 101.682 para R$ 144.735, com arredondamento no HTML).
- Exportação CSV: geração e cabeçalho conferidos com os filtros aplicados.
- PDF executivo: cinco páginas renderizadas para inspeção visual; conteúdo derivado do mesmo modelo que alimenta o HTML.

## Critérios de qualidade

Os indicadores usam dados sintéticos e distinguem realizados simulados dos valores projetados. As comparações dos cards usam orçamento para o mesmo período e dimensões. A identidade visual muda a apresentação sem alterar a matemática do pipeline.

## Reconstrução

1. Instalar `requirements.txt`.
2. Executar `python codigo/executar.py`.
3. Executar `python -m unittest discover -s testes -v`.
4. Abrir `index.html` e verificar as interações. Para atualizar a miniatura, obter uma captura real do dashboard e executar `python codigo/gerar_miniatura.py`.
