from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class POICreate(BaseModel):
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None
    notes: Optional[str] = None
    category: str = "other"


class POIUpdate(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None


class POIResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None
    notes: Optional[str] = None
    category: str
    created_at: datetime | None = None
