"""Packing list routes — CRUD + batch toggle."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.packing_item import PackingItem
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.packing import (
    BatchToggleRequest,
    PackingItemCreate,
    PackingItemResponse,
    PackingItemUpdate,
)

router = APIRouter(tags=["packing"])


async def _verify_trip_access(trip_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == trip_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")


@router.get("/api/trips/{trip_id}/packing", response_model=list[PackingItemResponse])
async def list_packing_items(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(PackingItem)
        .where(PackingItem.trip_id == trip_id)
        .order_by(PackingItem.category, PackingItem.created_at)
    )
    return result.scalars().all()


@router.post("/api/trips/{trip_id}/packing", response_model=PackingItemResponse, status_code=status.HTTP_201_CREATED)
async def create_packing_item(
    trip_id: str,
    body: PackingItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    item = PackingItem(
        trip_id=trip_id,
        user_id=user.id,
        name=body.name,
        category=body.category,
        quantity=body.quantity,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/api/packing/{item_id}", response_model=PackingItemResponse)
async def update_packing_item(
    item_id: str,
    body: PackingItemUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PackingItem).where(PackingItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await _verify_trip_access(item.trip_id, user, db)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/api/packing/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packing_item(
    item_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PackingItem).where(PackingItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await _verify_trip_access(item.trip_id, user, db)
    await db.delete(item)
    await db.commit()


@router.put("/api/trips/{trip_id}/packing/batch-toggle")
async def batch_toggle(
    trip_id: str,
    body: BatchToggleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(PackingItem).where(
            PackingItem.id.in_(body.item_ids),
            PackingItem.trip_id == trip_id,
        )
    )
    items = result.scalars().all()
    for item in items:
        item.checked = body.checked
    await db.commit()
    return {"updated": len(items)}
