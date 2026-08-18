# MVP — Resiliência setorial em cenários de estresse

Este pacote serve para testar rapidamente a viabilidade de dados do projeto.

## O que já está automatizado

- Banco Central / SGS:
  - IBC-Br dessazonalizado — 24364
  - Meta Selic — 432
  - USD/BRL venda — 1
- IBGE / SIDRA:
  - IPCA — tabela 1737
  - PIB trimestral — tabela 1621
  - Taxa de desocupação — tabela 6381

## B3

Para evitar depender de scraping frágil, a primeira versão usa os arquivos históricos oficiais
baixados manualmente das páginas da B3.

Coloque-os em `data/raw/b3/` com um destes formatos:

- `ibovespa.csv` ou `ibovespa.xlsx`
- `ifnc.csv` ou `ifnc.xlsx`
- `icon.csv` ou `icon.xlsx`
- `iee.csv` ou `iee.xlsx`

O script gera um inventário apontando o que ainda está faltando.

## Instalação

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python src/download_mvp.py
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python src/download_mvp.py
```

## Saídas

### `data/raw/`

Mantém o dado mais próximo possível da fonte.

### `data/processed/`

- `ipca_selecionado.csv`
- `pib_selecionado.csv`
- `desemprego_selecionado.csv`
- `b3_inventory.csv`
- `coverage_report.csv`

O `coverage_report.csv` mostra quantidade de linhas, colunas, células vazias e erros.

## Estratégia recomendada

1. Executar o script somente com BCB + IBGE.
2. Conferir `coverage_report.csv`.
3. Baixar os quatro históricos da B3.
4. Executar novamente.
5. Só então desenvolver a etapa que converte todas as séries para frequência mensal.
6. Depois incorporar datas de divulgação para evitar look-ahead bias.

A janela inicial sugerida no código é 2012 em diante, alinhada à PNAD Contínua.


## Correção v2 — limite da API SGS

Desde 26/03/2025, consultas por intervalo na API BCData/SGS são limitadas
a no máximo 10 anos. Esta versão baixa automaticamente as séries BCB em
blocos de 9 anos e concatena os resultados.

Isso evita erro HTTP 406 para séries como Meta Selic (432) e USD/BRL (1)
quando a janela começa em 2012.


## Correção v3

### Selic (SGS 432)
- downloads do BCB agora usam blocos de 5 anos;
- parâmetros são enviados por `requests.get(..., params=...)`;
- há retries automáticos;
- se o BCB devolver HTML, texto ou resposta vazia, o erro mostra uma prévia do corpo.

### PIB (SIDRA 1621)
- a consulta agora seleciona explicitamente:
  - classificação 11255 — Setores e subsetores
  - categoria 90707 — PIB a preços de mercado
- portanto `pib_selecionado.csv` não depende mais de localizar o texto da categoria depois do download.
