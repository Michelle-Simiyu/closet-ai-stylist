import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ....core.security import get_current_user
from ....models.user import User
from ....services.ai_service import analyze_image

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze")
async def analyze_clothing_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Analyze an uploaded clothing image and suggest attributes."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    try:
        result = await analyze_image(image_data)
        return result
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Image analysis failed")
