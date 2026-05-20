#!/usr/bin/env python3
"""Regenerate favicon and OG images using exact site palette from style.css."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

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

FONT_GEORGIA_BOLD = [
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/Library/Fonts/Georgia Bold.ttf",
]
FONT_HELVETICA = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _open_font(candidates: list[str], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size, index=index)
    return ImageFont.load_default()


def georgia_bold(size: int) -> ImageFont.FreeTypeFont:
    return _open_font(FONT_GEORGIA_BOLD, size)


def sans(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return _open_font(FONT_HELVETICA, size, index=1 if bold else 0)


def draw_site_background(size: tuple[int, int]) -> Image.Image:
    w, h = size
    base = Image.new("RGB", size, CREAM)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse((-int(w * 0.15), -int(h * 0.2), int(w * 0.75), int(h * 0.55)), fill=LAVENDER + "B0")
    draw.ellipse((int(w * 0.45), -int(h * 0.15), int(w * 1.05), int(h * 0.5)), fill=PEACH + "A0")
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def _center_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill: str) -> None:
    w = draw.im.size[0]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) / 2, y), text, font=font, fill=fill)


def generate_og() -> None:
    img = draw_site_background((1200, 630))
    draw = ImageDraw.Draw(img)

    _center_text(draw, 118, "AI-POWERED VERSE FACTORY", sans(22, bold=True), MINT)
    _center_text(draw, 168, "Limerickster", georgia_bold(108), INK)
    _center_text(draw, 248, "Tell us about someone and we'll write them a limerick.", sans(30), MUTED)

    rhyme_y = 370
    labels = [("A", ACCENT), ("A", ACCENT), ("B", MINT), ("B", MINT), ("A", ACCENT)]
    spacing = 120
    start_x = 600 - (len(labels) - 1) * spacing / 2
    font = sans(20, bold=True)
    for i, (letter, color) in enumerate(labels):
        x = start_x + i * spacing
        bbox = draw.textbbox((0, 0), letter, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw / 2, rhyme_y), letter, font=font, fill=color)

    btn_w, btn_h = 360, 56
    btn_x = (1200 - btn_w) / 2
    btn_y = 430
    draw.rounded_rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), radius=8, fill=MINT)
    _center_text(draw, btn_y + 14, "Generate Limerick", sans(22, bold=True), "#ffffff")

    img.save(STATIC / "og-image.jpg", format="JPEG", quality=88, optimize=True)
    print(f"Wrote {STATIC / 'og-image.jpg'}")


def generate_icon(size: int, out_name: str) -> None:
    img = draw_site_background((size, size))
    draw = ImageDraw.Draw(img)
    pad = max(1, size // 16)
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=max(2, size // 5),
        fill=CARD,
        outline=BORDER,
        width=max(1, size // 32),
    )

    bar_h = max(2, size // 16)
    bar_w = size // 3
    bar_x = (size - bar_w) / 2
    draw.rounded_rectangle((bar_x, pad + 2, bar_x + bar_w, pad + 2 + bar_h), radius=1, fill=MINT)

    font = georgia_bold(int(size * 0.56))
    letter = "L"
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, size * 0.38), letter, font=font, fill=INK)

    dot_r = max(2, size // 12)
    draw.ellipse(
        (size - pad - dot_r * 2, size - pad - dot_r * 2, size - pad, size - pad),
        fill=ACCENT,
    )

    out = STATIC / out_name
    img.save(out, format="PNG", optimize=True)
    print(f"Wrote {out}")


def main() -> None:
    generate_og()
    generate_icon(32, "favicon-32.png")
    generate_icon(16, "favicon-16.png")
    generate_icon(180, "apple-touch-icon.png")

    ico = Image.open(STATIC / "favicon-32.png")
    ico.save(STATIC / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32)])
    print(f"Wrote {STATIC / 'favicon.ico'}")


if __name__ == "__main__":
    main()
