"""Guest join endpoints — no account needed."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.travelmate.auth.guest_jwt import create_guest_token
from src.travelmate.database import get_db
from src.travelmate.models.trip import Trip
from src.travelmate.schemas.guest import GuestJoinRequest, GuestTokenResponse

router = APIRouter(tags=["guest"])


@router.post("/api/trips/join", response_model=GuestTokenResponse)
async def join_trip_as_guest(body: GuestJoinRequest, db: AsyncSession = Depends(get_db)):
    """Join a trip using trip_id + join_code (no account needed)."""
    result = await db.execute(select(Trip).where(Trip.id == body.trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.join_code != body.join_code:
        raise HTTPException(status_code=403, detail="Invalid join code")
    token = create_guest_token(body.trip_id, body.nickname)
    return GuestTokenResponse(access_token=token, trip_id=body.trip_id, nickname=body.nickname)


@router.get("/api/trips/{trip_id}/join-info")
async def get_join_info(trip_id: str, db: AsyncSession = Depends(get_db)):
    """Get the trip title and whether it exists (does NOT reveal join_code)."""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"id": trip.id, "title": trip.title}
