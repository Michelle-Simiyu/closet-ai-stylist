from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json


class OutfitBase(SQLModel):
    name: Optional[str] = None
    occasion: str = "casual"


class Outfit(OutfitBase, table=True):
    __tablename__ = "outfits"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    items_json: str = Field(default="[]")  # JSON list of item IDs
    compatibility_score: float = Field(default=0.0)
    liked: bool = Field(default=False)
    worn_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_saved: bool = Field(default=False)
    # Cached AI data
    feedback_json: Optional[str] = None
    description: Optional[str] = None

    @property
    def items(self) -> List[str]:
        return json.loads(self.items_json)

    @items.setter
    def items(self, value: List[str]):
        self.items_json = json.dumps(value)

    @property
    def feedback(self) -> List[str]:
        if self.feedback_json:
            return json.loads(self.feedback_json)
        return []

    @feedback.setter
    def feedback(self, value: List[str]):
        self.feedback_json = json.dumps(value)


class OutfitRead(SQLModel):
    id: str
    user_id: str
    name: Optional[str]
    occasion: str
    items: List[str]
    compatibility_score: float
    liked: bool
    worn_count: int
    created_at: datetime
    is_saved: bool
    feedback: List[str]
    description: Optional[str]


class OutfitWithItems(SQLModel):
    id: str
    user_id: str
    name: Optional[str]
    occasion: str
    items: List[Any]  # ClothingItemRead objects
    compatibility_score: float
    liked: bool
    worn_count: int
    created_at: datetime
    is_saved: bool
    feedback: List[str]
    description: Optional[str]


class GenerateOutfitsRequest(SQLModel):
    occasion: str = "casual"
    weather: Optional[str] = None
    temperature: Optional[float] = None
    max_outfits: int = Field(default=5, ge=1, le=10)
    style_preference: Optional[str] = None


class OutfitGenerationResponse(SQLModel):
    outfits: List[OutfitWithItems]
    count: int
    occasion: str
    generation_time_ms: float


class FeedbackRequest(SQLModel):
    liked: bool
