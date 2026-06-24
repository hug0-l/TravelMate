from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.poi import POI
from src.travelmate.models.user import User
from src.travelmate.schemas.poi import POICreate, POIResponse, POIUpdate

router = APIRouter(tags=["pois"])


async def _verify_trip_access(trip_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == trip_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")


@router.get("/api/trips/{trip_id}/pois", response_model=list[POIResponse])
async def list_pois(trip_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(select(POI).where(POI.trip_id == trip_id).order_by(POI.created_at.desc()))
    return result.scalars().all()


@router.post("/api/trips/{trip_id}/pois", response_model=POIResponse, status_code=status.HTTP_201_CREATED)
async def create_poi(trip_id: str, body: POICreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _verify_trip_access(trip_id, user, db)
    poi = POI(trip_id=trip_id, name=body.name, address=body.address, lat=body.lat, lng=body.lng,
              place_id=body.place_id, notes=body.notes, category=body.category)
    db.add(poi)
    await db.commit()
    await db.refresh(poi)
    return poi


@router.put("/api/pois/{poi_id}", response_model=POIResponse)
async def update_poi(poi_id: str, body: POIUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(POI).join(Trip).join(TripMember).where(POI.id == poi_id, TripMember.user_id == user.id)
    )
    poi = result.scalar_one_or_none()
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(poi, field, val)
    await db.commit()
    await db.refresh(poi)
    return poi


@router.delete("/api/pois/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poi(poi_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(POI).join(Trip).join(TripMember).where(POI.id == poi_id, TripMember.user_id == user.id)
    )
    poi = result.scalar_one_or_none()
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    await db.delete(poi)
    await db.commit()
