# Relatório da Entrega 3 - Aplicação de ML

## Problema

Prever se o mês seguinte será classificado como `Stress`, usando condições
macroeconômicas disponíveis até o mês atual. O target foi construído como
`X(t) -> Stress(t+1)`.

## Dados e divisão

- Fonte: `data/curated/dataset_mvp.csv`.
- Features: IBC-Br, Selic, variação da Selic, retorno e volatilidade cambial,
  IPCA acumulado, variação do PIB e desemprego.
- Dataset final: 167 observações completas.
- Treino: 2012-09 a 2018-12, 76 observações, 26 stress.
- Validação: 2019-01 a 2020-12, 24 observações, 7 stress.
- Teste: 2021-01 a 2026-07, 67 observações, 11 stress.

A divisão respeita a ordem temporal. Não foi usado embaralhamento.

## Modelos comparados

| Modelo | F1 validação | ROC-AUC validação |
|---|---:|---:|
| Regressão Logística | 0,20 | 0,61 |
| Random Forest | 0,00 | 0,73 |

A Regressão Logística foi escolhida por apresentar melhor F1 na validação.
Depois da escolha, foi ajustada novamente usando treino + validação.

## Resultado no teste

- Accuracy: 0,76.
- Precision: 0,22.
- Recall: 0,18.
- F1: 0,20.
- ROC-AUC: 0,67.

Matriz de confusão:

| Real / Predito | Normal | Stress |
|---|---:|---:|
| Normal | 49 | 7 |
| Stress | 9 | 2 |

O recall baixo mostra que o modelo deixou de identificar 9 dos 11 eventos de
stress no teste. Portanto, o modelo é um baseline acadêmico e ainda não deve
ser usado para decisão financeira ou operacional.

## Artefatos

- Comparação: `data/curated/model_comparison.csv`.
- Modelo: `model_artifacts/model_final.joblib`.
- Predições: `reports/entrega3/test_predictions.csv`.
- Matriz: `reports/entrega3/confusion_matrix.png`.
- ROC: `reports/entrega3/roc_curve.png`.
- Importância: `reports/entrega3/feature_importance.csv`.

## Limitações e melhorias

- A amostra mensal é pequena.
- Eventos de stress são concentrados em poucos períodos.
- O target P75 é exploratório.
- O score e o percentil ainda são calculados sobre todo o histórico; uma
  próxima versão deve calcular esses parâmetros somente dentro do treino.
- O threshold de decisão pode ser calibrado para priorizar recall.
- É necessário testar validação temporal em janela móvel antes de concluir
  sobre generalização.
