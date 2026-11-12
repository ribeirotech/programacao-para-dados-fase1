"""Gera UMA VEZ a amostra aleatória de 20 jogos usada nos testes.

Os 20 primeiros registros do arquivo são excluídos do sorteio (exigência
do enunciado). A semente fixa torna o sorteio reproduzível, mas a amostra
já gerada é guardada em ``data/amostra_20_jogos.csv`` e entregue junto.
"""

import csv
import random
import sys
from pathlib import Path

csv.field_size_limit(2**31 - 1)
SEMENTE = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
RAIZ = Path(__file__).resolve().parent.parent

with open(RAIZ / "data" / "steam_games.csv", encoding="utf-8", newline="") as f:
    leitor = csv.reader(f)
    cabecalho = next(leitor)
    registros = list(leitor)

candidatos = registros[20:]  # fora dos 20 jogos iniciais
amostra = random.Random(SEMENTE).sample(candidatos, 20)

destino = RAIZ / "data" / "amostra_20_jogos.csv"
if "--gravar" in sys.argv:
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecalho)
        escritor.writerows(amostra)
    print("Gravado em", destino)
else:
    for r in amostra:
        print(r[0], r[1][:30], r[2], r[6], r[22], r[23])
