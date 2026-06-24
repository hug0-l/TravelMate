from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MemoryCreate(BaseModel):
    title: str
    content: Optional[str] = None
    photo_urls: Optional[list[str]] = None  # List of URLs, will be stored as JSON
    date: date


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    photo_urls: Optional[list[str]] = None


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    user_id: str
    user_name: str = ""
    title: str
    content: Optional[str] = None
    photo_urls: Optional[list[str]] = None
    date: date
    created_at: datetime | None = None
    updated_at: datetime | None = None
