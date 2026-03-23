from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str


class User(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    password_hash: str
    style_profile_json: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_demo: bool = Field(default=False)

    @property
    def style_profile(self) -> Dict[str, Any]:
        if self.style_profile_json:
            return json.loads(self.style_profile_json)
        return {}

    @style_profile.setter
    def style_profile(self, value: Dict[str, Any]):
        self.style_profile_json = json.dumps(value)


class UserCreate(SQLModel):
    email: str
    username: str
    password: str


class UserRead(SQLModel):
    id: str
    email: str
    username: str
    style_profile: Optional[Dict[str, Any]] = None
    created_at: datetime


class UserLogin(SQLModel):
    email: str
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class StyleQuizResponse(SQLModel):
    preferred_styles: list[str]
    formality_preference: int  # 1-5
    color_preference: str  # neutral, bold, mixed
    occasion_priority: str  # casual, work, formal
    budget_sensitivity: str  # low, medium, high
