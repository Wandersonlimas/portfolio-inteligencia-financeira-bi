# Metodologia e dicionário de dados | Case 03

## 1. Escopo e corte temporal

Estudo demonstrativo, **100% sintético**, reproduzível com `seed=20261108`, data de preparação 08/11/2026. Operação digital fictícia com três canais (`Marketplace A`, `Marketplace B`, `Loja online`) e três linhas (`Essencial`, `Premium`, `Acessórios`). Nenhum dado veio de empresa, pessoa, cliente ou sistema externo.

Janeiro–outubro de 2026 é chamado **realizado simulado**. Novembro–dezembro é **projetado**. Orçamento existe de janeiro a dezembro. O dashboard compara **apenas os mesmos meses e as mesmas dimensões**.

## 2. Esquemas das quatro fontes

### `dados/brutos/vendas.csv`

`mes` (1–10); `canal`; `linha`; `pedidos` (inteiro > 0); `receita_bruta_centavos` (inteiro > 0); `deducoes_centavos`, `cmv_centavos`, `taxas_centavos`, `frete_centavos` (inteiros >= 0). Cada chave `(mes,canal,linha)` é única após validação. O gerador injeta um duplicado, um registro com receita negativa e um mês 13: **três erros controlados**. São auditados em `dados/processados/rejeicoes.csv`.

### `dados/brutos/orcamento_vendas.csv`

Mesmo esquema, cobrindo os 12 meses. É hipotético, não um orçamento real. Registros inválidos são erro fatal no pipeline.

### `dados/brutos/despesas_fixas.csv` e `orcamento_despesas.csv`

`mes` (realizado 1–10; orçado 1–12), `categoria` (`Pessoal`, `Marketing`, `Tecnologia`, `Administrativo`) e `valor_centavos` (inteiro >= 0). Uma linha por categoria e por mês. Não são despesas contabilizadas em ERP.

## 3. Cálculos da DRE simplificada

Valores são inteiros, em centavos, em todo o pipeline:

1. `Receita líquida = Receita bruta - Deduções`.
2. `Lucro bruto = Receita líquida - CMV`.
3. `Margem de contribuição (R$) = Lucro bruto - Taxas de venda - Frete/logística`.
4. `EBITDA gerencial simplificado (R$) = Margem de contribuição - Despesas fixas alocadas`.
5. `Margem EBITDA (%) = EBITDA / Receita líquida × 100`.
6. `Desvio vs orçamento (R$) = Simulado - Orçado`, com o mesmo recorte. Diferenças nos itens de custo são apresentadas sem reinterpretar sinal como favorable/unfavorable automaticamente.
7. `Ponto de equilíbrio gerencial = Despesas fixas / (Margem de contribuição / Receita líquida)`; ignora hipóteses de mudança no mix.

**Observação:** a abreviação EBITDA é usada como um *proxy operacional*, não como demonstração societária. Não existem depreciação/amortização, despesas financeiras e impostos sobre lucro modelados, nem previsão de caixa, provisões ou balanço patrimonial. As deduções são uma taxa ilustrativa da receita bruta, não o cálculo de tributos de empresa real.

## 4. Rateio gerencial de despesas fixas

Em cada mês e cenário (realizado, orçamento ou projetado), o total das despesas fixas é distribuído entre 9 combinações canal/linha proporcionalmente à receita líquida. Para evitar divergência de centavos, a última linha recebe o saldo residual após a divisão inteira.

`despesa_fixa_alocada[linha] = floor(total_fixos_mês × receita_líquida_linha / receita_líquida_mês)`; última linha = saldo. Esse rateio existe para permitir filtros, **não configura centro de custo nem critério contábil oficial**.

## 5. Forecast determinístico

A previsão por combinação canal/linha usa média simples de agosto, setembro e outubro (meses simulados) em cada componente de receita/custo e em pedidos.

- Novembro: `média Ago–Out × 1,12`.
- Dezembro: `média Ago–Out × 1,17`.
- Despesas fixas por categoria: média Ago–Out × `1,025` (nov) e × `1,05` (dez).

Os fatores são **arbitrários e transparentes** para a demonstração. Não há treinamento preditivo, confiança estatística, projeção de demanda real, custo de capital ou série histórica externa. A média de três meses não deve ser interpretada como método validado de forecasting comercial.

## 6. Cenários

Os três presets são:

| Cenário | Receita nov–dez | Eficiência nos custos variáveis nov–dez |
|---|---:|---:|
| Conservador | -8% | 0% |
| Base | 0% | 0% |
| Otimista | +10% | 4% |

Os controles manuais aceitam receita de -15% a +25% e eficiência de 0% a 12%. Aplicam-se somente a linhas `projetado`. Receita bruta e deduções multiplicam-se por `(1 + variação_receita)`. CMV, taxas e frete multiplicam-se por `(1 + variação_receita) × (1 - eficiência)`. Despesas fixas não variam. Recalculam-se as identidades da DRE por linha, arredondando para centavos.

Nenhuma simulação altera valores `realizado` nem `orcamento`. A seção de cenários exibe sempre o fechamento anual, independentemente do filtro de período, mas respeita canal/linha. As demais seções refletem o período escolhido.

## 7. Limitações e proteção

- Base agregada por mês, canal e linha, sem ticket detalhado por transação.
- Sem fluxo de caixa, capital de giro, recebíveis, inadimplência, estoque, descontos individuais, impostos sobre lucro ou depreciação.
- Sem poder inferencial; nenhuma economia, ROI, produtividade, crescimento ou rentabilidade foi observada em negócio real.
- Não há dados pessoais, logotipos corporativos, marca comercial do usuário nem integração com serviços externos.
- Diagnósticos gerados por regras e comparações determinísticas, **não por IA generativa**.
- Saída CSV em centavos para preservar somas exatas. Formatação BRL na interface apenas para leitura.

## 8. Garantias de qualidade

Os testes em `testes/test_pipeline.py` verificam: cobertura, quarentena, distinção realizado/projetado, identidades da DRE, orçamento no mesmo período, distribuição por mês/canal/linha e consistência global. O dashboard é testável em navegador sem rede.
