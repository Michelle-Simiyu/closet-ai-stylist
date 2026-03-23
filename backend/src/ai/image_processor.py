"""
Image processing utilities: background removal, resizing, color extraction.
"""
import io
import base64
import logging
from typing import Optional, Tuple, Dict, Any

# Pillow is optional — image resize/color features degrade gracefully without it
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logging.getLogger(__name__).warning(
        "Pillow not installed — image resizing and color extraction disabled. "
        "Install with: pip install Pillow>=11.0.0"
    )

logger = logging.getLogger(__name__)

# Try importing rembg (background removal)
try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
    logger.info("rembg background removal available")
except ImportError:
    REMBG_AVAILABLE = False
    logger.warning("rembg not available — background removal disabled")

# Try importing Cloudinary
try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

MAX_DIMENSION = 800
THUMBNAIL_SIZE = (200, 200)


def remove_background(image_data: bytes) -> bytes:
    """Remove background from image. Falls back to original if rembg unavailable."""
    if not REMBG_AVAILABLE:
        return image_data
    try:
        result = rembg_remove(image_data)
        return result
    except Exception as e:
        logger.error(f"Background removal failed: {e}")
        return image_data


def resize_image(image_data: bytes, max_dimension: int = MAX_DIMENSION) -> bytes:
    """Resize image while maintaining aspect ratio."""
    if not PILLOW_AVAILABLE:
        return image_data
    try:
        img = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if needed for JPEG
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background

        # Resize if needed
        w, h = img.size
        if max(w, h) > max_dimension:
            ratio = max_dimension / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return image_data


def extract_dominant_colors(image_data: bytes, n_colors: int = 3) -> list:
    """Extract dominant colors from image using simple clustering."""
    if not PILLOW_AVAILABLE:
        return ["unknown"]
    try:
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        img = img.resize((100, 100))  # Downscale for speed

        pixels = list(img.getdata())
        # Simple color extraction: average clusters
        # Skip very light (background) and very dark pixels
        filtered = [
            p for p in pixels
            if not (p[0] > 240 and p[1] > 240 and p[2] > 240)  # not white
            and not (p[0] < 15 and p[1] < 15 and p[2] < 15)    # not black
        ]

        if not filtered:
            filtered = pixels

        # Very simple: take average and find color name
        avg_r = sum(p[0] for p in filtered) // len(filtered)
        avg_g = sum(p[1] for p in filtered) // len(filtered)
        avg_b = sum(p[2] for p in filtered) // len(filtered)

        color_name = rgb_to_color_name(avg_r, avg_g, avg_b)
        return [color_name]
    except Exception as e:
        logger.error(f"Color extraction failed: {e}")
        return ["unknown"]


def rgb_to_color_name(r: int, g: int, b: int) -> str:
    """Convert RGB values to a color name."""
    # Brightness
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    if brightness > 230:
        return "white"
    if brightness < 30:
        return "black"

    # Saturation
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    saturation = (max_val - min_val) / max(max_val, 1)

    if saturation < 0.15:
        if brightness > 180:
            return "light gray"
        elif brightness > 100:
            return "gray"
        else:
            return "dark gray"

    # Hue detection
    if max_val == r:
        hue = (g - b) / max(max_val - min_val, 1) * 60
    elif max_val == g:
        hue = 2 + (b - r) / max(max_val - min_val, 1) * 60
    else:
        hue = 4 + (r - g) / max(max_val - min_val, 1) * 60

    if hue < 0:
        hue += 360

    if hue < 30 or hue >= 330:
        return "red" if saturation > 0.5 else "pink"
    elif hue < 60:
        return "orange"
    elif hue < 80:
        return "yellow"
    elif hue < 150:
        return "green"
    elif hue < 200:
        return "teal"
    elif hue < 260:
        return "blue"
    elif hue < 290:
        return "purple"
    elif hue < 330:
        return "pink"

    return "colorful"


def auto_tag_clothing(image_data: bytes) -> Dict[str, Any]:
    """
    Auto-detect clothing attributes from image.
    Returns suggested tags (category, color, style).
    """
    colors = extract_dominant_colors(image_data)
    primary_color = colors[0] if colors else "unknown"

    # Placeholder: in production would use ML classifier
    return {
        "color": primary_color,
        "confidence": 0.70,
        "suggestions": {
            "color": primary_color,
        },
    }


def upload_to_cloudinary(
    image_data: bytes,
    public_id: Optional[str] = None,
    folder: str = "closet-ai",
) -> Optional[str]:
    """Upload image to Cloudinary and return URL."""
    if not CLOUDINARY_AVAILABLE:
        return None

    try:
        result = cloudinary.uploader.upload(
            image_data,
            public_id=public_id,
            folder=folder,
            resource_type="image",
            transformation=[
                {"width": MAX_DIMENSION, "height": MAX_DIMENSION, "crop": "limit"},
                {"quality": "auto"},
            ],
        )
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None


def image_to_base64(image_data: bytes) -> str:
    """Convert image bytes to base64 data URL."""
    b64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"
