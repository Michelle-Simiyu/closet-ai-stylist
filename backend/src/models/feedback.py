from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    outfit_id: str = Field(foreign_key="outfits.id", index=True)
    liked: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackCreate(SQLModel):
    outfit_id: str
    liked: bool


class FeedbackRead(SQLModel):
    id: str
    user_id: str
    outfit_id: str
    liked: bool
    timestamp: datetime
