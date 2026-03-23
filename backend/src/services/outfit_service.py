import logging
import time
import uuid
from typing import List, Optional, Dict, Any
from itertools import combinations
from sqlmodel import Session, select
from ..models.clothing import ClothingItem, Category
from ..models.outfit import Outfit, GenerateOutfitsRequest, OutfitWithItems
from ..models.feedback import Feedback
from ..core.exceptions import NotFoundError, AuthorizationError
from ..ai.compatibility import score_outfit, generate_outfit_description, apply_user_preferences
from ..ai.rules_engine import outfit_complete, OUTFIT_TEMPLATES

logger = logging.getLogger(__name__)


def _build_outfit_with_items(
    outfit: Outfit,
    items_map: Dict[str, ClothingItem],
) -> OutfitWithItems:
    """Combine outfit record with its item objects."""
    outfit_items = [items_map[iid] for iid in outfit.items if iid in items_map]
    return OutfitWithItems(
        id=outfit.id,
        user_id=outfit.user_id,
        name=outfit.name,
        occasion=outfit.occasion,
        items=outfit_items,
        compatibility_score=outfit.compatibility_score,
        liked=outfit.liked,
        worn_count=outfit.worn_count,
        created_at=outfit.created_at,
        is_saved=outfit.is_saved,
        feedback=outfit.feedback,
        description=outfit.description,
    )


async def generate_outfits(
    session: Session,
    user_id: str,
    request: GenerateOutfitsRequest,
    style_profile: Dict[str, Any],
    all_items: List[ClothingItem],
) -> Dict[str, Any]:
    """Generate outfit combinations from user's closet."""
    start_time = time.time()

    if not all_items:
        return {
            "outfits": [],
            "count": 0,
            "occasion": request.occasion,
            "generation_time_ms": 0,
        }

    # Filter by season/weather if provided
    temperature = request.temperature
    items_to_use = all_items

    # Group items by category
    by_category: Dict[str, List[ClothingItem]] = {}
    for item in items_to_use:
        cat = item.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)

    templates = OUTFIT_TEMPLATES.get(request.occasion, OUTFIT_TEMPLATES["casual"])
    candidates: List[List[ClothingItem]] = []

    # Generate all valid combinations from templates
    for template in templates:
        cat_values = [c.value for c in template]
        # Check all required categories are available
        if not all(c in by_category for c in cat_values):
            continue

        # Get item lists for each category in template
        cat_item_lists = [by_category[c] for c in cat_values]

        # Generate combinations (limit per template to avoid explosion)
        max_per_template = 20
        count = 0
        for combo in _cartesian_product(*cat_item_lists):
            if count >= max_per_template:
                break
            candidates.append(list(combo))
            count += 1

    if not candidates:
        # Fallback: return best available combinations
        tops = by_category.get("top", []) + by_category.get("dress", [])
        bottoms = by_category.get("bottom", [])
        if tops and bottoms:
            for t in tops[:3]:
                for b in bottoms[:3]:
                    candidates.append([t, b])
        elif tops:
            candidates = [[t] for t in tops[:5]]

    # Score and rank all candidates
    scored: List[tuple] = []
    for combo in candidates:
        score, breakdown = score_outfit(
            combo,
            occasion=request.occasion,
            temperature=temperature,
        )
        # Apply user preferences
        score = apply_user_preferences(score, combo, style_profile)
        scored.append((score, breakdown, combo))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Deduplicate and take top N
    seen_signatures = set()
    top_outfits: List[OutfitWithItems] = []

    for score, breakdown, combo in scored:
        if len(top_outfits) >= request.max_outfits:
            break

        # Signature: sorted item IDs
        sig = tuple(sorted(item.id for item in combo))
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)

        description = generate_outfit_description(combo, request.occasion, score)

        outfit_obj = OutfitWithItems(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=None,
            occasion=request.occasion,
            items=combo,
            compatibility_score=score,
            liked=False,
            worn_count=0,
            created_at=__import__("datetime").datetime.utcnow(),
            is_saved=False,
            feedback=breakdown.get("feedback", []),
            description=description,
        )
        top_outfits.append(outfit_obj)

        # Persist outfit to DB
        db_outfit = Outfit(
            id=outfit_obj.id,
            user_id=user_id,
            occasion=request.occasion,
            compatibility_score=score,
            description=description,
        )
        db_outfit.items = [item.id for item in combo]
        db_outfit.feedback = breakdown.get("feedback", [])
        session.add(db_outfit)

    session.commit()

    elapsed_ms = (time.time() - start_time) * 1000

    return {
        "outfits": top_outfits,
        "count": len(top_outfits),
        "occasion": request.occasion,
        "generation_time_ms": round(elapsed_ms, 2),
    }


def _cartesian_product(*lists):
    """Yield all combinations from multiple lists."""
    if not lists:
        yield ()
        return
    for item in lists[0]:
        for rest in _cartesian_product(*lists[1:]):
            yield (item,) + rest


async def get_saved_outfits(
    session: Session,
    user_id: str,
    all_items: List[ClothingItem],
) -> List[OutfitWithItems]:
    """Get user's saved outfits."""
    outfits = session.exec(
        select(Outfit).where(
            Outfit.user_id == user_id,
            Outfit.is_saved == True,
        )
    ).all()

    items_map = {item.id: item for item in all_items}
    return [_build_outfit_with_items(o, items_map) for o in outfits]


async def save_outfit(session: Session, outfit_id: str, user_id: str) -> Outfit:
    """Save an outfit."""
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise NotFoundError("Outfit", outfit_id)
    if outfit.user_id != user_id:
        raise AuthorizationError()
    outfit.is_saved = True
    session.add(outfit)
    session.commit()
    session.refresh(outfit)
    return outfit


async def like_outfit(
    session: Session,
    outfit_id: str,
    user_id: str,
    liked: bool,
) -> Outfit:
    """Like or dislike an outfit and record feedback."""
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise NotFoundError("Outfit", outfit_id)
    if outfit.user_id != user_id:
        raise AuthorizationError()

    outfit.liked = liked
    session.add(outfit)

    # Record feedback
    feedback = Feedback(user_id=user_id, outfit_id=outfit_id, liked=liked)
    session.add(feedback)
    session.commit()
    session.refresh(outfit)
    return outfit
