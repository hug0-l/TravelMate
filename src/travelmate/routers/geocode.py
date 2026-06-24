from fastapi import APIRouter, HTTPException
import httpx

from src.travelmate.schemas.location import GeocodeSearchResult

router = APIRouter(prefix="/api/geocode", tags=["geocode"])

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


@router.get("/search", response_model=list[GeocodeSearchResult])
async def search_places(q: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            NOMINATIM_URL,
            params={"q": q, "format": "json", "limit": 10},
            headers={"User-Agent": "TravelMate/0.1"},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Geocoding service error")
        data = resp.json()
    return [
        GeocodeSearchResult(
            display_name=item["display_name"],
            lat=float(item["lat"]),
            lng=float(item["lon"]),
            place_id=str(item["osm_id"]),
        )
        for item in data
    ]
