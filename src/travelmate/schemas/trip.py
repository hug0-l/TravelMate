from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.travelmate.models.trip import TripVisibility


class TripCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None  # Auto-calculated if duration_days given
    duration_days: Optional[int] = None  # If set, auto-generate days + end_date
    visibility: TripVisibility = TripVisibility.PRIVATE
    origin_country: Optional[str] = None
    destination_country: Optional[str] = None
    destination_tz_offset: Optional[int] = None  # Hours from UTC


class TripUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    visibility: Optional[TripVisibility] = None
    origin_country: Optional[str] = None
    destination_country: Optional[str] = None
    destination_tz_offset: Optional[int] = None


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    cover_url: Optional[str] = None
    share_code: str
    visibility: TripVisibility = TripVisibility.PRIVATE
    origin_country: Optional[str] = None
    destination_country: Optional[str] = None
    destination_tz_offset: Optional[int] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TripListResponse(BaseModel):
    trips: list[TripResponse]
