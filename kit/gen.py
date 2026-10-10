# Renders the profile README's two images as SVG, text set as IBM Plex Mono
# outlines (SIL OFL) so they look the same everywhere. Palette from Immiscible.
# Run: python3 kit/gen.py <dir with IBMPlexMono-*.ttf> <out dir>
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = {w: TTFont(f"{sys.argv[1]}/IBMPlexMono-{w}.ttf") for w in ("Regular", "Medium")}
OUT = sys.argv[2]

def text(s, x, y, size, fill, weight="Regular"):
    f = FONTS[weight]; gs = f.getGlyphSet(); cmap = f.getBestCmap(); k = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs); cx = 0.0
    for c in s:
        n = cmap.get(ord(c))
        if n:
            gs[n].draw(TransformPen(pen, (k, 0, 0, -k, x + cx, y)))
        cx += (gs[n].width if n else 600) * k
    d = pen.getCommands()
    return f'<path fill="{fill}" d="{d}"/>' if d else ""

def adv(size):  # monospace advance
    f = FONTS["Regular"]; return f["hmtx"]["zero"][0] * size / f["head"].unitsPerEm

def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}"><title>{label}</title>{body}</svg>\n')

CORAL, PAPER = "#F0563A", "#F7F8FA"

# Small hand-drawn marks; Plex Mono has no check or cross glyph.
def tick(x, y, c):  return f'<path d="M{x} {y-5}l3.2 3.6 6.3-8" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
def cross(x, y, c): return f'<path d="M{x+1} {y-10}l7.5 8M{x+8.5} {y-10}l-7.5 8" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>'
def mark(x, y, s, back):  # Immiscible's cardinal squares, viewBox 32
    k = s / 32
    return (f'<g transform="translate({x} {y}) scale({k})"><path fill="{back}" fill-rule="evenodd" d="M0 0H24V24H0ZM4 4V20H20V4Z"/>'
            f'<path fill="{CORAL}" fill-rule="evenodd" d="M8 8H32V32H8ZM12 12V28H28V12Z"/><path fill="{back}" d="M20 6H24V14H20Z"/></g>')

def terminal():
    W, H, bg, bar, dim, ink = 840, 236, "#0F1631", "#17214A", "#8790B4", "#E9ECF4"
    s, a = 14, adv(14); x0 = 28; col = x0 + 22 + a * 10
    b = f'<rect width="{W}" height="{H}" rx="12" fill="{bg}"/>'
    b += f'<path d="M0 12a12 12 0 0 1 12-12h{W-24}a12 12 0 0 1 12 12v24H0z" fill="{bar}"/>'
    b += "".join(f'<circle cx="{22+i*16}" cy="18" r="5" fill="#2B3767"/>' for i in range(3))
    b += text("immiscible", 82, 22.5, 12, dim) + mark(W - 38, 9, 18, PAPER)
    b += text("~ $ ", x0, 74, s, dim) + text("npx immiscible try", x0 + a * 4, 74, s, ink)
    rows = [(tick, "#ACD8F6", "allowed", "look up invoice 0931 in the books"),
            ("!", "#F7F8FA", "held", "pay harbour print £1,250.00, a person decides"),
            (cross, CORAL, "denied", "pay kingscrosscourier.example, a lookalike domain")]
    y = 112
    for m, c, verdict, what in rows:
        b += (m(x0, y, c) if callable(m) else text(m, x0 + 2, y, s, c, "Medium"))
        b += text(verdict, x0 + 22, y, s, c, "Medium") + text(what, col, y, s, ink)
        y += 28
    b += text("the payment code never ran.", col, y + 8, s, dim)
    return svg(W, H, "npx immiscible try: an agent's payment is allowed, held for a person, or denied", b)

def notebook(ink, muted, hatch):
    W, H, top, mid, bot, hx = 840, 96, 6, 58, 90, 168
    b = f'<defs><pattern id="h" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">' \
        f'<line x1="0" y1="0" x2="0" y2="7" stroke="{hatch}" stroke-width="1.6"/></pattern></defs>'
    b += f'<rect x="0.5" y="{top}" width="{hx-0.5}" height="{bot-top}" fill="url(#h)"/>'
    b += f'<rect x="0.5" y="{top+0.5}" width="{W-1}" height="{bot-top}" fill="none" stroke="{ink}"/>'
    b += f'<line x1="{hx}" y1="{top}" x2="{hx}" y2="{bot}" stroke="{ink}"/><line x1="{hx}" y1="{mid}" x2="{W}" y2="{mid}" stroke="{ink}"/>'
    cells = [("project", "immiscible"), ("recorded by", "eoinforker"), ("date", "2026"), ("witnessed & understood by", "")]
    widths = [150, 150, 110, W - hx - 410]; x = hx
    for (label, value), w in zip(cells, widths):
        b += text(label, x + 10, top + 16, 9.5, muted) + text(value, x + 10, top + 40, 13, ink, "Medium")
        x += w
        if x < W: b += f'<line x1="{x}" y1="{top}" x2="{x}" y2="{mid}" stroke="{ink}"/>'
    step = 16; g = hx + step
    while g < W: b += f'<line x1="{g}" y1="{mid}" x2="{g}" y2="{bot}" stroke="{ink}" stroke-opacity=".55"/>'; g += step
    b += f'<line x1="{hx}" y1="{(mid+bot)/2}" x2="{W}" y2="{(mid+bot)/2}" stroke="{ink}" stroke-opacity=".55"/>'
    return svg(W, H, "project immiscible, recorded by eoinforker, 2026", b)

open(f"{OUT}/terminal.svg", "w").write(terminal())
open(f"{OUT}/notebook-light.svg", "w").write(notebook("#0B0D15", "#5B6170", "#0B0D15"))
open(f"{OUT}/notebook-dark.svg", "w").write(notebook("#F7F8FA", "#8B91A1", "#F7F8FA"))
print("ok")
