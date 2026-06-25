"""Poll routes — CRUD + vote."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.poll import Poll, PollOption, PollVote
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.poll import (
    PollCreate,
    PollOptionResponse,
    PollResponse,
    PollVoteRequest,
)

router = APIRouter(tags=["polls"])


async def _verify_trip_access(trip_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Trip).join(TripMember).where(Trip.id == trip_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")


@router.get("/api/trips/{trip_id}/polls", response_model=list[PollResponse])
async def list_polls(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    result = await db.execute(
        select(Poll)
        .options(selectinload(Poll.options).selectinload(PollOption.votes))
        .where(Poll.trip_id == trip_id)
        .order_by(Poll.created_at.desc())
    )
    polls = result.scalars().all()
    
    # Enrich with creator names and vote info
    user_ids = {p.creator_id for p in polls}
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u.name for u in users_result.scalars().all()}
    
    responses = []
    for p in polls:
        total_votes = sum(len(o.votes) for o in p.options)
        options = [
            PollOptionResponse(
                id=o.id,
                label=o.label,
                vote_count=len(o.votes),
                voted=any(v.user_id == user.id for v in o.votes),
            )
            for o in p.options
        ]
        responses.append(PollResponse(
            id=p.id,
            trip_id=p.trip_id,
            creator_id=p.creator_id,
            creator_name=users.get(p.creator_id, "Unknown"),
            question=p.question,
            is_closed=p.is_closed,
            options=options,
            total_votes=total_votes,
            created_at=p.created_at,
        ))
    return responses


@router.post("/api/trips/{trip_id}/polls", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
async def create_poll(
    trip_id: str,
    body: PollCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_trip_access(trip_id, user, db)
    if len(body.options) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 options")
    
    poll = Poll(trip_id=trip_id, creator_id=user.id, question=body.question)
    db.add(poll)
    await db.flush()
    
    for label in body.options:
        db.add(PollOption(poll_id=poll.id, label=label))
    
    await db.commit()
    await db.refresh(poll)
    
    # Reload with options
    result = await db.execute(
        select(Poll).options(selectinload(Poll.options).selectinload(PollOption.votes))
        .where(Poll.id == poll.id)
    )
    poll = result.scalar_one()
    
    return PollResponse(
        id=poll.id,
        trip_id=poll.trip_id,
        creator_id=poll.creator_id,
        creator_name=user.name,
        question=poll.question,
        is_closed=poll.is_closed,
        options=[
            PollOptionResponse(id=o.id, label=o.label, vote_count=0, voted=False)
            for o in poll.options
        ],
        total_votes=0,
        created_at=poll.created_at,
    )


@router.post("/api/polls/{poll_id}/vote")
async def vote_poll(
    poll_id: str,
    body: PollVoteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Poll).options(selectinload(Poll.options)).where(Poll.id == poll_id)
    )
    poll = result.scalar_one_or_none()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll.is_closed:
        raise HTTPException(status_code=400, detail="Poll is closed")
    await _verify_trip_access(poll.trip_id, user, db)
    
    # Check option belongs to poll
    option_ids = [o.id for o in poll.options]
    if body.option_id not in option_ids:
        raise HTTPException(status_code=400, detail="Invalid option")
    
    # Remove previous vote
    old_vote = await db.execute(
        select(PollVote).where(PollVote.option_id.in_(option_ids), PollVote.user_id == user.id)
    )
    for v in old_vote.scalars().all():
        await db.delete(v)
    
    # Add new vote
    vote = PollVote(option_id=body.option_id, user_id=user.id)
    db.add(vote)
    await db.commit()
    return {"status": "voted"}


@router.put("/api/polls/{poll_id}/close")
async def close_poll(
    poll_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Poll).where(Poll.id == poll_id))
    poll = result.scalar_one_or_none()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    await _verify_trip_access(poll.trip_id, user, db)
    poll.is_closed = True
    await db.commit()
    return {"status": "closed"}
