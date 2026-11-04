# Monitor de Prontidão Civil

Site público: https://prontidao-civil.pages.dev

Painel que acompanha orientações de defesa civil e estoque doméstico em 14 países, a pressão de guerra por conflito, ataques cibernéticos e o El Niño (pela classificação oficial da NOAA e do Painel El Niño do Inmet). Classifica cada dia em VERDE, AMARELO ou VERMELHO com critérios fixos e públicos.

## Como funciona

- Um relatório diário e uma sentinela a cada 2 horas (agentes do Claude Code) pesquisam fontes oficiais e de imprensa séria e atualizam `data.json` só quando há mudança.
- `check.py` valida o formato do `data.json` e barra dado pessoal antes de qualquer publicação.
- `build.sh` gera `dist/` (página, PWA, imagem de compartilhamento com o nível do dia) e, com `deploy`, publica no Cloudflare Pages.

## Arquivos

| Arquivo | O que é |
|---|---|
| `index.html` | Página (D3 + TopoJSON, sem build de front) |
| `data.json` | Todos os dados exibidos, abertos para conferência |
| `check.py` | Validação antes de publicar |
| `build.sh` | Gera e publica |
| `geo/` | Contornos de países (Natural Earth via world-atlas) e estados do Brasil |
| `og/` | Gera a imagem de compartilhamento |
| `pwa/` | Manifesto, ícones e service worker |

## Rodar localmente

```bash
./build.sh
python3 -m http.server 8765 --directory dist
```

Para publicar, defina `CLOUDFLARE_ACCOUNT_ID` (ou crie `.cf-account`) e rode `./build.sh deploy`.

## Fontes de clima e tempo no Brasil

Cemaden, CPTEC/INPE, Inmet (Painel El Niño) e IPMet/Unesp.

Não é alerta oficial. Em emergência, siga a Defesa Civil (199) e o alerta por SMS (CEP para 40199).
