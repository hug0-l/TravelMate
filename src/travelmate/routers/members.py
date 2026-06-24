"""Member management routes — invite, list, remove trip members."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.auth import TokenResponse
from pydantic import BaseModel, ConfigDict, EmailStr

router = APIRouter(tags=["members"])


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    email: str
    role: str


class InviteRequest(BaseModel):
    email: EmailStr


@router.get("/api/trips/{trip_id}/members", response_model=list[MemberResponse])
async def list_members(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify requester is a member
    result = await db.execute(
        select(TripMember).where(
            TripMember.trip_id == trip_id,
            TripMember.user_id == user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")

    members_result = await db.execute(
        select(TripMember, User)
        .join(User, TripMember.user_id == User.id)
        .where(TripMember.trip_id == trip_id)
    )
    rows = members_result.all()
    return [
        MemberResponse(
            id=row.TripMember.id,
            user_id=row.User.id,
            name=row.User.name,
            email=row.User.email,
            role=row.TripMember.role,
        )
        for row in rows
    ]


@router.post("/api/trips/{trip_id}/members/invite", status_code=status.HTTP_201_CREATED)
async def invite_member(
    trip_id: str,
    body: InviteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invite a user by email to join the trip. Only owner/editor can invite."""
    # Verify requester is owner
    result = await db.execute(
        select(TripMember).where(
            TripMember.trip_id == trip_id,
            TripMember.user_id == user.id,
            TripMember.role == "owner",
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only trip owner can invite members")

    # Find user by email
    user_result = await db.execute(select(User).where(User.email == body.email))
    invited_user = user_result.scalar_one_or_none()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check not already a member
    existing = await db.execute(
        select(TripMember).where(
            TripMember.trip_id == trip_id,
            TripMember.user_id == invited_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")

    member = TripMember(trip_id=trip_id, user_id=invited_user.id, role="editor")
    db.add(member)
    await db.commit()
    return {"message": f"{invited_user.name} has been added as editor"}


@router.delete("/api/trips/{trip_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    trip_id: str,
    member_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member. Only owner can remove. Cannot remove self (use leave)."""
    # Verify requester is owner
    result = await db.execute(
        select(TripMember).where(
            TripMember.trip_id == trip_id,
            TripMember.user_id == user.id,
            TripMember.role == "owner",
        )
    )
    owner_member = result.scalar_one_or_none()
    if not owner_member:
        raise HTTPException(status_code=403, detail="Only trip owner can remove members")

    # Find the member to remove
    member_result = await db.execute(
        select(TripMember).where(TripMember.id == member_id, TripMember.trip_id == trip_id)
    )
    member = member_result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself as owner")

    await db.delete(member)
    await db.commit()
