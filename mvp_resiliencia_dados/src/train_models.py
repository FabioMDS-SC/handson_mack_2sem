"""Train and compare the baseline classifiers for the stress regime."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from prepare_ml_features import FEATURE_COLUMNS, project_root


def metrics_for(model, x, y, split: str, name: str) -> dict:
    prediction = model.predict(x)
    probability = model.predict_proba(x)[:, 1]
    return {
        "modelo": name,
        "split": split,
        "accuracy": accuracy_score(y, prediction),
        "precision": precision_score(y, prediction, zero_division=0),
        "recall": recall_score(y, prediction, zero_division=0),
        "f1": f1_score(y, prediction, zero_division=0),
        "roc_auc": roc_auc_score(y, probability),
        "observacoes": len(y),
        "stress": int(y.sum()),
    }


def build_models() -> dict:
    preprocessing = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
    return {
        "logistic_regression": Pipeline(
            preprocessing
            + [
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=42,
                    ),
                )
            ]
        ),
        "random_forest": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=4,
                        min_samples_leaf=4,
                        class_weight="balanced",
                        random_state=42,
                        # n_jobs=1 mantém a execução portátil em Windows e
                        # evita criar processos desnecessários nesta amostra.
                        n_jobs=1,
                    ),
                ),
            ]
        ),
    }


def main() -> None:
    root = project_root()
    data = pd.read_csv(
        root / "data" / "curated" / "dataset_ml_features.csv",
        parse_dates=["date"],
    )
    x = data[FEATURE_COLUMNS]
    y = data["target_stress"]
    train = data["split"] == "train"
    validation = data["split"] == "validation"
    test = data["split"] == "test"

    models = build_models()
    rows = []
    for name, model in models.items():
        model.fit(x[train], y[train])
        rows.append(metrics_for(model, x[train], y[train], "train", name))
        rows.append(metrics_for(model, x[validation], y[validation], "validation", name))

    validation_metrics = pd.DataFrame(rows)
    ranking = validation_metrics[validation_metrics["split"] == "validation"].sort_values(
        ["f1", "roc_auc", "recall"], ascending=False
    )
    selected_name = ranking.iloc[0]["modelo"]

    selected = clone(models[selected_name])
    train_validation = train | validation
    selected.fit(x[train_validation], y[train_validation])
    rows.append(metrics_for(selected, x[test], y[test], "test", selected_name))

    output_dir = root / "model_artifacts"
    output_dir.mkdir(exist_ok=True)
    joblib.dump(selected, output_dir / "model_final.joblib")
    comparison = pd.DataFrame(rows)
    comparison["modelo_escolhido"] = selected_name
    comparison.to_csv(
        root / "data" / "curated" / "model_comparison.csv", index=False
    )
    print(comparison.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print(f"Modelo escolhido pela validação: {selected_name}")


if __name__ == "__main__":
    main()
