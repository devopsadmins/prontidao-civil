"""Gera a imagem de compartilhamento (1200x630) com o nível do dia a partir do data.json.
Uso: python3 -I og/og.py <data.json> <saida.png>"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).parent
FONTES = AQUI / "fonts"
COR = {"verde": (46, 138, 87), "amarelo": (221, 161, 21), "vermelho": (198, 55, 44)}
TINTA = {"verde": (255, 255, 255), "amarelo": (36, 26, 0), "vermelho": (255, 255, 255)}
NOME = {"verde": "VERDE", "amarelo": "AMARELO", "vermelho": "VERMELHO"}
PRESSAO = {"baixa": "BAIXA", "media": "MÉDIA", "alta": "ALTA"}
PAPEL, MUTED, GUERRA = (229, 236, 242), (147, 162, 177), (209, 69, 110)


def archivo(tam, peso, largura):
    f = ImageFont.truetype(str(FONTES / "Archivo.ttf"), tam)
    f.set_variation_by_axes([peso, largura])
    return f


def mono(tam):
    return ImageFont.truetype(str(FONTES / "IBMPlexMono-Medium.ttf"), tam)


def fundo_limpo():
    """A arte gerada traz pontos coloridos que não são dados reais; apaga-os."""
    cache = AQUI / "fundo-limpo.png"
    if cache.exists():
        return Image.open(cache).convert("RGB")
    img = Image.open(AQUI / "fundo.png").convert("RGB")
    hsv = img.convert("HSV")
    h, s, v = hsv.split()
    # Pontos quentes: saturados, claros e de matiz vermelho a âmbar.
    mask = Image.eval(s, lambda x: 255 if x > 90 else 0)
    quente = Image.eval(h, lambda x: 255 if (x < 45 or x > 225) else 0)
    claro = Image.eval(v, lambda x: 255 if x > 70 else 0)
    from PIL import ImageChops
    m = ImageChops.multiply(ImageChops.multiply(mask, quente), claro).filter(ImageFilter.MaxFilter(9))
    liso = img.filter(ImageFilter.GaussianBlur(10))
    img.paste(liso, mask=m)
    img.save(cache)
    return img


def main(dados, saida):
    d = json.loads(Path(dados).read_text(encoding="utf-8"))
    dia = d["dias"][-1]
    nivel = dia["nivel"]
    data = "/".join(reversed(dia["data"].split("-")))
    W, H = 1200, 630
    img = fundo_limpo().resize((W, H))
    dr = ImageDraw.Draw(img)

    # Placa do nível, à esquerda, com listras diagonais como no site.
    pw = 560
    placa = Image.new("RGB", (pw, H), COR[nivel])
    pd = ImageDraw.Draw(placa)
    sombra = tuple(int(c * 0.93) for c in COR[nivel])
    for x in range(-H, pw, 52):
        pd.polygon([(x, H), (x + 26, H), (x + 26 + H, 0), (x + H, 0)], fill=sombra)
    img.paste(placa, (0, 0))
    tinta = TINTA[nivel]
    dr.text((48, 52), "NÍVEL DO DIA", font=mono(22), fill=tinta)
    palavra = NOME[nivel]
    tam = 190
    while True:
        f = archivo(tam, 800, 62)
        if dr.textlength(palavra, font=f) <= pw - 96 or tam < 80:
            break
        tam -= 4
    dr.text((44, 330), palavra, font=f, fill=tinta, anchor="ls")
    extra = f" · intensidade {dia['intensidade']}" if dia.get("intensidade") else ""
    dr.text((48, 372), data + extra, font=mono(24), fill=tinta)
    # Escala de três degraus.
    for i, n in enumerate(["verde", "amarelo", "vermelho"]):
        x0 = 48 + i * 158
        box = (x0, 540, x0 + 146, 556)
        if list(COR).index(n) <= list(COR).index(nivel):
            dr.rectangle(box, fill=tinta)
        else:
            dr.rectangle(box, outline=tinta, width=3)

    # Lado direito: marca, pressão de guerra e endereço.
    x = pw + 48
    dr.text((x, 52), "MONITOR DE", font=archivo(40, 800, 75), fill=PAPEL)
    dr.text((x, 96), "PRONTIDÃO CIVIL", font=archivo(40, 800, 75), fill=PAPEL)
    if dia.get("guerra"):
        dr.text((x, 404), "PRESSÃO DE GUERRA NO MUNDO", font=mono(20), fill=MUTED)
        dr.text((x, 498), PRESSAO[dia["guerra"]], font=archivo(64, 800, 70), fill=GUERRA, anchor="ls")
    dr.text((x, 532), "Justificativa e fontes abertas", font=mono(20), fill=MUTED)
    dr.text((x, 562), "prontidao-civil.pages.dev", font=mono(22), fill=PAPEL)
    img.save(saida, "JPEG", quality=86, optimize=True, progressive=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
