"""Executa as três perguntas da Fase I.

Uso::

    python principal.py                          # arquivo completo
    python principal.py data/amostra_20_jogos.csv  # amostra
"""

import sys
from pathlib import Path

from jogos import CatalogoJogos

RAIZ = Path(__file__).resolve().parent
COMPLETO = RAIZ / "data" / "steam_games.csv"


def responder(caminho) -> None:
    """Imprime as respostas das três perguntas para o arquivo indicado."""
    catalogo = CatalogoJogos.de_csv_steam(caminho)
    print(f"Arquivo: {caminho}  ({len(catalogo)} jogos)\n")

    perc = catalogo.percentual_gratuitos_pagos()
    cont = catalogo.contagem_gratuitos_pagos()
    print("P1) Gratuitos: {:.2f}% ({})  Pagos: {:.2f}% ({})\n".format(
        perc["gratuitos"], cont["gratuitos"], perc["pagos"], cont["pagos"]))

    por_ano = catalogo.lancamentos_por_ano()
    anos = catalogo.anos_com_mais_lancamentos()
    print(f"P2) Ano(s) com mais lançamentos: {anos} ({por_ano[anos[0]]} jogos)\n")

    print("P3) Aprovação (% de avaliações positivas) por faixa de preço:")
    for r in catalogo.aprovacao_por_faixa_de_preco():
        aprov = "sem avaliações" if r.aprovacao is None else f"{r.aprovacao:.2f}%"
        print(f"   {r.faixa:<16} jogos={r.jogos:<5} aprovação={aprov}")


if __name__ == "__main__":
    responder(sys.argv[1] if len(sys.argv) > 1 else COMPLETO)
