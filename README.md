# handson_mack_2sem

Repositório referente ao projeto Hands On - MBA em Engenharia de Dados Mackenzie.

# Integrantes

Fábio Silva de Medeiros - RA 10734804  
Jackson Ventura - RA 10737764

# Título

**Oportunidades em meio ao Caos: Previsibilidade financeira em momentos de estresse socioeconômico**

# Problema

Diferentes setores econômicos tendem a se comportar de maneiras distintas em momentos de estresse socioeconômico, como períodos eleitorais, epidemias e crises econômicas.

O projeto busca responder à seguinte questão:

> Como utilizar dados socioeconômicos e financeiros para identificar, de forma objetiva, quais setores apresentam maior resiliência ou maior risco em cenários de estresse?

# V5 - Pré-processamento + MinIO + EDA de Stress e Resiliência

Esta versão mantém a coleta e o Data Lake local com MinIO, o pré-processamento das fontes e amplia a Análise Exploratória de Dados (EDA) com análises voltadas à identificação exploratória de períodos de stress e à comparação da resiliência dos índices setoriais.

A classificação de stress e o índice de resiliência implementados nesta etapa possuem caráter **exploratório**. Eles são utilizados para testar hipóteses e apoiar a preparação da futura etapa de Machine Learning, não representando ainda o target definitivo do modelo.

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
      ↓
Análise Exploratória (EDA)
      ↓
Stress Score exploratório
      ↓
Normal x Stress
      ↓
Análise de resiliência setorial
      ↓
Preparação para Machine Learning
```

A ideia é manter os dados separados por etapa:

- `raw`: dados próximos da fonte original;
- `processed`: dados tratados e padronizados por fonte;
- `curated`: datasets integrados e preparados para análise.

---

## 1. Subir o MinIO

Copie `.env.example` para `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up -d
```

A API S3 fica em:

```text
http://localhost:9000
```

O Console do MinIO fica em:

```text
http://localhost:9001
```

As credenciais do `.env.example` são apenas para desenvolvimento local.

---

## 2. Instalar dependências

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Caso o notebook seja executado localmente, também é necessário ter Jupyter instalado no ambiente.

A EDA utiliza correlação de Spearman. Por isso, o ambiente também deve possuir a biblioteca `scipy`, preferencialmente declarada no `requirements.txt`.

Exemplo:

```text
scipy>=1.11
```

---

## 3. Coletar ou atualizar as fontes

```powershell
python src/download_mvp.py
```

O script realiza a coleta das fontes do Banco Central do Brasil e do IBGE.

Os arquivos da B3 são obtidos manualmente e armazenados na pasta:

```text
data/raw/b3/
```

A coleta mantém uma cópia dos dados próxima da fonte original.

Algumas normalizações mínimas são realizadas para permitir a leitura dos arquivos, como:

- conversão de datas;
- conversão de valores numéricos;
- ordenação dos registros;
- validação da estrutura dos arquivos.

O pré-processamento principal é realizado posteriormente pelo `preprocess_mvp.py`.

---

## 4. Enviar Raw Data para o MinIO

```powershell
python src/upload_raw_minio.py
```

Buckets utilizados:

- `raw`;
- `processed`;
- `curated`.

A estrutura representa uma organização simples de Data Lake para o projeto.

---

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

O objetivo do pré-processamento é colocar as diferentes fontes em uma estrutura comum, principalmente com frequência mensal.

---

# Regras principais do pré-processamento

## Banco Central

### IBC-Br

- frequência original mensal;
- valor mantido em frequência mensal;
- criação da variação percentual do indicador.

A variação ajuda a observar aceleração ou desaceleração da atividade econômica.

### Selic

- utiliza o último valor disponível do mês;
- criação da diferença em relação ao mês anterior.

A Selic representa o nível da taxa de juros, enquanto sua variação mostra se os juros estão subindo, caindo ou permanecendo estáveis.

### Dólar

- utiliza o último valor disponível do mês;
- calcula retorno mensal;
- calcula volatilidade mensal com base nos retornos diários.

O retorno representa a variação percentual da cotação.

A volatilidade ajuda a representar a intensidade das oscilações do dólar durante o período.

---

## IBGE

### IPCA

São utilizadas principalmente:

- `Variação mensal` - código 63;
- `Variação acumulada em 12 meses` - código 2265.

A variação mensal representa a inflação mais recente.

O acumulado de 12 meses ajuda a representar períodos de inflação persistente.

### Desemprego

É utilizada:

- `Taxa de desocupação` - código 4099.

Também é calculada a variação em relação ao período anterior para observar melhora ou deterioração do mercado de trabalho.

### PIB

É utilizado o índice trimestral dessazonalizado da tabela SIDRA 1621.

Como a base final possui frequência mensal, o último valor trimestral é propagado até a próxima observação.

Esse tratamento é combinado com uma defasagem na base de modelagem para reduzir o risco de utilizar informações antes de sua divulgação.

---

## B3

O parser considera o formato disponibilizado nos arquivos históricos da B3.

Exemplo:

```text
Mês;Ano;Valor
1;2015;24.635,26
```

Durante a leitura são tratados:

- cabeçalhos adicionais;
- encoding dos arquivos;
- separador `;`;
- decimal no padrão brasileiro;
- duplicidades de mês e ano.

Exemplo de conversão:

```text
24.635,26
```

para:

```text
24635.26
```

Os índices utilizados são:

- Ibovespa;
- IFNC - Índice Financeiro;
- ICON - Índice de Consumo;
- IEE - Índice de Energia Elétrica.

Para os índices também são criadas variáveis como:

- retorno mensal (`*_return_1m`);
- retorno de 3 meses (`*_return_3m`);
- volatilidade anualizada em janela móvel de 3 meses (`*_volatility_3m_ann`);
- drawdown (`*_drawdown`).

---

# Look-ahead bias

Um dos cuidados do projeto é evitar que o futuro modelo utilize uma informação antes de ela estar disponível na realidade.

Por esse motivo são mantidas diferentes visões dos dados.

## `dataset_monthly_reference.csv`

Os indicadores são associados ao mês ao qual se referem.

Esse dataset é mais adequado para:

- análise histórica;
- gráficos;
- estatística descritiva;
- análise exploratória;
- comparação temporal;
- análise de correlação e defasagens históricas.

Ele não deve ser utilizado automaticamente como dataset de Machine Learning, pois algumas informações econômicas são divulgadas depois do mês de referência.

## `dataset_mvp.csv`

Versão preparada para a futura modelagem.

São aplicados lags aproximados de disponibilidade:

- IBC-Br: 2 meses;
- IPCA: 1 mês;
- desemprego: 1 mês;
- PIB: 3 meses.

Esses lags são uma aproximação inicial.

Em uma versão mais rigorosa, o ideal é utilizar as datas oficiais de divulgação de cada indicador.

## `dataset_mvp_complete.csv`

Contém somente os meses em que todas as principais séries utilizadas na integração estão disponíveis em conjunto.

Esse arquivo é útil quando uma análise realmente exige todas as variáveis completas.

Ele não deve ser utilizado automaticamente para toda análise, porque uma série com histórico menor pode reduzir desnecessariamente a quantidade de observações.

---

# Saídas do pré-processamento

## `data/processed/`

Exemplos:

- `bcb_monthly.csv`;
- `ibge_monthly_reference.csv`;
- `b3_monthly.csv`.

Esses arquivos representam dados tratados separadamente por fonte.

## `data/curated/`

- `dataset_monthly_reference.csv`;
- `dataset_mvp.csv`;
- `dataset_mvp_complete.csv`;
- `quality_report.csv`.

Os arquivos da camada `curated` são as principais entradas para a análise exploratória e para as próximas etapas do projeto.

---

# 6. Análise Exploratória de Dados (EDA)

O projeto possui um notebook específico para análise exploratória:

```text
notebooks/EDA_MVP_Resiliencia.ipynb
```

O notebook deve ser executado depois do pré-processamento.

Exemplo:

```powershell
jupyter notebook notebooks/EDA_MVP_Resiliencia.ipynb
```

A EDA atual contempla:

- qualidade dos dados;
- cobertura histórica das variáveis;
- valores ausentes;
- duplicidades;
- estatística descritiva;
- média e mediana;
- desvio padrão;
- assimetria;
- curtose;
- distribuições;
- outliers;
- evolução temporal;
- retornos dos índices;
- volatilidade;
- drawdown;
- correlações de Pearson e Spearman;
- relações entre variáveis macroeconômicas e mercado;
- análise de defasagens macroeconômicas;
- comparação de correlações entre regimes Normal e Stress;
- sazonalidade;
- comparação entre subperíodos;
- eventos extremos pelo critério IQR;
- Stress Score exploratório;
- classificação exploratória dos regimes;
- análise do tempo de recuperação dos índices;
- comparação de desempenho e risco durante Stress;
- índice exploratório de resiliência setorial;
- quantidade de observações disponível para Machine Learning.

---

# Stress Score exploratório

Como etapa intermediária entre a EDA e o futuro modelo de Machine Learning, foi criado um indicador exploratório de stress socioeconômico.

Entre as variáveis consideradas estão:

- variação do IBC-Br;
- variação da Selic;
- retorno do dólar;
- volatilidade do dólar;
- IPCA acumulado em 12 meses;
- variação do desemprego;
- variação do PIB.

As variáveis são padronizadas utilizando **z-score**:

```text
z = (valor - média) / desvio padrão
```

A direção das variáveis é ajustada para que valores maiores do componente representem maior intensidade de stress.

Exemplos de sinais associados a maior stress:

- atividade econômica em queda;
- PIB em queda;
- desemprego em alta;
- inflação mais elevada;
- dólar em alta;
- maior volatilidade cambial.

Os componentes disponíveis são agregados em um `stress_score` exploratório.

Na versão atual, percentis da distribuição são utilizados para separar níveis como:

- `Normal`;
- `Atenção`;
- `Stress elevado`.

Também é utilizada uma visão binária `Normal / Stress` em análises comparativas.

> Essa classificação possui caráter exploratório e não representa ainda o target definitivo do modelo de Machine Learning.

---

# Análise de defasagens macroeconômicas

A EDA verifica se alterações nas variáveis macroeconômicas possuem associação com os retornos dos índices no mesmo mês ou alguns meses depois.

São analisadas defasagens de:

- 0 meses;
- 1 mês;
- 3 meses;
- 6 meses.

Interpretação:

```text
lag = 0  → macro(t)   x retorno(t)
lag = 1  → macro(t-1) x retorno(t)
lag = 3  → macro(t-3) x retorno(t)
lag = 6  → macro(t-6) x retorno(t)
```

São calculadas correlações de Pearson e Spearman.

Essa análise busca identificar possíveis relações temporais e **não deve ser interpretada como evidência de causalidade**.

Para essa análise histórica é utilizado preferencialmente o dataset de referência, evitando misturar o lag econômico investigado com os lags de disponibilidade aplicados na base destinada à modelagem.

---

# Análise de resiliência setorial

Após a identificação exploratória dos períodos de Stress, os índices são comparados considerando múltiplas dimensões de retorno e risco.

A versão atual considera principalmente:

- retorno médio durante Stress;
- volatilidade durante Stress;
- percentual de meses negativos;
- pior retorno mensal;
- drawdown;
- tempo de recuperação após a principal queda histórica.

## Tempo de recuperação

A análise identifica:

```text
pico anterior
      ↓
pior drawdown
      ↓
recuperação
      ↓
retorno ao pico anterior
```

Quanto menor o tempo necessário para retornar ao pico anterior, maior a evidência exploratória de capacidade de recuperação.

## Índice exploratório de resiliência

As métricas possuem escalas diferentes e são normalizadas para permitir comparação relativa.

O score combina dimensões em que:

- maior retorno é melhor;
- menor volatilidade é melhor;
- menor frequência de perdas é melhor;
- pior mês menos negativo é melhor;
- drawdown menos severo é melhor;
- menor tempo de recuperação é melhor.

O resultado é apresentado em escala de 0 a 100 por meio de `resilience_score_100`.

> O score é relativo aos índices, períodos e critérios analisados. Ele não representa probabilidade de sucesso, previsão de retorno ou recomendação de investimento.

---

# Estratégia de uso dos datasets na EDA

Não é necessário utilizar o mesmo dataset em todas as análises.

## Para análise histórica

Utilizar preferencialmente:

```text
dataset_monthly_reference.csv
```

Isso permite aproveitar melhor o histórico disponível.

## Para análise das futuras features do modelo

Utilizar:

```text
dataset_mvp.csv
```

Esse arquivo já considera as defasagens aplicadas para reduzir look-ahead bias.

## Para análises que exigem todas as variáveis completas

Utilizar:

```text
dataset_mvp_complete.csv
```

O `dropna` também pode ser aplicado apenas nas colunas realmente utilizadas em determinada análise.

Exemplo:

```python
cols = [
    "date",
    "ibc_br_change",
    "selic",
    "usd_brl_return",
    "ipca_12m"
]

df_analysis = df[cols].dropna()
```

Isso evita perder observações por causa de uma variável que não participa daquela análise.

---

# Resultado atual da EDA

Na execução atual, a análise mostrou que o histórico disponível depende das variáveis escolhidas.

Quando são consideradas apenas as principais features macroeconômicas candidatas ao modelo de regime, existem aproximadamente:

```text
167 observações completas
2012-09 até 2026-07
```

Quando também é exigida a presença de todos os índices setoriais, incluindo IEE, a janela fica em aproximadamente:

```text
139 observações completas
2015-01 até 2026-07
```

O IEE é atualmente a série que mais limita a janela comum entre os índices.

Isso indica que não é necessário limitar o futuro modelo de classificação de regime ao mesmo período utilizado na comparação completa dos setores.

Os números podem mudar quando as fontes forem atualizadas. Por isso, devem ser tratados como resultado da execução atual e não como valores fixos do projeto.

---

# Separação conceitual dos datasets

A EDA indicou que é útil trabalhar com duas visões principais.

## Dataset de regime

Voltado para identificação e futura classificação de períodos de stress.

Principais candidatas:

- IBC-Br;
- variação do IBC-Br;
- Selic;
- variação da Selic;
- retorno do dólar;
- volatilidade do dólar;
- IPCA;
- PIB;
- desemprego.

Fluxo esperado:

```text
Macroeconomia
      ↓
Stress Score exploratório
      ↓
Definição / validação do target
      ↓
Machine Learning
      ↓
Stress / Normal
```

## Dataset de resiliência

Voltado para comparação dos setores.

Principais dados:

- Ibovespa;
- IFNC;
- ICON;
- IEE;
- retornos;
- volatilidade;
- drawdown;
- tempo de recuperação.

Fluxo esperado:

```text
Regime identificado
      ↓
IFNC / ICON / IEE
      ↓
Retorno + volatilidade + drawdown + recuperação
      ↓
Análise de resiliência
```

Essa separação ainda será validada antes da etapa final de modelagem.

---

# Cuidados identificados pela EDA

## Volume de dados

O dataset possui frequência mensal e quantidade limitada de observações.

Por isso, modelos muito complexos podem gerar overfitting.

A primeira versão deverá priorizar modelos simples e interpretáveis.

## Correlação

Correlação é utilizada para investigar relações entre variáveis, mas não é tratada como causalidade.

## Defasagens

Os lags investigados na análise econômica não devem ser confundidos com os lags de disponibilidade utilizados para reduzir look-ahead bias.

## Outliers

Valores extremos não são removidos automaticamente.

Como o objetivo do projeto é estudar momentos de stress, alguns outliers podem representar justamente períodos importantes, como crises e choques de mercado.

## Stress Score

A regra atual baseada em z-score e percentis é exploratória e deverá ser validada antes de ser transformada no target definitivo do modelo.

## Índice de resiliência

O ranking depende das métricas escolhidas, da normalização utilizada e do período analisado. Portanto, seu uso atual é comparativo e exploratório.

## Séries temporais

A futura divisão entre treino e teste deverá respeitar a ordem temporal dos dados.

Não será utilizado um split aleatório tradicional sem justificativa.

---

# Documentação adicional

Documentações complementares do projeto devem ser mantidas na pasta `docs/`.

## Dicionário de dados

```text
docs/data_dictionary.md
```

Contém:

- origem das variáveis;
- tipos de dados;
- frequência;
- significado econômico;
- fórmulas das variáveis derivadas;
- métricas utilizadas pela EDA;
- componentes do Stress Score;
- métricas do índice de resiliência.

## Guia da EDA

```text
docs/Guia_Completo_EDA_Resiliencia_v2.md
```

Apresenta a interpretação das principais métricas utilizadas no notebook, incluindo retorno, volatilidade, drawdown, correlação, Stress Score, defasagens e resiliência.

---

# Estrutura atual do projeto

Estrutura simplificada:

```text
.
├── data/
│   ├── raw/
│   │   ├── bcb/
│   │   ├── ibge/
│   │   └── b3/
│   ├── processed/
│   └── curated/
│       ├── dataset_monthly_reference.csv
│       ├── dataset_mvp.csv
│       ├── dataset_mvp_complete.csv
│       └── quality_report.csv
│
├── docs/
│   ├── data_dictionary.md
│   └── Guia_Completo_EDA_Resiliencia_v2.md
│
├── notebooks/
│   └── EDA_MVP_Resiliencia.ipynb
│
├── src/
│   ├── download_mvp.py
│   ├── preprocess_mvp.py
│   ├── minio_utils.py
│   └── upload_raw_minio.py
│
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

# Fluxo de execução

Uma execução completa do projeto segue a ordem:

```text
1. Subir MinIO
      ↓
2. Coletar dados
      ↓
3. Enviar Raw para MinIO
      ↓
4. Pré-processar
      ↓
5. Gerar datasets curated
      ↓
6. Executar EDA
      ↓
7. Construir Stress Score exploratório
      ↓
8. Comparar Normal x Stress
      ↓
9. Avaliar defasagens macroeconômicas
      ↓
10. Avaliar resiliência setorial
      ↓
11. Validar a definição do target
      ↓
12. Preparar Machine Learning
```

Comandos principais:

```powershell
docker compose up -d

python src/download_mvp.py

python src/upload_raw_minio.py

python src/preprocess_mvp.py

jupyter notebook notebooks/EDA_MVP_Resiliencia.ipynb
```

---

# Próximos passos

As próximas etapas previstas são:

- revisar e validar a regra exploratória de Stress;
- avaliar o balanceamento das classes após a definição do target;
- selecionar as features mais adequadas para classificação de regime;
- verificar redundância entre variáveis;
- definir estratégia temporal de treino, validação e teste;
- implementar modelos simples e interpretáveis como baseline;
- comparar modelos de classificação;
- analisar a estabilidade da resiliência setorial entre diferentes regimes e períodos.

