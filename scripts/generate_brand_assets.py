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

FONT_MONO = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]
FONT_MONO_BOLD = [
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
]
def _open_font(candidates: list[str], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size, index=index)
    return ImageFont.load_default()


def mono_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return _open_font(FONT_MONO_BOLD if bold else FONT_MONO, size)


def display_font(size: int) -> ImageFont.FreeTypeFont:
    return mono_font(size, bold=True)


def body_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return mono_font(size, bold=bold)


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


def _center_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill: str) -> None:
    w = draw.im.size[0]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) / 2, y), text, font=font, fill=fill)


def generate_og() -> None:
    """Match the live app hero: cream/lavender/peach, mint eyebrow, typewriter title."""
    img = draw_site_background((1200, 630))
    draw = ImageDraw.Draw(img)

    _center_text(draw, 240, "AI-POWERED VERSE FACTORY", body_font(22, bold=True), MINT)
    _center_text(draw, 340, "Limerickster", display_font(108), INK)

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

    font = display_font(max(10, int(size * 0.46)))
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
    generate_og()
    generate_icon(32, "favicon-32.png")
    generate_icon(16, "favicon-16.png")
    generate_icon(180, "apple-touch-icon.png")

    ico = Image.open(STATIC / "favicon-32.png")
    ico.save(STATIC / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32)])
    print(f"Wrote {STATIC / 'favicon.ico'}")


if __name__ == "__main__":
    main()
