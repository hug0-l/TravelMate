from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.travelmate.config import settings


def create_guest_token(trip_id: str, nickname: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"trip_id": trip_id, "nickname": nickname, "exp": expire, "type": "guest"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_guest_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
