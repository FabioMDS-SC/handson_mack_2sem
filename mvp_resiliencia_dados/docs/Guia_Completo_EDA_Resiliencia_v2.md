# Guia Completo da EDA

## Oportunidades em meio ao Caos

*Dicionário de indicadores, cálculos, interpretação e análise de resiliência*

Versão atualizada com Stress Score, defasagens, correlação por regime, recuperação e índice exploratório de resiliência.

## 1. Como ler a EDA

A Análise Exploratória de Dados (EDA) é a etapa em que verificamos a
qualidade da base, entendemos o comportamento das variáveis e levantamos
hipóteses antes de treinar qualquer modelo. No projeto, ela conecta o
cenário macroeconômico com o comportamento do Ibovespa e dos índices
setoriais IFNC, ICON e IEE.

| **Grupo**     | **Pergunta principal**                                           | **Exemplos**                                        |
|---------------|------------------------------------------------------------------|-----------------------------------------------------|
| Qualidade     | Os dados estão completos e consistentes?                         | Missing, duplicidades, cobertura temporal           |
| Macroeconomia | Como está o ambiente econômico?                                  | IBC-Br, Selic, dólar, IPCA, PIB, desemprego         |
| Mercado       | Como os setores se comportaram?                                  | Retorno, volatilidade, drawdown, recuperação        |
| Relações      | As variáveis se movem juntas ou com atraso?                      | Pearson, Spearman, lags 0/1/3/6                     |
| Resiliência   | Qual setor preservou melhor retorno e risco nos meses de Stress? | Retorno, perdas, drawdown, recuperação, score 0–100 |

Regra de interpretação: um valor matematicamente positivo não significa
necessariamente uma situação econômica positiva. O sinal indica direção;
o significado depende da variável e do contexto.

## 2. Dicionário dos indicadores macroeconômicos

| **Variável**        | **O que mede**                 | **Cálculo/Origem**                         | **Interpretação**                                                             |
|---------------------|--------------------------------|--------------------------------------------|-------------------------------------------------------------------------------|
| ibc_br              | Nível do IBC-Br                | Atividade econômica                        | Nível maior sugere atividade mais forte; interpretar junto da tendência.      |
| ibc_br_change       | Variação percentual mensal     | (IBC_t / IBC_t-1) - 1                      | \> 0: expansão/aceleração; \< 0: retração/desaceleração.                      |
| selic               | Meta Selic no fim do mês       | Último valor do mês                        | Nível alto = política monetária mais restritiva; não é bom/ruim isoladamente. |
| selic_change        | Mudança em pontos percentuais  | Selic_t - Selic_t-1                        | \> 0: juros subindo; \< 0: juros caindo.                                      |
| usd_brl             | Cotação do dólar               | Último valor do mês                        | Maior valor = dólar mais caro / real mais fraco.                              |
| usd_brl_return      | Retorno mensal do dólar        | (USD_t / USD_t-1) - 1                      | \> 0: dólar valorizou; \< 0: dólar caiu.                                      |
| usd_brl_volatility  | Oscilação cambial              | desvio padrão dos retornos diários × √21   | Quanto maior, mais instável o câmbio. Não possui interpretação por sinal.     |
| ipca_month          | Inflação mensal                | Valor oficial do mês                       | \> 0: inflação; \< 0: deflação.                                               |
| ipca_12m            | Inflação acumulada em 12 meses | Série oficial acumulada                    | Nível alto indica inflação persistente.                                       |
| pib_index           | Índice trimestral do PIB       | Série trimestral propagada na grade mensal | Nível da atividade agregada; não interpretar isoladamente como crescimento.   |
| pib_change_3m       | Mudança em 3 meses             | (PIB_t / PIB_t-3) - 1                      | \> 0: expansão; \< 0: contração.                                              |
| unemployment        | Taxa de desemprego             | Taxa de desocupação                        | Maior tende a representar pior condição do mercado de trabalho.               |
| unemployment_change | Mudança do desemprego          | Desemprego_t - Desemprego_t-1              | \> 0: desemprego aumentando; \< 0: desemprego diminuindo.                     |

## 3. Dicionário dos indicadores de mercado

Os índices em pontos são úteis para acompanhar a trajetória, mas a
comparação entre setores é feita principalmente pelas medidas derivadas.

| **Variável**                 | **O que mede**               | **Fórmula**                           | **Como interpretar**                                                                         |
|------------------------------|------------------------------|---------------------------------------|----------------------------------------------------------------------------------------------|
| ibovespa / ifnc / icon / iee | Nível do índice              | Pontos                                | Usado para trajetória e cálculo das métricas; não comparar níveis diretamente entre índices. |
| \*\_return_1m                | Retorno mensal               | (Índice_t / Índice_t-1) - 1           | \> 0: valorização; \< 0: queda.                                                              |
| \*\_return_3m                | Retorno em três meses        | (Índice_t / Índice_t-3) - 1           | Mostra tendência de curto prazo menos sensível a um único mês.                               |
| \*\_volatility_3m_ann        | Volatilidade anualizada      | std(retornos mensais, janela 3) × √12 | Maior = maior oscilação/risco. Menor = maior estabilidade.                                   |
| \*\_drawdown                 | Distância em relação ao pico | Índice_t / máximo acumulado_t - 1     | 0 = no pico; valores mais negativos = perda mais profunda.                                   |

## 4. Estatística descritiva

| **Métrica**       | **Significado**                   | **Leitura**                                                           |
|-------------------|-----------------------------------|-----------------------------------------------------------------------|
| n                 | Quantidade de observações válidas | Maior n significa maior cobertura; comparar entre variáveis.          |
| média             | Valor médio                       | Sensível a extremos.                                                  |
| mediana           | Valor central                     | Mais robusta a outliers; diferença grande da média sugere assimetria. |
| desvio padrão     | Dispersão                         | Maior = maior variabilidade.                                          |
| q25 / q75         | Quartis                           | Definem a faixa central e ajudam no IQR.                              |
| assimetria / skew | Formato da distribuição           | \>0 cauda direita; \<0 cauda esquerda; ~0 mais simétrica.             |
| curtose           | Peso das caudas                   | No pandas, normal ~0; valor alto sugere mais eventos extremos.        |

## 5. Outliers, correlação e sazonalidade

### 5.1 Outliers pelo IQR

A regra utilizada considera como potencial outlier valores fora de Q1 -
1,5×IQR e Q3 + 1,5×IQR, onde IQR = Q3 - Q1. No projeto, outlier não é
sinônimo de erro: crises e choques podem gerar justamente os valores
mais relevantes.

### 5.2 Pearson e Spearman

| **Métrica** | **O que identifica**                  | **Interpretação**                                                    |
|-------------|---------------------------------------|----------------------------------------------------------------------|
| Pearson     | Relação linear                        | Vai de -1 a +1. Sinal mostra direção; magnitude mostra força linear. |
| Spearman    | Relação monotônica baseada em ranking | Útil quando a relação não é perfeitamente linear ou há extremos.     |

Correlação não prova causalidade. Exemplo: uma correlação negativa entre
dólar e ICON indica associação histórica, não prova que o dólar causou a
queda do setor.

### 5.3 Sazonalidade

O notebook agrupa retornos por mês do ano para observar se janeiro,
fevereiro etc. apresentam comportamento diferente. Como o histórico é
relativamente curto, qualquer padrão sazonal deve ser tratado como
hipótese e não como regra.

## 6. Stress Score exploratório

A versão atual do notebook constrói um indicador exploratório de Stress
a partir de várias variáveis macroeconômicas. Ele não é o target
definitivo do futuro modelo; serve para organizar a EDA e comparar o
comportamento dos setores em ambientes mais adversos.

| **Componente**      | **Direção de Stress** | **Interpretação**                             |
|---------------------|-----------------------|-----------------------------------------------|
| ibc_br_change       | -1                    | Queda da atividade aumenta o score.           |
| selic_change        | +1                    | Alta de juros aumenta o score.                |
| usd_brl_return      | +1                    | Valorização do dólar aumenta o score.         |
| usd_brl_volatility  | +1                    | Maior instabilidade cambial aumenta o score.  |
| ipca_12m            | +1                    | Inflação acumulada mais alta aumenta o score. |
| unemployment_change | +1                    | Aumento do desemprego aumenta o score.        |
| pib_change_3m       | -1                    | Contração do PIB aumenta o score.             |

### 6.1 Padronização por z-score

> z = (x - média) / desvio_padrão

O z-score coloca variáveis de escalas diferentes em uma medida
comparável. z = 0 significa próximo da média; z positivo significa acima
da média; z negativo significa abaixo. Depois, o notebook multiplica por
+1 ou -1 conforme a direção econômica de Stress.

### 6.2 Score final e níveis

> stress_score = média dos componentes stress_z disponíveis

O notebook usa percentis da própria distribuição: acima do percentil 90
= Stress elevado; entre os percentis 75 e 90 = Atenção; abaixo do
percentil 75 = Normal. Em análises binárias posteriores, meses acima do
percentil 75 são tratados exploratoriamente como Stress.

Importante: como o Stress Score atual é construído sobre o dataset MVP
com lags de disponibilidade, ele representa uma visão ajustada ao que
estaria conhecido naquele momento. Não deve ser confundido com um índice
oficial de crise.

## 7. Análise de defasagens macroeconômicas

A nova seção 14 verifica se um indicador macroeconômico se relaciona com
o retorno do setor no mesmo mês ou com atraso. São analisados lags de 0,
1, 3 e 6 meses.

| **lag_meses** | **Comparação**          | **Interpretação**                              |
|---------------|-------------------------|------------------------------------------------|
| 0             | macro(t) × retorno(t)   | Relação contemporânea.                         |
| 1             | macro(t-1) × retorno(t) | Indicador macro antecede o retorno em 1 mês.   |
| 3             | macro(t-3) × retorno(t) | Indicador macro antecede o retorno em 3 meses. |
| 6             | macro(t-6) × retorno(t) | Indicador macro antecede o retorno em 6 meses. |

Para esta análise exploratória, as variações macro são calculadas no
dataset de referência. Isso evita aplicar um novo lag sobre uma variável
que já foi defasada para modelagem. O resultado continua sendo
associação estatística e não evidência de causalidade.

A tabela guarda Pearson e Spearman, além dos valores absolutos. O maior
valor absoluto é usado apenas para destacar a defasagem com associação
mais forte em cada par macro × setor; isso não significa que esse lag
deva ser adotado automaticamente no modelo.

## 8. Correlação por regime

As relações são recalculadas em três grupos: Todos, Normal e Stress. O
objetivo é verificar se a associação muda em períodos adversos. Uma
correlação que aparece apenas em Stress pode indicar comportamento
dependente do regime, mas precisa de cautela porque o número de meses de
Stress é menor.

## 9. Drawdown e velocidade de recuperação

### 9.1 Drawdown

> drawdown(t) = índice(t) / máximo_histórico_até_t - 1

Quanto mais negativo, maior a perda em relação ao pico. Na versão
corrigida, o drawdown durante Stress é o pior drawdown histórico
observado em meses classificados como Stress. Não são concatenados meses
de Stress não consecutivos para montar uma série artificial.

### 9.2 Tempo de recuperação

Para cada índice, o notebook identifica o pior drawdown histórico, o
pico anterior e o primeiro mês em que o índice volta ao nível daquele
pico. A diferença em meses é `meses_para_recuperar`. Menor tempo
sugere recuperação mais rápida.

Na versão atual, essa métrica considera o pior drawdown do histórico
completo, e não apenas episódios de Stress. Por isso ela entra no índice
de resiliência como componente exploratório complementar.

## 10. Índice exploratório de resiliência

A nova seção 18 cria um ranking relativo entre os setores nos meses
classificados como Stress. O índice não é uma métrica financeira oficial
e não substitui Sharpe, Sortino ou uma validação estatística. Ele
organiza várias dimensões de resiliência em uma escala comum.

| **Componente**             | **Melhor direção**     | **O que representa**                                 |
|----------------------------|------------------------|------------------------------------------------------|
| retorno_medio_stress       | Maior                  | Desempenho médio nos meses de Stress.                |
| volatilidade_stress        | Menor                  | Estabilidade dos retornos nos meses de Stress.       |
| percentual_negativo_stress | Menor                  | Frequência de meses com perda.                       |
| pior_mes_stress            | Maior / menos negativo | Severidade da pior perda mensal.                     |
| drawdown_stress            | Maior / menos negativo | Profundidade da queda em relação ao pico.            |
| tempo_recuperacao          | Menor                  | Velocidade para recuperar o pior drawdown histórico. |

### 10.1 Normalização Min-Max

> score = (x - mínimo) / (máximo - mínimo)

Para métricas em que menor é melhor, o notebook usa `1 - score`. Assim
todos os componentes ficam na direção “maior = melhor”. Como existem
poucos setores, o score é relativo ao conjunto comparado e pode mudar se
novos setores forem adicionados.

### 10.2 Score final

> resilience_score = média simples dos scores disponíveis  
> resilience_score_100 = resilience_score × 100

Todos os componentes têm o mesmo peso nesta versão. Um valor de 100 não
significa “sem risco”; significa melhor posição relativa nos critérios
usados. O ranking é exploratório e deve ser validado em etapas futuras.

## 11. Ajustes técnicos realizados na versão atual

| **Problema**                                | **Causa**                                                                           | **Correção**                                                                                                           |
|---------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Nenhum setor encontrado na seção 14         | Código procurava `ifnc_return`, `icon_return` etc.                              | Usar os nomes reais `\*\_return_1m`.                                                                                 |
| Algumas variáveis macro ausentes em ref_eda | Variações eram criadas apenas no dataset MVP.                                       | Recalcular `ibc_br_change`, `unemployment_change` e `pib_change_3m` na base de referência para a análise de lag. |
| Merge do tempo de recuperação               | `recovery_table` possui coluna `indice`, não `setor`.                         | Criar uma chave compatível antes do merge.                                                                             |
| Drawdown em Stress artificial               | Meses de Stress não consecutivos eram acumulados como se fossem sequência contínua. | Usar o drawdown histórico observado nos meses de Stress.                                                               |

## 12. Qual dataset usar em cada etapa

| **Dataset**                   | **Uso principal**                                        | **Cuidado**                                                                          |
|-------------------------------|----------------------------------------------------------|--------------------------------------------------------------------------------------|
| dataset_monthly_reference.csv | EDA histórica, gráficos e relações por mês de referência | Pode conter informação econômica que só foi divulgada posteriormente.                |
| dataset_mvp.csv               | Preparação das features para modelagem                   | Já contém lags de disponibilidade; não aplicar novos lags sem definir o significado. |
| dataset_mvp_complete.csv      | Análises que exigem todas as séries completas            | Reduz a amostra por causa das séries com menor histórico.                            |

## 13. Como interpretar “positivo” e “negativo”

| **Exemplo**         | **Sinal positivo significa**           | **Sinal negativo significa**     |
|---------------------|----------------------------------------|----------------------------------|
| ibc_br_change       | atividade aumentando                   | atividade caindo                 |
| selic_change        | juros subindo                          | juros caindo                     |
| usd_brl_return      | dólar valorizando / real enfraquecendo | dólar caindo / real fortalecendo |
| unemployment_change | desemprego aumentando                  | desemprego diminuindo            |
| retorno setorial    | valorização                            | queda                            |
| drawdown            | normalmente 0 no pico                  | queda em relação ao pico         |

A interpretação econômica depende da combinação. Exemplo: Selic subindo
pode ser ruim para crédito e consumo, mas a motivação da alta pode ser
combater inflação; dólar subindo pode sinalizar aversão a risco, mas
beneficiar exportadores.

## 14. O que ainda é exploratório

- O Stress Score não é um índice oficial e ainda não é o target
  definitivo do modelo.

- Os percentis 75 e 90 são critérios exploratórios e precisam de
  validação.

- A correlação com defasagem não prova causalidade e pode ser instável
  com uma amostra pequena.

- O índice de resiliência usa pesos iguais e normalização relativa entre
  poucos setores.

- O tempo de recuperação ainda é calculado sobre o pior drawdown
  histórico total, não por episódio de Stress.

- A futura modelagem deverá usar validação temporal e controlar
  overfitting.

## 15. Fluxo conceitual final

> Macroeconomia  
> ↓  
> Stress Score exploratório / futuro modelo de regime  
> ↓  
> Normal x Stress  
> ↓  
> Retornos + volatilidade + drawdown + recuperação  
> ↓  
> Índice exploratório de resiliência  
> ↓  
> Hipóteses para validação futura

A EDA não tem como objetivo provar que um setor é sempre melhor. Ela
mostra como os dados se comportam, onde existem relações interessantes e
quais hipóteses merecem ser testadas na modelagem e na validação futura.
