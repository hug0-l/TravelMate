from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.travelmate.models.activity import ActivityCategory


class LocationBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lat: float | None = None
    lng: float | None = None
    name: str | None = None


class ActivityCreate(BaseModel):
    title: str
    notes: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    transport_mode: Optional[str] = None
    category: ActivityCategory = ActivityCategory.OTHER
    location_id: Optional[str] = None
    from_location_id: Optional[str] = None
    to_location_id: Optional[str] = None
    assignee_id: Optional[str] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    transport_mode: Optional[str] = None
    category: Optional[ActivityCategory] = None
    location_id: Optional[str] = None
    from_location_id: Optional[str] = None
    to_location_id: Optional[str] = None
    assignee_id: Optional[str] = None


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day_id: str
    location_id: Optional[str] = None
    title: str
    notes: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    transport_mode: Optional[str] = None
    from_location_id: Optional[str] = None
    to_location_id: Optional[str] = None
    category: ActivityCategory
    order_index: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    location: LocationBrief | None = None
    assignee_id: str | None = None
    assignee_name: str | None = None


class ActivityReorder(BaseModel):
    activity_ids: list[str]
