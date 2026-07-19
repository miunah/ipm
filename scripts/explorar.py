# -*- coding: utf-8 -*-
"""Explora o dataset: extrai definicoes 'O que e isso?' e estatisticas de modulos."""
import re, sys, io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

linhas = open("dataset_limpo_kimi.txt", encoding="utf-8").read().splitlines()
print(f"total linhas: {len(linhas)}")

def parse(linha):
    if " | " not in linha:
        return None
    titulo, resto = linha.split(" | ", 1)
    m = re.search(r"Acess[íi]vel em: (.*?)(?:\.\s|\.$|$)", resto)
    caminho = m.group(1).strip() if m else ""
    return titulo.strip(), resto, caminho

# modulos (normaliza "1 - X" -> "X")
modulos = Counter()
areas = defaultdict(Counter)
for l in linhas:
    p = parse(l)
    if not p or not p[2]:
        continue
    partes = [s.strip() for s in p[2].split(">>")]
    mod = re.sub(r"^\d+\s*-\s*", "", partes[0])
    modulos[mod] += 1
    if len(partes) > 1:
        areas[mod][partes[1]] += 1

print("\n== MODULOS ==")
for m, c in modulos.most_common():
    print(f"{c:5d}  {m}")

print("\n== AREAS por modulo (top 6) ==")
for m, _ in modulos.most_common(14):
    tops = ", ".join(f"{a} ({c})" for a, c in areas[m].most_common(6))
    print(f"{m}: {tops}")

# definicoes "O que e isso?"
print("\n== DEFINICOES 'O que e isso?' ==")
defs = []
for l in linhas:
    p = parse(l)
    if not p:
        continue
    titulo, resto, _ = p
    m = re.search(r"O que [eé] isso\?\s*(.{60,450}?)(?:[A-Z][a-zç]+ [a-zç]+:|O que posso|Composi|$)", resto)
    if m:
        defs.append((titulo, re.sub(r"\s+", " ", m.group(1)).strip()))
print(f"total definicoes: {len(defs)}")
for t, d in defs:
    print(f"\n### {t}\n{d[:400]}")
