"""Leitores de arquivos de dados: transformam linhas de CSV em :class:`Jogo`.

Para suportar outro distribuidor (Epic, Paradox...) basta criar uma nova
subclasse de :class:`LeitorBase` (ou de :class:`LeitorSteamCSV`, trocando
o mapeamento de colunas). O restante da biblioteca não precisa mudar.
"""

import csv
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterator, List

from .excecoes import ArquivoDadosError, ColunaAusenteError, RegistroInvalidoError
from .modelos import Jogo

# Linhas do CSV da Steam têm descrições longas; remove o limite padrão.
csv.field_size_limit(2**31 - 1)


def converter_data(texto: str) -> date:
    """Converte datas da Steam para :class:`datetime.date`.

    Aceita ``"Oct 21, 2008"`` e ``"Oct 2008"`` (neste caso, dia 1).

    >>> converter_data("Oct 21, 2008")
    datetime.date(2008, 10, 21)
    >>> converter_data("Oct 2008")
    datetime.date(2008, 10, 1)
    >>> converter_data("ontem")
    Traceback (most recent call last):
        ...
    ValueError: Data em formato desconhecido: 'ontem'
    """
    texto = texto.strip()
    for formato in ("%b %d, %Y", "%b %Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ValueError(f"Data em formato desconhecido: {texto!r}")


def _para_bool(texto: str) -> bool:
    return texto.strip().lower() == "true"


class LeitorBase(ABC):
    """Contrato de todo leitor: iterar sobre objetos :class:`Jogo`."""

    @abstractmethod
    def ler(self) -> Iterator[Jogo]:
        """Gera os jogos do arquivo, um a um."""


class LeitorSteamCSV(LeitorBase):
    """Lê o arquivo ``steam_games.csv`` (ou uma amostra com o mesmo layout).

    Parâmetros
    ----------
    caminho:
        Caminho do arquivo CSV.
    estrito:
        Se ``True`` (padrão), a primeira linha inválida levanta
        :class:`RegistroInvalidoError`. Se ``False``, linhas inválidas são
        ignoradas e guardadas em :attr:`erros`.
    """

    COLUNAS = {
        "app_id": "AppID",
        "nome": "Name",
        "data_lancamento": "Release date",
        "preco": "Price",
        "positivas": "Positive",
        "negativas": "Negative",
        "windows": "Windows",
        "mac": "Mac",
        "linux": "Linux",
        "generos": "Genres",
    }
    """Mapeia cada atributo de :class:`Jogo` para o nome da coluna no arquivo."""

    def __init__(self, caminho, estrito: bool = True):
        self.caminho = Path(caminho)
        self.estrito = estrito
        self.erros: List[RegistroInvalidoError] = []

    def ler(self) -> Iterator[Jogo]:
        self.erros = []
        try:
            arquivo = open(self.caminho, encoding="utf-8", newline="")
        except OSError as erro:
            raise ArquivoDadosError(
                f"Não foi possível abrir '{self.caminho}': {erro.strerror}"
            ) from erro
        with arquivo:
            leitor = csv.DictReader(arquivo)
            self._validar_cabecalho(leitor.fieldnames)
            for numero, linha in enumerate(leitor, start=1):
                try:
                    yield self._converter(linha)
                except (ValueError, KeyError, TypeError) as erro:
                    problema = RegistroInvalidoError(numero, str(erro))
                    if self.estrito:
                        raise problema from erro
                    self.erros.append(problema)

    def _validar_cabecalho(self, cabecalho) -> None:
        cabecalho = cabecalho or []
        for coluna in self.COLUNAS.values():
            if coluna not in cabecalho:
                raise ColunaAusenteError(coluna, self.caminho)

    def _converter(self, linha: Dict[str, str]) -> Jogo:
        c = self.COLUNAS
        generos = tuple(g.strip() for g in linha[c["generos"]].split(",") if g.strip())
        return Jogo(
            app_id=int(linha[c["app_id"]]),
            nome=linha[c["nome"]],
            data_lancamento=converter_data(linha[c["data_lancamento"]]),
            preco=float(linha[c["preco"]]),
            positivas=int(linha[c["positivas"]]),
            negativas=int(linha[c["negativas"]]),
            windows=_para_bool(linha[c["windows"]]),
            mac=_para_bool(linha[c["mac"]]),
            linux=_para_bool(linha[c["linux"]]),
            generos=generos,
        )
