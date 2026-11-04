"""Gera os ícones do app (PWA) com a marca do monitor: três barras vermelho, amarelo e verde sobre fundo escuro.
Uso: python3 -I pwa/icons.py <pasta de saída>"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FUNDO = (13, 20, 27)
BARRAS = [(238, 91, 76), (240, 187, 55), (69, 181, 120)]


def icone(tam, margem):
    """margem: fração do lado deixada livre em volta da marca (maior no ícone 'maskable')."""
    img = Image.new("RGB", (tam, tam), FUNDO)
    d = ImageDraw.Draw(img)
    lado = tam * (1 - 2 * margem)
    x0, y0 = (tam - lado) / 2, (tam - lado) / 2
    gap = lado * 0.09
    h = (lado - 2 * gap) / 3
    for i, cor in enumerate(BARRAS):
        y = y0 + i * (h + gap)
        d.rounded_rectangle([x0, y, x0 + lado, y + h], radius=lado * 0.03, fill=cor)
    return img


saida = Path(sys.argv[1])
saida.mkdir(parents=True, exist_ok=True)
icone(192, .2).save(saida / "icon-192.png")
icone(512, .2).save(saida / "icon-512.png")
icone(512, .3).save(saida / "icon-maskable-512.png")
icone(180, .18).save(saida / "apple-touch-icon.png")
