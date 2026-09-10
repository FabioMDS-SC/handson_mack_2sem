"""Apply the persisted stress model to a CSV containing regime features."""

import argparse
from pathlib import Path

import joblib
import pandas as pd

from prepare_ml_features import FEATURE_COLUMNS, project_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()

    root = project_root()
    model = joblib.load(root / "model_artifacts" / "model_final.joblib")
    data = pd.read_csv(args.input_csv, parse_dates=["date"])
    missing = sorted(set(FEATURE_COLUMNS).difference(data.columns))
    if missing:
        raise ValueError(f"Features ausentes: {missing}")

    result = data[["date", *FEATURE_COLUMNS]].copy()
    result["prediction_stress"] = model.predict(result[FEATURE_COLUMNS]).astype(int)
    result["probability_stress"] = model.predict_proba(result[FEATURE_COLUMNS])[:, 1]
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output_csv, index=False, date_format="%Y-%m-%d")
    print(f"Predições salvas em: {args.output_csv}")


if __name__ == "__main__":
    main()
