import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from ....core.database import get_session
from ....core.security import get_current_user
from ....core.exceptions import NotFoundError, AuthorizationError
from ....models.user import User, UserPublic
from ....models.social import (
    FriendshipRead,
    ClosetListingCreate, ClosetListingRead,
    ClosetRecommendationCreate, ClosetRecommendationRead,
)
from ....services import social_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/social", tags=["social"])


# ── Public Feed ──────────────────────────────────────────────────────────────

@router.get("/feed")
async def get_feed(
    style: str = Query(None),
    country: str = Query(None),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.get_public_feed(
        session, current_user.id,
        style=style, country=country,
        limit=limit, offset=offset,
    )


# ── User search & profiles ───────────────────────────────────────────────────

@router.get("/users/search", response_model=List[UserPublic])
async def search_users(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.search_users(session, q, current_user.id)


@router.get("/users/{user_id}", response_model=UserPublic)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.get_user_public(session, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users/{user_id}/closet")
async def get_user_closet(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.get_friend_closet(session, current_user.id, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="This closet is private")


@router.get("/users/{user_id}/outfits")
async def get_user_outfits(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.get_friend_saved_outfits(session, current_user.id, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="This closet is private")


# ── Friends ──────────────────────────────────────────────────────────────────

@router.get("/friends", response_model=List[UserPublic])
async def get_friends(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.get_friends(session, current_user.id)


@router.get("/friends/requests", response_model=List[FriendshipRead])
async def get_friend_requests(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.get_pending_requests(session, current_user.id)


@router.get("/friends/sent", response_model=List[FriendshipRead])
async def get_sent_requests(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.get_sent_requests(session, current_user.id)


@router.post("/friends/{user_id}")
async def send_friend_request(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        f = social_service.send_friend_request(session, current_user.id, user_id)
        return {"message": "Friend request sent", "friendship_id": f.id}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/friends/accept/{friendship_id}")
async def accept_friend_request(
    friendship_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        f = social_service.accept_friend_request(session, friendship_id, current_user.id)
        return {"message": "Friend request accepted", "friendship_id": f.id}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Friend request not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/friends/{user_id}")
async def remove_friend(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        social_service.decline_or_remove_friend(session, user_id, current_user.id)
        return {"message": "Friend removed"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Friendship not found")


# ── Marketplace ──────────────────────────────────────────────────────────────

@router.get("/marketplace")
async def browse_marketplace(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.get_marketplace(session, current_user.id)


@router.post("/marketplace", response_model=ClosetListingRead, status_code=201)
async def list_for_sale(
    data: ClosetListingCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.list_item_for_sale(session, data, current_user.id)
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Item not found or not yours")


@router.patch("/marketplace/{listing_id}/sold", response_model=ClosetListingRead)
async def mark_sold(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.mark_sold(session, listing_id, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Listing not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/marketplace/{listing_id}", status_code=204)
async def remove_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        social_service.remove_listing(session, listing_id, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Listing not found")
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")


# ── Recommendations ──────────────────────────────────────────────────────────

@router.get("/recommendations", response_model=List[ClosetRecommendationRead])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return social_service.get_my_recommendations(session, current_user.id)


@router.post("/recommendations", response_model=ClosetRecommendationRead, status_code=201)
async def send_recommendation(
    data: ClosetRecommendationCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.send_recommendation(session, data, current_user.id)
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="You can only recommend to friends")


@router.post("/recommendations/{rec_id}/read", response_model=ClosetRecommendationRead)
async def mark_read(
    rec_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        return social_service.mark_recommendation_read(session, rec_id, current_user.id)
    except AuthorizationError:
        raise HTTPException(status_code=403, detail="Not authorized")
