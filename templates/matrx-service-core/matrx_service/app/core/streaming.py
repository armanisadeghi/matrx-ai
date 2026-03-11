"""
Core streaming primitives.

Two patterns are provided:
  1. SSE (Server-Sent Events) — typed event stream over HTTP GET/POST,
     supported by EventSource and most fetch clients.
  2. NDJSON — newline-delimited JSON chunks via StreamingResponse,
     useful for programmatic consumers that prefer plain JSON lines.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Any

import orjson
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------


async def sse_generator(
    source: AsyncGenerator[dict[str, Any]],
    keepalive_interval: float = 15.0,
) -> AsyncGenerator[dict[str, Any]]:
    """
    Wraps an async source and injects SSE keepalive comments so idle
    connections don't time out through proxies / load balancers.

    Each yielded dict maps directly to SSE fields:
      { "event": "...", "data": "...", "id": "...", "retry": int }
    """
    keepalive_task: asyncio.Task[None] | None = None
    queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

    async def _keepalive() -> None:
        while True:
            await asyncio.sleep(keepalive_interval)
            await queue.put({"comment": "keepalive"})

    async def _drain_source() -> None:
        try:
            async for chunk in source:
                await queue.put(chunk)
        finally:
            await queue.put(None)  # sentinel

    keepalive_task = asyncio.create_task(_keepalive())
    drain_task = asyncio.create_task(_drain_source())

    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item
    finally:
        keepalive_task.cancel()
        drain_task.cancel()
        with suppress(asyncio.CancelledError):
            await keepalive_task
        with suppress(asyncio.CancelledError):
            await drain_task


def make_sse_response(
    generator: AsyncGenerator[dict[str, Any]],
    keepalive_interval: float = 15.0,
) -> EventSourceResponse:
    return EventSourceResponse(
        sse_generator(generator, keepalive_interval=keepalive_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )


# ---------------------------------------------------------------------------
# NDJSON streaming
# ---------------------------------------------------------------------------


async def ndjson_generator(
    source: AsyncIterator[dict[str, Any]],
) -> AsyncGenerator[bytes]:
    """Serialise each dict as a JSON line terminated with \\n."""
    async for chunk in source:
        yield orjson.dumps(chunk) + b"\n"


def make_ndjson_response(
    source: AsyncIterator[dict[str, Any]],
) -> StreamingResponse:
    return StreamingResponse(
        ndjson_generator(source),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Utility: convert a regular async generator to an SSE data stream
# ---------------------------------------------------------------------------


async def text_chunks_to_sse(
    source: AsyncGenerator[str],
    event: str = "chunk",
    done_event: str = "done",
) -> AsyncGenerator[dict[str, Any]]:
    """
    Convert a raw text-chunk generator (e.g. from an LLM SDK) into
    properly structured SSE dicts.
    """
    try:
        async for text in source:
            yield {"event": event, "data": json.dumps({"text": text})}
        yield {"event": done_event, "data": json.dumps({"done": True})}
    except Exception as exc:
        logger.exception("Streaming error: %s", exc)
        yield {"event": "error", "data": json.dumps({"error": str(exc)})}


# contextlib.suppress re-export so callers don't need an extra import
from contextlib import suppress  # noqa: E402
