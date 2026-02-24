from __future__ import annotations

import asyncio
import json
from typing import Any, Awaitable, Callable

from fastapi.responses import StreamingResponse

from matrx_utils import vcprint

from context.app_context import AppContext
from context.stream_emitter import StreamEmitter


def create_streaming_response(
    ctx: AppContext,
    task_fn: Callable[..., Awaitable[None]],
    *task_args: Any,
    initial_message: str = "Connecting...",
    debug_label: str = "stream",
) -> StreamingResponse:
    """Wire a streaming task to an NDJSON response.

    Context is already fully set by AuthMiddleware (both request.state and
    the ContextVar). Callers must call ctx.extend() with any route-specific
    fields (conversation_id, debug, etc.) BEFORE calling this function.

    Parameters
    ----------
    ctx             AppContext from context_dep — already live in the ContextVar.
    task_fn         async def _run_something(emitter: StreamEmitter, *task_args)
    *task_args      Forwarded to task_fn after emitter.
    initial_message First status_update event sent to the client.
    debug_label     Used in error log messages.
    """
    emitter: StreamEmitter = ctx.emitter

    async def _stream():
        yield json.dumps({
            "event": "status_update",
            "data": {
                "status": "connected",
                "system_message": "Stream established",
                "user_message": initial_message,
            },
        }) + "\n"

        if ctx.conversation_id:
            yield json.dumps({
                "event": "data",
                "data": {
                    "event": "conversation_id",
                    "conversation_id": ctx.conversation_id,
                },
            }) + "\n"

        async def _run_with_error_handling():
            try:
                await task_fn(emitter, *task_args)
            except asyncio.CancelledError:
                vcprint(f"Task cancelled (client disconnected)", f"[{debug_label}]", color="yellow")
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                vcprint(str(e), f"[{debug_label}] Task error", color="red")
                print(tb_str)
                await emitter.fatal_error(
                    error_type=f"{debug_label.lower()}_error",
                    message=str(e),
                    user_message=f"{debug_label} failed.",
                )

        task = asyncio.create_task(_run_with_error_handling())
        emitter.set_task(task)

        async for item in emitter.generate():
            yield item

    headers: dict[str, str] = {}
    if ctx.request_id:
        headers["X-Request-ID"] = ctx.request_id
    if ctx.conversation_id:
        headers["X-Conversation-ID"] = ctx.conversation_id

    return StreamingResponse(
        _stream(),
        media_type="application/x-ndjson",
        headers=headers,
    )
