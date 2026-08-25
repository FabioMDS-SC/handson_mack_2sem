# handson_mack_2sem — MVP de Resiliência Setorial

Projeto do Hands On do MBA em Engenharia de Dados — Mackenzie.

## Título

**Oportunidades em meio ao Caos: Previsibilidade financeira em momentos de estresse socioeconômico**

## Problema

Diferentes setores econômicos podem se comportar de maneiras diferentes em períodos de estresse socioeconômico, como recessões, pandemias e períodos eleitorais.

O projeto investiga como dados macroeconômicos, socioeconômicos e financeiros podem ser utilizados para identificar esses cenários e comparar a resiliência histórica de diferentes setores do mercado brasileiro.

## Dados do MVP

| Dado | Fonte | Código/Tabela | Papel | Frequência original |
|---|---|---:|---|---|
| IBC-Br dessazonalizado | BCB | SGS 24364 | Feature | Mensal |
| Selic | BCB | SGS 432 | Feature | Diária/eventos |
| Dólar USD/BRL | BCB | SGS 1 | Feature | Diária |
| IPCA | IBGE | SIDRA 1737 | Feature | Mensal |
| PIB | IBGE | SIDRA 1621 | Feature | Trimestral |
| Taxa de desemprego | IBGE | SIDRA 6381 | Feature | Trimestre móvel |
| Ibovespa | B3 | - | Benchmark | Mensal no arquivo utilizado |
| IFNC | B3 | - | Target setorial | Mensal |
| ICON | B3 | - | Target setorial | Mensal |
| IEE | B3 | - | Target setorial | Mensal |

## Estrutura

```text
mvp_resiliencia_dados_v4_minio/
├── data/
│   ├── raw/
│   ├── processed/
│   └── curated/
├── src/
│   ├── download_mvp.py
│   ├── upload_raw_minio.py
│   ├── minio_utils.py
│   └── preprocess_mvp.py
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README_V4.md
```

Consulte `README_V4.md` para executar a etapa de pré-processamento e MinIO.
