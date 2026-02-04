"""
TikTok Caption Style - Pixel-Perfect TikTok Slideshow Captions

Reverse-engineered from real TikTok slideshows (January 2026).
Uses official TikTok Sans font (v4.000, open-source).

Key discoveries:
- Font: TikTok Sans 36pt SemiBold
- Size: 5.1% of image width (~42px at 828px, ~55px at 1080px)
- Line height: 1.06 ratio (very tight)
- Stroke: 3px black (#000000)
- Fill: White (#FFFFFF) - appears slightly off-white due to anti-aliasing
- Position: Upper-middle area, 18% from top
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Font paths - TikTok Sans SemiBold is the exact match
FONT_PATHS = [
    Path(__file__).parent / "fonts" / "TikTokSans36pt-SemiBold.ttf",
    Path(__file__).parent / "fonts" / "TikTokSans36pt-Bold.ttf",
    Path(__file__).parent / "fonts" / "TikTokSans16pt-SemiBold.ttf",
]

# Pixel-matched TikTok settings (January 2026)
TIKTOK_STYLE = {
    "font_size_ratio": 0.051,      # 5.1% of width
    "font_size_min": 38,
    "font_size_max": 60,
    "line_height_ratio": 1.06,     # Very tight line spacing
    "fill_color": "#FFFFFF",
    "stroke_color": "#000000",
    "stroke_width": 4,
    "max_width_ratio": 0.88,
    "margin_top_ratio": 0.18,      # 18% from top (TikTok upper-middle position)
}

# Font cache
_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Load TikTok Sans font with caching."""
    cache_key = ("tiktok", size)
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    for font_path in FONT_PATHS:
        if font_path.exists():
            try:
                font = ImageFont.truetype(str(font_path), size)
                _font_cache[cache_key] = font
                return font
            except Exception:
                continue

    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> list[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def burn_caption(
    image_path: Path | str,
    caption: str,
    output_path: Path | str = None,
    position: str = "upper",
    supersample: int = 2,
) -> Path:
    """
    Burn TikTok-style caption onto an image.

    Args:
        image_path: Path to source image
        caption: Text to burn onto image
        output_path: Where to save (defaults to overwriting original)
        position: "upper" (TikTok default), "center", or "bottom"
        supersample: Render at Nx resolution for smoother text (default 2x)

    Returns:
        Path to output image
    """
    image_path = Path(image_path)
    if output_path is None:
        output_path = image_path
    else:
        output_path = Path(output_path)

    if not caption or not caption.strip():
        return image_path

    # Load image
    img = Image.open(image_path).convert("RGBA")
    orig_size = img.size

    # Supersample for smoother anti-aliasing
    scale = supersample
    img_scaled = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img_scaled)

    # Calculate font size (5.1% of original width)
    base_size = int(orig_size[0] * TIKTOK_STYLE["font_size_ratio"])
    base_size = max(TIKTOK_STYLE["font_size_min"], min(TIKTOK_STYLE["font_size_max"], base_size))
    font_size = base_size * scale
    font = get_font(font_size)

    # Text wrapping
    max_width = int(img_scaled.width * TIKTOK_STYLE["max_width_ratio"])
    lines = wrap_text(caption, font, max_width, draw)

    # Calculate line height and total text height
    line_height = int(font_size * TIKTOK_STYLE["line_height_ratio"])
    total_height = len(lines) * line_height

    # Calculate Y position based on position parameter
    if position == "center":
        y = (img_scaled.height - total_height) // 2
    elif position == "bottom":
        margin = int(img_scaled.height * 0.12)
        y = img_scaled.height - margin - total_height
    else:  # upper (TikTok default)
        y = int(img_scaled.height * TIKTOK_STYLE["margin_top_ratio"])

    # Draw text
    stroke_width = TIKTOK_STYLE["stroke_width"] * scale
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (img_scaled.width - line_width) // 2

        draw.text(
            (x, y),
            line,
            font=font,
            fill=TIKTOK_STYLE["fill_color"],
            stroke_width=stroke_width,
            stroke_fill=TIKTOK_STYLE["stroke_color"],
        )
        y += line_height

    # Downscale back to original size
    img_final = img_scaled.resize(orig_size, Image.Resampling.LANCZOS)

    # Convert to RGB for saving
    if img_final.mode == "RGBA":
        background = Image.new("RGB", img_final.size, (0, 0, 0))
        background.paste(img_final, mask=img_final.split()[3])
        img_final = background

    img_final.save(output_path, "PNG")
    return output_path


def create_preview(
    caption: str,
    width: int = 1080,
    height: int = 1920,
    background_color: tuple = (80, 80, 80),
) -> Image.Image:
    """
    Create a preview image with TikTok-style caption on solid background.

    Args:
        caption: Text to render
        width: Image width (default 1080 for TikTok)
        height: Image height (default 1920 for TikTok)
        background_color: RGB tuple for background

    Returns:
        PIL Image object
    """
    import tempfile

    img = Image.new("RGB", (width, height), background_color)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        temp_path = Path(f.name)
        img.save(temp_path)

    burn_caption(temp_path, caption)
    result = Image.open(temp_path)
    temp_path.unlink(missing_ok=True)

    return result


if __name__ == "__main__":
    # Demo
    preview = create_preview(
        "Unhinged mental health\nhacks I learned in therapy\n(that actually work)"
    )
    preview.save("demo_output.png")
    print("Created demo_output.png")
