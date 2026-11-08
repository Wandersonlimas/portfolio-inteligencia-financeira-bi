# Case 03 | Revisão visual V2

Data: 08/11/2026.

## Objetivo

A versão anterior reservava espaço excessivo ao banner inicial e deixava os principais indicadores financeiros abaixo da primeira dobra. A revisão prioriza leitura operacional, navegação e diferenciação estética em relação ao Case 02.

## Mudanças implementadas

- Substituição do banner de abertura por faixa informativa compacta de 40 px, sem slogans.
- Cabeçalho com identidade do projeto e exportação CSV, seguido das quatro abas e dos três filtros.
- Cinco KPIs consolidados em um painel horizontal com separadores, mantendo números e fórmulas originais.
- Paleta própria com grafite, azul-petróleo, verde profundo e âmbar discreto para sinalização de orçamento e projeções.
- Revisão de cards, tabelas, gráficos, botões, filtros, alertas, estados de seleção e espaçamentos.
- Layout responsivo: cartões e filtros reorganizados para telas pequenas, navegação por abas com rolagem horizontal sem estourar a largura da página.
- Atualização da capa e cores do relatório PDF executivo.
- Nova miniatura para LinkedIn produzida com captura do dashboard real.
- Arquivos do dashboard gerados novamente a partir de `src/web/` via `codigo/gerar_dashboard.py`, mantendo versão offline autocontida.

## Comportamento preservado

- Visões: Executiva, DRE e rentabilidade, Forecast e cenários, Engenharia e auditoria.
- Filtros: período, canal e linha de negócio.
- Projeções: alterações limitadas a novembro e dezembro de 2026.
- Exportação CSV do recorte com números em centavos inteiros.
- Dados, fórmulas e metodologia permanecem sintéticos e rastreáveis.

## Qualidade

Os testes `python -m unittest discover -s testes -v` cobrem a lógica financeira, segregação de períodos e integridade da página gerada. Foi realizada inspeção visual da tela de 1550 px e de um viewport móvel de 390 px. A interface foi exercitada em navegador headless quanto a abas, filtros e limpeza do recorte.

**Importante:** não existe deploy público para este Case 03 até a publicação separada no GitHub Pages. Não divulgar como publicado antes da checagem do endereço público.
