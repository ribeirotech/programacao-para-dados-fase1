"""Biblioteca ``jogos``: consultas sobre catálogos de jogos eletrônicos.

Uso básico::

    from jogos import CatalogoJogos
    catalogo = CatalogoJogos.de_csv_steam("data/steam_games.csv")
    catalogo.percentual_gratuitos_pagos()
"""

from .catalogo import CatalogoJogos, ResumoFaixa
from .excecoes import (
    ArquivoDadosError,
    CatalogoVazioError,
    ColunaAusenteError,
    JogosError,
    RegistroInvalidoError,
)
from .leitores import LeitorBase, LeitorSteamCSV
from .modelos import FAIXAS_PADRAO, FaixaPreco, Jogo

__all__ = [
    "CatalogoJogos", "ResumoFaixa", "Jogo", "FaixaPreco", "FAIXAS_PADRAO",
    "LeitorBase", "LeitorSteamCSV", "JogosError", "ArquivoDadosError",
    "ColunaAusenteError", "RegistroInvalidoError", "CatalogoVazioError",
]
