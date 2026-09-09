# Dicionário de Dados — MVP Resiliência Econômica e Setorial

Este documento descreve os dados utilizados no projeto **Oportunidades em meio ao Caos**, incluindo as séries originais consolidadas, variáveis derivadas no pré-processamento e métricas criadas durante a Análise Exploratória de Dados (EDA).

O objetivo do dicionário é facilitar a manutenção do repositório, a interpretação das análises e a preparação das próximas etapas de Machine Learning.

> **Importante:** o sinal matemático de uma variável não significa automaticamente que o resultado é economicamente "bom" ou "ruim". Por exemplo, `usd_brl_return > 0` indica valorização do dólar frente ao real, enquanto `unemployment_change > 0` indica aumento do desemprego. A interpretação depende do contexto.

---

## 1. Fontes de dados

| Fonte | Dados utilizados | Frequência original | Papel no projeto |
|---|---|---|---|
| Banco Central do Brasil (BCB/SGS) | IBC-Br, Selic e USD/BRL | Mensal / diária | Condições macroeconômicas, juros e câmbio |
| IBGE/SIDRA | IPCA, PIB e desemprego | Mensal / trimestral / trimestre móvel | Inflação, atividade econômica e mercado de trabalho |
| B3 | Ibovespa, IFNC, ICON e IEE | Histórico de índices, consolidado mensalmente | Mercado geral e comparação de resiliência setorial |

Todos os dados são integrados em uma referência mensal no pré-processamento.

---

# 2. Datasets principais

## `dataset_monthly_reference.csv`

Base integrada pelo **mês de referência** de cada indicador. É utilizada principalmente para:

- EDA histórica;
- gráficos temporais;
- comparação entre indicadores;
- retorno, volatilidade e drawdown dos índices;
- análise de correlação e relações contemporâneas.

Essa base não aplica as defasagens conservadoras de disponibilidade utilizadas no dataset de modelagem.

## `dataset_mvp.csv`

Base destinada à preparação da modelagem. Aplica defasagens conservadoras para reduzir risco de **look-ahead bias**:

| Indicador | Defasagem aplicada |
|---|---:|
| IBC-Br | 2 meses |
| IPCA mensal | 1 mês |
| IPCA 12 meses | 1 mês |
| Desemprego | 1 mês |
| PIB | 3 meses |

Depois das defasagens são calculadas `ibc_br_change`, `pib_change_3m` e `unemployment_change`.

## `dataset_mvp_complete.csv`

Subconjunto de `dataset_mvp.csv` contendo somente meses em que as principais séries estão simultaneamente disponíveis. É útil em análises que realmente exigem todas as séries, mas não deve ser usado automaticamente em toda EDA porque reduz a janela histórica.

---

# 3. Tipos de dados utilizados

Os tipos abaixo representam os tipos esperados após leitura com pandas.

| Tipo | Significado |
|---|---|
| `datetime64[ns]` | Data mensal ou data de evento |
| `float64` | Número contínuo, percentual, índice, retorno, volatilidade, correlação ou score |
| `int64` / `Int64` | Contagem ou quantidade de meses/observações |
| `string` / `object` | Nome de setor, período, regime ou classificação textual |
| `category` | Pode ser utilizado futuramente para classificações como `Normal`, `Atenção` e `Stress elevado` |

---

# 4. Dimensão temporal

| Variável | Tipo | Origem | Significado | Interpretação |
|---|---|---|---|---|
| `date` | `datetime64[ns]` | Todas as fontes | Último dia do mês utilizado como chave temporal comum | Identifica o mês da observação |

---

# 5. Indicadores macroeconômicos — Banco Central

## 5.1 IBC-Br

| Variável | Tipo | Frequência | Papel | Significado / cálculo | Interpretação |
|---|---|---|---|---|---|
| `ibc_br` | `float64` | Mensal | Feature macroeconômica | Índice de Atividade Econômica do Banco Central, dessazonalizado | Valores mais altos representam nível maior de atividade. Deve ser interpretado principalmente junto da variação |
| `ibc_br_change` | `float64` | Mensal | Feature derivada | `ibc_br / ibc_br.shift(1) - 1` | `> 0`: atividade aumentou; `< 0`: atividade caiu. Quedas persistentes podem indicar desaceleração econômica |

### Uso no Stress Score

No score exploratório, `ibc_br_change` recebe direção **-1**: valores mais baixos são transformados em maior contribuição para stress.

---

## 5.2 Selic

| Variável | Tipo | Frequência | Papel | Significado / cálculo | Interpretação |
|---|---|---|---|---|---|
| `selic` | `float64` | Mensal | Feature macroeconômica | Último valor da meta Selic disponível no mês | Mede o nível de juros. Não existe interpretação universal de positivo/negativo isoladamente |
| `selic_change` | `float64` | Mensal | Feature derivada | `selic.diff()` | `> 0`: juros subiram; `< 0`: juros caíram. A unidade é ponto percentual, não retorno percentual |

### Uso no Stress Score

`selic_change` recebe direção **+1**: aumentos mais fortes dos juros elevam o componente exploratório de stress.

---

## 5.3 Câmbio USD/BRL

| Variável | Tipo | Frequência | Papel | Significado / cálculo | Interpretação |
|---|---|---|---|---|---|
| `usd_brl` | `float64` | Mensal | Feature macroeconômica | Última cotação de venda USD/BRL disponível no mês | Valor maior significa dólar mais caro em reais / real mais depreciado |
| `usd_brl_return` | `float64` | Mensal | Feature derivada | `usd_brl.pct_change()` | `> 0`: dólar valorizou frente ao real; `< 0`: dólar caiu frente ao real |
| `usd_brl_volatility` | `float64` | Mensal | Feature de risco cambial | Desvio padrão dos retornos diários do dólar × `sqrt(21)` | Quanto maior, maior a instabilidade cambial. Não possui interpretação de sinal negativo/positivo; o nível é o que importa |

### Fórmula da volatilidade cambial

```text
retorno_diario = valor_t / valor_t-1 - 1
volatilidade_mensal ≈ std(retorno_diario) × sqrt(21)
```

### Uso no Stress Score

`usd_brl_return` e `usd_brl_volatility` recebem direção **+1**.

---

# 6. Indicadores IBGE

## 6.1 IPCA

| Variável | Tipo | Frequência | Papel | Origem | Significado | Interpretação |
|---|---|---|---|---|---|---|
| `ipca_month` | `float64` | Mensal | Feature macroeconômica | SIDRA 1737, variável 63 | Variação percentual do IPCA no mês | Valor positivo = inflação no mês; negativo = deflação |
| `ipca_12m` | `float64` | Mensal | Feature macroeconômica | SIDRA 1737, variável 2265 | Inflação acumulada em 12 meses | Valores elevados representam inflação mais persistente; deve ser analisado em conjunto com atividade e juros |

### Uso no Stress Score

`ipca_12m` recebe direção **+1**.

---

## 6.2 Desemprego

| Variável | Tipo | Frequência | Papel | Origem | Significado / cálculo | Interpretação |
|---|---|---|---|---|---|---|
| `unemployment` | `float64` | Trimestre móvel em grade mensal | Feature socioeconômica | SIDRA 6381, variável 4099 | Taxa de desocupação | Valor maior normalmente representa pior condição do mercado de trabalho |
| `unemployment_change` | `float64` | Mensal | Feature derivada | Calculada | `unemployment.diff()` | `> 0`: desemprego aumentou; `< 0`: desemprego caiu. Unidade: ponto percentual |

### Uso no Stress Score

`unemployment_change` recebe direção **+1**.

---

## 6.3 PIB

| Variável | Tipo | Frequência | Papel | Origem | Significado / cálculo | Interpretação |
|---|---|---|---|---|---|---|
| `pib_index` | `float64` | Trimestral, propagado para grade mensal | Feature macroeconômica | SIDRA 1621 | Índice trimestral utilizado para representar atividade econômica agregada | Valor maior indica nível maior do índice; a direção é melhor observada pela variação |
| `pib_change_3m` | `float64` | Mensal após tratamento | Feature derivada | Calculada | `pib_index.pct_change(3)` | `> 0`: expansão em relação a 3 meses antes; `< 0`: retração |

### Uso no Stress Score

`pib_change_3m` recebe direção **-1**: quedas mais fortes aumentam a contribuição para stress.

---

# 7. Índices B3

| Variável | Tipo | Frequência | Papel | Significado |
|---|---|---|---|---|
| `ibovespa` | `float64` | Mensal | Benchmark de mercado | Nível do Ibovespa, referência geral do mercado acionário brasileiro |
| `ifnc` | `float64` | Mensal | Setor analisado | Nível do Índice Financeiro (IFNC) |
| `icon` | `float64` | Mensal | Setor analisado | Nível do Índice de Consumo (ICON) |
| `iee` | `float64` | Mensal | Setor analisado | Nível do Índice de Energia Elétrica (IEE) |

O nível em pontos é útil para observar evolução histórica, mas não deve ser comparado diretamente entre índices como medida de desempenho. Para comparação são utilizados retornos, volatilidade e drawdown.

---

# 8. Variáveis derivadas dos índices B3

As variáveis abaixo existem para cada prefixo:

```text
ibovespa
ifnc
icon
iee
```

## 8.1 Retorno mensal

| Padrão de variável | Tipo | Fórmula | Significado | Interpretação |
|---|---|---|---|---|
| `<indice>_return_1m` | `float64` | `indice.pct_change()` | Retorno percentual em relação ao mês anterior | `> 0`: valorização; `< 0`: queda |

Exemplos:

- `ibovespa_return_1m`
- `ifnc_return_1m`
- `icon_return_1m`
- `iee_return_1m`

## 8.2 Retorno de 3 meses

| Padrão de variável | Tipo | Fórmula | Significado | Interpretação |
|---|---|---|---|---|
| `<indice>_return_3m` | `float64` | `indice.pct_change(3)` | Retorno em relação ao nível observado 3 meses antes | Positivo = valorização acumulada no horizonte; negativo = perda no horizonte |

Exemplos:

- `ibovespa_return_3m`
- `ifnc_return_3m`
- `icon_return_3m`
- `iee_return_3m`

## 8.3 Volatilidade de 3 meses anualizada

| Padrão de variável | Tipo | Fórmula | Significado | Interpretação |
|---|---|---|---|---|
| `<indice>_volatility_3m_ann` | `float64` | `rolling(3).std() × sqrt(12)` sobre retornos mensais | Oscilação dos retornos nos últimos 3 meses, anualizada | Quanto maior, maior a instabilidade/risco observado |

Exemplos:

- `ibovespa_volatility_3m_ann`
- `ifnc_volatility_3m_ann`
- `icon_volatility_3m_ann`
- `iee_volatility_3m_ann`

> A volatilidade usada em algumas tabelas da EDA é simplesmente `std()` dos retornos mensais de um período e, portanto, **não é a mesma métrica** da volatilidade móvel anualizada acima.

## 8.4 Drawdown

| Padrão de variável | Tipo | Fórmula | Significado | Interpretação |
|---|---|---|---|---|
| `<indice>_drawdown` | `float64` | `indice / indice.cummax() - 1` | Distância percentual em relação ao maior nível histórico observado até o mês | `0` = no pico; valores negativos = abaixo do pico; quanto mais negativo, pior a perda |

Exemplos:

- `ibovespa_drawdown`
- `ifnc_drawdown`
- `icon_drawdown`
- `iee_drawdown`

---

# 9. Variáveis do Stress Score exploratório

O Stress Score é criado durante a EDA. Ele ainda **não é o target definitivo do modelo**.

## 9.1 Componentes padronizados

Para cada indicador disponível, é calculado:

```text
z = (x - média) / desvio_padrão
stress_z = z × direção
```

| Variável criada | Tipo | Direção | Interpretação |
|---|---|---:|---|
| `ibc_br_change_stress_z` | `float64` | -1 | Quedas incomuns da atividade aumentam o score |
| `selic_change_stress_z` | `float64` | +1 | Altas incomuns da Selic aumentam o score |
| `usd_brl_return_stress_z` | `float64` | +1 | Valorização incomum do dólar aumenta o score |
| `usd_brl_volatility_stress_z` | `float64` | +1 | Maior instabilidade cambial aumenta o score |
| `ipca_12m_stress_z` | `float64` | +1 | Inflação de 12 meses acima do padrão aumenta o score |
| `unemployment_change_stress_z` | `float64` | +1 | Aumento incomum do desemprego aumenta o score |
| `pib_change_3m_stress_z` | `float64` | -1 | Queda incomum da atividade do PIB aumenta o score |

## 9.2 Score agregado

| Variável | Tipo | Cálculo | Significado | Interpretação |
|---|---|---|---|---|
| `stress_score` | `float64` | Média dos componentes `*_stress_z` disponíveis | Intensidade relativa de condições macro/socioeconômicas adversas | Valores maiores representam maior stress relativo à própria distribuição histórica da base |

O score não representa probabilidade e não possui unidade econômica direta.

## 9.3 Classificação em níveis

| Variável | Tipo | Valores | Regra atual | Significado |
|---|---|---|---|---|
| `stress_level` | `string` | `Normal`, `Atenção`, `Stress elevado` | `< P75`, `P75–P90`, `>= P90` do `stress_score` | Segmentação exploratória por intensidade de stress |
| `regime_eda` | `string` | `Normal`, `Stress` | `stress_score >= P75` = Stress | Classificação binária exploratória usada para comparar comportamento dos setores |

> Essas classificações são regras exploratórias da EDA. Devem ser diferenciadas do futuro target formal de Machine Learning.

---

# 10. Métricas de recuperação e drawdown

A tabela `recovery_table` é criada na EDA para cada índice.

| Variável | Tipo | Significado | Interpretação |
|---|---|---|---|
| `indice` | `string` | Nome do índice analisado | `IBOVESPA`, `IFNC`, `ICON` ou `IEE` |
| `pior_drawdown` | `float64` | Menor drawdown histórico encontrado | Quanto mais negativo, maior a pior perda histórica |
| `data_pior_drawdown` | `datetime64[ns]` | Data do ponto de pior drawdown | Identifica quando ocorreu a maior queda relativa ao pico |
| `data_pico_anterior` | `datetime64[ns]` | Data do pico de referência anterior ao pior drawdown | Início da principal trajetória de perda |
| `data_recuperacao` | `datetime64[ns]` | Primeiro mês posterior em que o índice retornou ao pico anterior | Pode ser ausente se o pico ainda não tiver sido recuperado |
| `meses_para_recuperar` | `float64` / `int64` | Número de meses entre o pico e a recuperação | Quanto menor, mais rápida a recuperação |
| `meses_em_drawdown` | `float64` | Proporção da série histórica com drawdown abaixo de zero | Quanto maior, maior o tempo relativo passado abaixo de máximos anteriores |

---

# 11. Análise de Stress x Normal

A tabela `stress_normal` compara cada índice em meses classificados como Normal e Stress.

| Variável | Tipo | Significado |
|---|---|---|
| `indice` | `string` | Índice analisado |
| `regime` | `string` | `Normal` ou `Stress` |
| `meses` | `int64` | Quantidade de observações válidas no regime |
| `retorno_medio` | `float64` | Média dos retornos mensais no regime |
| `retorno_acumulado` | `float64` | `(1 + retorno).prod() - 1` dentro do subconjunto analisado |
| `volatilidade` | `float64` | Desvio padrão dos retornos mensais no regime |
| `meses_negativos_pct` | `float64` | Proporção de meses com retorno negativo |
| `pior_mes` | `float64` | Menor retorno mensal observado no regime |

---

# 12. Análise de defasagens macroeconômicas

A tabela `lag_results` mede associação entre indicadores macro e retorno dos setores com lags de 0, 1, 3 e 6 meses.

| Variável | Tipo | Significado |
|---|---|---|
| `macro` | `string` | Variável macroeconômica analisada |
| `setor` | `string` | Retorno do índice/setor analisado |
| `lag_meses` | `int64` | Quantidade de meses de defasagem aplicada à variável macro |
| `observacoes` | `int64` | Número de pares válidos utilizados na correlação |
| `pearson` | `float64` | Correlação linear de Pearson |
| `spearman` | `float64` | Correlação de Spearman baseada na ordenação dos valores |
| `abs_pearson` | `float64` | Valor absoluto da correlação de Pearson, usado para ordenar força de associação |
| `abs_spearman` | `float64` | Valor absoluto da correlação de Spearman |

### Interpretação do lag

```text
lag = 0  -> macro(t)   x retorno(t)
lag = 1  -> macro(t-1) x retorno(t)
lag = 3  -> macro(t-3) x retorno(t)
lag = 6  -> macro(t-6) x retorno(t)
```

Correlação não implica causalidade.

> **Padronização de nomenclatura:** os retornos setoriais persistidos pelo pré-processamento usam o sufixo `_return_1m`. Portanto, o padrão recomendado para essa análise é `ibovespa_return_1m`, `ifnc_return_1m`, `icon_return_1m` e `iee_return_1m`.

---

# 13. Correlação por regime

A tabela `regime_correlations` verifica se a relação entre macroeconomia e setores muda conforme o regime.

| Variável | Tipo | Significado |
|---|---|---|
| `macro` | `string` | Indicador macroeconômico |
| `setor` | `string` | Retorno setorial |
| `regime` | `string` | `Todos`, `Normal` ou `Stress` |
| `observacoes` | `int64` | Quantidade de pares válidos |
| `pearson` | `float64` | Correlação linear no regime |
| `spearman` | `float64` | Correlação monotônica no regime |

Mudanças importantes entre `Normal` e `Stress` podem indicar sensibilidade diferente do setor ao contexto macroeconômico, mas não demonstram causalidade.

---

# 14. Outliers como eventos econômicos

Os retornos extremos são identificados pela regra do intervalo interquartil:

```text
IQR = Q3 - Q1
limite_inferior = Q1 - 1,5 × IQR
limite_superior = Q3 + 1,5 × IQR
```

## `outlier_events`

| Variável | Tipo | Significado |
|---|---|---|
| `date` | `datetime64[ns]` | Mês do evento extremo |
| `setor` | `string` | Índice/setor associado ao evento |
| `retorno` | `float64` | Retorno mensal identificado como extremo |
| `tipo` | `string` | `Perda extrema` ou `Ganho extremo` |
| `stress_score` | `float64` | Stress Score do mesmo mês |
| `regime_eda` | `string` | Regime exploratório no mês |

## `outlier_summary`

| Variável | Tipo | Significado |
|---|---|---|
| `setor` | `string` | Setor analisado |
| `eventos` | `int64` | Quantidade de outliers encontrados |
| `stress_medio` | `float64` | Stress Score médio nos meses extremos |
| `stress_maximo` | `float64` | Maior Stress Score entre os eventos extremos |
| `percentual_stress` | `float64` | Percentual de eventos extremos ocorridos em regime Stress |

Outliers não são removidos automaticamente porque podem representar eventos econômicos relevantes ao problema de pesquisa.

---

# 15. Estatísticas por subperíodo

A comparação por períodos históricos utiliza métricas como:

| Variável | Tipo | Significado |
|---|---|---|
| `periodo` | `string` | Nome do subperíodo histórico |
| `setor` | `string` | Índice/setor |
| `observacoes` | `int64` | Número de meses válidos |
| `retorno_medio_mensal` / `retorno_medio` | `float64` | Média dos retornos mensais |
| `mediana_retorno` | `float64` | Mediana dos retornos mensais |
| `retorno_acumulado` | `float64` | Retorno composto no período |
| `volatilidade_mensal` / `volatilidade` | `float64` | Desvio padrão dos retornos mensais |
| `meses_positivos_pct` | `float64` | Percentual de meses com retorno positivo |
| `meses_negativos_pct` / `percentual_negativo` | `float64` | Percentual de meses com retorno negativo |
| `melhor_mes` | `float64` | Maior retorno mensal |
| `pior_mes` | `float64` | Menor retorno mensal |

---

# 16. Índice exploratório de resiliência

O índice de resiliência é uma **métrica exploratória da EDA**, não um target de Machine Learning.

## 16.1 Base de resiliência

| Variável | Tipo | Significado | Melhor direção |
|---|---|---|---|
| `setor` | `string` | Retorno setorial analisado | — |
| `observacoes_stress` | `int64` | Número de meses em Stress utilizados | Mais observações aumentam robustez descritiva, mas não entram diretamente no score |
| `retorno_medio_stress` | `float64` | Retorno médio mensal durante Stress | Maior |
| `volatilidade_stress` | `float64` | Desvio padrão dos retornos em Stress | Menor |
| `percentual_negativo_stress` | `float64` | Percentual de retornos negativos em Stress | Menor |
| `pior_mes_stress` | `float64` | Pior retorno mensal em Stress | Maior / menos negativo |
| `drawdown_stress` | `float64` | Drawdown associado à análise de Stress | Maior / menos negativo |
| `tempo_recuperacao` | `float64` | Meses necessários para recuperar o pico de referência | Menor |

## 16.2 Scores normalizados

Os componentes são normalizados por Min-Max:

```text
score = (x - min) / (max - min)
```

Quando menor é melhor:

```text
score_final = 1 - score
```

| Variável | Tipo | Base | Melhor direção original |
|---|---|---|---|
| `score_retorno` | `float64` | `retorno_medio_stress` | Maior |
| `score_volatilidade` | `float64` | `volatilidade_stress` | Menor |
| `score_perdas` | `float64` | `percentual_negativo_stress` | Menor |
| `score_pior_mes` | `float64` | `pior_mes_stress` | Maior |
| `score_drawdown` | `float64` | `drawdown_stress` | Maior |
| `score_recuperacao` | `float64` | `tempo_recuperacao` | Menor |

Todos os scores são transformados para que **valores maiores representem uma situação mais favorável**.

## 16.3 Score final

| Variável | Tipo | Cálculo | Significado |
|---|---|---|---|
| `resilience_score` | `float64` | Média dos seis componentes normalizados disponíveis | Resiliência relativa em escala 0–1 |
| `resilience_score_100` | `float64` | `resilience_score × 100` | Mesma informação em escala 0–100 |
| `ranking` | `int64` | Ordem decrescente de `resilience_score_100` | 1 = maior score exploratório entre os setores comparados |

O `resilience_score_100` **não é probabilidade**, não mede chance de ganho e não deve ser usado como target do modelo. É uma comparação relativa dependente dos setores, período e critérios escolhidos.

---

# 17. Estatísticas descritivas da EDA

As tabelas descritivas usam as seguintes medidas:

| Métrica | Tipo | Significado |
|---|---|---|
| `n` / `observacoes` | `int64` | Número de valores válidos |
| `media` | `float64` | Média aritmética |
| `mediana` | `float64` | Valor central da distribuição |
| `desvio_padrao` | `float64` | Dispersão dos valores |
| `min` | `float64` | Menor valor observado |
| `q25` | `float64` | Primeiro quartil (25%) |
| `q75` | `float64` | Terceiro quartil (75%) |
| `max` | `float64` | Maior valor observado |
| `assimetria` | `float64` | Assimetria da distribuição; positiva = cauda à direita, negativa = cauda à esquerda |
| `curtose` | `float64` | Excesso de curtose; valores altos sugerem caudas mais pesadas/eventos extremos mais frequentes |

---

# 18. Métricas de qualidade e cobertura

## `quality_report.csv`

| Variável | Tipo | Significado |
|---|---|---|
| `column` | `string` | Nome da coluna avaliada |
| `rows` | `int64` | Total de linhas |
| `non_null` | `int64` | Quantidade de valores não nulos |
| `missing` | `int64` | Quantidade de valores ausentes |
| `missing_pct` | `float64` | Percentual de valores ausentes |
| `min` | `float64` | Menor valor da coluna |
| `max` | `float64` | Maior valor da coluna |

## Tabela `coverage` da EDA

| Variável | Tipo | Significado |
|---|---|---|
| `variavel` | `string` | Nome da série |
| `inicio` | `datetime64[ns]` | Primeira data com valor válido |
| `fim` | `datetime64[ns]` | Última data com valor válido |
| `observacoes` | `int64` | Quantidade de valores válidos |
| `missing` | `int64` | Quantidade de valores ausentes |
| `cobertura_pct` | `float64` | Percentual da janela com dados válidos |

---

# 19. Resumo das features candidatas ao primeiro modelo de regime

O notebook considera inicialmente as seguintes features, quando disponíveis:

| Feature | Família | Interpretação principal |
|---|---|---|
| `ibc_br_change` | Atividade | Crescimento ou queda da atividade econômica |
| `selic` | Juros | Nível da política monetária |
| `selic_change` | Juros | Direção da política monetária |
| `usd_brl_return` | Câmbio | Valorização/desvalorização mensal do dólar |
| `usd_brl_volatility` | Câmbio | Instabilidade cambial |
| `ipca_12m` | Inflação | Persistência inflacionária |
| `pib_change_3m` | Atividade | Expansão ou retração econômica |
| `unemployment` | Trabalho | Nível de desemprego |
| `unemployment_change` | Trabalho | Deterioração ou melhora do desemprego |

A seleção final deve considerar disponibilidade temporal, redundância, multicolinearidade, interpretabilidade e risco de overfitting.

---

# 20. Convenções de nomenclatura

| Sufixo / prefixo | Significado |
|---|---|
| `_change` | Diferença ou mudança em relação a período anterior |
| `_return_1m` | Retorno percentual de 1 mês |
| `_return_3m` | Retorno percentual em relação a 3 meses antes |
| `_volatility_3m_ann` | Volatilidade móvel de 3 meses anualizada |
| `_drawdown` | Queda percentual em relação ao maior nível histórico anterior |
| `_stress_z` | Componente padronizado e orientado para que maior valor represente maior stress |
| `score_` | Componente normalizado do índice exploratório de resiliência |
| `_pct` | Percentual ou proporção apresentada em percentual |

---

# 21. Cuidados de interpretação

1. **Correlação não significa causalidade.** Pearson e Spearman medem associação.
2. **Retorno positivo não significa baixo risco.** Um setor pode apresentar retorno elevado e grande volatilidade/drawdown.
3. **Volatilidade não possui sinal econômico positivo/negativo.** Quanto maior, maior a dispersão dos retornos.
4. **Drawdown é normalmente zero ou negativo.** Quanto mais negativo, maior a perda em relação ao pico anterior.
5. **Stress Score é relativo à amostra.** Ele depende da média e do desvio padrão observados na própria base.
6. **`stress_level` e `regime_eda` são classificações exploratórias.** Não são ainda o target definitivo de ML.
7. **`resilience_score_100` é um ranking relativo.** Não representa probabilidade, recomendação de investimento ou garantia de desempenho futuro.
8. **Lags econômicos e lags de disponibilidade são conceitos diferentes.** O primeiro investiga relação temporal; o segundo reduz look-ahead bias.
9. **Outliers não devem ser removidos automaticamente.** Em um estudo de stress, eles podem representar os eventos mais relevantes.
10. **As séries possuem coberturas diferentes.** Análises devem remover `NaN` apenas das variáveis realmente necessárias para cada cálculo.

---

# 22. Fluxo conceitual dos dados

```text
BCB / IBGE / B3
      |
      v
Dados brutos (raw)
      |
      v
Pré-processamento mensal
      |
      +--> dataset_monthly_reference.csv --> EDA histórica
      |
      +--> dataset_mvp.csv ---------------> features com defasagens
      |
      +--> dataset_mvp_complete.csv ------> análises que exigem todas as séries

Macroeconomia / dados socioeconômicos
      |
      v
Stress Score exploratório
      |
      v
Normal / Stress
      |
      v
Retorno + volatilidade + drawdown + recuperação
      |
      v
Índice exploratório de resiliência setorial
```

---

# 23. Arquivos relacionados

```text
data/raw/
data/processed/bcb_monthly.csv
data/processed/ibge_monthly_reference.csv
data/processed/b3_monthly.csv
data/curated/dataset_monthly_reference.csv
data/curated/dataset_mvp.csv
data/curated/dataset_mvp_complete.csv
data/curated/quality_report.csv
notebooks/EDA_MVP_Resiliencia.ipynb
src/preprocess_mvp.py
```

Este dicionário deve ser atualizado sempre que uma nova variável persistente, feature ou regra de cálculo for adicionada ao pipeline.
