"""Monta o notebook da Fase I (execute depois com nbconvert, mantendo as saídas)."""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
md = lambda t: nbf.v4.new_markdown_cell(t)
code = lambda t: nbf.v4.new_code_cell(t)

nb.cells = [
md("""# Programação para Dados — Fase I
**Catálogo de jogos (Steam)** · consultas com a biblioteca `jogos` (sem pandas/numpy)

Estrutura do projeto:
- `jogos/modelos.py` — `Jogo` e `FaixaPreco` (dados do domínio, independentes do distribuidor)
- `jogos/leitores.py` — `LeitorBase` / `LeitorSteamCSV` (única parte que conhece o layout do CSV)
- `jogos/catalogo.py` — `CatalogoJogos` (consultas)
- `jogos/excecoes.py` — exceções próprias
- `tests/test_catalogo.py` — testes automatizados sobre a amostra de 20 jogos

Para suportar Epic ou Paradox basta criar outro leitor; as consultas não mudam."""),
code("""from pathlib import Path
from jogos import CatalogoJogos

RAIZ = Path.cwd()
ARQ_COMPLETO = RAIZ / "data" / "steam_games.csv"
ARQ_AMOSTRA = RAIZ / "data" / "amostra_20_jogos.csv\""""),
md("## 1. Testes automatizados (amostra de 20 jogos × cálculo manual em planilha)"),
code("""import unittest
suite = unittest.defaultTestLoader.discover(str(RAIZ / "tests"), top_level_dir=str(RAIZ))
resultado = unittest.TextTestRunner(verbosity=1).run(suite)
assert resultado.wasSuccessful()"""),
md("## 2. Funções de apresentação (mesmo código para amostra e arquivo completo)"),
code("""def responder(caminho):
    catalogo = CatalogoJogos.de_csv_steam(caminho)
    print(f"Arquivo: {Path(caminho).name} — {len(catalogo)} jogos\\n")

    # Pergunta 1
    perc, cont = catalogo.percentual_gratuitos_pagos(), catalogo.contagem_gratuitos_pagos()
    print("P1) Percentual de jogos gratuitos e pagos")
    print(f"    Gratuitos: {perc['gratuitos']:.2f}% ({cont['gratuitos']} jogos)")
    print(f"    Pagos:     {perc['pagos']:.2f}% ({cont['pagos']} jogos)\\n")

    # Pergunta 2
    por_ano, anos = catalogo.lancamentos_por_ano(), catalogo.anos_com_mais_lancamentos()
    print(f"P2) Ano(s) com mais lançamentos: {anos} — {por_ano[anos[0]]} jogos")
    print("    Lançamentos por ano:")
    maior = max(por_ano.values())
    for ano, qtd in por_ano.items():
        print(f"    {ano}  {qtd:>5}  {'#' * round(30 * qtd / maior)}")
    print()

    # Pergunta 3 (própria)
    print("P3) Aprovação dos jogadores (% de avaliações positivas) por faixa de preço")
    print(f"    {'Faixa':<16}{'Jogos':>7}{'Avaliados':>11}{'Positivas':>11}{'Negativas':>11}{'Aprovação':>11}")
    for r in catalogo.aprovacao_por_faixa_de_preco():
        aprov = "—" if r.aprovacao is None else f"{r.aprovacao:.2f}%"
        print(f"    {r.faixa:<16}{r.jogos:>7}{r.jogos_avaliados:>11}{r.positivas:>11}{r.negativas:>11}{aprov:>11}")"""),
md("## 3. Respostas sobre o arquivo completo"),
code("responder(ARQ_COMPLETO)"),
md("## 4. Respostas sobre a amostra (conferidas contra a planilha `docs/calculo_manual_amostra.xlsx`)"),
code("responder(ARQ_AMOSTRA)"),
md("""## 5. Facilidade de modificação
Uma nova faixa de preço, por exemplo, não exige alterar a biblioteca:"""),
code("""from jogos import FaixaPreco
inf = float("inf")
catalogo = CatalogoJogos.de_csv_steam(ARQ_COMPLETO)
for r in catalogo.aprovacao_por_faixa_de_preco([FaixaPreco("Até US$ 5", 0, 5), FaixaPreco("Acima de US$ 5", 5, inf)]):
    print(r.faixa, r.jogos, f"{r.aprovacao:.2f}%")"""),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).resolve().parent.parent / "Fase1_Programacao_para_Dados.ipynb")
