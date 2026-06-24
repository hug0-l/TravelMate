"""WebSocket manager for real-time trip collaboration."""

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections grouped by trip_id."""

    def __init__(self) -> None:
        # trip_id -> list of (websocket, user_id, user_name)
        self._rooms: dict[str, list[tuple[WebSocket, str, str]]] = {}

    async def connect(self, trip_id: str, ws: WebSocket, user_id: str, user_name: str) -> None:
        await ws.accept()
        if trip_id not in self._rooms:
            self._rooms[trip_id] = []
        self._rooms[trip_id].append((ws, user_id, user_name))
        await self._broadcast_presence(trip_id)

    def disconnect(self, trip_id: str, ws: WebSocket) -> None:
        if trip_id in self._rooms:
            self._rooms[trip_id] = [(w, uid, un) for w, uid, un in self._rooms[trip_id] if w != ws]
            if not self._rooms[trip_id]:
                del self._rooms[trip_id]

    async def broadcast(self, trip_id: str, message: dict[str, Any], exclude: WebSocket | None = None) -> None:
        if trip_id not in self._rooms:
            return
        payload = json.dumps(message)
        for ws, _uid, _un in self._rooms[trip_id]:
            if ws != exclude:
                try:
                    await ws.send_text(payload)
                except Exception:
                    pass

    def get_presence(self, trip_id: str) -> list[dict[str, str]]:
        if trip_id not in self._rooms:
            return []
        seen: set[str] = set()
        result: list[dict[str, str]] = []
        for _ws, uid, un in self._rooms[trip_id]:
            if uid not in seen:
                seen.add(uid)
                result.append({"user_id": uid, "user_name": un})
        return result

    async def _broadcast_presence(self, trip_id: str) -> None:
        presence = self.get_presence(trip_id)
        await self.broadcast(trip_id, {"type": "presence", "users": presence})


manager = ConnectionManager()
