"""Tile slide screenshots into one contact sheet for review.
Usage: python3 tools/contact_sheet.py <dir with slide-XX.png> <out.png> [cols]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

src, out = Path(sys.argv[1]), sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
files = sorted(src.glob("slide-*.png"))
tw, th, pad = 640, 360, 16
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + 24) + pad), "#DDDDDD")
draw = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th))
    x, y = pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad + 24)
    sheet.paste(im, (x, y + 24))
    draw.text((x, y + 4), f.stem, fill="#000000")
sheet.save(out)
print("wrote", out)
