"""Exceções específicas da biblioteca ``jogos``.

Todas herdam de :class:`JogosError`, de modo que quem usa a biblioteca
pode capturar qualquer falha prevista com um único ``except JogosError``.
"""


class JogosError(Exception):
    """Classe base de todas as exceções da biblioteca."""


class ArquivoDadosError(JogosError):
    """O arquivo de dados não existe ou não pôde ser lido."""


class ColunaAusenteError(JogosError):
    """O arquivo não possui uma coluna obrigatória no cabeçalho."""

    def __init__(self, coluna, caminho=None):
        self.coluna = coluna
        self.caminho = caminho
        onde = f" em '{caminho}'" if caminho else ""
        super().__init__(f"Coluna obrigatória ausente{onde}: '{coluna}'")


class RegistroInvalidoError(JogosError):
    """Uma linha do arquivo contém um valor que não pôde ser interpretado."""

    def __init__(self, numero_linha, motivo):
        self.numero_linha = numero_linha
        self.motivo = motivo
        super().__init__(f"Registro inválido (registro {numero_linha}): {motivo}")


class CatalogoVazioError(JogosError):
    """A consulta exige ao menos um jogo, mas o catálogo está vazio."""
