# TikTok Caption Style

Pixel-perfect TikTok slideshow captions for Python. Reverse-engineered from real TikTok slideshows (January 2026).

## The Problem

TikTok's slideshow captions have a very specific look that's hard to replicate. Wrong font, wrong size, wrong spacing = obviously fake content that doesn't convert.

## The Solution

This repo contains:
- **Official TikTok Sans font** (v4.000, open-source from [tiktok/TikTokSans](https://github.com/tiktok/TikTokSans))
- **Pixel-matched settings** discovered through overlay comparison testing
- **Drop-in Python module** using Pillow

## Key Discoveries

| Setting | Value | Notes |
|---------|-------|-------|
| Font | TikTok Sans 36pt SemiBold | Not Bold - SemiBold matches exactly |
| Size | **5.1% of width** | ~42px at 828px, ~55px at 1080px |
| Line height | **1.06 ratio** | Very tight spacing |
| Stroke | 4px black (#000000) | Clean, readable |
| Fill | White (#FFFFFF) | May need #F0F0F0 to compensate for Pillow's brighter rendering |
| Position | 18% from top | TikTok's "upper-middle" placement |
| Max width | 88% of image width | Prevents edge overflow |

## Installation

```bash
pip install Pillow
```

Then copy the `fonts/` folder and `tiktok_captions.py` to your project.

## Usage

```python
from tiktok_captions import burn_caption, create_preview

# Burn caption onto existing image
burn_caption("path/to/image.png", "your caption text here")

# Create preview on gray background
preview = create_preview("Unhinged mental health hacks")
preview.save("output.png")
```

## Positions

```python
# TikTok default - upper area (18% from top)
burn_caption(img, caption, position="upper")

# Center of image
burn_caption(img, caption, position="center")

# Bottom area
burn_caption(img, caption, position="bottom")
```

## Supersampling

For smoother text edges, the module renders at 2x resolution and downscales:

```python
# Default 2x supersampling
burn_caption(img, caption, supersample=2)

# Higher quality (slower)
burn_caption(img, caption, supersample=4)

# No supersampling (faster, slightly rougher edges)
burn_caption(img, caption, supersample=1)
```

## Font Files Included

- `TikTokSans36pt-SemiBold.ttf` - **Primary** (matches TikTok captions)
- `TikTokSans36pt-Bold.ttf` - Fallback
- `TikTokSans16pt-SemiBold.ttf` - For smaller text

These are official fonts from TikTok's open-source release.

## Research Process

1. Captured real TikTok slideshow screenshots
2. Downloaded official TikTok Sans from GitHub
3. Created overlay comparisons with different sizes
4. Found 5.1% ratio by overlapping red test text on TikTok's white text
5. Adjusted line height from standard 1.15 to tight 1.06
6. Verified with pixel-level comparison

## License

- Code: MIT
- TikTok Sans font: [OFL (SIL Open Font License)](https://github.com/nicokosi/gh-actions-test/blob/main/OFL.txt)

## Credits

Research and implementation by [@ergophobian](https://github.com/ergophobian)
