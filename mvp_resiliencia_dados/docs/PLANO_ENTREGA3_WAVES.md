# Plano de implementação da Entrega 3

Este documento registra a evolução da parte de Machine Learning em waves. Cada
wave deve ser executada, testada e documentada antes da próxima.

## Wave 1 - Dataset e target

Status: concluída.

- Dataset de entrada: `data/curated/dataset_mvp.csv`.
- Target: `target_stress = 1` quando o `stress_score` do mês seguinte está no
  percentil 75 ou acima.
- A última observação é removida porque não possui mês seguinte conhecido.
- Script reprodutível: `python src/build_ml_target.py`.
- Saída: `data/curated/dataset_ml_target.csv`.

Validações mínimas:

- datas ordenadas e únicas;
- target sem valores ausentes;
- somente classes 0 e 1;
- presença das duas classes.

Observação metodológica: nesta wave o score e o percentil ainda são calculados
sobre todo o histórico. A validação temporal e o cálculo sem informação futura
serão tratados na Wave 2/3.

## Wave 2 - Features e divisão temporal

Status: concluída.

Criar o conjunto de features macroeconômicas, excluir colunas que representam
o futuro e separar treino, validação e teste sem embaralhamento.

Features iniciais: `ibc_br_change`, `selic`, `selic_change`, `usd_brl_return`,
`usd_brl_volatility`, `ipca_12m`, `pib_change_3m`, `unemployment` e
`unemployment_change`.

Script: `python src/prepare_ml_features.py`.

Saídas: `data/curated/dataset_ml_features.csv` e
`data/curated/ml_split_summary.csv`.

Como a divisão percentual 70/15/15 colocou o teste em um período sem nenhum
evento de stress, os cortes finais foram definidos por calendário: treino até
2018-12, validação de 2019-01 a 2020-12 e teste a partir de 2021-01. Essa
decisão preserva eventos nas três partes e mantém a ordem temporal.

## Wave 3 - Treinamento e comparação

Status: em implementação.

Treinar Regressão Logística e Random Forest, usando as mesmas partições e
comparando accuracy, precision, recall, F1 e ROC-AUC.

Script: `python src/train_models.py`.

O modelo é escolhido pela validação, priorizando F1, ROC-AUC e recall nessa
ordem. Depois da escolha, ele é refeito com treino + validação e avaliado uma
única vez no teste.

## Wave 4 - Avaliação e documentação

Status: em implementação.

Gerar matriz de confusão, curva ROC, importância das features, tabela de
comparação e justificativa técnica/de negócio para a escolha do modelo.

Script: `python src/evaluate_model.py`.

Saída esperada: `reports/entrega3/` com previsões do teste, matriz de confusão,
curva ROC e importância por permutação.

## Wave 5 - Inferência e fechamento

Criar rotina para aplicar o modelo a dados novos, documentar limitações,
dependências, monitoramento e atualização do modelo.
