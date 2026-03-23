import logging
from datetime import datetime
from typing import List, Optional, Tuple
from sqlmodel import Session, select, or_, and_
from ..models.user import User, UserPublic
from ..models.social import (
    Friendship, FriendshipStatus,
    ClosetListing, ClosetListingCreate,
    ClosetRecommendation, ClosetRecommendationCreate,
)
from ..models.clothing import ClothingItem, ClothingItemRead
from ..models.outfit import Outfit, OutfitWithItems
from ..core.exceptions import NotFoundError, AuthorizationError

logger = logging.getLogger(__name__)


# ── User search ─────────────────────────────────────────────────────────────

def search_users(session: Session, query: str, current_user_id: str) -> List[UserPublic]:
    users = session.exec(
        select(User).where(
            User.username.contains(query),
            User.id != current_user_id,
            User.is_demo == False,
        ).limit(20)
    ).all()
    return [
        UserPublic(
            id=u.id, username=u.username, bio=u.bio,
            avatar_url=u.avatar_url, closet_visibility=u.closet_visibility,
            created_at=u.created_at,
        )
        for u in users
    ]


def get_user_public(session: Session, user_id: str) -> UserPublic:
    user = session.get(User, user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return UserPublic(
        id=user.id, username=user.username, bio=user.bio,
        avatar_url=user.avatar_url, closet_visibility=user.closet_visibility,
        created_at=user.created_at,
    )


# ── Friendship helpers ───────────────────────────────────────────────────────

def _get_friendship(session: Session, user_a: str, user_b: str) -> Optional[Friendship]:
    return session.exec(
        select(Friendship).where(
            or_(
                and_(Friendship.requester_id == user_a, Friendship.addressee_id == user_b),
                and_(Friendship.requester_id == user_b, Friendship.addressee_id == user_a),
            )
        )
    ).first()


def _friend_ids(session: Session, user_id: str) -> List[str]:
    friendships = session.exec(
        select(Friendship).where(
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
            Friendship.status == FriendshipStatus.accepted,
        )
    ).all()
    ids = []
    for f in friendships:
        ids.append(f.addressee_id if f.requester_id == user_id else f.requester_id)
    return ids


def _is_friend(session: Session, user_a: str, user_b: str) -> bool:
    f = _get_friendship(session, user_a, user_b)
    return f is not None and f.status == FriendshipStatus.accepted


# ── Friend requests ──────────────────────────────────────────────────────────

def send_friend_request(session: Session, requester_id: str, addressee_id: str) -> Friendship:
    if requester_id == addressee_id:
        raise ValueError("Cannot friend yourself")
    addressee = session.get(User, addressee_id)
    if not addressee:
        raise NotFoundError("User", addressee_id)
    existing = _get_friendship(session, requester_id, addressee_id)
    if existing:
        if existing.status == FriendshipStatus.accepted:
            raise ValueError("Already friends")
        if existing.status == FriendshipStatus.pending:
            raise ValueError("Friend request already sent")
    f = Friendship(requester_id=requester_id, addressee_id=addressee_id)
    session.add(f)
    session.commit()
    session.refresh(f)
    return f


def accept_friend_request(session: Session, friendship_id: str, user_id: str) -> Friendship:
    f = session.get(Friendship, friendship_id)
    if not f:
        raise NotFoundError("Friendship", friendship_id)
    if f.addressee_id != user_id:
        raise AuthorizationError()
    if f.status != FriendshipStatus.pending:
        raise ValueError("Request is not pending")
    f.status = FriendshipStatus.accepted
    f.updated_at = datetime.utcnow()
    session.add(f)
    session.commit()
    session.refresh(f)
    return f


def decline_or_remove_friend(session: Session, other_user_id: str, current_user_id: str) -> None:
    f = _get_friendship(session, current_user_id, other_user_id)
    if not f:
        raise NotFoundError("Friendship", other_user_id)
    session.delete(f)
    session.commit()


def get_friends(session: Session, user_id: str) -> List[UserPublic]:
    ids = _friend_ids(session, user_id)
    if not ids:
        return []
    users = session.exec(select(User).where(User.id.in_(ids))).all()
    return [
        UserPublic(
            id=u.id, username=u.username, bio=u.bio,
            avatar_url=u.avatar_url, closet_visibility=u.closet_visibility,
            created_at=u.created_at,
        )
        for u in users
    ]


def get_pending_requests(session: Session, user_id: str) -> List[Friendship]:
    """Incoming pending friend requests."""
    return list(session.exec(
        select(Friendship).where(
            Friendship.addressee_id == user_id,
            Friendship.status == FriendshipStatus.pending,
        )
    ).all())


def get_sent_requests(session: Session, user_id: str) -> List[Friendship]:
    return list(session.exec(
        select(Friendship).where(
            Friendship.requester_id == user_id,
            Friendship.status == FriendshipStatus.pending,
        )
    ).all())


# ── Shared closet / outfits ──────────────────────────────────────────────────

def _can_view_closet(session: Session, viewer_id: str, owner_id: str) -> bool:
    if viewer_id == owner_id:
        return True
    owner = session.get(User, owner_id)
    if not owner:
        return False
    if owner.closet_visibility == "public":
        return True
    if owner.closet_visibility == "friends":
        return _is_friend(session, viewer_id, owner_id)
    return False


def get_friend_closet(
    session: Session, viewer_id: str, owner_id: str
) -> List[ClothingItemRead]:
    if not _can_view_closet(session, viewer_id, owner_id):
        raise AuthorizationError()
    items = session.exec(
        select(ClothingItem).where(
            ClothingItem.user_id == owner_id,
            ClothingItem.is_demo == False,
        )
    ).all()
    return [ClothingItemRead.model_validate(i) for i in items]


def get_friend_saved_outfits(
    session: Session, viewer_id: str, owner_id: str
) -> List[dict]:
    if not _can_view_closet(session, viewer_id, owner_id):
        raise AuthorizationError()
    outfits = session.exec(
        select(Outfit).where(
            Outfit.user_id == owner_id,
            Outfit.is_saved == True,
        )
    ).all()
    # Build item map
    all_item_ids = set()
    for o in outfits:
        all_item_ids.update(o.items)
    items_map = {}
    if all_item_ids:
        for item in session.exec(select(ClothingItem).where(ClothingItem.id.in_(all_item_ids))).all():
            items_map[item.id] = ClothingItemRead.model_validate(item)
    return [
        {
            "id": o.id, "occasion": o.occasion,
            "items": [items_map[iid] for iid in o.items if iid in items_map],
            "compatibility_score": o.compatibility_score,
            "description": o.description,
        }
        for o in outfits
    ]


# ── Marketplace ──────────────────────────────────────────────────────────────

def list_item_for_sale(
    session: Session, data: ClosetListingCreate, user_id: str
) -> ClosetListing:
    item = session.get(ClothingItem, data.item_id)
    if not item or item.user_id != user_id:
        raise AuthorizationError()
    listing = ClosetListing(**data.model_dump(), user_id=user_id)
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


def get_marketplace(session: Session, user_id: str) -> List[dict]:
    """All active listings from friends + self."""
    friend_ids = _friend_ids(session, user_id)
    visible_ids = friend_ids + [user_id]
    listings = session.exec(
        select(ClosetListing).where(
            ClosetListing.user_id.in_(visible_ids),
            ClosetListing.is_sold == False,
        )
    ).all()
    # Enrich with item data
    item_ids = [l.item_id for l in listings]
    items_map = {}
    if item_ids:
        for it in session.exec(select(ClothingItem).where(ClothingItem.id.in_(item_ids))).all():
            items_map[it.id] = ClothingItemRead.model_validate(it)
    return [
        {
            "id": l.id, "user_id": l.user_id,
            "item": items_map.get(l.item_id),
            "price": l.price, "currency": l.currency,
            "description": l.description, "created_at": l.created_at,
        }
        for l in listings
    ]


def mark_sold(session: Session, listing_id: str, user_id: str) -> ClosetListing:
    listing = session.get(ClosetListing, listing_id)
    if not listing:
        raise NotFoundError("Listing", listing_id)
    if listing.user_id != user_id:
        raise AuthorizationError()
    listing.is_sold = True
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


def remove_listing(session: Session, listing_id: str, user_id: str) -> None:
    listing = session.get(ClosetListing, listing_id)
    if not listing:
        raise NotFoundError("Listing", listing_id)
    if listing.user_id != user_id:
        raise AuthorizationError()
    session.delete(listing)
    session.commit()


# ── Recommendations ──────────────────────────────────────────────────────────

def send_recommendation(
    session: Session, data: ClosetRecommendationCreate, from_user_id: str
) -> ClosetRecommendation:
    if not _is_friend(session, from_user_id, data.to_user_id):
        raise AuthorizationError()
    rec = ClosetRecommendation(**data.model_dump(), from_user_id=from_user_id)
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec


def get_my_recommendations(session: Session, user_id: str) -> List[ClosetRecommendation]:
    return list(session.exec(
        select(ClosetRecommendation).where(
            ClosetRecommendation.to_user_id == user_id,
        ).order_by(ClosetRecommendation.created_at.desc())
    ).all())


def mark_recommendation_read(
    session: Session, rec_id: str, user_id: str
) -> ClosetRecommendation:
    rec = session.get(ClosetRecommendation, rec_id)
    if not rec or rec.to_user_id != user_id:
        raise AuthorizationError()
    rec.is_read = True
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec
