# -*- coding: utf-8 -*-
"""Gera dados.js (rotinas + resumo de modulos) a partir do dataset."""
import re, json, io, sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LINHAS = open("dataset_limpo_kimi.txt", encoding="utf-8").read().splitlines()

MAPA_MODULO = {
    "cadastro unico": "Cadastros Únicos", "cadastro unicos": "Cadastros Únicos",
    "cadastros unico": "Cadastros Únicos", "cadastros únicos": "Cadastros Únicos",
    "recurso humanos": "Recursos Humanos", "folha de pagamento": "Recursos Humanos",
    "portal do cidadão": "Governo Digital", "portal do cidadão/autoatendimento": "Governo Digital",
    "gerenciamento do sistema": "Gerenciamento", "tarifa de água": "Arrecadação",
    "indicadores": "Menu Inicial", "alta gestão": "Menu Inicial",
    "benefícios": "Social", "educação": "Outros",
}

def sem_acento(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

MAPA_NORM = {sem_acento(k).lower(): v for k, v in MAPA_MODULO.items()}

def norm_modulo(seg):
    s = re.sub(r"^\d+\s*-\s*", "", seg).strip()
    return MAPA_NORM.get(sem_acento(s).lower(), s)

def limpa(txt):
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = txt.replace("Atende.net 1", "Atende.net").replace("Atende.Net", "Atende.net")
    return txt

def primeira_frase(txt, limite=210):
    m = re.match(r"(.{40,}?[.!?])(?:\s|$)", txt)
    out = m.group(1) if m else txt
    if len(out) > limite:
        corte = out[:limite].rsplit(" ", 1)[0]
        out = corte.rstrip(",;:") + "…"
    return out

rotinas = []
modulos = defaultdict(lambda: {"n": 0, "areas": Counter()})

for linha in LINHAS:
    if " | " not in linha:
        continue
    titulo, resto = linha.split(" | ", 1)
    titulo = limpa(titulo)
    m = re.search(r"Acess[íi]vel em: (.*?)(?:\.\s|\.$|$|(?=\s*(?:O que|Conheça|Nenhum|Através|Consulte)))", resto)
    caminho = limpa(m.group(1)) if m else ""
    caminho = caminho.replace("Nenhum conteúdo disponível", "").strip()
    caminho = re.sub(r"^\d+\s*-\s*", "", caminho)
    modulo, area = "Outros", ""
    if caminho:
        partes = [p.strip() for p in re.split(r"\s*>>?\s*", caminho) if p.strip()]
        if partes:
            modulo = norm_modulo(partes[0])
            if len(partes) > 1:
                area = partes[1]

    desc = ""
    corpo = resto.replace("Nenhum conteúdo disponível.", "")
    dq = re.search(r"O que [eé] isso\?\s*(.{60,})", corpo)
    pq = re.search(r"O que posso fazer aqui\?\s*(.{60,})", corpo)
    fonte = dq.group(1) if dq else (pq.group(1) if pq else "")
    if fonte:
        # corta antes do proximo rotulo de secao
        fonte = re.split(r"(?:Composi[çc][ãa]o da Tela|Como faço|Acesse também|Saiba mais)", fonte)[0]
        desc = limpa(primeira_frase(fonte))

    rotinas.append({"t": titulo, "m": modulo, "c": caminho, "d": desc})
    modulos[modulo]["n"] += 1
    if area:
        modulos[modulo]["areas"][area] += 1

resumo_mod = {}
for m, d in modulos.items():
    if d["n"] < 10:
        modulos["Outros"]["n"] += d["n"]
        modulos["Outros"]["areas"].update(d["areas"])
        for r in rotinas:
            if r["m"] == m:
                r["m"] = "Outros"
resumo_mod = {
    m: {"n": d["n"], "areas": [a for a, _ in d["areas"].most_common(8)]}
    for m, d in sorted(modulos.items(), key=lambda kv: -kv[1]["n"])
    if d["n"] >= 10 or m == "Outros"
}

saida = {
    "total": len(rotinas),
    "modulos": resumo_mod,
    "rotinas": rotinas,
}
with open("dados.js", "w", encoding="utf-8") as f:
    f.write("const DADOS = ")
    json.dump(saida, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

import os
print(f"rotinas: {len(rotinas)} | com descricao: {sum(1 for r in rotinas if r['d'])}")
print(f"modulos: {len(resumo_mod)} | tamanho dados.js: {os.path.getsize('dados.js')//1024} KB")
for m, d in resumo_mod.items():
    print(f"  {d['n']:4d} {m}")
