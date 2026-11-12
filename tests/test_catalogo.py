"""Testes automatizados da biblioteca ``jogos``.

Os valores esperados para a amostra de 20 jogos foram calculados
manualmente em planilha (``docs/calculo_manual_amostra.xlsx``) e escritos
aqui como constantes, independentes do código testado.

Execução (a partir da raiz do projeto)::

    python -m unittest discover -s tests -v
"""

import doctest
import tempfile
import unittest
from datetime import date
from pathlib import Path

import jogos.catalogo
import jogos.leitores
import jogos.modelos
from jogos import (
    ArquivoDadosError, CatalogoJogos, CatalogoVazioError, ColunaAusenteError,
    FaixaPreco, Jogo, JogosError, LeitorSteamCSV, RegistroInvalidoError,
)

RAIZ = Path(__file__).resolve().parent.parent
AMOSTRA = RAIZ / "data" / "amostra_20_jogos.csv"

# ---- Gabarito da planilha de conferência manual -------------------------
ESPERADO_TOTAL = 20
ESPERADO_GRATUITOS = 2
ESPERADO_PAGOS = 18
ESPERADO_PERC_GRATUITOS = 10.0
ESPERADO_PERC_PAGOS = 90.0
ESPERADO_ANOS_MAIS_LANCAMENTOS = [2021]
ESPERADO_LANCAMENTOS_2021 = 5
# faixa: (jogos, avaliados, positivas, negativas, aprovação %)
ESPERADO_FAIXAS = {
    "Gratuito": (2, 1, 26, 15, 63.4146341463415),
    "Até US$ 10": (10, 9, 742, 229, 76.4160659114315),
    "US$ 10 a 30": (8, 8, 5550, 1004, 84.6811107720476),
    "Acima de US$ 30": (0, 0, 0, 0, None),
}


def load_tests(loader, tests, ignore):
    """Inclui os doctests dos módulos na execução do unittest."""
    for modulo in (jogos.catalogo, jogos.leitores, jogos.modelos):
        tests.addTests(doctest.DocTestSuite(modulo))
    return tests


class TestAmostra(unittest.TestCase):
    """Respostas do sistema sobre a amostra == cálculo manual."""

    @classmethod
    def setUpClass(cls):
        cls.catalogo = CatalogoJogos.de_csv_steam(AMOSTRA)

    def test_amostra_tem_20_jogos(self):
        self.assertEqual(len(self.catalogo), ESPERADO_TOTAL)

    def test_pergunta1_contagem(self):
        self.assertEqual(
            self.catalogo.contagem_gratuitos_pagos(),
            {"gratuitos": ESPERADO_GRATUITOS, "pagos": ESPERADO_PAGOS},
        )

    def test_pergunta1_percentual(self):
        perc = self.catalogo.percentual_gratuitos_pagos()
        self.assertAlmostEqual(perc["gratuitos"], ESPERADO_PERC_GRATUITOS)
        self.assertAlmostEqual(perc["pagos"], ESPERADO_PERC_PAGOS)
        self.assertAlmostEqual(sum(perc.values()), 100.0)

    def test_pergunta2_ano_com_mais_lancamentos(self):
        self.assertEqual(
            self.catalogo.anos_com_mais_lancamentos(), ESPERADO_ANOS_MAIS_LANCAMENTOS
        )
        self.assertEqual(
            self.catalogo.lancamentos_por_ano()[2021], ESPERADO_LANCAMENTOS_2021
        )

    def test_pergunta3_aprovacao_por_faixa(self):
        resumos = {r.faixa: r for r in self.catalogo.aprovacao_por_faixa_de_preco()}
        self.assertEqual(set(resumos), set(ESPERADO_FAIXAS))
        for nome, (jogos_, aval, pos, neg, aprov) in ESPERADO_FAIXAS.items():
            with self.subTest(faixa=nome):
                r = resumos[nome]
                self.assertEqual(
                    (r.jogos, r.jogos_avaliados, r.positivas, r.negativas),
                    (jogos_, aval, pos, neg),
                )
                if aprov is None:
                    self.assertIsNone(r.aprovacao)
                else:
                    self.assertAlmostEqual(r.aprovacao, aprov, places=9)

    def test_amostra_nao_contem_os_20_primeiros_jogos(self):
        completo = RAIZ / "data" / "steam_games.csv"
        if not completo.exists():
            self.skipTest("arquivo completo não disponível")
        primeiros = {j.app_id for j, _ in zip(LeitorSteamCSV(completo).ler(), range(20))}
        ids_amostra = {j.app_id for j in self.catalogo}
        self.assertFalse(primeiros & ids_amostra)


class TestRegrasDeNegocio(unittest.TestCase):
    """Casos limite com catálogos sintéticos pequenos."""

    def test_empate_retorna_lista_ordenada(self):
        cat = CatalogoJogos([
            Jogo(1, "A", date(2021, 1, 1), 1.0),
            Jogo(2, "B", date(2019, 1, 1), 1.0),
            Jogo(3, "C", date(2021, 5, 5), 1.0),
            Jogo(4, "D", date(2019, 9, 9), 1.0),
            Jogo(5, "E", date(2020, 2, 2), 1.0),
        ])
        self.assertEqual(cat.anos_com_mais_lancamentos(), [2019, 2021])

    def test_todos_gratuitos(self):
        cat = CatalogoJogos([Jogo(1, "A", date(2020, 1, 1), 0.0)])
        self.assertEqual(cat.percentual_gratuitos_pagos(),
                         {"gratuitos": 100.0, "pagos": 0.0})

    def test_catalogo_vazio_levanta_excecao(self):
        cat = CatalogoJogos([])
        for consulta in (cat.percentual_gratuitos_pagos,
                         cat.anos_com_mais_lancamentos,
                         cat.aprovacao_por_faixa_de_preco):
            with self.subTest(consulta=consulta.__name__):
                with self.assertRaises(CatalogoVazioError):
                    consulta()

    def test_faixas_personalizadas(self):
        cat = CatalogoJogos([
            Jogo(1, "A", date(2020, 1, 1), 5.0, 9, 1),
            Jogo(2, "B", date(2020, 1, 1), 50.0, 1, 1),
        ])
        faixas = [FaixaPreco("Barato", 0, 10), FaixaPreco("Caro", 10, float("inf"))]
        r = {x.faixa: x.aprovacao for x in cat.aprovacao_por_faixa_de_preco(faixas)}
        self.assertAlmostEqual(r["Barato"], 90.0)
        self.assertAlmostEqual(r["Caro"], 50.0)


class TestLeitor(unittest.TestCase):
    """Tratamento de erros na leitura de arquivos."""

    CABECALHO = "AppID,Name,Release date,Price,Positive,Negative,Windows,Mac,Linux,Genres\n"

    def _arquivo(self, conteudo):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        caminho = Path(pasta.name) / "dados.csv"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def test_arquivo_inexistente(self):
        with self.assertRaises(ArquivoDadosError):
            CatalogoJogos.de_csv_steam(RAIZ / "nao_existe.csv")

    def test_coluna_ausente(self):
        caminho = self._arquivo("AppID,Name\n1,A\n")
        with self.assertRaises(ColunaAusenteError):
            CatalogoJogos.de_csv_steam(caminho)

    def test_registro_invalido_modo_estrito(self):
        caminho = self._arquivo(self.CABECALHO + "1,A,Oct 21 2008,abc,0,0,True,False,False,Action\n")
        with self.assertRaises(RegistroInvalidoError) as ctx:
            CatalogoJogos.de_csv_steam(caminho)
        self.assertEqual(ctx.exception.numero_linha, 1)

    def test_registro_invalido_modo_tolerante(self):
        caminho = self._arquivo(
            self.CABECALHO
            + "1,A,Oct 21 2008,abc,0,0,True,False,False,Action\n"
            + "2,B,Oct 2008,9.99,5,1,True,False,False,\"Action,Indie\"\n"
        )
        leitor = LeitorSteamCSV(caminho, estrito=False)
        cat = CatalogoJogos.de_leitor(leitor)
        self.assertEqual(len(cat), 1)
        self.assertEqual(len(leitor.erros), 1)
        jogo = next(iter(cat))
        self.assertEqual(jogo.data_lancamento, date(2008, 10, 1))  # "Oct 2008"
        self.assertEqual(jogo.generos, ("Action", "Indie"))

    def test_todas_as_excecoes_herdam_de_jogos_error(self):
        for exc in (ArquivoDadosError, ColunaAusenteError,
                    RegistroInvalidoError, CatalogoVazioError):
            self.assertTrue(issubclass(exc, JogosError))


if __name__ == "__main__":
    unittest.main()
