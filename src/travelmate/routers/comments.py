"""Activity comment routes — CRUD."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.travelmate.auth.deps import get_current_user
from src.travelmate.database import get_db
from src.travelmate.models.activity_comment import ActivityComment
from src.travelmate.models.activity import Activity
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.schemas.activity_comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)

router = APIRouter(tags=["comments"])


async def _verify_activity_access(activity_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Activity)
        .join(Trip)
        .join(TripMember)
        .where(Activity.id == activity_id, TripMember.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Activity not found")


@router.get("/api/activities/{activity_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    activity_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_activity_access(activity_id, user, db)
    result = await db.execute(
        select(ActivityComment)
        .where(ActivityComment.activity_id == activity_id)
        .order_by(ActivityComment.created_at)
    )
    comments = result.scalars().all()

    # Enrich with user names
    user_ids = {c.user_id for c in comments}
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u.name for u in users_result.scalars().all()}

    return [
        CommentResponse(
            id=c.id,
            activity_id=c.activity_id,
            user_id=c.user_id,
            user_name=users.get(c.user_id, "Unknown"),
            content=c.content,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in comments
    ]


@router.post(
    "/api/activities/{activity_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    activity_id: str,
    body: CommentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_activity_access(activity_id, user, db)
    comment = ActivityComment(
        activity_id=activity_id,
        user_id=user.id,
        content=body.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentResponse(
        id=comment.id,
        activity_id=comment.activity_id,
        user_id=comment.user_id,
        user_name=user.name,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ActivityComment).where(ActivityComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot delete others' comments")
    await db.delete(comment)
    await db.commit()
