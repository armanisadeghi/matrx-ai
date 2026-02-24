from __future__ import annotations

import asyncio
import time


class CancellationRegistry:
    """In-memory registry for request cancellation.

    Endpoints set a cancellation flag via ``cancel(request_id)``.
    Long-running loops (e.g. ``execute_until_complete``) poll via
    ``is_cancelled(request_id)`` between iterations.

    Entries auto-expire after ``ttl_seconds`` to prevent memory leaks.
    """

    _instance: CancellationRegistry | None = None

    def __init__(self, ttl_seconds: float = 60.0):
        self._cancelled: dict[str, float] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> CancellationRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def cancel(self, request_id: str) -> None:
        async with self._lock:
            self._cancelled[request_id] = time.time()

    def is_cancelled(self, request_id: str) -> bool:
        ts = self._cancelled.get(request_id)
        if ts is None:
            return False
        if time.time() - ts > self._ttl:
            self._cancelled.pop(request_id, None)
            return False
        return True

    async def cleanup_expired(self) -> int:
        now = time.time()
        async with self._lock:
            expired = [k for k, v in self._cancelled.items() if now - v > self._ttl]
            for k in expired:
                del self._cancelled[k]
            return len(expired)
