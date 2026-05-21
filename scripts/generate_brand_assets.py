#!/usr/bin/env python3
"""Regenerate favicon and OG images using exact site palette and fonts from style.css."""

import urllib.request
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
FONTS = STATIC / "fonts"

# style.css tokens
CREAM = "#faf6ef"
CARD = "#fffdf9"
INK = "#1a1423"
ACCENT = "#e85d4c"
MINT = "#3d8b7a"
MINT_DARK = "#2d6b5e"
LAVENDER = "#d4c5f9"
PEACH = "#fde8d8"
BORDER = "#e8dfd0"
MUTED = "#6b5f72"

FONT_MONO = FONTS / "IBMPlexMono-Regular.ttf"
FONT_SANS_SEMIBOLD = FONTS / "IBMPlexSans-SemiBold.ttf"

FONT_MONO_FALLBACK = [
    "/System/Library/Fonts/Supplemental/Menlo.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]

FONT_DOWNLOADS = {
    FONT_MONO: "https://fonts.gstatic.com/s/ibmplexmono/v20/-F63fjptAgt5VM-kVkqdyU8n5ig.ttf",
    FONT_SANS_SEMIBOLD: "https://fonts.gstatic.com/s/ibmplexsans/v23/zYXGKVElMYYaJe8bpLHnCwDKr932-G7dytD-Dmu1swZSAXcomDVmadSDNF5zAA.ttf",
}


def ensure_fonts() -> None:
    FONTS.mkdir(parents=True, exist_ok=True)
    for path, url in FONT_DOWNLOADS.items():
        if path.exists():
            continue
        print(f"Downloading {path.name}...")
        urllib.request.urlretrieve(url, path)


def _open_font(path: Path, size: int, fallbacks: Optional[List[str]] = None) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    for candidate in fallbacks or []:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def sans_font(size: int) -> ImageFont.FreeTypeFont:
    """IBM Plex Sans 600 — matches .eyebrow (inherits body sans, weight 600)."""
    return _open_font(FONT_SANS_SEMIBOLD, size)


def mono_font(size: int) -> ImageFont.FreeTypeFont:
    """IBM Plex Mono 400 — matches .hero h1."""
    return _open_font(FONT_MONO, size, FONT_MONO_FALLBACK)


def draw_site_background(size: tuple[int, int]) -> Image.Image:
    """Match body background in style.css (lavender + peach on cream)."""
    w, h = size
    base = Image.new("RGB", size, CREAM)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(
        (-int(w * 0.15), -int(h * 0.2), int(w * 0.75), int(h * 0.55)),
        fill=LAVENDER + "CC",
    )
    draw.ellipse(
        (int(w * 0.45), -int(h * 0.15), int(w * 1.05), int(h * 0.5)),
        fill=PEACH + "B3",
    )
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def _text_width(draw: ImageDraw.ImageDraw, text: str, font, letter_spacing: float = 0) -> float:
    if not letter_spacing:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    return sum(
        draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0]
        for ch in text
    ) + letter_spacing * max(len(text) - 1, 0)


def _center_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font,
    fill: str,
    *,
    letter_spacing: float = 0,
) -> None:
    w = draw.im.size[0]
    tw = _text_width(draw, text, font, letter_spacing)
    x = (w - tw) / 2
    if not letter_spacing:
        draw.text((x, y), text, font=font, fill=fill)
        return
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0] + letter_spacing


def generate_og() -> None:
    """Match hero: IBM Plex Sans eyebrow + IBM Plex Mono title."""
    img = draw_site_background((1200, 630))
    draw = ImageDraw.Draw(img)

    eyebrow_font = sans_font(26)
    title_font = mono_font(96)
    eyebrow_tracking = 0.12 * 26  # letter-spacing: 0.12em from .eyebrow

    _center_text(
        draw,
        248,
        "AI-POWERED VERSE FACTORY",
        eyebrow_font,
        MINT,
        letter_spacing=eyebrow_tracking,
    )
    _center_text(draw, 338, "Limerickster", title_font, INK, letter_spacing=96 * 0.02)

    img.save(STATIC / "og-image.jpg", format="JPEG", quality=88, optimize=True)
    print(f"Wrote {STATIC / 'og-image.jpg'}")


def generate_icon(size: int, out_name: str) -> None:
    """Match OG/hero: gradient background, mint eyebrow bar, typewriter L."""
    img = draw_site_background((size, size))
    draw = ImageDraw.Draw(img)
    pad = max(2, size // 10)

    bar_h = max(2, size // 10)
    bar_w = max(size // 2, size - pad * 4)
    bar_x = (size - bar_w) / 2
    draw.rounded_rectangle(
        (bar_x, pad, bar_x + bar_w, pad + bar_h),
        radius=max(1, size // 32),
        fill=MINT,
    )

    font = mono_font(max(10, int(size * 0.46)))
    letter = "L"
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 + size * 0.04), letter, font=font, fill=INK)

    dot_r = max(2, size // 10)
    draw.ellipse(
        (size - pad - dot_r * 2, size - pad - dot_r * 2, size - pad, size - pad),
        fill=ACCENT,
    )

    out = STATIC / out_name
    img.save(out, format="PNG", optimize=True)
    print(f"Wrote {out}")


def main() -> None:
    ensure_fonts()
    generate_og()
    generate_icon(32, "favicon-32.png")
    generate_icon(16, "favicon-16.png")
    generate_icon(180, "apple-touch-icon.png")

    ico = Image.open(STATIC / "favicon-32.png")
    ico.save(STATIC / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32)])
    print(f"Wrote {STATIC / 'favicon.ico'}")


if __name__ == "__main__":
    main()
