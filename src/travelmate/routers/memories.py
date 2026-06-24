"""Memory routes — CRUD for trip memories."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.memory import Memory
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.memory import MemoryCreate, MemoryResponse, MemoryUpdate

router = APIRouter(tags=["memories"])


async def _verify_trip_access(trip_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == trip_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")


def _serialize_photo_urls(photo_urls: list[str] | None) -> str | None:
    if photo_urls is None:
        return None
    return json.dumps(photo_urls)


def _deserialize_photo_urls(photo_urls: str | None) -> list[str] | None:
    if photo_urls is None:
        return None
    return json.loads(photo_urls)


async def _enrich_memories(memories: list[Memory], db: AsyncSession) -> list[MemoryResponse]:
    """Attach user names to memory responses."""
    user_ids = {m.user_id for m in memories}
    users = {}
    if user_ids:
        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = {u.id: u.name for u in result.scalars().all()}

    return [
        MemoryResponse(
            id=m.id,
            trip_id=m.trip_id,
            user_id=m.user_id,
            user_name=users.get(m.user_id, "Unknown"),
            title=m.title,
            content=m.content,
            photo_urls=_deserialize_photo_urls(m.photo_urls),
            date=m.date,
            created_at=m.created_at,
        )
        for m in memories
    ]


@router.get("/api/trips/{trip_id}/memories", response_model=list[MemoryResponse])
async def list_memories(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(Memory).where(Memory.trip_id == trip_id).order_by(Memory.date.desc())
    )
    memories = result.scalars().all()
    return await _enrich_memories(memories, db)


@router.post("/api/trips/{trip_id}/memories", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    trip_id: str,
    body: MemoryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    memory = Memory(
        trip_id=trip_id,
        user_id=user.id,
        title=body.title,
        content=body.content,
        photo_urls=_serialize_photo_urls(body.photo_urls),
        date=body.date,
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    enriched = await _enrich_memories([memory], db)
    return enriched[0]


@router.put("/api/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    body: MemoryUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Verify ownership
    if memory.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this memory")

    update_data = body.model_dump(exclude_unset=True)
    # Handle photo_urls serialization
    if "photo_urls" in update_data:
        update_data["photo_urls"] = _serialize_photo_urls(update_data["photo_urls"])
    for field, value in update_data.items():
        setattr(memory, field, value)

    await db.commit()
    await db.refresh(memory)
    enriched = await _enrich_memories([memory], db)
    return enriched[0]


@router.delete("/api/memories/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    memory = result.scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Verify ownership
    if memory.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this memory")

    await db.delete(memory)
    await db.commit()
