"""Generate evaluation artifacts for the selected model on the untouched test set."""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, confusion_matrix

from prepare_ml_features import FEATURE_COLUMNS, project_root


def main() -> None:
    root = project_root()
    data = pd.read_csv(
        root / "data" / "curated" / "dataset_ml_features.csv",
        parse_dates=["date"],
    )
    test = data[data["split"] == "test"].copy()
    model = joblib.load(root / "model_artifacts" / "model_final.joblib")
    x_test = test[FEATURE_COLUMNS]
    y_test = test["target_stress"]
    prediction = model.predict(x_test)
    probability = model.predict_proba(x_test)[:, 1]

    report_dir = root / "reports" / "entrega3"
    report_dir.mkdir(parents=True, exist_ok=True)
    predictions = test[["date", "target_stress"]].copy()
    predictions["prediction"] = prediction
    predictions["probability_stress"] = probability
    predictions.to_csv(report_dir / "test_predictions.csv", index=False, date_format="%Y-%m-%d")

    cm = confusion_matrix(y_test, prediction)
    cm_table = pd.DataFrame(
        cm,
        index=["real_0_normal", "real_1_stress"],
        columns=["pred_0_normal", "pred_1_stress"],
    )
    cm_table.to_csv(report_dir / "confusion_matrix.csv")

    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(cm, display_labels=["Normal", "Stress"]).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Matriz de confusão - conjunto de teste")
    fig.tight_layout()
    fig.savefig(report_dir / "confusion_matrix.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    RocCurveDisplay.from_predictions(y_test, probability, ax=ax)
    ax.set_title("Curva ROC - conjunto de teste")
    fig.tight_layout()
    fig.savefig(report_dir / "roc_curve.png", dpi=160)
    plt.close(fig)

    importance = permutation_importance(
        model,
        x_test,
        y_test,
        scoring="f1",
        n_repeats=30,
        random_state=42,
    )
    importance_table = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)
    importance_table.to_csv(report_dir / "feature_importance.csv", index=False)

    print(f"Artefatos salvos em: {report_dir}")
    print(cm_table.to_string())
    print(importance_table.to_string(index=False))


if __name__ == "__main__":
    main()
