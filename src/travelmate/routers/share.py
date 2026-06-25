from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.travelmate.database import get_db
from src.travelmate.models.day import Day
from src.travelmate.models.trip import Trip, TripVisibility
from src.travelmate.schemas.trip import TripDetailResponse

router = APIRouter(tags=["share"])


@router.get("/api/trips/share/{share_code}", response_model=TripDetailResponse)
async def get_shared_trip(share_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trip)
        .options(selectinload(Trip.days).selectinload(Day.activities), selectinload(Trip.members))
        .where(Trip.share_code == share_code, Trip.visibility.in_([TripVisibility.SHARED, TripVisibility.PUBLIC]))
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not shared")
    return trip
