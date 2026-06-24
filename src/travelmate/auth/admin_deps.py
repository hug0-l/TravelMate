from fastapi import Depends, HTTPException, status

from src.travelmate.auth.deps import get_current_user
from src.travelmate.models.user import User


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
