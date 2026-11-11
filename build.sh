#!/usr/bin/env bash
# Gera dist/ (versão pública) e publica no Cloudflare Pages.
# Uso: ./build.sh            -> só gera dist/
#      ./build.sh deploy     -> gera e publica
set -euo pipefail
cd "$(dirname "$0")"
python3 -I check.py
rm -rf dist && mkdir -p dist/geo
{
  printf '<!doctype html>\n<html lang="pt-BR">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<style>html{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%%}</style>\n'
  cat index.html
  printf '\n</html>\n'
} > dist/index.html
cp data.json dist/
cp geo/countries-110m.json geo/brasil-uf.json dist/geo/
# App instalável (PWA): manifesto, ícones e service worker com versão nova a cada build.
python3 -I pwa/icons.py dist/icons
cp pwa/manifest.webmanifest dist/
cp publico/* dist/
# Status curto para os outros apps da família (Boatos, Regeneração, Reserva da Casa) lerem sem baixar o data.json inteiro.
python3 -I - <<'PY'
import json, re
from pathlib import Path
d = json.loads(Path("data.json").read_text(encoding="utf-8"))
dia = d["dias"][-1]
frase = re.split(r"(?<=[.!?])\s", dia["motivo"].strip(), maxsplit=1)[0]
Path("dist/status.json").write_text(json.dumps({"nivel": dia["nivel"], "data": dia["data"], "hora": d.get("hora", ""), "resumo": frase}, ensure_ascii=False), encoding="utf-8")
PY
sed "s/__VERSAO__/$(date +%Y%m%d%H%M%S)/" pwa/sw.js > dist/sw.js
# Imagem de compartilhamento com o nível do dia; a versão na URL força as redes a buscarem a nova.
python3 -I og/og.py data.json dist/og.jpg
python3 -I - <<'EOF'
import json
from pathlib import Path
d = json.loads(Path("data.json").read_text(encoding="utf-8"))
dia = d["dias"][-1]
nivel = {"verde": "VERDE", "amarelo": "AMARELO", "vermelho": "VERMELHO"}[dia["nivel"]]
p = Path("dist/index.html")
s = p.read_text(encoding="utf-8")
titulo = f"Nível do dia: {nivel} · Monitor de Prontidão Civil"
for tag in ("og:title", "twitter:title"):
    attr = "property" if tag.startswith("og") else "name"
    s = s.replace(f'{attr}="{tag}" content="Monitor de Prontidão Civil"', f'{attr}="{tag}" content="{titulo}"')
s = s.replace("/og.jpg\"", f"/og.jpg?v={dia['data']}\"")
s = s.replace('property="og:description" content="', 'property="og:description" content="' + dia["motivo"].replace('"', "'")[:180].rsplit(" ", 1)[0] + "… ", 1) if len(dia["motivo"]) > 180 else s.replace('property="og:description" content="', 'property="og:description" content="' + dia["motivo"].replace('"', "'") + " ", 1)
# Placa do dia já preenchida no HTML: o texto aparece na primeira pintura, sem esperar o JavaScript.
import html as H
fmt = lambda x: "/".join(reversed(x.split("-"))) if len(x) == 10 else x
cor = {"verde": "var(--verde)", "amarelo": "var(--amarelo)", "vermelho": "var(--vermelho)"}[dia["nivel"]]
on = "var(--on-amarelo)" if dia["nivel"] == "amarelo" else "var(--on-sinal)"
sub = fmt(dia["data"]) + (" · intensidade " + dia["intensidade"] if dia.get("intensidade") else "")
upd = fmt(d.get("atualizado", "")) + (" às " + d["hora"] if d.get("hora") else "")
trocas = [
  ('<div class="signal" id="signal">', f'<div class="signal" id="signal" style="--lvl:{cor};--lvl-on:{on}">'),
  ('<div class="signal-word" id="sig-word">—</div>', f'<div class="signal-word" id="sig-word">{nivel.capitalize()}</div>'),
  ('<div class="signal-sub" id="sig-sub">carregando</div>', f'<div class="signal-sub" id="sig-sub">{H.escape(sub)}</div>'),
  ('<p class="lead" id="why">—</p>', f'<p class="lead" id="why">{H.escape(dia["motivo"])}</p>'),
  ('<span id="why-br">—</span>', f'<span id="why-br">{H.escape(dia.get("brasil", ""))}</span>'),
  ('<span id="upd" class="mono">—</span>', f'<span id="upd" class="mono">{H.escape(upd)}</span>'),
]
for velho, novo in trocas:
    assert s.count(velho) == 1, velho
    s = s.replace(velho, novo)
p.write_text(s, encoding="utf-8")
EOF
if [[ "${1:-}" == "deploy" ]]; then
  # A conta vem da variável de ambiente ou do arquivo local .cf-account (fora do git).
  CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-$(cat .cf-account 2>/dev/null)}" \
    npx -y wrangler@4 pages deploy dist --project-name prontidao-civil --branch main --commit-dirty=true
fi
