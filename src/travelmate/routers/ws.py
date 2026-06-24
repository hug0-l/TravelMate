"""WebSocket route for real-time trip collaboration."""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from src.travelmate.auth.jwt import decode_access_token
from src.travelmate.database import async_session
from src.travelmate.models.trip import Trip, TripMember
from src.travelmate.models.user import User
from src.travelmate.ws import manager

router = APIRouter()


@router.websocket("/ws/trip/{trip_id}")
async def trip_websocket(ws: WebSocket, trip_id: str):
    """WebSocket endpoint with auth via first message.

    Connect, then send: {"type": "auth", "token": "<jwt>"}
    """
    await ws.accept()

    # Wait for auth message (first message must be auth)
    try:
        raw = await ws.receive_text()
        auth_msg = json.loads(raw)
    except (json.JSONDecodeError, WebSocketDisconnect):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = auth_msg.get("token", "") if isinstance(auth_msg, dict) else ""
    payload = decode_access_token(token)
    if payload is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = payload.get("sub")
    if user_id is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Verify trip membership
    async with async_session() as db:
        result = await db.execute(
            select(Trip).join(TripMember).where(
                Trip.id == trip_id,
                TripMember.user_id == user_id,
            )
        )
        trip = result.scalar_one_or_none()
        if not trip:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        user_name = user.name if user else "Unknown"

    await manager.connect(trip_id, ws, user_id, user_name)
    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                msg["sender_id"] = user_id
                msg["sender_name"] = user_name
                await manager.broadcast(trip_id, msg, exclude=ws)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(trip_id, ws)
