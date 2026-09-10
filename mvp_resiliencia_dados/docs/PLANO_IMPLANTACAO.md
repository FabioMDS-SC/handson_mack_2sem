# Plano de implantação do modelo

Este plano é opcional para a Entrega 3. O modelo atual não deve ser implantado
em produção sem melhorias, pois o recall no teste foi 0,18.

## Arquitetura proposta

```text
Fontes BCB/IBGE/B3 -> raw -> processed -> curated -> features
                                                        |
                                                        v
                                              inferência batch mensal
                                                        |
                                                        v
                                             previsão + probabilidade
                                                        |
                                                        v
                                             revisão humana/dashboard
```

A primeira implantação deve ser batch mensal, não uma API em tempo real, pois
os dados e o problema possuem frequência mensal.

## Artefatos

- Modelo: `model_artifacts/model_final.joblib`.
- Inferência: `src/predict_stress.py`.
- Features: `src/prepare_ml_features.py`.
- Saída: data, `prediction_stress` e `probability_stress`.
- Dependências: `requirements.txt`.

## Processo mensal

1. Coletar as novas fontes após o fechamento do mês.
2. Validar cobertura, tipos, duplicidades e ausências.
3. Executar o pré-processamento.
4. Gerar as features com os mesmos nomes e transformações.
5. Executar `predict_stress.py`.
6. Armazenar previsão, probabilidade, versão e data de execução.
7. Revisar o alerta com contexto econômico antes de qualquer decisão.

## Monitoramento

Monitorar mensalmente falhas de coleta, valores ausentes, drift das features,
quantidade de alertas, precision, recall, F1, tempo de execução e versões das
dependências.

## Critérios de bloqueio

Não publicar uma previsão se faltar feature, houver mês duplicado, a data não
for a esperada, a probabilidade estiver fora de 0 a 1 ou o modelo estiver fora
da versão aprovada.

## Retreinamento

Revisar o modelo trimestralmente ou após eventos relevantes. O novo modelo deve
ser comparado ao vigente, mantendo a versão anterior até a aprovação da nova.

## Versionamento e rollback

Registrar versão, data de treinamento, período dos dados, features, métricas e
hash do artefato. Rollback significa restaurar o último modelo aprovado e
interromper a versão com falha.

## Segurança e governança

- Não armazenar credenciais no repositório.
- Validar arquivos antes do processamento.
- Restringir escrita no diretório de modelos.
- Manter logs sem dados sensíveis.
- Exibir o resultado como apoio à decisão, não como recomendação automática.
