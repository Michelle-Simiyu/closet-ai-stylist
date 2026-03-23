import logging
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from ..models.clothing import ClothingItem, ClothingItemCreate, ClothingItemUpdate
from ..core.exceptions import NotFoundError, AuthorizationError

logger = logging.getLogger(__name__)


# Demo closet items — pre-loaded for demos
DEMO_ITEMS = [
    {
        "name": "White Button-Down Shirt",
        "category": "top",
        "color": "white",
        "style": "minimalist",
        "pattern": "solid",
        "formality": 3,
        "season": "all",
        "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400",
    },
    {
        "name": "Navy Slim Chinos",
        "category": "bottom",
        "color": "navy",
        "style": "minimalist",
        "pattern": "solid",
        "formality": 3,
        "season": "all",
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400",
    },
    {
        "name": "Black Blazer",
        "category": "outerwear",
        "color": "black",
        "style": "formal",
        "pattern": "solid",
        "formality": 4,
        "season": "all",
        "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400",
    },
    {
        "name": "Floral Summer Dress",
        "category": "dress",
        "color": "pink",
        "secondary_color": "white",
        "style": "bohemian",
        "pattern": "floral",
        "formality": 2,
        "season": "summer",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400",
    },
    {
        "name": "Blue Denim Jeans",
        "category": "bottom",
        "color": "denim",
        "style": "casual",
        "pattern": "solid",
        "formality": 2,
        "season": "all",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
    },
    {
        "name": "Striped Casual Tee",
        "category": "top",
        "color": "white",
        "secondary_color": "navy",
        "style": "casual",
        "pattern": "striped",
        "formality": 1,
        "season": "summer",
        "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400",
    },
    {
        "name": "Camel Wool Coat",
        "category": "outerwear",
        "color": "camel",
        "style": "minimalist",
        "pattern": "solid",
        "formality": 3,
        "season": "winter",
        "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400",
    },
    {
        "name": "White Leather Sneakers",
        "category": "shoes",
        "color": "white",
        "style": "casual",
        "pattern": "solid",
        "formality": 1,
        "season": "all",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
    },
    {
        "name": "Black Ankle Boots",
        "category": "shoes",
        "color": "black",
        "style": "minimalist",
        "pattern": "solid",
        "formality": 3,
        "season": "fall",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400",
    },
    {
        "name": "Olive Cargo Pants",
        "category": "bottom",
        "color": "olive",
        "style": "casual",
        "pattern": "solid",
        "formality": 2,
        "season": "fall",
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400",
    },
]


async def get_closet(
    session: Session,
    user_id: str,
    category: Optional[str] = None,
    color: Optional[str] = None,
    include_demo: bool = False,
) -> List[ClothingItem]:
    query = select(ClothingItem).where(ClothingItem.user_id == user_id)

    if not include_demo:
        query = query.where(ClothingItem.is_demo == False)

    if category:
        query = query.where(ClothingItem.category == category)

    if color:
        query = query.where(ClothingItem.color.contains(color))

    items = session.exec(query).all()
    return list(items)


async def get_item(session: Session, item_id: str, user_id: str) -> ClothingItem:
    item = session.get(ClothingItem, item_id)
    if not item:
        raise NotFoundError("ClothingItem", item_id)
    if item.user_id != user_id:
        raise AuthorizationError()
    return item


async def create_item(
    session: Session,
    item_data: ClothingItemCreate,
    user_id: str,
) -> ClothingItem:
    item = ClothingItem.model_validate(item_data)
    item.user_id = user_id
    session.add(item)
    session.commit()
    session.refresh(item)
    logger.info(f"Created item {item.id} for user {user_id}")
    return item


async def update_item(
    session: Session,
    item_id: str,
    item_data: ClothingItemUpdate,
    user_id: str,
) -> ClothingItem:
    item = await get_item(session, item_id, user_id)
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


async def delete_item(session: Session, item_id: str, user_id: str) -> None:
    item = await get_item(session, item_id, user_id)
    session.delete(item)
    session.commit()
    logger.info(f"Deleted item {item_id}")


async def load_demo_closet(session: Session, user_id: str) -> List[ClothingItem]:
    """Load demo clothing items for a user."""
    # Remove existing demo items
    existing = session.exec(
        select(ClothingItem).where(
            ClothingItem.user_id == user_id,
            ClothingItem.is_demo == True,
        )
    ).all()
    for item in existing:
        session.delete(item)

    items = []
    for data in DEMO_ITEMS:
        item = ClothingItem(**data, user_id=user_id, is_demo=True)
        session.add(item)
        items.append(item)

    session.commit()
    for item in items:
        session.refresh(item)

    logger.info(f"Loaded {len(items)} demo items for user {user_id}")
    return items


async def get_closet_stats(session: Session, user_id: str) -> dict:
    """Get analytics stats for user's closet."""
    items = await get_closet(session, user_id, include_demo=True)

    if not items:
        return {"total": 0, "categories": {}, "colors": {}, "styles": {}}

    categories: dict = {}
    colors: dict = {}
    styles: dict = {}

    for item in items:
        cat = item.category.value
        categories[cat] = categories.get(cat, 0) + 1

        col = item.color
        colors[col] = colors.get(col, 0) + 1

        sty = item.style.value
        styles[sty] = styles.get(sty, 0) + 1

    return {
        "total": len(items),
        "categories": categories,
        "colors": colors,
        "styles": styles,
        "most_worn": max(items, key=lambda x: x.times_worn).name if items else None,
    }
