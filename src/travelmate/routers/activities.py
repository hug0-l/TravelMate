from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.activity import Activity
from src.travelmate.models.day import Day
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.activity import ActivityCreate, ActivityReorder, ActivityResponse, ActivityUpdate

router = APIRouter(tags=["activities"])


async def _verify_trip_access_via_day(day_id: str, user: User, db: AsyncSession):
    result = await db.execute(select(Day).where(Day.id == day_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    trip_result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == day.trip_id, TripMember.user_id == user.id)
    )
    if not trip_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")
    return day


@router.get("/api/days/{day_id}/activities", response_model=list[ActivityResponse])
async def list_activities(day_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _verify_trip_access_via_day(day_id, user, db)
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.location))
        .where(Activity.day_id == day_id)
        .order_by(Activity.order_index)
    )
    return result.scalars().all()


@router.post("/api/days/{day_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    day_id: str, body: ActivityCreate,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access_via_day(day_id, user, db)
    result = await db.execute(
        select(Activity).where(Activity.day_id == day_id).order_by(Activity.order_index.desc()).limit(1)
    )
    last = result.scalar_one_or_none()
    order_index = (last.order_index + 1) if last else 0
    activity = Activity(
        day_id=day_id,
        title=body.title,
        notes=body.notes,
        start_time=body.start_time,
        end_time=body.end_time,
        duration_minutes=body.duration_minutes,
        transport_mode=body.transport_mode,
        category=body.category,
        location_id=body.location_id,
        from_location_id=body.from_location_id,
        to_location_id=body.to_location_id,
        order_index=order_index,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    # Re-fetch with location loaded for response
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.location))
        .where(Activity.id == activity.id)
    )
    return result.scalar_one()


@router.put("/api/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: str, body: ActivityUpdate,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity).options(selectinload(Activity.location)).where(Activity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    await _verify_trip_access_via_day(activity.day_id, user, db)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    await db.commit()
    await db.refresh(activity)
    # Re-fetch with location loaded for response
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.location))
        .where(Activity.id == activity.id)
    )
    return result.scalar_one()


@router.delete("/api/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    await _verify_trip_access_via_day(activity.day_id, user, db)
    await db.delete(activity)
    await db.commit()


@router.put("/api/days/{day_id}/activities/reorder", response_model=list[ActivityResponse])
async def reorder_activities(
    day_id: str, body: ActivityReorder,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access_via_day(day_id, user, db)
    for idx, activity_id in enumerate(body.activity_ids):
        await db.execute(update(Activity).where(Activity.id == activity_id).values(order_index=idx))
    await db.commit()
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.location))
        .where(Activity.day_id == day_id)
        .order_by(Activity.order_index)
    )
    return result.scalars().all()
