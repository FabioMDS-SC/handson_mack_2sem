# Checklist final da Entrega 3

Referência: `docs/HandsOn_Eng_Dados_Aula4.pdf`.

| Item solicitado | Evidência | Status |
|---|---|---|
| Dataset final para modelagem | `data/curated/dataset_ml_features.csv` | Atendido |
| Features selecionadas e target | `src/prepare_ml_features.py` e `src/build_ml_target.py` | Atendido |
| Código de treinamento | `src/train_models.py` | Atendido |
| Validação temporal | `data/curated/ml_split_summary.csv` | Atendido |
| Comparação de modelos | `data/curated/model_comparison.csv` | Atendido |
| Métricas | Accuracy, precision, recall, F1 e ROC-AUC | Atendido |
| Matriz de confusão | `reports/entrega3/confusion_matrix.png` | Atendido |
| Curva ROC | `reports/entrega3/roc_curve.png` | Atendido |
| Importância das features | `reports/entrega3/feature_importance.csv` | Atendido |
| Pipeline de inferência | `src/predict_stress.py` | Atendido |
| Modelo persistido | `model_artifacts/model_final.joblib` | Atendido |
| Documentação técnica | `docs/RELATORIO_ENTREGA3.md` | Atendido |
| Plano de implantação | Opcional no PDF | Não necessário |

## Execução completa

```powershell
python src/build_ml_target.py
python src/prepare_ml_features.py
python src/train_models.py
python src/evaluate_model.py
python src/predict_stress.py data/curated/dataset_ml_features.csv caminho\saida.csv
```

## Observação importante

A entrega está completa em termos de artefatos e fluxo, mas o modelo final é
um baseline exploratório. O recall de 0,18 no teste indica que ele ainda não é
adequado para decisões financeiras ou operação em produção.
