from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DayCreate(BaseModel):
    date: date
    title: Optional[str] = None


class DayUpdate(BaseModel):
    date: Optional[date] = None
    title: Optional[str] = None


class DayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    date: date
    title: Optional[str] = None
    order_index: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DayReorder(BaseModel):
    day_ids: list[str]
