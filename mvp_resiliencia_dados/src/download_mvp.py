
from pathlib import Path
import re
import sys
import json
import requests
import pandas as pd
import time

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

START_DATE = "01/01/2012"
END_DATE = None  # None = até o dado mais recente disponível

BCB_SERIES = {
    "ibc_br": 24364,
    "selic": 432,
    "usd_brl": 1,
}

SIDRA_TABLES = {
    "ipca": 1737,
    "pib": 1621,
    "desemprego": 6381,
}

B3_EXPECTED = ["ibovespa", "ifnc", "icon", "iee"]

def ensure_dirs():
    for p in [RAW / "bcb", RAW / "ibge", RAW / "b3", PROCESSED]:
        p.mkdir(parents=True, exist_ok=True)

def get_json(url, params=None, timeout=120, retries=4):
    """
    GET robusto:
    - usa params do requests (evita problemas de encoding na URL)
    - faz retries para respostas transitórias
    - valida se o corpo realmente é JSON
    - mostra parte da resposta quando o servidor devolve HTML/texto vazio
    """
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(
                url,
                params=params,
                timeout=timeout,
                headers={
                    "User-Agent": "mvp-resiliencia/1.0",
                    "Accept": "application/json,text/plain,*/*",
                },
            )
            r.raise_for_status()

            body = r.text.strip()
            if not body:
                raise RuntimeError(
                    f"Resposta vazia (HTTP {r.status_code}) em {r.url}"
                )

            try:
                return r.json()
            except ValueError:
                preview = body[:500].replace("\n", " ")
                raise RuntimeError(
                    f"Resposta nao-JSON (HTTP {r.status_code}) em {r.url}. "
                    f"Inicio do corpo: {preview!r}"
                )

        except Exception as e:
            last_error = e
            if attempt < retries:
                wait = 2 ** (attempt - 1)
                print(f"      tentativa {attempt} falhou; repetindo em {wait}s...")
                time.sleep(wait)
            else:
                break

    raise RuntimeError(str(last_error))

def download_bcb(name, code):
    """
    Baixa uma série SGS em blocos de 5 anos.
    O limite oficial é de até 10 anos por consulta; usamos blocos menores
    para reduzir a chance de respostas instáveis em séries longas.
    """
    start = pd.to_datetime(START_DATE, format="%d/%m/%Y")
    end = (
        pd.to_datetime(END_DATE, format="%d/%m/%Y")
        if END_DATE
        else pd.Timestamp.today().normalize()
    )

    frames = []
    current_start = start
    base_url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"

    while current_start <= end:
        current_end = min(
            current_start + pd.DateOffset(years=5) - pd.Timedelta(days=1),
            end
        )

        data_inicial = current_start.strftime("%d/%m/%Y")
        data_final = current_end.strftime("%d/%m/%Y")

        params = {
            "formato": "json",
            "dataInicial": data_inicial,
            "dataFinal": data_final,
        }

        print(f"    bloco {data_inicial} -> {data_final}")
        data = get_json(base_url, params=params)

        if data:
            frames.append(pd.DataFrame(data))

        current_start = current_end + pd.Timedelta(days=1)

    if not frames:
        raise RuntimeError(f"BCB {name} ({code}) retornou vazio.")

    df = pd.concat(frames, ignore_index=True)

    df["data"] = pd.to_datetime(
        df["data"], format="%d/%m/%Y", errors="coerce"
    )
    df["valor"] = pd.to_numeric(
        df["valor"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

    df = (
        df.dropna(subset=["data"])
          .drop_duplicates(subset=["data"], keep="last")
          .sort_values("data")
          .reset_index(drop=True)
    )

    out = RAW / "bcb" / f"{name}.csv"
    df.to_csv(out, index=False)
    return df

def sidra_raw(table, name=None):
    """
    Consulta SIDRA.

    Para a tabela 1621, a categoria precisa ser informada explicitamente:
    classificacao 11255 / categoria 90707 = PIB a precos de mercado.
    """
    if table == 1621 or name == "pib":
        url = (
            "https://apisidra.ibge.gov.br/values/"
            "t/1621/n1/all/v/all/p/all/c11255/90707/d/v584%202"
        )
    else:
        url = f"https://apisidra.ibge.gov.br/values/t/{table}/n1/all/v/all/p/all"

    data = get_json(url)

    if not data or len(data) < 2:
        raise RuntimeError(f"SIDRA tabela {table} retornou vazia.")

    header = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows).rename(columns=header)
    return df

def save_sidra(name, table):
    df = sidra_raw(table, name=name)
    out = RAW / "ibge" / f"{name}_sidra_{table}.csv"
    df.to_csv(out, index=False)
    return df

def normalize_text(s):
    return (
        s.astype(str)
         .str.normalize("NFKD")
         .str.encode("ascii", errors="ignore")
         .str.decode("ascii")
         .str.lower()
    )

def find_rows(df, patterns):
    # Busca flexível em todas as colunas textuais.
    combined = pd.Series("", index=df.index, dtype="object")
    for c in df.columns:
        combined = combined + " " + normalize_text(df[c])
    mask = pd.Series(False, index=df.index)
    for p in patterns:
        mask |= combined.str.contains(p, regex=True, na=False)
    return df[mask].copy()

def extract_numeric_value(df):
    # SIDRA normalmente possui coluna "Valor"; fallback procura coluna equivalente.
    candidates = [c for c in df.columns if str(c).strip().lower() == "valor"]
    if not candidates:
        candidates = [c for c in df.columns if "valor" in str(c).lower()]
    if not candidates:
        return None
    c = candidates[0]
    s = (
        df[c].astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"...": None, "-": None, "X": None})
    )
    return pd.to_numeric(s, errors="coerce")

def guess_period_column(df):
    candidates = [c for c in df.columns if "mes" in str(c).lower() or "trimestre" in str(c).lower() or "periodo" in str(c).lower()]
    if candidates:
        return candidates[0]
    return None

def reduce_ibge(name, df):
    if name == "ipca":
        # Guardar linhas relacionadas a variação mensal e 12 meses.
        sel = find_rows(df, [r"variacao mensal", r"12 meses"])
    elif name == "pib":
        # A consulta da tabela 1621 ja traz somente PIB a precos de mercado.
        sel = df.copy()
    elif name == "desemprego":
        sel = find_rows(df, [r"taxa de desocupacao"])
    else:
        sel = df.copy()

    val = extract_numeric_value(sel)
    if val is not None:
        sel["valor_numerico"] = val

    out = PROCESSED / f"{name}_selecionado.csv"
    sel.to_csv(out, index=False)
    return sel

def parse_market_file(path):
    """
    Le arquivos CSV/XLS/XLSX da B3.

    Os CSVs da B3 possuem:
    - uma linha de titulo antes do cabecalho;
    - separador ;
    - numeros no formato brasileiro;
    - encoding que pode ser Latin-1;
    - pequenas variacoes no nome da coluna Mes.
    """

    suffix = path.suffix.lower()

    # Excel
    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(path)

        if len(df.columns) >= 3:
            df = df.iloc[:, :3]
            df.columns = ["mes", "ano", "valor"]

        return df

    # CSV
    if suffix == ".csv":

        # Latin-1 funciona com os arquivos exportados pela B3
        with open(path, "r", encoding="latin1") as f:
            lines = f.readlines()

        header_index = None

        # Nao procurar "Mes" porque o caractere pode vir corrompido.
        # "Ano;Valor" e suficiente para identificar o cabecalho.
        for i, line in enumerate(lines):

            normalized = line.strip().lower()

            if ";ano;valor" in normalized:
                header_index = i
                break

        if header_index is None:
            print("\nPrimeiras linhas encontradas:")
            for line in lines[:10]:
                print(repr(line))

            raise ValueError(
                f"Cabecalho da B3 nao encontrado em {path}"
            )

        df = pd.read_csv(
            path,
            sep=";",
            skiprows=header_index,
            encoding="latin1",
            decimal=",",
            thousands=".",
            skip_blank_lines=True
        )

        # Nao dependemos do nome original da primeira coluna
        df = df.iloc[:, :3]
        df.columns = ["mes", "ano", "valor"]

        return df

    raise ValueError(
        f"Formato nao reconhecido: {path}"
    )

def inventory_b3():
    rows = []
    folder = RAW / "b3"
    for name in B3_EXPECTED:
        matches = list(folder.rglob(f"{name}.*"))
        rows.append({
            "serie": name,
            "arquivo_encontrado": matches[0].name if matches else None,
            "status": "OK" if matches else "PENDENTE",
        })
    pd.DataFrame(rows).to_csv(PROCESSED / "b3_inventory.csv", index=False)
    return rows

def coverage_report():
    rows = []
    for folder, source in [(RAW / "bcb", "BCB"), (RAW / "ibge", "IBGE"), (RAW / "b3", "B3")]:
        for p in sorted(folder.rglob("*")):
            if not p.is_file():
                continue
            try:
                if p.suffix.lower() in [".xlsx", ".xls", ".csv"]:
                    if source == "B3":
                        df = parse_market_file(p)
                    else:
                        df = pd.read_csv(p)
                    rows.append({
                        "fonte": source,
                        "arquivo": p.name,
                        "linhas": len(df),
                        "colunas": len(df.columns),
                        "missing_cells": int(df.isna().sum().sum()),
                        "status": "OK" if len(df) else "VAZIO",
                    })
            except Exception as e:
                rows.append({
                    "fonte": source,
                    "arquivo": p.name,
                    "linhas": None,
                    "colunas": None,
                    "missing_cells": None,
                    "status": f"ERRO: {e}",
                })
    report = pd.DataFrame(rows)
    report.to_csv(PROCESSED / "coverage_report.csv", index=False)
    return report

def main():
    ensure_dirs()
    print("1/4 Baixando Banco Central...")
    for name, code in BCB_SERIES.items():
        try:
            df = download_bcb(name, code)
            print(f"  OK {name}: {len(df)} linhas")
        except Exception as e:
            print(f"  ERRO {name}: {e}")

    print("2/4 Baixando IBGE/SIDRA...")
    for name, table in SIDRA_TABLES.items():
        try:
            df = save_sidra(name, table)
            selected = reduce_ibge(name, df)
            print(f"  OK {name} tabela {table}: {len(df)} linhas brutas; {len(selected)} selecionadas")
        except Exception as e:
            print(f"  ERRO {name}: {e}")

    print("3/4 Conferindo arquivos B3...")
    inv = inventory_b3()
    for x in inv:
        print(f"  {x['serie']}: {x['status']}")

    print("4/4 Gerando relatório de cobertura...")
    report = coverage_report()
    print(report.to_string(index=False))

    print("\nConcluído.")
    print(f"Dados brutos: {RAW}")
    print(f"Relatórios: {PROCESSED}")
    print("\nPróximo passo: coloque os arquivos oficiais B3 em data/raw/b3 com nomes:")
    print("ibovespa.csv/xlsx, ifnc.csv/xlsx, icon.csv/xlsx, iee.csv/xlsx")
    print("e rode o script novamente.")

if __name__ == "__main__":
    main()
