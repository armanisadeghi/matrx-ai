"""Browser session manager for persistent Playwright sessions across tool calls.

Sessions are keyed by session_id. Each session holds a live Playwright browser
and page. A model navigates with browser_navigate (which returns a session_id),
then uses that session_id for browser_click, browser_type_text, and
browser_screenshot to operate on the same live page.

Lifecycle:
- Sessions are created by browser_navigate and closed by browser_close.
- Idle sessions older than SESSION_TTL_SECONDS are evicted automatically by a
  background task that starts lazily when the first session is created.
- All sessions are force-closed on process shutdown via atexit.
"""
from __future__ import annotations

import asyncio
import atexit
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from matrx_utils import vcprint

SESSION_TTL_SECONDS = 300       # 5 minutes idle before auto-close
EVICTION_INTERVAL_SECONDS = 60  # check every minute


@dataclass
class BrowserSession:
    session_id: str
    pw: Any        # AsyncPlaywright instance
    browser: Any   # Browser instance
    page: Any      # Page instance
    last_used: float = field(default_factory=time.time)

    async def close(self) -> None:
        try:
            await self.browser.close()
        except Exception:
            pass
        try:
            await self.pw.stop()
        except Exception:
            pass


class BrowserSessionManager:
    """Process-global registry of live browser sessions with automatic TTL eviction."""

    def __init__(self) -> None:
        self._sessions: dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        self._eviction_task: asyncio.Task[None] | None = None

    def _ensure_eviction_task(self) -> None:
        """Start the background eviction task if not already running."""
        if self._eviction_task is None or self._eviction_task.done():
            try:
                loop = asyncio.get_running_loop()
                self._eviction_task = loop.create_task(self._eviction_loop(), name="browser-session-eviction")
            except RuntimeError:
                pass  # No running event loop yet — eviction starts on first create()

    async def _eviction_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(EVICTION_INTERVAL_SECONDS)
                await self.evict_stale()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                vcprint(f"Browser session eviction error: {exc}", "[BrowserSessions] Eviction loop error", color="red")

    async def create(self) -> BrowserSession:
        from playwright.async_api import async_playwright

        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        session_id = str(uuid.uuid4())[:8]
        session = BrowserSession(
            session_id=session_id,
            pw=pw,
            browser=browser,
            page=page,
        )
        async with self._lock:
            self._sessions[session_id] = session
        self._ensure_eviction_task()
        return session

    async def get(self, session_id: str) -> BrowserSession | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.last_used = time.time()
        return session

    async def close(self, session_id: str) -> None:
        async with self._lock:
            session = self._sessions.pop(session_id, None)
        if session:
            await session.close()

    async def close_all(self) -> None:
        async with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        if self._eviction_task and not self._eviction_task.done():
            self._eviction_task.cancel()
            try:
                await self._eviction_task
            except asyncio.CancelledError:
                pass
        for session in sessions:
            await session.close()

    async def evict_stale(self) -> None:
        cutoff = time.time() - SESSION_TTL_SECONDS
        async with self._lock:
            stale_ids = [sid for sid, s in self._sessions.items() if s.last_used < cutoff]
            stale_sessions = [self._sessions.pop(sid) for sid in stale_ids]
        for session in stale_sessions:
            await session.close()

    @property
    def active_count(self) -> int:
        return len(self._sessions)

    @property
    def session_ids(self) -> list[str]:
        return list(self._sessions.keys())


# ─── Process-level singleton ─────────────────────────────────────────────────

_manager: BrowserSessionManager | None = None


def get_browser_session_manager() -> BrowserSessionManager:
    global _manager
    if _manager is None:
        _manager = BrowserSessionManager()
    return _manager


def _shutdown_browser_sessions() -> None:
    """atexit handler — synchronously closes all sessions on process exit."""
    global _manager
    if _manager is None or _manager.active_count == 0:
        return
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_manager.close_all())
        else:
            loop.run_until_complete(_manager.close_all())
    except Exception as exc:
        vcprint(f"Error during browser session shutdown: {exc}", "[BrowserSessions] Shutdown error", color="red")


atexit.register(_shutdown_browser_sessions)
