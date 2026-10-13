"""Coleta indicadores do Banco Central (API SGS) e atualiza dados/ e README.md."""

import csv
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).parent
DADOS = RAIZ / "dados"
BRT = timezone(timedelta(hours=-3))
URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
    "?formato=json&dataInicial={inicio:%d/%m/%Y}&dataFinal={fim:%d/%m/%Y}"
)

# codigo SGS, nome do arquivo, descricao, unidade
SERIES = [
    (1, "dolar", "Dólar PTAX (venda)", "R$"),
    (432, "selic", "Selic meta", "% a.a."),
    (12, "cdi", "CDI diário", "% a.d."),
    (433, "ipca", "IPCA mensal", "%"),
]


def buscar(codigo, fim, dias=90, tentativas=3):
    """Retorna lista de (data_iso, valor) dos últimos `dias` até `fim`; levanta exceção após esgotar tentativas."""
    req = urllib.request.Request(
        URL.format(codigo=codigo, inicio=fim - timedelta(days=dias), fim=fim),
        headers={"User-Agent": "Mozilla/5.0 (indicadores-bcb)", "Accept": "application/json"},
    )
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return [(converter_data(p["data"]), p["valor"]) for p in json.load(resp)]
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(5 * (i + 1))
    raise ValueError("tentativas deve ser >= 1")


def converter_data(data_br):
    """'09/10/2026' -> '2026-10-09'."""
    return datetime.strptime(data_br, "%d/%m/%Y").date().isoformat()


def mesclar(arquivo, pontos):
    """Acrescenta ao CSV apenas datas novas; devolve todas as linhas ordenadas."""
    existentes = {}
    if arquivo.exists():
        with arquivo.open(newline="", encoding="utf-8") as f:
            existentes = {linha["data"]: linha["valor"] for linha in csv.DictReader(f)}
    existentes.update({d: v for d, v in pontos if d not in existentes})
    linhas = sorted(existentes.items())
    with arquivo.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["data", "valor"])
        w.writerows(linhas)
    return linhas


def gerar_readme(ultimos, agora):
    linhas = [
        "# Indicadores BCB",
        "",
        "Histórico diário de indicadores econômicos coletados automaticamente da "
        "[API SGS do Banco Central do Brasil](https://dadosabertos.bcb.gov.br/).",
        "",
        "| Indicador | Valor | Referência |",
        "|---|---|---|",
    ]
    for _, nome, descricao, unidade in SERIES:
        if nome in ultimos:
            data, valor = ultimos[nome]
            linhas.append(f"| {descricao} | {valor} {unidade} | {data} |")
        else:
            linhas.append(f"| {descricao} | indisponível | — |")
    linhas += [
        "",
        f"Última coleta: {agora:%Y-%m-%d %H:%M} (horário de Brasília).",
        "",
        "## Como funciona",
        "",
        "- Um workflow do GitHub Actions roda `coletar.py` todo dia às 21h (Brasília).",
        "- Cada série é gravada em `dados/<indicador>.csv`, acrescentando só datas novas.",
        "- Cada execução registra a coleta em `dados/coletas.log`.",
        "- Sem dependências: apenas a biblioteca padrão do Python.",
        "",
        "Séries SGS: 1 (dólar PTAX venda), 432 (Selic meta), 12 (CDI), 433 (IPCA).",
        "",
    ]
    return "\n".join(linhas)


def main():
    DADOS.mkdir(exist_ok=True)
    agora = datetime.now(BRT)
    ultimos, status = {}, []
    for codigo, nome, _, _ in SERIES:
        try:
            linhas = mesclar(DADOS / f"{nome}.csv", buscar(codigo, agora.date()))
            ultimos[nome] = linhas[-1]
            status.append(f"{nome}=ok")
        except Exception as e:
            status.append(f"{nome}=falha({type(e).__name__})")
    (RAIZ / "README.md").write_text(gerar_readme(ultimos, agora), encoding="utf-8")
    with (DADOS / "coletas.log").open("a", encoding="utf-8") as f:
        f.write(f"{agora:%Y-%m-%d %H:%M} {' '.join(status)}\n")
    print(" ".join(status))


if __name__ == "__main__":
    main()
