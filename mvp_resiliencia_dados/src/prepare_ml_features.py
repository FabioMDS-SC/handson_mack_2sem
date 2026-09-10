"""Prepare regime features and chronological train/validation/test splits."""

from pathlib import Path

import pandas as pd


FEATURE_COLUMNS = [
    "ibc_br_change",
    "selic",
    "selic_change",
    "usd_brl_return",
    "usd_brl_volatility",
    "ipca_12m",
    "pib_change_3m",
    "unemployment",
    "unemployment_change",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def prepare_features(input_path: Path, output_path: Path, split_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path, parse_dates=["date"])
    required = {"date", "target_stress", *FEATURE_COLUMNS}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    result = df[["date", *FEATURE_COLUMNS, "target_stress"]].copy()
    result = result.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    result = result.dropna(subset=[*FEATURE_COLUMNS, "target_stress"]).reset_index(drop=True)

    # A ordem temporal é preservada. Os limites foram escolhidos por período,
    # e não por amostragem aleatória, para que validação e teste tenham eventos
    # de stress observáveis. O período posterior a 2021 permanece no teste,
    # inclusive os meses sem eventos, pois isso também mede falsos positivos.
    train_end = pd.Timestamp("2018-12-31")
    validation_end = pd.Timestamp("2020-12-31")
    result["split"] = "test"
    result.loc[result["date"] <= train_end, "split"] = "train"
    result.loc[
        (result["date"] > train_end) & (result["date"] <= validation_end),
        "split",
    ] = "validation"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    split_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, date_format="%Y-%m-%d")

    summary = (
        result.groupby("split", sort=False)
        .agg(
            linhas=("date", "size"),
            inicio=("date", "min"),
            fim=("date", "max"),
            stress=("target_stress", "sum"),
        )
        .reset_index()
    )
    summary["normal"] = summary["linhas"] - summary["stress"]
    summary.to_csv(split_path, index=False, date_format="%Y-%m-%d")
    return result


def validate_splits(df: pd.DataFrame) -> None:
    assert df["date"].is_monotonic_increasing
    assert set(df["split"]) == {"train", "validation", "test"}
    order = {"train": 0, "validation": 1, "test": 2}
    encoded = df["split"].map(order)
    assert encoded.is_monotonic_increasing
    assert (df.groupby("split")["target_stress"].nunique() >= 2).all()


if __name__ == "__main__":
    root = project_root()
    features = prepare_features(
        root / "data" / "curated" / "dataset_ml_target.csv",
        root / "data" / "curated" / "dataset_ml_features.csv",
        root / "data" / "curated" / "ml_split_summary.csv",
    )
    validate_splits(features)
    print(f"Features preparadas: {len(features)} linhas")
    print(features.groupby("split")["target_stress"].agg(["size", "sum"]).to_string())
