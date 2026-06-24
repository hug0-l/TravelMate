from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.day import Day
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.day import DayCreate, DayResponse, DayReorder, DayUpdate

router = APIRouter(tags=["days"])


async def _verify_trip_access(trip_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == trip_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")


@router.get("/api/trips/{trip_id}/days", response_model=list[DayResponse])
async def list_days(trip_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(Day).where(Day.trip_id == trip_id).order_by(Day.order_index)
    )
    return result.scalars().all()


@router.post("/api/trips/{trip_id}/days", response_model=DayResponse, status_code=status.HTTP_201_CREATED)
async def create_day(
    trip_id: str, body: DayCreate,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    # Get max order_index
    result = await db.execute(
        select(Day).where(Day.trip_id == trip_id).order_by(Day.order_index.desc()).limit(1)
    )
    last = result.scalar_one_or_none()
    order_index = (last.order_index + 1) if last else 0
    day = Day(trip_id=trip_id, date=body.date, title=body.title, order_index=order_index)
    db.add(day)
    await db.commit()
    await db.refresh(day)
    return day


@router.put("/api/days/{day_id}", response_model=DayResponse)
async def update_day(
    day_id: str, body: DayUpdate,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Day).where(Day.id == day_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    await _verify_trip_access(day.trip_id, user, db)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(day, field, value)
    await db.commit()
    await db.refresh(day)
    return day


@router.delete("/api/days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_day(day_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Day).where(Day.id == day_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    await _verify_trip_access(day.trip_id, user, db)
    await db.delete(day)
    await db.commit()


@router.put("/api/trips/{trip_id}/days/reorder", response_model=list[DayResponse])
async def reorder_days(
    trip_id: str, body: DayReorder,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    for idx, day_id in enumerate(body.day_ids):
        await db.execute(update(Day).where(Day.id == day_id).values(order_index=idx))
    await db.commit()
    result = await db.execute(select(Day).where(Day.trip_id == trip_id).order_by(Day.order_index))
    return result.scalars().all()
