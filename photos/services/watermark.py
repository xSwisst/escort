from __future__ import annotations

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

WATERMARK_TEXT = "elegant-agency.fun"

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
)


def _get_font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    for font_path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def apply_watermark(
    image_bytes: bytes,
    text: str = WATERMARK_TEXT,
    opacity: int = 115,
) -> bytes:
    """
    Apply centered semi-transparent white text watermark onto image bytes.
    Returns JPEG bytes.
    """
    with Image.open(BytesIO(image_bytes)) as orig:
        transposed = ImageOps.exif_transpose(orig)
        base = transposed.convert("RGBA")

    w, h = base.size
    font_size = max(16, min(w, h) // 10)
    font = _get_font(font_size)

    txt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    while text_w > w * 0.75 and font_size > 14:
        font_size = max(14, int(font_size * 0.85))
        font = _get_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

    x = (w - text_w) // 2 - bbox[0]
    y = (h - text_h) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))

    composited = Image.alpha_composite(base, txt_layer)
    background = Image.new("RGBA", composited.size, (255, 255, 255, 255))
    final_img = Image.alpha_composite(background, composited).convert("RGB")

    output = BytesIO()
    final_img.save(output, format="JPEG", quality=92)
    return output.getvalue()


def compress_avatar(
    image_bytes: bytes,
    max_size: int = 128,
    quality: int = 35,
) -> bytes:
    """
    Resize and compress a client avatar into an ultra-lightweight JPEG thumbnail.
    """
    with Image.open(BytesIO(image_bytes)) as orig:
        transposed = ImageOps.exif_transpose(orig)
        if transposed.mode in ("RGBA", "LA", "P"):
            rgba = transposed.convert("RGBA")
            bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            img = Image.alpha_composite(bg, rgba).convert("RGB")
        else:
            img = transposed.convert("RGB")
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    output = BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True, subsampling=2)
    return output.getvalue()
