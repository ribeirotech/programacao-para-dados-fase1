# Programação para Dados — Fase I

Biblioteca `jogos` (somente biblioteca padrão do Python) para consultas sobre catálogos de jogos.

## Estrutura
- `jogos/` — biblioteca: `modelos.py` (Jogo, FaixaPreco), `leitores.py` (leitor do CSV da Steam; ponto de extensão para Epic/Paradox), `catalogo.py` (consultas), `excecoes.py`
- `data/steam_games.csv` — arquivo completo · `data/amostra_20_jogos.csv` — amostra de testes (20 jogos aleatórios, fora dos 20 primeiros)
- `docs/calculo_manual_amostra.xlsx` — cálculo manual (planilha) dos resultados esperados na amostra
- `tests/test_catalogo.py` — testes automatizados + doctests
- `Fase1_Programacao_para_Dados.ipynb` — respostas das 3 perguntas (já executado)
- `principal.py` — mesmas respostas pela linha de comando
- `scripts/` — scripts usados para gerar a amostra, a planilha e o notebook

## Como executar (na raiz do projeto, Python 3.8+)
    python -m unittest discover -s tests -v     # testes (amostra)
    python principal.py                         # arquivo completo
    python principal.py data/amostra_20_jogos.csv
O notebook deve ser aberto com a raiz do projeto como diretório de trabalho.
