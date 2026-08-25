# V4 — Pré-processamento + MinIO

Esta versão mantém a coleta existente e acrescenta uma etapa simples de Data Lake local usando MinIO.

## Arquitetura

```text
BCB / IBGE / B3
      ↓
data/raw
      ↓
MinIO bucket raw
      ↓
preprocess_mvp.py
      ↓
data/processed + bucket processed
      ↓
data/curated + bucket curated
```

## 1. Subir o MinIO

Copie `.env.example` para `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up -d
```

A API S3 fica em `http://localhost:9000` e o Console em `http://localhost:9001`.

As credenciais de exemplo são apenas para desenvolvimento local.

## 2. Instalar dependências

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Coletar/atualizar as fontes

```powershell
python src/download_mvp.py
```

## 4. Enviar Raw Data para o MinIO

```powershell
python src/upload_raw_minio.py
```

Buckets criados automaticamente:

- `raw`
- `processed`
- `curated`

## 5. Pré-processar

Para processar somente localmente:

```powershell
python src/preprocess_mvp.py
```

Para também publicar os resultados no MinIO:

```powershell
$env:UPLOAD_TO_MINIO="true"
python src/preprocess_mvp.py
```

## Regras principais

### BCB

- IBC-Br: frequência mensal.
- Selic: último valor disponível do mês.
- Dólar: último valor do mês.
- Dólar também gera retorno mensal e volatilidade mensal baseada nos retornos diários.

### IBGE

- IPCA: somente `Variação mensal` (código 63) e `Variação acumulada em 12 meses` (2265).
- Desemprego: somente `Taxa de desocupação` (4099).
- PIB: índice trimestral dessazonalizado da tabela 1621, propagado entre os meses para formar a grade mensal.

### B3

O parser lê o padrão manual da B3:

```text
Mês;Ano;Valor
1;2015;24.635,26
```

Ele ignora cabeçalhos extras, converte decimal brasileiro e remove duplicidades por mês (incluindo o ICON 2015).

## Look-ahead bias

São gerados dois datasets:

### `dataset_monthly_reference.csv`

Alinha os indicadores pelo período ao qual eles se referem. Útil para EDA e análise histórica.

### `dataset_mvp.csv`

Versão mais conservadora para modelagem, com lags aproximados de disponibilidade:

- IBC-Br: 2 meses
- IPCA: 1 mês
- desemprego: 1 mês
- PIB: 3 meses

Esses lags são uma aproximação inicial. Em uma versão mais rigorosa, devem ser substituídos pelas datas oficiais de divulgação de cada observação.

## Saídas

`data/processed/`:

- `bcb_monthly.csv`
- `ibge_monthly_reference.csv`
- `b3_monthly.csv`

`data/curated/`:

- `dataset_monthly_reference.csv`
- `dataset_mvp.csv`
- `dataset_mvp_complete.csv`
- `quality_report.csv`

O `dataset_mvp_complete.csv` contém somente meses em que as principais séries já estão disponíveis em conjunto.
