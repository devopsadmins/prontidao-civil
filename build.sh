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
p.write_text(s, encoding="utf-8")
EOF
if [[ "${1:-}" == "deploy" ]]; then
  # A conta vem da variável de ambiente ou do arquivo local .cf-account (fora do git).
  CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-$(cat .cf-account 2>/dev/null)}" \
    npx -y wrangler@4 pages deploy dist --project-name prontidao-civil --branch main --commit-dirty=true
fi
