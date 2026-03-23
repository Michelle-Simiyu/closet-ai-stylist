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
    style_profile_json: Optional[str] = Field(default=None)
    # Profile fields
    gender: Optional[str] = Field(default=None)          # male/female/nonbinary/prefer_not_to_say
    country: Optional[str] = Field(default=None)          # e.g. "Kenya", "United States"
    bio: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    # Privacy
    closet_visibility: str = Field(default="private")     # private / friends / public
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


class UserUpdate(SQLModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    avatar_url: Optional[str] = None
    closet_visibility: Optional[str] = None


class UserChangePassword(SQLModel):
    current_password: str
    new_password: str


class UserRead(SQLModel):
    id: str
    email: str
    username: str
    style_profile: Optional[Dict[str, Any]] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    closet_visibility: str = "private"
    created_at: datetime


class UserPublic(SQLModel):
    """Public profile — no sensitive fields exposed."""
    id: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    closet_visibility: str
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
    color_preference: str      # neutral, bold, mixed
    occasion_priority: str     # casual, work, formal
    budget_sensitivity: str    # low, medium, high
    gender: Optional[str] = None
    country: Optional[str] = None
