from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum


class Category(str, Enum):
    top = "top"
    bottom = "bottom"
    dress = "dress"
    shoes = "shoes"
    outerwear = "outerwear"
    accessory = "accessory"


class Style(str, Enum):
    casual = "casual"
    formal = "formal"
    sporty = "sporty"
    bohemian = "bohemian"
    minimalist = "minimalist"


class Pattern(str, Enum):
    solid = "solid"
    striped = "striped"
    checkered = "checkered"
    floral = "floral"
    geometric = "geometric"
    abstract = "abstract"


class Season(str, Enum):
    summer = "summer"
    winter = "winter"
    spring = "spring"
    fall = "fall"
    all = "all"


class ClothingItemBase(SQLModel):
    name: str
    category: Category
    subcategory: Optional[str] = None
    color: str
    secondary_color: Optional[str] = None
    style: Style = Style.casual
    pattern: Pattern = Pattern.solid
    formality: int = Field(default=2, ge=1, le=5)
    season: Season = Season.all
    image_url: Optional[str] = None
    brand: Optional[str] = None
    notes: Optional[str] = None


class ClothingItem(ClothingItemBase, table=True):
    __tablename__ = "clothing_items"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    times_worn: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_demo: bool = Field(default=False)


class ClothingItemCreate(ClothingItemBase):
    pass


class ClothingItemUpdate(SQLModel):
    name: Optional[str] = None
    category: Optional[Category] = None
    subcategory: Optional[str] = None
    color: Optional[str] = None
    secondary_color: Optional[str] = None
    style: Optional[Style] = None
    pattern: Optional[Pattern] = None
    formality: Optional[int] = Field(default=None, ge=1, le=5)
    season: Optional[Season] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    notes: Optional[str] = None


class ClothingItemRead(ClothingItemBase):
    id: str
    user_id: str
    times_worn: int
    created_at: datetime
    is_demo: bool
