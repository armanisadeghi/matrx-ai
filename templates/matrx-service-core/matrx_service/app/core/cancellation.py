"""In-memory request cancellation registry.

Long-running task loops poll is_cancelled() between iterations.
Cancellation endpoints call cancel(request_id) to set the flag.
Entries auto-expire after ttl_seconds to prevent unbounded memory growth.

Usage
-----
    registry = CancellationRegistry.get_instance()

    # In a cancellation endpoint:
    await registry.cancel(request_id)

    # In a task loop:
    for iteration in range(max_iterations):
        if registry.is_cancelled(ctx.request_id):
            await emitter.send_cancelled()
            return
        ...
"""

from __future__ import annotations

import asyncio
import time


class CancellationRegistry:
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
