import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from ....core.database import get_session
from ....core.security import get_current_user
from ....core.exceptions import NotFoundError, AuthorizationError
from ....models.user import User
from ....models.clothing import (
    ClothingItem, ClothingItemCreate, ClothingItemRead, ClothingItemUpdate
)
from ....services import closet_service
from ....services.ai_service import process_clothing_image

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/closet", tags=["closet"])


@router.get("", response_model=List[ClothingItemRead])
async def get_closet(
    category: Optional[str] = None,
    color: Optional[str] = None,
    include_demo: bool = True,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all clothing items in user's closet."""
    items = await closet_service.get_closet(
        session, current_user.id, category=category, color=color, include_demo=include_demo
    )
    return items


@router.post("", response_model=ClothingItemRead, status_code=201)
async def add_item(
    item_data: ClothingItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a new clothing item."""
    return await closet_service.create_item(session, item_data, current_user.id)


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get analytics stats for user's closet."""
    return await closet_service.get_closet_stats(session, current_user.id)


@router.post("/demo", response_model=List[ClothingItemRead])
async def load_demo(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Load demo closet items for demos and testing."""
    return await closet_service.load_demo_closet(session, current_user.id)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    remove_bg: bool = True,
    current_user: User = Depends(get_current_user),
):
    """Upload a clothing image with optional background removal."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    max_size = 10 * 1024 * 1024  # 10MB
    image_data = await file.read()
    if len(image_data) > max_size:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    try:
        result = await process_clothing_image(
            image_data,
            remove_bg=remove_bg,
            public_id=f"{current_user.id}/{file.filename}",
        )
        return result
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image processing failed")


@router.get("/{item_id}", response_model=ClothingItemRead)
async def get_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return await closet_service.get_item(session, item_id, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{item_id}", response_model=ClothingItemRead)
async def update_item(
    item_id: str,
    item_data: ClothingItemUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return await closet_service.update_item(session, item_id, item_data, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        await closet_service.delete_item(session, item_id, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")
