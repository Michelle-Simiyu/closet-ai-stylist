from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class FriendshipStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    blocked = "blocked"


class Friendship(SQLModel, table=True):
    __tablename__ = "friendships"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    requester_id: str = Field(foreign_key="users.id", index=True)
    addressee_id: str = Field(foreign_key="users.id", index=True)
    status: FriendshipStatus = Field(default=FriendshipStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class FriendshipRead(SQLModel):
    id: str
    requester_id: str
    addressee_id: str
    status: FriendshipStatus
    created_at: datetime


class ClosetListing(SQLModel, table=True):
    __tablename__ = "closet_listings"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    item_id: str = Field(foreign_key="clothing_items.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    price: Optional[float] = None
    currency: str = Field(default="USD")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_sold: bool = Field(default=False)


class ClosetListingCreate(SQLModel):
    item_id: str
    price: Optional[float] = None
    currency: str = "USD"
    description: Optional[str] = None


class ClosetListingRead(SQLModel):
    id: str
    item_id: str
    user_id: str
    price: Optional[float]
    currency: str
    description: Optional[str]
    created_at: datetime
    is_sold: bool


class ClosetRecommendation(SQLModel, table=True):
    __tablename__ = "closet_recommendations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    from_user_id: str = Field(foreign_key="users.id", index=True)
    to_user_id: str = Field(foreign_key="users.id", index=True)
    item_id: Optional[str] = Field(default=None, foreign_key="clothing_items.id")
    outfit_id: Optional[str] = Field(default=None, foreign_key="outfits.id")
    message: Optional[str] = None
    rec_type: str = Field(default="add")   # add / remove / replace / outfit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = Field(default=False)


class ClosetRecommendationCreate(SQLModel):
    to_user_id: str
    item_id: Optional[str] = None
    outfit_id: Optional[str] = None
    message: Optional[str] = None
    rec_type: str = "add"


class ClosetRecommendationRead(SQLModel):
    id: str
    from_user_id: str
    to_user_id: str
    item_id: Optional[str]
    outfit_id: Optional[str]
    message: Optional[str]
    rec_type: str
    created_at: datetime
    is_read: bool
