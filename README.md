# handson_mack_2sem
Repositório referente ao projeto Hands on - MBA engenharia de dados Mackenzie.
# Integrantes
Fábio Silva de Medeiros RA 10734804
Jackson Ventura         RA 10737764
# Título
Oportunidades em meio ao Caos: Previsibilidade financeira em momentos de estresse socioeconômico
# Problema
Identificar oportunidades e riscos financeiros em momentos de stress socio econômico.

Como: desenvolver uma ferramenta baseada em Machine Learning que combina dados financeiros, macroeconômicos e socioeconômicos.
O modelo analisará períodos de grande instabilidade, como crises financeiras, eleições e pandemias, identificando quais setores do mercado apresentam maior resiliência nesses cenários.
A ferramenta será capaz de indicar, para um determinado cenário de estresse, quais setores historicamente demonstraram melhor desempenho e menor risco relativo.

# Índice do DATASET

| # | CSV | Fonte | Link de download | Papel | Detalhes | Inicio dos dados | Fim dos dados |
|---|---|---|---|---|---|---|---|
| 1 | Indice | - | - | INDICE | Compilado de todas as tabelas da pasta database | - | - |
| 2 | IBC_DESSAZONALIZADO | BCB | [Abrir IBC-Br](https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries) | Atividade econômica | O IBC-Br dessazonalizado é a série do Índice de Atividade Econômica do Banco Central do Brasil que retira as influências sazonais do calendário para mostrar a tendência real da economia | 01/01/2003 | 01/05/2026 |
| 3 | SELIC | BCB | [Abrir Selic – SGS 432](https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries) | Juros | A Meta Selic é a taxa básica de juros da economia brasileira, cujo valor alvo é definido a cada 45 dias pelo Comitê de Política Monetária (Copom) do Banco Central (BC). | 01/01/2003 | 31/05/2026 |
| 4 | TAXA_DE_CAMBIO_DOLAR | BCB | [Abrir Dólar – SGS 1](https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries) | Câmbio | Taxa de câmbio livre do dólar americano (venda) no fechamento diário é o preço oficial pago em reais para adquirir um dólar no mercado cambial livre, calculado e divulgado diariamente pelo Banco Central do Brasil. | 01/01/2003 | 31/05/2026 |
| 5 | DADOS_IPCA | IBGE | [Abrir IPCA – tabela 7060](https://sidra.ibge.gov.br/tabela/7060) | Inflação | O IPCA (Índice Nacional de Preços ao Consumidor Amplo) é o índice oficial da inflação no Brasil. Calculado mensalmente pelo IBGE, ele mede a variação de preços de uma cesta de produtos e serviços consumida pelas famílias urbanas, indicando a perda ou o ganho do poder de compra da moeda ao longo do tempo. | 01/07/1994 | 01/07/2026 |
| 6 | DADOS_PIB | IBGE | [Abrir PIB – tabela 6784](https://sidra.ibge.gov.br/tabela/6784) | Crescimento | O Produto Interno Bruto (PIB) dos Municípios é o indicador econômico que mede o valor total de todos os bens e serviços finais produzidos em uma cidade específica durante um período determinado, geralmente de um ano | 2002 | 2023 |
| 7 | EVOLUCAO_Mensal_IBOVESPA | B3 | [Abrir Ibovespa](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/) | Target | Evolução mensal do índice Ibovespa | 2002 | 2026 |
| 8 | DICIONARIO_SIGLAS_PIB | IBGE | - | INDICE | Dicionario de Siglas e UFS | - | - |
| 9 | DADOS_PIB_SETOR | IBGE | - | Crescimento | O Produto Interno Bruto (PIB) separado por UF e categorizado por SETOR | 2002 | 2020 |
| **10** | **dim_b3_ticker_setor.csv** | **B3 / API Brapi** | **-** | **Dicionário** | **Lista completa de tickers negociados na B3 com o respectivo Nome da Empresa, Setor de atuação e Subsetor. Essencial para classificação setorial, enriquecimento de bases de dados e análises fundamentais.** | **-** | **-** |
| 11 | IBOVESPA_1994_2020 | B3 | [https://www.b3.com.br/.../historical-quotes/](https://www.b3.com.br/en_us/market-data-and-indices/data-services/market-data/historical-data/equities/historical-quotes/) | Target | Lista de transações da Ibovespa entre 1994 e 2020 | 1994 | 2020 |
