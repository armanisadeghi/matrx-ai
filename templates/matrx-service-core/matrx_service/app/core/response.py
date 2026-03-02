"""Streaming response factory.

create_streaming_response() is the single entry point for every route that
returns an NDJSON stream. It:

  1. Sends an immediate status_update("connected") so the client knows the
     stream is live before any async work begins.
  2. Optionally sends the conversation_id as a DATA event so clients can
     track which conversation this response belongs to.
  3. Spawns the caller's task_fn as an asyncio.Task and wires it to the
     StreamEmitter queue.
  4. Catches all exceptions inside the task and turns them into structured
     error + end events (never a bare exception or silent failure).
  5. Sets X-Request-ID and X-Conversation-ID response headers.

Usage in a route handler
------------------------
    from matrx_service.app.core.response import create_streaming_response
    from matrx_service.context.app_context import context_dep, AppContext

    @router.post("/my-endpoint")
    async def my_endpoint(
        request: MyRequest,
        ctx: AppContext = Depends(context_dep),
    ):
        ctx.extend(conversation_id=request.conversation_id)
        return create_streaming_response(
            ctx,
            my_task_fn,       # async def my_task_fn(emitter, *args)
            request.payload,  # forwarded as *task_args
            initial_message="Processing...",
            debug_label="MyTask",
        )
"""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi.responses import StreamingResponse

from matrx_service.context._log import log
from matrx_service.context.app_context import AppContext
from matrx_service.context.emitter_protocol import Emitter


def create_streaming_response(
    ctx: AppContext,
    task_fn: Callable[..., Awaitable[None]],
    *task_args: Any,
    initial_message: str = "Connecting...",
    debug_label: str = "stream",
) -> StreamingResponse:
    """Wire an async task to an NDJSON StreamingResponse.

    Parameters
    ----------
    ctx             AppContext from Depends(context_dep). Call ctx.extend()
                    with any route-specific fields BEFORE calling this.
    task_fn         async def task_fn(emitter: StreamEmitter, *task_args)
    *task_args      Forwarded to task_fn after emitter.
    initial_message First user_message in the opening status_update event.
    debug_label     Prefix for error log messages.
    """
    if ctx.emitter is None:
        raise RuntimeError("AppContext.emitter must be set before create_streaming_response()")
    emitter: Emitter = ctx.emitter

    async def _stream():
        # Immediate connected event — client receives this before any async work.
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

        async def _run_with_error_handling() -> None:
            try:
                await task_fn(emitter, *task_args)
            except asyncio.CancelledError:
                print(
                    f"\n[{debug_label}] Task cancelled (client disconnected)",
                    file=sys.stderr,
                    flush=True,
                )
                log("Task cancelled (client disconnected)", title=f"[{debug_label}]", color="yellow")
            except Exception as e:
                tb = traceback.format_exc()
                print(
                    f"\n[{debug_label}] TASK CRASHED — {type(e).__name__}: {e}\n{tb}",
                    file=sys.stderr,
                    flush=True,
                )
                log(e, title=f"[{debug_label}] TASK CRASHED — {type(e).__name__}", color="red")
                await emitter.fatal_error(
                    error_type=f"{debug_label.lower()}_error",
                    message=str(e),
                    user_message=f"{debug_label} failed.",
                )

        task = asyncio.create_task(_run_with_error_handling())
        emitter.set_task(task)

        async for item in emitter.generate():
            yield item

        # Belt-and-suspenders: log any exception that escaped the handler.
        if task.done() and not task.cancelled():
            exc = task.exception()
            if exc is not None:
                tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                print(
                    f"\n[{debug_label}] TASK EXCEPTION ESCAPED HANDLER — "
                    f"{type(exc).__name__}: {exc}\n{tb}",
                    file=sys.stderr,
                    flush=True,
                )

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
