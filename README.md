# handson_mack_2sem
Repositório referente ao projeto Hands on - MBA engenharia de dados Mackenzie.

# Integrantes
Fábio Silva de Medeiros RA 10734804 Jackson Ventura RA 10737764

# Oportunidades em meio ao Caos

Projeto de Engenharia de Dados e Machine Learning para identificar regimes de
stress socioeconômico e comparar a resiliência de índices setoriais da B3.

## Resultado atual

O fluxo da Entrega 3 está completo e reproduzível. O modelo selecionado é uma
Regressão Logística, com ROC-AUC de 0,67 e recall de 0,18 no conjunto de teste.
Ele deve ser apresentado como baseline acadêmico, não como recomendação de
investimento ou sistema produtivo.

## Execução rápida

Use Python 3.11+ em um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Execute as etapas na ordem:

```powershell
python src/build_ml_target.py
python src/prepare_ml_features.py
python src/train_models.py
python src/evaluate_model.py
```

Para aplicar o modelo a uma base nova contendo `date` e as nove features do
modelo:

```powershell
python src/predict_stress.py entrada.csv saida_predictions.csv
```

## Fluxo do projeto

```text
data/raw -> data/processed -> data/curated
                                  |
                                  v
                           target e features
                                  |
                                  v
                         treino temporal e modelos
                                  |
                                  v
                     métricas, gráficos e inferência
```

## Estrutura principal

- `data/raw`: dados originais das fontes.
- `data/processed`: dados tratados por fonte.
- `data/curated`: bases integradas e artefatos tabulares do ML.
- `src`: scripts reproduzíveis de preparação, treino, avaliação e inferência.
- `model_artifacts`: modelo persistido.
- `reports/entrega3`: métricas, previsões e gráficos.
- `docs`: documentação técnica, resultados e implantação.

## Documentação

Comece pelo [índice da documentação](docs/INDICE_DOCUMENTACAO.md).

- [Checklist da Entrega 3](docs/ENTREGA3_CHECKLIST.md)
- [Guia de resultados e escolhas](docs/GUIA_RESULTADOS_MODELO.md)
- [Relatório técnico da Entrega 3](docs/RELATORIO_ENTREGA3.md)
- [Plano de implantação](docs/PLANO_IMPLANTACAO.md)
- [Conclusão do projeto](docs/CONCLUSAO_PROJETO.md)
- [Dicionário de dados](docs/DICIONARIO_DADOS_MVP_RESILIENCIA.md)
- [Referência da disciplina](docs/HandsOn_Eng_Dados_Aula4.pdf)

## Regeneração dos dados de origem

Quando for necessário atualizar as fontes:

```powershell
docker compose up -d
python src/download_mvp.py
python src/upload_raw_minio.py
python src/preprocess_mvp.py
```

Depois, execute novamente o fluxo de ML acima. A execução do modelo não exige
MinIO quando os arquivos locais já estão disponíveis.
