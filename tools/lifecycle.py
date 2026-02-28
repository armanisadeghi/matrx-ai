from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from matrx_utils import vcprint

CleanupFn = Callable[[], Coroutine[Any, Any, None]]


class ToolLifecycleManager:
    """Manages resource cleanup for tool executions.

    Tools register cleanup callbacks that run when:
      - A conversation ends (explicit or idle timeout)
      - The periodic cleanup sweep runs
      - The server shuts down gracefully
    """

    _instance: ToolLifecycleManager | None = None

    def __init__(self) -> None:
        self._cleanup_fns: dict[str, list[CleanupFn]] = defaultdict(list)
        self._last_activity: dict[str, float] = {}
        self._idle_timeout_seconds: float = 1800  # 30 minutes
        self._sweep_interval_seconds: float = 300  # 5 minutes
        self._sweep_task: asyncio.Task[None] | None = None

    @classmethod
    def get_instance(cls) -> ToolLifecycleManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_cleanup(self, conversation_id: str, cleanup_fn: CleanupFn) -> None:
        self._cleanup_fns[conversation_id].append(cleanup_fn)
        self._last_activity[conversation_id] = time.time()

    def touch(self, conversation_id: str) -> None:
        self._last_activity[conversation_id] = time.time()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def cleanup_conversation(self, conversation_id: str) -> int:
        fns = self._cleanup_fns.pop(conversation_id, [])
        self._last_activity.pop(conversation_id, None)
        errors = 0
        for fn in fns:
            try:
                await fn()
            except Exception as exc:
                vcprint(f"Cleanup error for conversation '{conversation_id}': {exc}", "[ToolLifecycle] Cleanup callback failed", color="red")
                errors += 1
        return len(fns) - errors

    async def cleanup_idle(self) -> list[str]:
        now = time.time()
        idle_conversations: list[str] = []

        for conv_id, last in list(self._last_activity.items()):
            if now - last > self._idle_timeout_seconds:
                idle_conversations.append(conv_id)

        for conv_id in idle_conversations:
            await self.cleanup_conversation(conv_id)
            vcprint(f"Cleaned up idle conversation '{conv_id}'", "[ToolLifecycle] Idle cleanup", color="cyan")

        return idle_conversations

    async def cleanup_all(self) -> int:
        all_convs = list(self._cleanup_fns.keys())
        total = 0
        for conv_id in all_convs:
            total += await self.cleanup_conversation(conv_id)
        return total

    # ------------------------------------------------------------------
    # Background sweep
    # ------------------------------------------------------------------

    @property
    def sweep_running(self) -> bool:
        return self._sweep_task is not None and not self._sweep_task.done()

    def start_background_sweep(self) -> None:
        if self._sweep_task is None or self._sweep_task.done():
            self._sweep_task = asyncio.create_task(self._sweep_loop())

    def stop_background_sweep(self) -> None:
        if self._sweep_task and not self._sweep_task.done():
            self._sweep_task.cancel()

    async def _sweep_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._sweep_interval_seconds)
                cleaned = await self.cleanup_idle()
                if cleaned:
                    vcprint(f"Sweep cleaned {len(cleaned)} idle conversations", "[ToolLifecycle] Sweep", color="cyan")
            except asyncio.CancelledError:
                break
            except Exception as exc:
                vcprint(f"Sweep error: {exc}", "[ToolLifecycle] Sweep error", color="red")

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    @property
    def active_conversations(self) -> int:
        return len(self._cleanup_fns)

    @property
    def pending_cleanups(self) -> int:
        return sum(len(fns) for fns in self._cleanup_fns.values())
