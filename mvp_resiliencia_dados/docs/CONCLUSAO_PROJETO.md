# Conclusão do projeto - Oportunidades em meio ao Caos

## Problema investigado

O projeto buscou avaliar se indicadores macroeconômicos brasileiros podem
antecipar períodos de estresse e apoiar a comparação da resiliência de índices
setoriais da B3, especialmente IFNC, ICON e IEE.

## O que foi construído

1. Coleta de dados do BCB, IBGE e B3.
2. Camadas raw, processed e curated.
3. Integração mensal das séries.
4. Defasagens para reduzir look-ahead bias.
5. EDA com qualidade, cobertura, retornos, volatilidade, drawdown,
   recuperação e índice exploratório de resiliência.
6. Target binário para prever stress no mês seguinte.
7. Features macroeconômicas e divisão temporal.
8. Comparação entre Regressão Logística e Random Forest.
9. Avaliação com métricas, matriz de confusão e curva ROC.
10. Pipeline de inferência com modelo persistido.

## Conclusão analítica

O fluxo técnico solicitado foi implementado e demonstrado de ponta a ponta.
Entretanto, os resultados não sustentam afirmar que o modelo prevê stress com
alta confiabilidade. A Regressão Logística foi o melhor baseline pela validação,
mas obteve recall de 0,18 no teste e deixou de identificar 9 dos 11 eventos de
stress.

Assim, a conclusão correta é que existe algum sinal preditivo nas variáveis
macroeconômicas analisadas, mas ele é fraco e instável na amostra disponível.
O ranking de resiliência setorial deve ser tratado como análise exploratória,
não como recomendação de investimento.

## Melhorias recomendadas

- Calcular score e threshold somente com informação disponível no treino.
- Usar validação temporal em janela móvel ou expanding window.
- Avaliar thresholds diferentes de decisão para priorizar recall.
- Aumentar o histórico e revisar a definição econômica de stress.
- Testar lags adicionais e variáveis de mercado sem vazamento.
- Calibrar probabilidades e medir estabilidade por subperíodo.
- Monitorar drift, cobertura dos dados e queda de desempenho antes de qualquer
  uso operacional.

## Conclusão para apresentação

O projeto entrega uma solução de dados e Machine Learning reproduzível para
identificação exploratória de regimes de stress. A solução atende aos
artefatos da Entrega 3, mas o modelo deve ser apresentado como baseline
acadêmico e ponto de partida para evolução, não como sistema produtivo.
