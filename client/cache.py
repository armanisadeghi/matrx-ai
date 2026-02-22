"""
Centralized TTL + LRU cache for AI objects (agents, conversations, configs).

Usage:
    from client.cache import TTLCache

    # Create a cache with 30-minute TTL and max 200 entries
    cache: TTLCache[MyType] = TTLCache(ttl_seconds=1800, max_size=200)
    cache.set("key", value)
    result = cache.get("key")  # None if expired or evicted
"""

import time
from collections import OrderedDict
from typing import Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Generic TTL + LRU cache.

    - Items expire after `ttl_seconds` of inactivity (last access, not creation).
    - When `max_size` is reached, the least-recently-used item is evicted.
    - `get()` refreshes the TTL (marks the item as recently used).
    - Thread-safe for single-threaded async (no locks needed with asyncio).
    """

    def __init__(self, ttl_seconds: int = 1800, max_size: int = 200):
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: OrderedDict[str, T] = OrderedDict()
        self._timestamps: Dict[str, float] = {}

    def get(self, key: str) -> Optional[T]:
        if key not in self._store:
            return None

        # Check expiry
        if self._is_expired(key):
            self._remove(key)
            return None

        # Refresh: move to end (most recently used) and update timestamp
        self._store.move_to_end(key)
        self._timestamps[key] = time.monotonic()
        return self._store[key]

    def set(self, key: str, value: T) -> None:
        # If key already exists, update in place
        if key in self._store:
            self._store.move_to_end(key)
            self._store[key] = value
            self._timestamps[key] = time.monotonic()
            return

        # Evict expired entries first (lazy cleanup)
        self._evict_expired()

        # If still at capacity, evict LRU (oldest)
        while len(self._store) >= self._max_size:
            oldest_key, _ = self._store.popitem(last=False)
            self._timestamps.pop(oldest_key, None)

        self._store[key] = value
        self._timestamps[key] = time.monotonic()

    def remove(self, key: str) -> None:
        self._remove(key)

    def exists(self, key: str) -> bool:
        if key not in self._store:
            return False
        if self._is_expired(key):
            self._remove(key)
            return False
        return True

    def clear(self) -> None:
        self._store.clear()
        self._timestamps.clear()

    @property
    def size(self) -> int:
        return len(self._store)

    def _is_expired(self, key: str) -> bool:
        ts = self._timestamps.get(key, 0)
        return (time.monotonic() - ts) > self._ttl

    def _remove(self, key: str) -> None:
        self._store.pop(key, None)
        self._timestamps.pop(key, None)

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, ts in self._timestamps.items() if (now - ts) > self._ttl]
        for k in expired:
            self._remove(k)
