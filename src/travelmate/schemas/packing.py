"""Packing list schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PackingItemCreate(BaseModel):
    name: str
    category: str = "other"
    quantity: int = 1


class PackingItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    checked: Optional[bool] = None
    quantity: Optional[int] = None


class PackingItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    user_id: str
    name: str
    category: str
    checked: bool
    quantity: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BatchToggleRequest(BaseModel):
    item_ids: list[str]
    checked: bool
