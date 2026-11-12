"""Modelos de domínio: o que é um jogo e uma faixa de preço."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple


@dataclass(frozen=True)
class Jogo:
    """Um jogo do catálogo de uma plataforma de distribuição.

    A classe é imutável e independente da fonte dos dados: qualquer
    distribuidor (Steam, Epic, Paradox...) deve ser convertido para ela
    por um leitor (veja :mod:`jogos.leitores`).

    >>> j = Jogo(1, "Exemplo", date(2020, 5, 1), 0.0, 90, 10)
    >>> j.gratuito, j.ano_lancamento, j.taxa_aprovacao
    (True, 2020, 90.0)
    """

    app_id: int
    nome: str
    data_lancamento: date
    preco: float
    positivas: int = 0
    negativas: int = 0
    windows: bool = False
    mac: bool = False
    linux: bool = False
    generos: Tuple[str, ...] = ()

    @property
    def gratuito(self) -> bool:
        """``True`` quando o preço é zero."""
        return self.preco == 0

    @property
    def ano_lancamento(self) -> int:
        """Ano de lançamento do jogo."""
        return self.data_lancamento.year

    @property
    def total_avaliacoes(self) -> int:
        """Número de avaliações (positivas + negativas)."""
        return self.positivas + self.negativas

    @property
    def taxa_aprovacao(self) -> Optional[float]:
        """Percentual de avaliações positivas, ou ``None`` sem avaliações.

        >>> Jogo(2, "Sem notas", date(2020, 1, 1), 5.0).taxa_aprovacao is None
        True
        """
        if self.total_avaliacoes == 0:
            return None
        return 100 * self.positivas / self.total_avaliacoes


@dataclass(frozen=True)
class FaixaPreco:
    """Intervalo de preços semiaberto ``(inferior, superior]``.

    >>> faixa = FaixaPreco("Barato", 0, 10)
    >>> faixa.contem(10), faixa.contem(10.01), faixa.contem(0)
    (True, False, False)
    """

    nome: str
    inferior: float
    superior: float

    def contem(self, preco: float) -> bool:
        """Indica se ``preco`` pertence à faixa."""
        return self.inferior < preco <= self.superior


FAIXAS_PADRAO = (
    FaixaPreco("Gratuito", float("-inf"), 0),
    FaixaPreco("Até US$ 10", 0, 10),
    FaixaPreco("US$ 10 a 30", 10, 30),
    FaixaPreco("Acima de US$ 30", 30, float("inf")),
)
"""Faixas de preço usadas por padrão na consulta de aprovação."""
