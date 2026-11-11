"""Confere data.json antes de publicar. Sai com erro e não deixa publicar se algo estiver fora do formato."""
import json
import re
import sys
from pathlib import Path

DADOS = Path(__file__).with_name("data.json")
NIVEIS = {"verde", "amarelo", "vermelho"}
GUERRA = {"latente", "elevada", "ativa"}
PRESSAO = {"baixa", "media", "alta"}
CIBER = {"monitorar", "grave", "critico"}
CLIMA = {"neutro", "fraco", "moderado", "forte", "muito forte"}
# O site é público: nada da casa ou da família pode aparecer nele.
PROIBIDO = re.compile(r"\b(everton|esposa|marido|filh[oa]s?|nossa casa|plano\.md|preparacao-casa|são josé dos campos.*casa)\b", re.I)

erros = []
try:
    texto = DADOS.read_text(encoding="utf-8")
    d = json.loads(texto)
except Exception as e:
    sys.exit(f"data.json inválido: {e}")

if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d.get("atualizado", "")):
    erros.append("campo 'atualizado' sem data AAAA-MM-DD")
dias = d.get("dias") or []
if not dias:
    erros.append("lista 'dias' vazia")
elif dias[-1].get("data") != d.get("atualizado"):
    erros.append("o último item de 'dias' não é a data de 'atualizado'")
for x in dias:
    if x.get("nivel") not in NIVEIS:
        erros.append(f"dia {x.get('data')}: nível inválido {x.get('nivel')!r}")
    if x.get("guerra") is not None and x["guerra"] not in PRESSAO:
        erros.append(f"dia {x.get('data')}: pressão de guerra inválida {x['guerra']!r}")
    if x.get("ciber") is not None and x["ciber"] not in PRESSAO:
        erros.append(f"dia {x.get('data')}: pressão cibernética inválida {x['ciber']!r}")
    if not x.get("motivo"):
        erros.append(f"dia {x.get('data')}: sem motivo")

def eventos(dono, lista):
    for e in lista:
        if not str(e.get("url", "")).startswith(("https://", "http://")):
            erros.append(f"{dono}: evento sem link válido ({e.get('titulo')!r})")
        if e.get("tipo") not in {"oficial", "imprensa"}:
            erros.append(f"{dono}: tipo de fonte inválido {e.get('tipo')!r}")

for x in d.get("locais", []) + d.get("blocos", []):
    if x.get("nivel") not in NIVEIS:
        erros.append(f"{x.get('nome')}: nível inválido {x.get('nivel')!r}")
    eventos(x.get("nome"), x.get("eventos", []))
for t in d.get("guerra", []):
    if t.get("nivel") not in GUERRA:
        erros.append(f"{t.get('nome')}: pressão inválida {t.get('nivel')!r}")
    if not t.get("paises"):
        erros.append(f"{t.get('nome')}: sem países")
    eventos(t.get("nome"), t.get("eventos", []))

for k in d.get("ciber", []):
    if k.get("nivel") not in CIBER:
        erros.append(f"{k.get('nome')}: gravidade cibernética inválida {k.get('nivel')!r}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", k.get("data", "")):
        erros.append(f"{k.get('nome')}: data inválida")
    if k.get("atribuicao") not in {"oficial", "imprensa", "desconhecida"}:
        erros.append(f"{k.get('nome')}: atribuição inválida {k.get('atribuicao')!r}")
    if not k.get("paises"):
        erros.append(f"{k.get('nome')}: sem países")
    eventos(k.get("nome"), k.get("eventos", []))

for b in d.get("boatos", []):
    if b.get("veredito") not in {"falso", "fora de contexto", "enganoso"}:
        erros.append(f"boato {b.get('id')}: veredito inválido {b.get('veredito')!r}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", b.get("data", "")):
        erros.append(f"boato {b.get('id')}: data inválida")
    if not b.get("diz") or not b.get("verdade"):
        erros.append(f"boato {b.get('id')}: falta o que circula ou a verdade")
    if not b.get("eventos"):
        erros.append(f"boato {b.get('id')}: sem fonte do desmentido")
    eventos(f"boato {b.get('id')}", b.get("eventos", []))

for c in d.get("clima", []):
    if c.get("nivel") not in NIVEIS:
        erros.append(f"{c.get('nome')}: nível inválido {c.get('nivel')!r}")
    if c.get("classificacao") not in CLIMA:
        erros.append(f"{c.get('nome')}: classificação inválida {c.get('classificacao')!r}")
    eventos(c.get("nome"), c.get("eventos", []))
    for rg in c.get("regioes", []):
        if rg.get("efeito") not in {"chuva", "seca", "misto"}:
            erros.append(f"{c.get('nome')}: efeito inválido {rg.get('efeito')!r}")
        if not rg.get("paises"):
            erros.append(f"{c.get('nome')}: região sem países")
    for u in c.get("brasil_uf", []):
        if u.get("efeito") not in {"chuva", "seca", "misto", "normal"}:
            erros.append(f"{c.get('nome')}: efeito inválido em {u.get('uf')!r}")
        if not u.get("resumo"):
            erros.append(f"{c.get('nome')}: {u.get('uf')!r} sem resumo")
        for n in u.get("noticias", []):
            dono = f"{u.get('uf')} notícia {n.get('titulo')!r}"
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", n.get("data", "")):
                erros.append(f"{dono}: data inválida")
            if n.get("gravidade") not in {"alerta", "atencao", "informativo"}:
                erros.append(f"{dono}: gravidade inválida {n.get('gravidade')!r}")
            if n.get("impacto") not in {"chuva", "seca", "calor", "fogo", "agro", "abastecimento", "saude", "outro"}:
                erros.append(f"{dono}: impacto inválido {n.get('impacto')!r}")
            if n.get("atribuicao") not in {"oficial", "imprensa", "contexto"}:
                erros.append(f"{dono}: atribuição inválida {n.get('atribuicao')!r}")
        eventos(f"notícias de {u.get('uf')}", u.get("noticias", []))

achado = PROIBIDO.search(texto)
if achado:
    erros.append(f"dado da casa ou da família no texto público: {achado.group(0)!r}")

if erros:
    sys.exit("data.json reprovado:\n- " + "\n- ".join(erros))
print(f"data.json ok: {len(dias)} dias, {len(d.get('locais', []))} locais, {len(d.get('guerra', []))} conflitos")
