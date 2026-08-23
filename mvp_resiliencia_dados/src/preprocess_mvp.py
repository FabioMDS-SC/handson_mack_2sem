from __future__ import annotations

import io
import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
CURATED = BASE / "data" / "curated"
load_dotenv(BASE / ".env")

START = pd.Timestamp("2012-01-31")
TODAY = pd.Timestamp.today().normalize()
LAST_COMPLETE_MONTH = (TODAY - pd.offsets.MonthBegin(1)).to_period("M").to_timestamp("M")


def month_end(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s).dt.to_period("M").dt.to_timestamp("M")


def read_b3(path: Path, name: str) -> pd.DataFrame:
    raw = path.read_bytes()
    text = None
    for enc in ("utf-8-sig", "cp1252", "latin1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        raise UnicodeError(f"Nao foi possivel decodificar {path}")

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not re.match(r"^\d{1,2};\d{4};", line):
            continue
        parts = line.split(";")
        if len(parts) < 3:
            continue
        mes, ano, valor = parts[:3]
        valor = valor.strip().replace(".", "").replace(",", ".")
        rows.append((int(ano), int(mes), float(valor)))

    if not rows:
        raise RuntimeError(f"Nenhuma linha de dados encontrada em {path}")

    df = pd.DataFrame(rows, columns=["ano", "mes", name])
    df["date"] = pd.to_datetime(dict(year=df["ano"], month=df["mes"], day=1)) + pd.offsets.MonthEnd(0)
    duplicate_count = int(df.duplicated(subset=["date"]).sum())
    if duplicate_count:
        print(f"  {name}: removendo {duplicate_count} duplicidade(s)")
    df = df.drop_duplicates(subset=["date"], keep="first")
    return df[["date", name]].sort_values("date").reset_index(drop=True)


def preprocess_bcb() -> pd.DataFrame:
    ibc = pd.read_csv(RAW / "bcb" / "ibc_br.csv")
    ibc["date"] = month_end(ibc["data"])
    ibc["ibc_br"] = pd.to_numeric(ibc["valor"], errors="coerce")
    ibc = ibc[["date", "ibc_br"]].drop_duplicates("date", keep="last")

    selic = pd.read_csv(RAW / "bcb" / "selic.csv")
    selic["data"] = pd.to_datetime(selic["data"])
    selic["valor"] = pd.to_numeric(selic["valor"], errors="coerce")
    selic["date"] = month_end(selic["data"])
    selic = selic.sort_values("data").groupby("date", as_index=False).agg(selic=("valor", "last"))

    fx = pd.read_csv(RAW / "bcb" / "usd_brl.csv")
    fx["data"] = pd.to_datetime(fx["data"])
    fx["valor"] = pd.to_numeric(fx["valor"], errors="coerce")
    fx = fx.sort_values("data")
    fx["daily_return"] = fx["valor"].pct_change()
    fx["date"] = month_end(fx["data"])
    fx_month = fx.groupby("date", as_index=False).agg(
        usd_brl=("valor", "last"),
        usd_brl_volatility=("daily_return", lambda x: x.std() * (21 ** 0.5)),
    )

    out = ibc.merge(selic, on="date", how="outer").merge(fx_month, on="date", how="outer")
    out = out.sort_values("date")
    out["selic_change"] = out["selic"].diff()
    out["usd_brl_return"] = out["usd_brl"].pct_change()
    out.to_csv(PROCESSED / "bcb_monthly.csv", index=False)
    return out


def preprocess_ipca() -> pd.DataFrame:
    df = pd.read_csv(RAW / "ibge" / "ipca_sidra_1737.csv")
    df["Variável (Código)"] = pd.to_numeric(df["Variável (Código)"], errors="coerce")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df["Mês (Código)"] = pd.to_numeric(df["Mês (Código)"], errors="coerce")
    df = df[df["Variável (Código)"].isin([63, 2265])].copy()
    df["date"] = pd.to_datetime(df["Mês (Código)"].astype("Int64").astype(str), format="%Y%m", errors="coerce") + pd.offsets.MonthEnd(0)
    name_map = {63: "ipca_month", 2265: "ipca_12m"}
    df["metric"] = df["Variável (Código)"].map(name_map)
    out = df.pivot_table(index="date", columns="metric", values="Valor", aggfunc="first").reset_index()
    return out


def preprocess_unemployment() -> pd.DataFrame:
    df = pd.read_csv(RAW / "ibge" / "desemprego_sidra_6381.csv")
    df["Variável (Código)"] = pd.to_numeric(df["Variável (Código)"], errors="coerce")
    df = df[df["Variável (Código)"] == 4099].copy()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df["Trimestre Móvel (Código)"] = pd.to_numeric(df["Trimestre Móvel (Código)"], errors="coerce")
    df["date"] = pd.to_datetime(df["Trimestre Móvel (Código)"].astype("Int64").astype(str), format="%Y%m", errors="coerce") + pd.offsets.MonthEnd(0)
    return df[["date", "Valor"]].rename(columns={"Valor": "unemployment"}).drop_duplicates("date", keep="last")


def preprocess_gdp() -> pd.DataFrame:
    df = pd.read_csv(RAW / "ibge" / "pib_sidra_1621.csv")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    code = pd.to_numeric(df["Trimestre (Código)"], errors="coerce").astype("Int64")
    df["year"] = code.astype(str).str[:4].astype(float).astype("Int64")
    df["quarter"] = code.astype(str).str[-2:].astype(float).astype("Int64")
    month = df["quarter"].map({1: 3, 2: 6, 3: 9, 4: 12})
    df["date"] = pd.to_datetime(dict(year=df["year"], month=month, day=1)) + pd.offsets.MonthEnd(0)
    return df[["date", "Valor"]].rename(columns={"Valor": "pib_index"}).drop_duplicates("date", keep="last")


def preprocess_ibge() -> pd.DataFrame:
    ipca = preprocess_ipca()
    unemployment = preprocess_unemployment()
    gdp = preprocess_gdp()

    idx = pd.DataFrame({"date": pd.date_range(START, LAST_COMPLETE_MONTH, freq="ME")})
    out = idx.merge(ipca, on="date", how="left").merge(unemployment, on="date", how="left").merge(gdp, on="date", how="left")
    out["pib_index"] = out["pib_index"].ffill()
    out.to_csv(PROCESSED / "ibge_monthly_reference.csv", index=False)
    return out


def find_b3_file(name: str) -> Path:
    matches = list((RAW / "b3").rglob(f"{name}.csv")) + list((RAW / "b3").rglob(f"{name}.xlsx"))
    if not matches:
        raise FileNotFoundError(f"Arquivo B3 nao encontrado para {name}")
    return matches[0]


def preprocess_b3() -> pd.DataFrame:
    frames = []
    for name in ["ibovespa", "ifnc", "icon", "iee"]:
        path = find_b3_file(name)
        if path.suffix.lower() != ".csv":
            raise ValueError("Esta versao do pre-processamento espera os CSVs B3 ja baixados.")
        frames.append(read_b3(path, name))

    out = frames[0]
    for frame in frames[1:]:
        out = out.merge(frame, on="date", how="outer")
    out = out.sort_values("date").reset_index(drop=True)

    for name in ["ibovespa", "ifnc", "icon", "iee"]:
        out[f"{name}_return_1m"] = out[name].pct_change(fill_method=None)
        out[f"{name}_return_3m"] = out[name].pct_change(3, fill_method=None)
        out[f"{name}_volatility_3m_ann"] = out[f"{name}_return_1m"].rolling(3).std() * (12 ** 0.5)
        out[f"{name}_drawdown"] = out[name] / out[name].cummax() - 1

    out.to_csv(PROCESSED / "b3_monthly.csv", index=False)
    return out


def build_curated(bcb: pd.DataFrame, ibge: pd.DataFrame, b3: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = pd.DataFrame({"date": pd.date_range(START, LAST_COMPLETE_MONTH, freq="ME")})
    ref = idx.merge(bcb, on="date", how="left").merge(ibge, on="date", how="left").merge(b3, on="date", how="left")
    ref = ref.sort_values("date").reset_index(drop=True)
    ref.to_csv(CURATED / "dataset_monthly_reference.csv", index=False)

    model = ref.copy()
    # Defasagens conservadoras para reduzir look-ahead bias.
    model["ibc_br"] = model["ibc_br"].shift(2)
    model["ipca_month"] = model["ipca_month"].shift(1)
    model["ipca_12m"] = model["ipca_12m"].shift(1)
    model["unemployment"] = model["unemployment"].shift(1)
    model["pib_index"] = model["pib_index"].shift(3)

    model["ibc_br_change"] = model["ibc_br"].pct_change(fill_method=None)
    model["pib_change_3m"] = model["pib_index"].pct_change(3, fill_method=None)
    model["unemployment_change"] = model["unemployment"].diff()

    model.to_csv(CURATED / "dataset_mvp.csv", index=False)

    core = ["ibc_br", "selic", "usd_brl", "ipca_month", "ipca_12m", "pib_index", "unemployment", "ibovespa", "ifnc", "icon", "iee"]
    complete = model.dropna(subset=core).reset_index(drop=True)
    complete.to_csv(CURATED / "dataset_mvp_complete.csv", index=False)
    return model, complete


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        if col == "date":
            continue
        s = df[col]
        rows.append({
            "column": col,
            "rows": len(s),
            "non_null": int(s.notna().sum()),
            "missing": int(s.isna().sum()),
            "missing_pct": round(float(s.isna().mean() * 100), 2),
            "min": s.min(skipna=True),
            "max": s.max(skipna=True),
        })
    out = pd.DataFrame(rows)
    out.to_csv(CURATED / "quality_report.csv", index=False)
    return out


def upload_outputs_to_minio() -> None:
    if os.getenv("UPLOAD_TO_MINIO", "false").lower() not in {"1", "true", "yes", "y"}:
        print("\nUPLOAD_TO_MINIO=false: arquivos ficaram locais.")
        return

    from minio_utils import get_client, ensure_bucket

    client = get_client()
    buckets = {
        PROCESSED: os.getenv("MINIO_BUCKET_PROCESSED", "processed"),
        CURATED: os.getenv("MINIO_BUCKET_CURATED", "curated"),
    }
    for folder, bucket in buckets.items():
        ensure_bucket(client, bucket)
        for path in folder.glob("*.csv"):
            client.fput_object(bucket, path.name, str(path))
            print(f"MINIO OK s3://{bucket}/{path.name}")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    CURATED.mkdir(parents=True, exist_ok=True)

    print("1/5 BCB -> mensal")
    bcb = preprocess_bcb()
    print(f"  OK: {len(bcb)} meses")

    print("2/5 IBGE -> mensal")
    ibge = preprocess_ibge()
    print(f"  OK: {len(ibge)} meses")

    print("3/5 B3 -> mensal")
    b3 = preprocess_b3()
    print(f"  OK: {len(b3)} meses")

    print("4/5 Consolidando")
    model, complete = build_curated(bcb, ibge, b3)
    report = quality_report(model)
    print(f"  dataset_mvp.csv: {len(model)} linhas")
    print(f"  dataset_mvp_complete.csv: {len(complete)} linhas completas")
    if not complete.empty:
        print(f"  janela completa: {complete['date'].min().date()} -> {complete['date'].max().date()}")

    print("5/5 MinIO")
    upload_outputs_to_minio()
    print("\nConcluido.")


if __name__ == "__main__":
    main()
