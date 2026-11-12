"""Catálogo de jogos e as consultas de negócio sobre ele."""

from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from .excecoes import CatalogoVazioError
from .leitores import LeitorBase, LeitorSteamCSV
from .modelos import FAIXAS_PADRAO, FaixaPreco, Jogo


@dataclass(frozen=True)
class ResumoFaixa:
    """Resultado da consulta de aprovação para uma faixa de preço."""

    faixa: str
    jogos: int
    jogos_avaliados: int
    positivas: int
    negativas: int

    @property
    def aprovacao(self) -> Optional[float]:
        """Percentual de avaliações positivas na faixa (``None`` se não há)."""
        total = self.positivas + self.negativas
        return None if total == 0 else 100 * self.positivas / total


class CatalogoJogos:
    """Coleção de jogos com métodos de consulta.

    É o único ponto de contato que o programador usuário precisa conhecer:

    >>> from datetime import date
    >>> catalogo = CatalogoJogos([
    ...     Jogo(1, "A", date(2020, 1, 1), 0.0),
    ...     Jogo(2, "B", date(2020, 6, 1), 10.0),
    ...     Jogo(3, "C", date(2021, 3, 1), 20.0),
    ...     Jogo(4, "D", date(2021, 4, 1), 30.0),
    ... ])
    >>> len(catalogo)
    4
    >>> catalogo.percentual_gratuitos_pagos()
    {'gratuitos': 25.0, 'pagos': 75.0}
    >>> catalogo.anos_com_mais_lancamentos()
    [2020, 2021]
    """

    def __init__(self, jogos: Iterable[Jogo]):
        self._jogos: List[Jogo] = list(jogos)

    @classmethod
    def de_leitor(cls, leitor: LeitorBase) -> "CatalogoJogos":
        """Cria o catálogo a partir de qualquer leitor (qualquer distribuidor)."""
        return cls(leitor.ler())

    @classmethod
    def de_csv_steam(cls, caminho, estrito: bool = True) -> "CatalogoJogos":
        """Atalho para carregar um CSV no layout da Steam."""
        return cls.de_leitor(LeitorSteamCSV(caminho, estrito))

    def __len__(self) -> int:
        return len(self._jogos)

    def __iter__(self):
        return iter(self._jogos)

    def _exigir_nao_vazio(self) -> None:
        if not self._jogos:
            raise CatalogoVazioError("O catálogo não possui jogos.")

    # ------------------------------------------------------------------
    # Pergunta 1
    # ------------------------------------------------------------------
    def contagem_gratuitos_pagos(self) -> Dict[str, int]:
        """Quantidade de jogos gratuitos (preço 0) e pagos."""
        gratuitos = sum(1 for j in self._jogos if j.gratuito)
        return {"gratuitos": gratuitos, "pagos": len(self._jogos) - gratuitos}

    def percentual_gratuitos_pagos(self) -> Dict[str, float]:
        """Percentual de jogos gratuitos e pagos (soma 100).

        Levanta :class:`CatalogoVazioError` se não houver jogos.
        """
        self._exigir_nao_vazio()
        total = len(self._jogos)
        return {
            nome: 100 * qtd / total
            for nome, qtd in self.contagem_gratuitos_pagos().items()
        }

    # ------------------------------------------------------------------
    # Pergunta 2
    # ------------------------------------------------------------------
    def lancamentos_por_ano(self) -> Dict[int, int]:
        """Número de jogos lançados em cada ano, em ordem cronológica."""
        contagem = Counter(j.ano_lancamento for j in self._jogos)
        return dict(sorted(contagem.items()))

    def anos_com_mais_lancamentos(self) -> List[int]:
        """Anos com o maior número de lançamentos.

        Sempre devolve uma lista; em caso de empate, todos os anos
        empatados, em ordem crescente.
        """
        self._exigir_nao_vazio()
        por_ano = self.lancamentos_por_ano()
        maximo = max(por_ano.values())
        return [ano for ano, qtd in por_ano.items() if qtd == maximo]

    # ------------------------------------------------------------------
    # Pergunta 3 (proposta pelo estudante)
    # ------------------------------------------------------------------
    def aprovacao_por_faixa_de_preco(
        self, faixas: Sequence[FaixaPreco] = FAIXAS_PADRAO
    ) -> List[ResumoFaixa]:
        """Aprovação dos jogadores (avaliações positivas) por faixa de preço.

        Combina dois atributos (preço e avaliações). A aprovação de cada
        faixa é ``soma(positivas) / soma(positivas + negativas)``, ou seja,
        jogos com mais avaliações pesam mais. Jogos sem nenhuma avaliação
        contam em ``jogos`` mas não em ``jogos_avaliados``.

        Para mudar as faixas basta passar outras ``FaixaPreco``; para
        outra métrica, escreva outro método usando os mesmos atributos.
        """
        self._exigir_nao_vazio()
        resumos = []
        for faixa in faixas:
            jogos = [j for j in self._jogos if faixa.contem(j.preco)]
            avaliados = [j for j in jogos if j.total_avaliacoes > 0]
            resumos.append(
                ResumoFaixa(
                    faixa=faixa.nome,
                    jogos=len(jogos),
                    jogos_avaliados=len(avaliados),
                    positivas=sum(j.positivas for j in jogos),
                    negativas=sum(j.negativas for j in jogos),
                )
            )
        return resumos
