"""Admin-only endpoints for system maintenance."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.admin_deps import require_admin
from src.travelmate.database import get_db
from src.travelmate.models.activity import Activity
from src.travelmate.models.day import Day
from src.travelmate.models.expense import Expense
from src.travelmate.models.memory import Memory
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    """System statistics."""
    users = (await db.execute(select(func.count(User.id)))).scalar()
    trips = (await db.execute(select(func.count(Trip.id)))).scalar()
    activities = (await db.execute(select(func.count(Activity.id)))).scalar()
    expenses = (await db.execute(select(func.count(Expense.id)))).scalar()
    memories = (await db.execute(select(func.count(Memory.id)))).scalar()
    return {
        "total_users": users,
        "total_trips": trips,
        "total_activities": activities,
        "total_expenses": expenses,
        "total_memories": memories,
    }


@router.get("/users")
async def list_users(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(100))
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "is_admin": u.is_admin,
            "created_at": str(u.created_at) if u.created_at else None,
        }
        for u in users
    ]


@router.put("/users/{user_id}/toggle-admin")
async def toggle_admin(user_id: str, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own admin status")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin
    await db.commit()
    return {"id": user.id, "is_admin": user.is_admin}


@router.get("/trips/recent")
async def list_recent_trips(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).order_by(Trip.created_at.desc()).limit(50))
    trips = result.scalars().all()
    return [{"id": t.id, "title": t.title, "created_at": str(t.created_at) if t.created_at else None} for t in trips]
