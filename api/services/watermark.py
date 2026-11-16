import logging
import math
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

logger = logging.getLogger(__name__)

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]


def _get_font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Retrieve TrueType font with fallbacks to system default."""
    for font_path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def apply_watermark(image_bytes: bytes, text: str, opacity: int = 40) -> bytes:
    """
    Apply a diagonal repeating text watermark across the entire image.

    :param image_bytes: Raw input image bytes (JPEG, PNG, WebP, etc.)
    :param text: Text to render across the image
    :param opacity: Alpha opacity 0-255 (40 ≈ 15% visible)
    :return: Output JPEG bytes
    """
    with Image.open(BytesIO(image_bytes)) as orig:
        # Normalize orientation using EXIF if present
        transposed = ImageOps.exif_transpose(orig)
        base = transposed.convert("RGBA")

    w, h = base.size
    font_size = max(w, h) // 15
    font = _get_font(font_size)

    diag = int(math.sqrt(w ** 2 + h ** 2))
    canvas_size = diag * 2
    txt_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    spacing_x = text_w + font_size * 2
    spacing_y = text_h + font_size * 3

    y = 0
    while y < canvas_size:
        x = 0
        while x < canvas_size:
            draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))
            x += spacing_x
        y += spacing_y

    txt_layer = txt_layer.rotate(35, expand=False)

    cx, cy = txt_layer.size[0] // 2, txt_layer.size[1] // 2
    txt_layer = txt_layer.crop((cx - w // 2, cy - h // 2, cx - w // 2 + w, cy - h // 2 + h))

    result = Image.alpha_composite(base, txt_layer)

    # Composite onto solid white background in case source had alpha transparency
    background = Image.new("RGBA", result.size, (255, 255, 255, 255))
    final_img = Image.alpha_composite(background, result).convert("RGB")

    output = BytesIO()
    final_img.save(output, format="JPEG", quality=92)
    return output.getvalue()
