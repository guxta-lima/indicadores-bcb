# Indicadores BCB

Histórico diário de indicadores econômicos coletados automaticamente da [API SGS do Banco Central do Brasil](https://dadosabertos.bcb.gov.br/).

| Indicador | Valor | Referência |
|---|---|---|
| Dólar PTAX (venda) | 5.0277 R$ | 2026-10-21 |
| Selic meta | 13.75 % a.a. | 2026-10-21 |
| CDI diário | 0.050788 % a.d. | 2026-10-20 |
| IPCA mensal | 0.82 % | 2026-09-01 |

Última coleta: 2026-10-21 23:35 (horário de Brasília).

## Como funciona

- Um workflow do GitHub Actions roda `coletar.py` todo dia às 21h (Brasília).
- Cada série é gravada em `dados/<indicador>.csv`, acrescentando só datas novas.
- Cada execução registra a coleta em `dados/coletas.log`.
- Sem dependências: apenas a biblioteca padrão do Python.

Séries SGS: 1 (dólar PTAX venda), 432 (Selic meta), 12 (CDI), 433 (IPCA).
