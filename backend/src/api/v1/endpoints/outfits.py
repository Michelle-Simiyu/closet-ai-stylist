import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ....core.database import get_session
from ....core.security import get_current_user
from ....core.exceptions import NotFoundError, AuthorizationError
from ....models.user import User
from ....models.outfit import (
    GenerateOutfitsRequest, OutfitGenerationResponse, OutfitWithItems, FeedbackRequest
)
from ....services import closet_service, outfit_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/outfits", tags=["outfits"])


@router.post("/generate", response_model=OutfitGenerationResponse)
async def generate_outfits(
    request: GenerateOutfitsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate AI-powered outfit combinations from user's closet."""
    try:
        all_items = await closet_service.get_closet(session, current_user.id, include_demo=True)
        result = await outfit_service.generate_outfits(
            session,
            current_user.id,
            request,
            current_user.style_profile,
            all_items,
        )
        return OutfitGenerationResponse(**result)
    except Exception as e:
        logger.error(f"Outfit generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Outfit generation failed")


@router.get("/saved", response_model=List[OutfitWithItems])
async def get_saved_outfits(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user's saved outfits."""
    all_items = await closet_service.get_closet(session, current_user.id, include_demo=True)
    return await outfit_service.get_saved_outfits(session, current_user.id, all_items)


@router.post("/{outfit_id}/save")
async def save_outfit(
    outfit_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        outfit = await outfit_service.save_outfit(session, outfit_id, current_user.id)
        return {"message": "Outfit saved", "outfit_id": outfit.id}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Outfit not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.post("/{outfit_id}/like")
async def like_outfit(
    outfit_id: str,
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Like or dislike an outfit."""
    try:
        outfit = await outfit_service.like_outfit(
            session, outfit_id, current_user.id, feedback.liked
        )
        action = "liked" if feedback.liked else "disliked"
        return {"message": f"Outfit {action}", "outfit_id": outfit.id, "liked": outfit.liked}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Outfit not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")
