# handson_mack_2sem
Repositório referente ao projeto Hands on - MBA engenharia de dados Mackenzie.
# Integrantes
Fábio Silva de Medeiros RA 10734804
Jackson Ventura         RA 10737764
# Título
Oportunidades em meio ao Caos: Previsibilidade financeira em momentos de estresse socioeconômico
# Problema
Diferentes setores econômicos tendem a se comportar de maneiras diferentes em momentos de estresse socioeconômicos ( Período eleitoral, epidemias, crises econômicas). 
Como utilizar  dados socioeconômicos e financeiros para objetivamente  identificar quais setores comerciais apresentam maior resiliência ou risco nesses cenários?

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


