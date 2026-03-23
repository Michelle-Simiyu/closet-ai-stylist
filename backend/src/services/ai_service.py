import logging
from typing import Optional, Dict, Any
from ..ai.image_processor import (
    remove_background,
    resize_image,
    auto_tag_clothing,
    upload_to_cloudinary,
    image_to_base64,
    CLOUDINARY_AVAILABLE,
)
from ..core.config import settings

logger = logging.getLogger(__name__)


async def process_clothing_image(
    image_data: bytes,
    remove_bg: bool = True,
    upload: bool = True,
    public_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process uploaded clothing image:
    1. Remove background (if enabled)
    2. Resize to max dimension
    3. Auto-tag (color, category suggestion)
    4. Upload to Cloudinary (if configured)
    5. Return URL + suggestions
    """
    # Remove background
    if remove_bg:
        image_data = remove_background(image_data)

    # Resize
    image_data = resize_image(image_data)

    # Auto-tag
    tags = auto_tag_clothing(image_data)

    # Upload or use base64
    image_url = None
    if upload and CLOUDINARY_AVAILABLE and settings.CLOUDINARY_CLOUD_NAME:
        _configure_cloudinary()
        image_url = upload_to_cloudinary(image_data, public_id=public_id)

    if not image_url:
        # Fallback: base64 data URL (not ideal for production but works for demo)
        image_url = image_to_base64(image_data)

    return {
        "image_url": image_url,
        "suggestions": tags.get("suggestions", {}),
        "confidence": tags.get("confidence", 0.0),
        "processed": True,
    }


def _configure_cloudinary():
    """Configure Cloudinary SDK from settings."""
    try:
        import cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
    except Exception as e:
        logger.error(f"Cloudinary config failed: {e}")


async def analyze_image(image_data: bytes) -> Dict[str, Any]:
    """Analyze image and return clothing attribute suggestions."""
    # Resize first for speed
    image_data = resize_image(image_data)
    tags = auto_tag_clothing(image_data)

    return {
        "color": tags["suggestions"].get("color", "unknown"),
        "confidence": tags["confidence"],
        "suggestions": {
            "color": tags["suggestions"].get("color", ""),
            "category": "",  # Would need ML model
            "style": "",     # Would need ML model
        },
    }


def get_mock_weather(city: str = "New York") -> Dict[str, Any]:
    """Return mock weather data for demo purposes."""
    mock_data = {
        "New York": {"temperature": 18, "condition": "partly cloudy", "season": "fall"},
        "Los Angeles": {"temperature": 26, "condition": "sunny", "season": "summer"},
        "Chicago": {"temperature": 8, "condition": "windy", "season": "winter"},
        "Miami": {"temperature": 30, "condition": "sunny", "season": "summer"},
        "Seattle": {"temperature": 12, "condition": "rainy", "season": "fall"},
    }
    data = mock_data.get(city, {"temperature": 20, "condition": "clear", "season": "all"})
    return {
        "city": city,
        "temperature_celsius": data["temperature"],
        "condition": data["condition"],
        "season": data["season"],
        "source": "mock",
    }
