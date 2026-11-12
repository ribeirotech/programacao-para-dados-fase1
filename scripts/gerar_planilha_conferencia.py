"""Gera a planilha de conferência manual da amostra (fórmulas de planilha).

As fórmulas calculam as respostas esperadas SEM usar o módulo ``jogos``,
servindo como gabarito independente para os testes automatizados.
"""

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

csv.field_size_limit(2**31 - 1)
RAIZ = Path(__file__).resolve().parent.parent
with open(RAIZ / "data" / "amostra_20_jogos.csv", encoding="utf-8", newline="") as f:
    linhas = list(csv.DictReader(f))

wb = Workbook()
ws = wb.active
ws.title = "Amostra"
ws.append(["AppID", "Nome", "Data de lançamento", "Ano", "Preço", "Gratuito (1/0)",
           "Positivas", "Negativas", "Faixa de preço"])
for i, r in enumerate(linhas, start=2):
    ws.append([int(r["AppID"]), r["Name"], r["Release date"],
               f"=VALUE(RIGHT(C{i},4))", float(r["Price"]), f"=IF(E{i}=0,1,0)",
               int(r["Positive"]), int(r["Negative"]),
               f'=IF(E{i}=0,"Gratuito",IF(E{i}<=10,"Até US$ 10",IF(E{i}<=30,"US$ 10 a 30","Acima de US$ 30")))'])
ultima = len(linhas) + 1
for c in ws[1]:
    c.font = Font(bold=True)

res = wb.create_sheet("Resultados")
res.append(["Pergunta 1", "Valor"])
res.append(["Total de jogos", f"=COUNTA(Amostra!A2:A{ultima})"])
res.append(["Gratuitos", f"=SUM(Amostra!F2:F{ultima})"])
res.append(["Pagos", "=B2-B3"])
res.append(["% gratuitos", "=100*B3/B2"])
res.append(["% pagos", "=100*B4/B2"])
res.append([])
res.append(["Pergunta 2", "Ano", "Jogos lançados"])
anos = sorted({int(r["Release date"][-4:]) for r in linhas})
inicio = res.max_row + 1
for ano in anos:
    n = res.max_row + 1
    res.append(["", ano, f"=COUNTIF(Amostra!D2:D{ultima},B{n})"])
fim = res.max_row
res.append(["Máximo de lançamentos", "", f"=MAX(C{inicio}:C{fim})"])
res.append([])
res.append(["Pergunta 3", "Jogos", "Avaliados", "Positivas", "Negativas", "% aprovação"])
for faixa in ("Gratuito", "Até US$ 10", "US$ 10 a 30", "Acima de US$ 30"):
    n = res.max_row + 1
    res.append([faixa,
                f'=COUNTIF(Amostra!I2:I{ultima},A{n})',
                f'=COUNTIFS(Amostra!I2:I{ultima},A{n},Amostra!G2:G{ultima},">0")+COUNTIFS(Amostra!I2:I{ultima},A{n},Amostra!G2:G{ultima},0,Amostra!H2:H{ultima},">0")',
                f'=SUMIF(Amostra!I2:I{ultima},A{n},Amostra!G2:G{ultima})',
                f'=SUMIF(Amostra!I2:I{ultima},A{n},Amostra!H2:H{ultima})',
                f'=IF(D{n}+E{n}=0,"sem avaliações",100*D{n}/(D{n}+E{n}))'])
for linha in res.iter_rows():
    if linha[0].value and str(linha[0].value).startswith("Pergunta"):
        for c in linha:
            c.font = Font(bold=True)
res.column_dimensions["A"].width = 26
wb.save(RAIZ / "docs" / "calculo_manual_amostra.xlsx")
