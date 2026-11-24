import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("ws")


class ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._connections.append(ws)
        logger.info("WS client connected (%d total)", len(self._connections))

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            if ws in self._connections:
                self._connections.remove(ws)
        logger.info("WS client disconnected (%d total)", len(self._connections))

    async def broadcast(self, data: dict[str, Any]):
        message = json.dumps(data, default=str)
        async with self._lock:
            stale: list[WebSocket] = []
            for ws in self._connections:
                try:
                    await ws.send_text(message)
                except Exception:
                    stale.append(ws)
            for ws in stale:
                self._connections.remove(ws)


ws_manager = ConnectionManager()
