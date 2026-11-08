"""Gera a miniatura de divulgação a partir de uma captura REAL do dashboard.

Uso: python codigo/gerar_miniatura.py
Requer Pillow e entregaveis/Preview_Case03.png.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path('/usr/share/fonts/truetype/lato')


def font(size, bold=False, heavy=False):
    kind = 'Lato-Heavy.ttf' if heavy else 'Lato-Bold.ttf' if bold else 'Lato-Regular.ttf'
    if (FONTS / kind).exists():
        return ImageFont.truetype(str(FONTS / kind), size)
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def build():
    source = ROOT / 'entregaveis' / 'Preview_Case03.png'
    target = ROOT / 'entregaveis' / 'Miniatura_LinkedIn_Case03.png'
    if not source.exists():
        raise FileNotFoundError(f'Primeiro gere uma captura real: {source}')

    W, H = 1200, 630
    bg = Image.new('RGB', (W, H), '#fcfaf7')
    d = ImageDraw.Draw(bg)
    # Uma peça editorial, não um dashboard falso: o lado direito é captura real.
    d.rectangle((0, 0, 11, H), fill='#bd673f')
    d.rounded_rectangle((44, 52, 108, 116), radius=14, fill='#bd673f')
    d.text((57, 69), 'WL', fill='#fff', font=font(27, heavy=True))
    d.text((126, 70), 'PORTFÓLIO TÉCNICO', fill='#6d6c69', font=font(16, bold=True))
    d.text((47, 157), 'CASE 03  /  FINANÇAS', fill='#b56036', font=font(17, bold=True))
    d.text((45, 219), 'Inteligência', fill='#252a2f', font=font(57, heavy=True))
    d.text((45, 291), 'Financeira', fill='#252a2f', font=font(57, heavy=True))
    d.rectangle((47, 379, 192, 384), fill='#c56b43')
    d.text((47, 418), 'DRE  ·  ORÇAMENTO  ·  FORECAST', fill='#695f59', font=font(19, bold=True))
    d.text((47, 459), 'Python  /  Business Intelligence', fill='#6c7074', font=font(18))
    d.rounded_rectangle((47, 535, 432, 582), radius=11, fill='#f7eee6')
    d.text((63, 550), 'ESTUDO 100% SINTÉTICO', fill='#ad5c38', font=font(16, bold=True))

    shot = Image.open(source).convert('RGB')
    # Enquadra o cabeçalho, KPIs e três painéis reais do projeto.
    sw, sh = shot.size
    crop = shot.crop((int(sw * .01), int(sh * .02), int(sw * .99), min(sh, int(sh * .99))))
    thumb = crop.resize((724, 410), Image.Resampling.LANCZOS)
    # Sombra suave de tela.
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((513, 103, 1190, 532), radius=17, fill=(65, 40, 28, 64))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    bg = Image.alpha_composite(bg.convert('RGBA'), shadow)
    # Recorte lateral com resolução nativa, sem criar dados nem gráficos.
    x, y, cw, ch = 506, 94, 661, 427
    crop_display = thumb.crop((0, 0, cw, ch))
    rounded_mask = Image.new('L', (cw, ch), 0)
    md = ImageDraw.Draw(rounded_mask)
    md.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=14, fill=255)
    bg.paste(crop_display, (x, y), rounded_mask)
    final_draw = ImageDraw.Draw(bg)
    final_draw.rounded_rectangle((x, y, x + cw, y + ch), radius=14, outline='#e5d6cb', width=3)
    final_draw.text((538, 552), 'Dashboard interativo · visão executiva', fill='#8a6351', font=font(17, bold=True))
    bg.convert('RGB').save(target, 'PNG', optimize=True)
    return target


if __name__ == '__main__':
    print('Miniatura:', build())
