from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    activity_id: str
    user_id: str
    user_name: str = ""
    content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
