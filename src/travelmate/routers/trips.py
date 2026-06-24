from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.day import Day
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.trip import TripCreate, TripResponse, TripUpdate

router = APIRouter(prefix="/api/trips", tags=["trips"])

async def _get_user_trip(trip_id: str, user: User, db: AsyncSession) -> Trip:
    result = await db.execute(
        select(Trip).join(TripMember).where(
            Trip.id == trip_id,
            TripMember.user_id == user.id,
        )
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("/", response_model=list[TripResponse])
async def list_trips(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trip).join(TripMember).where(TripMember.user_id == user.id).order_by(Trip.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(body: TripCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Calculate end_date from duration_days if provided
    end_date = body.end_date
    if body.duration_days and not end_date:
        end_date = body.start_date + timedelta(days=body.duration_days - 1)

    trip = Trip(
        title=body.title,
        description=body.description,
        start_date=body.start_date,
        end_date=end_date,
        visibility=body.visibility,
        origin_country=body.origin_country,
        destination_country=body.destination_country,
        destination_tz_offset=body.destination_tz_offset,
    )
    db.add(trip)
    await db.flush()

    # Auto-generate Day records if duration_days is provided
    if body.duration_days:
        for i in range(body.duration_days):
            day_date = body.start_date + timedelta(days=i)
            day = Day(
                trip_id=trip.id,
                date=day_date,
                title=f"第 {i + 1} 天" if not body.destination_country else f"Day {i + 1}",
                order_index=i,
            )
            db.add(day)

    member = TripMember(trip_id=trip.id, user_id=user.id, role="owner")
    db.add(member)
    await db.commit()
    await db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    trip = await _get_user_trip(trip_id, user, db)
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str, body: TripUpdate,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    trip = await _get_user_trip(trip_id, user, db)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
    await db.commit()
    await db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    trip = await _get_user_trip(trip_id, user, db)
    await db.delete(trip)
    await db.commit()
