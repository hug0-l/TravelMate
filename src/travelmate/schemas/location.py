from typing import Optional

from pydantic import BaseModel, ConfigDict


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None


class GeocodeSearchResult(BaseModel):
    display_name: str
    lat: float
    lng: float
    place_id: str
