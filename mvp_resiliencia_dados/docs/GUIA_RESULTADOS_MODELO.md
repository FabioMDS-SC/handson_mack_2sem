# Guia de resultados, scores e decisões do modelo

## 1. Problema

O problema foi definido como classificação binária temporal:

```text
condições conhecidas no mês t -> stress no mês t+1
```

O objetivo não é prever o retorno de um ativo nem recomendar compra ou venda.

## 2. Stress Score

O `stress_score` é um indicador exploratório composto por z-scores. Cada
componente recebe uma direção para que valores maiores representem maior stress.

| Componente | Direção | Justificativa |
|---|---:|---|
| `ibc_br_change` | -1 | Queda da atividade aumenta o stress. |
| `selic_change` | +1 | Alta de juros pode representar aperto monetário. |
| `usd_brl_return` | +1 | Alta do dólar representa pressão cambial. |
| `usd_brl_volatility` | +1 | Maior instabilidade indica risco elevado. |
| `ipca_12m` | +1 | Inflação persistente aumenta a pressão macroeconômica. |
| `unemployment_change` | +1 | Aumento do desemprego indica deterioração. |
| `pib_change_3m` | -1 | Contração da atividade aumenta o stress. |

O score é a média dos componentes disponíveis. Ele não é um índice oficial de
crise nem uma variável financeira padronizada.

## 3. Por que foi usado o P75

Foram considerados P75, P80 e P90. O P75 foi escolhido para o baseline porque
produz aproximadamente 25% de eventos, fornece mais exemplos para treinamento
e evita o número muito pequeno de eventos esperado no P90.

O resultado possui 175 observações válidas: 44 eventos de stress e 131 normais.
O último mês foi removido porque não existe mês seguinte conhecido.

Limitação: score e percentil ainda são calculados sobre todo o histórico. Uma
versão rigorosa deve calcular esses parâmetros somente com o período de treino.

## 4. Features utilizadas

Foram escolhidas nove features macroeconômicas:

`ibc_br_change`, `selic`, `selic_change`, `usd_brl_return`,
`usd_brl_volatility`, `ipca_12m`, `pib_change_3m`, `unemployment` e
`unemployment_change`.

Retornos setoriais, drawdown e `resilience_score_100` não foram usados como
features do classificador porque pertencem à análise de mercado/resiliência e
podem introduzir informação contemporânea ou circularidade.

## 5. Divisão temporal

Foi evitado o split aleatório porque os meses formam uma sequência temporal.

| Parte | Período | Linhas | Stress |
|---|---|---:|---:|
| Treino | 2012-09 a 2018-12 | 76 | 26 |
| Validação | 2019-01 a 2020-12 | 24 | 7 |
| Teste | 2021-01 a 2026-07 | 67 | 11 |

## 6. Modelos

### Regressão Logística

É o baseline interpretável para uma amostra pequena. A padronização facilita a
comparação das features e `class_weight="balanced"` reduz o viés para a classe
normal.

### Random Forest

Foi usado como alternativa capaz de representar relações não lineares. A
profundidade e o tamanho mínimo das folhas foram limitados para reduzir
overfitting.

## 7. Métricas e justificativa

| Métrica | Uso |
|---|---|
| Accuracy | Visão geral, mas insuficiente sozinha com desbalanceamento. |
| Precision | Mede quantos alertas de stress estavam corretos. |
| Recall | Mede quantos eventos foram encontrados; é importante neste projeto. |
| F1-score | Equilibra precision e recall para escolha do baseline. |
| ROC-AUC | Avalia a ordenação das probabilidades em vários thresholds. |

A escolha priorizou F1, depois ROC-AUC e recall na validação, evitando escolher
um modelo somente por accuracy.

## 8. Resultados

| Modelo | F1 validação | ROC-AUC validação |
|---|---:|---:|
| Regressão Logística | 0,20 | 0,61 |
| Random Forest | 0,00 | 0,73 |

A Regressão Logística foi selecionada por ter melhor F1 na validação.

No teste:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0,76 |
| Precision | 0,22 |
| Recall | 0,18 |
| F1-score | 0,20 |
| ROC-AUC | 0,67 |

O modelo identificou somente 2 dos 11 eventos de stress. Portanto, existe
algum sinal, mas ele é limitado e instável.

## 9. Score de resiliência setorial

O `resilience_score_100` da EDA não foi usado como target nem como feature. Ele
é uma síntese descritiva relativa entre setores, baseada em retorno,
volatilidade, perdas, drawdown e recuperação durante períodos de stress.

Ele ajuda a responder qual setor pareceu mais resiliente na amostra, mas não
mede probabilidade de ganho e não substitui validação estatística.

## 10. Melhorias prioritárias

1. Calcular score e threshold somente dentro de cada janela de treino.
2. Usar expanding window ou walk-forward validation.
3. Ajustar o threshold de decisão para testar maior recall.
4. Aumentar o histórico e revisar os eventos rotulados.
5. Calibrar probabilidades antes de transformar o resultado em alerta.
