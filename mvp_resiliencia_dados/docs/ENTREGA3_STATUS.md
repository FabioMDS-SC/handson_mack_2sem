# Status da Entrega 3

Todas as waves planejadas foram executadas e validadas:

| Wave | Entrega | Status |
|---|---|---|
| 1 | Target reproduzível e validações | Concluída |
| 2 | Features e divisão temporal | Concluída |
| 3 | Regressão Logística e Random Forest | Concluída |
| 4 | Métricas, gráficos e relatório | Concluída |
| 5 | Inferência com modelo persistido | Concluída |

Comandos de reprodução:

```powershell
python src/build_ml_target.py
python src/prepare_ml_features.py
python src/train_models.py
python src/evaluate_model.py
python src/predict_stress.py data/curated/dataset_ml_features.csv reports/entrega3/inference_sample.csv
```

Resultado atual: a Regressão Logística é o baseline selecionado, mas possui
recall de 0,18 no teste. O projeto atende à estrutura da Entrega 3, porém o
modelo deve ser apresentado como baseline exploratório, não como solução
produtiva ou recomendação financeira.
