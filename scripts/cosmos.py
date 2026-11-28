"""Generates assets/cosmos-{dark,light}.svg: a quiet universe of numbers, formulas and alphabets.

Run: python3 scripts/cosmos.py && node scripts/raster_rings.mjs && python3 scripts/cosmos.py
"""
import base64
import json
import math
import random
from pathlib import Path

W, H = 1200, 440
CX, CY = 600, 220
TILT = -9          # degrees, orbital plane tilt
SQUASH = 0.34      # orbital plane perspective

PALETTES = {
    "dark": dict(bg="#07080c", bg2="#10131c", ink="#e8e6df", dim="#8b90a0", glow="#f3d9a4", accent="#9fb4ff"),
    "light": dict(bg="#f7f5ef", bg2="#ece8de", ink="#1b1d24", dim="#6d7080", glow="#d99a3a", accent="#3e5bd6"),
}

GLYPHS = (
    "0123456789"
    "πφψωλΣΔΩθαβγ∞∑∫∂∇√≈≠≤±×÷∅∈ℵℏ"
    "абвгдежзиклмнопрстуфхцчшщэюя"
    "abcdefghijklmnopqrstuvwxyz"
    "אבגדהוזחטיכלמנ"
)

RINGS = [
    # radius, seconds per turn, font size, opacity, style, text
    (120, 70, 15, 0.95, "mono", "0 1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987 · "),
    (200, 110, 17, 0.85, "serif", "e^{iπ} + 1 = 0  ·  a² + b² = c²  ·  ∇ · E = ρ / ε₀  ·  E = mc²  ·  ∫ e^{−x²} dx = √π  ·  "),
    (285, 160, 15, 0.7, "mono", "А Б В Г Д Е Ж З И К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Э Ю Я  ·  α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω  ·  "),
    (375, 230, 14, 0.55, "mono", "2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 101 103 107 109 113 127 131 137 139 149 151 157 163 · "),
    (470, 320, 16, 0.4, "serif", "Σ 1/n² = π²/6  ·  φ = (1 + √5) / 2  ·  i² = −1  ·  ℵ₀ < 2^ℵ₀  ·  ΔxΔp ≥ ℏ/2  ·  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z  ·  א ב ג ד ה ו ז ח ט  ·  "),
]
PI = "3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"

# Rings are drawn once into bitmaps (scripts/raster_rings.mjs) and only the bitmaps
# rotate: spinning ~1000 live glyphs made the image crawl at ~6 fps.
BUILD = Path(__file__).resolve().parent / "build"
RASTER_IN = {}
try:
    RASTER = json.loads((BUILD / "rings.raster.json").read_text())
except FileNotFoundError:
    RASTER = {}
ITALIC = ' font-style="italic"'

FONTS = {
    "mono": "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace",
    "serif": "Georgia,'Times New Roman',serif",
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fit(text, r, size):
    """Repeat text so it roughly fills the circumference at this font size."""
    circ = 2 * math.pi * r
    per_char = size * 0.62
    n = max(1, round(circ / (len(text) * per_char)))
    return text * n


def build(theme):
    p = PALETTES[theme]
    rnd = random.Random(7)
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="Абстрактная вселенная из чисел, формул и азбук"><title>Вселенная из чисел, формул и азбук</title>')
    a("<style>")
    a(".spin{transform-origin:0 0;animation:spin linear infinite}@keyframes spin{to{transform:rotate(360deg)}}")
    for i in range(6):
        a(f".t{i}{{animation:tw {3 + i * 1.3:.1f}s ease-in-out {-i * 0.9:.1f}s infinite alternate}}")
    a("@keyframes tw{0%{opacity:.08}100%{opacity:1}}")
    a(".core{transform-origin:600px 220px;animation:pulse 6s ease-in-out infinite}")
    a("@keyframes pulse{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.12);opacity:1}}")
    a(".drift{animation:drift 40s linear infinite}@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-1300px)}}")
    a(".comet{offset-path:path('M1260 40 L -80 330');animation:comet 14s cubic-bezier(.4,0,.6,1) 3s infinite;opacity:0}")
    a("@keyframes comet{0%{offset-distance:0%;opacity:0}3%{opacity:1}18%{offset-distance:100%;opacity:0}100%{offset-distance:100%;opacity:0}}")
    a("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    a("</style>")
    a("<defs>")
    a(f'<radialGradient id="bg" cx="50%" cy="50%" r="75%"><stop offset="0" stop-color="{p["bg2"]}"/><stop offset="1" stop-color="{p["bg"]}"/></radialGradient>')
    a(f'<radialGradient id="glow"><stop offset="0" stop-color="{p["glow"]}" stop-opacity=".9"/><stop offset=".25" stop-color="{p["glow"]}" stop-opacity=".35"/><stop offset="1" stop-color="{p["glow"]}" stop-opacity="0"/></radialGradient>')
    a('<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".18" stop-color="#fff"/><stop offset=".82" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    a(f'<mask id="edges"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    a("</defs>")
    a(f'<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>')

    # star field of glyphs
    a(f'<g fill="{p["ink"]}" font-family="{FONTS["mono"]}" text-anchor="middle">')
    for _ in range(170):
        x, y = rnd.uniform(14, W - 14), rnd.uniform(16, H - 10)
        # keep the galaxy core a bit clearer
        if ((x - CX) / 260) ** 2 + ((y - CY) / 90) ** 2 < 1:
            continue
        if y > H - 44 and (x < 190 or x > W - 260):  # leave the captions clean
            continue
        size = rnd.choice([7, 8, 8, 9, 10, 11, 13])
        g = rnd.choice(GLYPHS)
        op = rnd.uniform(0.25, 0.75) * (1 if size < 11 else 0.8)
        a(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" opacity="{op:.2f}" class="t{rnd.randrange(6)}">{esc(g)}</text>')
    a("</g>")

    # far band of pi digits drifting, like a distant milky way
    a(f'<g mask="url(#edges)" opacity=".22" fill="{p["dim"]}" font-family="{FONTS["mono"]}" font-size="10" letter-spacing="3">')
    a(f'<g transform="rotate({TILT} {CX} {CY})"><g class="drift">')
    band = PI * 2
    a(f'<text x="0" y="{CY - 150}">{band}</text><text x="1300" y="{CY - 150}">{band}</text>')
    a("</g></g></g>")

    # core glow
    a(f'<circle class="core" cx="{CX}" cy="{CY}" r="120" fill="url(#glow)"/>')

    # orbits
    a(f'<g transform="translate({CX} {CY}) rotate({TILT}) scale(1 {SQUASH})">')
    for i, (r, secs, size, op, style, text) in enumerate(RINGS):
        a(f'<circle r="{r}" fill="none" stroke="{p["dim"]}" stroke-opacity="{op * 0.25:.2f}" stroke-width="2.4"/>')
        fill = p["accent"] if i == 1 else p["ink"]
        rev = " animation-direction:reverse;" if i % 2 else ""
        a(f'<g class="spin" style="animation-duration:{secs}s;{rev}">')
        attrs = f'font-family="{FONTS[style]}" font-size="{size}" fill="{fill}" opacity="{op}"' + (ITALIC if style == "serif" else "")
        chars = fit(text, r, size)
        n = len(chars)
        xs = " ".join(f"{r * math.cos(2 * math.pi * k / n):.1f}" for k in range(n))
        ys = " ".join(f"{r * math.sin(2 * math.pi * k / n):.1f}" for k in range(n))
        rot = " ".join(f"{360 * k / n + 90:.0f}" for k in range(n))
        R = r + size
        RASTER_IN[f"{theme}-{i}"] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{2 * R}" height="{2 * R}" viewBox="{-R} {-R} {2 * R} {2 * R}">'
            f'<text {attrs} text-anchor="middle" x="{xs}" y="{ys}" rotate="{rot}">{esc(chars)}</text></svg>')
        href = RASTER.get(f"{theme}-{i}") or "data:image/svg+xml;base64," + base64.b64encode(RASTER_IN[f"{theme}-{i}"].encode()).decode()
        a(f'<image x="{-R}" y="{-R}" width="{2 * R}" height="{2 * R}" href="{href}"/>')
        a("</g>")
    a("</g>")

    # bright nucleus
    a(f'<circle cx="{CX}" cy="{CY}" r="5" fill="{p["glow"]}"/>')
    a(f'<text x="{CX}" y="{CY + 4}" dy="-14" font-family="{FONTS["serif"]}" font-style="italic" font-size="22" fill="{p["ink"]}" text-anchor="middle" opacity=".9">∞</text>')

    # comet carrying a tiny formula
    a(f'<g class="comet"><text font-family="{FONTS["serif"]}" font-style="italic" font-size="13" fill="{p["accent"]}">dx/dt</text></g>')

    a("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "assets"
    root.mkdir(exist_ok=True)
    for theme in PALETTES:
        (root / f"cosmos-{theme}.svg").write_text(build(theme), encoding="utf-8")
        print("wrote", root / f"cosmos-{theme}.svg")
    BUILD.mkdir(exist_ok=True)
    (BUILD / "rings.json").write_text(json.dumps(RASTER_IN))
