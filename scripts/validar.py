# -*- coding: utf-8 -*-
"""Valida dados.js e simula a logica de busca do app.js."""
import json, re, unicodedata, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

src = open("dados.js", encoding="utf-8").read()
assert src.startswith("const DADOS = ") and src.rstrip().endswith(";")
d = json.loads(src[len("const DADOS = "):].rstrip().rstrip(";"))

print("total:", d["total"], "| modulos:", len(d["modulos"]))
assert d["total"] == len(d["rotinas"])
for r in d["rotinas"]:
    assert set(r.keys()) == {"t", "m", "c", "d"}, r.keys()
    assert r["m"] in d["modulos"], r["m"]

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()

def busca(termo, mod=""):
    termo = sem_acento(termo)
    out = []
    for r in d["rotinas"]:
        if mod and r["m"] != mod:
            continue
        chave = sem_acento(r["t"] + " " + r["c"] + " " + r["d"])
        if termo and termo not in chave:
            continue
        out.append(r)
    return out

for q in ["férias", "ferias", "IPTU", "centro de custo", "ponto", "certidão",
          "ouvidoria", "empenho", "salários"]:
    rs = busca(q)
    print(f"busca {q!r}: {len(rs)} resultados | 1o: {rs[0]['t'] if rs else '-'}")

rs = busca("", "Arrecadação")
print("filtro modulo Arrecadação:", len(rs), "rotinas")

# sem duplicatas exatas de titulo+caminho
vistos = set()
dup = 0
for r in d["rotinas"]:
    k = (r["t"], r["c"])
    if k in vistos:
        dup += 1
    vistos.add(k)
print("duplicatas titulo+caminho:", dup)
print("OK")
