"""Build and validate the supervised-learning target for the project.

The current baseline predicts whether the following month is in the upper
quartile (P75) of the exploratory stress score.  This script is intentionally
small and reproducible so the target can be regenerated outside a notebook.
"""

from pathlib import Path

import pandas as pd


STRESS_COMPONENTS = {
    "ibc_br_change": -1,
    "selic_change": 1,
    "usd_brl_return": 1,
    "usd_brl_volatility": 1,
    "ipca_12m": 1,
    "unemployment_change": 1,
    "pib_change_3m": -1,
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def add_stress_score(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    result = df.copy()
    score_columns: list[str] = []

    for column, direction in STRESS_COMPONENTS.items():
        if column not in result.columns:
            continue
        series = pd.to_numeric(result[column], errors="coerce")
        std = series.std()
        if pd.isna(std) or std == 0:
            continue
        score_column = f"{column}_stress_z"
        result[score_column] = ((series - series.mean()) / std) * direction
        score_columns.append(score_column)

    if not score_columns:
        raise ValueError("Nenhum componente disponível para construir stress_score.")

    result["stress_score"] = result[score_columns].mean(axis=1)
    return result, score_columns


def build_target(input_path: Path, output_path: Path, percentile: float = 0.75) -> pd.DataFrame:
    df = pd.read_csv(input_path, parse_dates=["date"])
    if "date" not in df.columns:
        raise ValueError("A base precisa conter a coluna date.")

    df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    df, _ = add_stress_score(df)
    threshold = df["stress_score"].quantile(percentile)
    next_score = df["stress_score"].shift(-1)

    # Comparações com NaN retornam False em pandas. A máscara explícita evita
    # classificar o último mês, que não possui observação futura conhecida.
    df["target_p75"] = (next_score.ge(threshold) & next_score.notna()).astype("Int64")
    df["target_stress"] = df["target_p75"]

    result = df.loc[next_score.notna()].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    return result


def validate_target(df: pd.DataFrame) -> None:
    assert df["date"].is_monotonic_increasing
    assert df["date"].is_unique
    assert df["target_stress"].notna().all()
    assert set(df["target_stress"].unique()) <= {0, 1}
    assert df["target_stress"].sum() > 0
    assert (len(df) - df["target_stress"].sum()) > 0


if __name__ == "__main__":
    root = project_root()
    output = root / "data" / "curated" / "dataset_ml_target.csv"
    built = build_target(root / "data" / "curated" / "dataset_mvp.csv", output)
    validate_target(built)
    print(f"Dataset salvo: {output}")
    print(f"Linhas: {len(built)}")
    print(f"Classes: {built['target_stress'].value_counts().sort_index().to_dict()}")
