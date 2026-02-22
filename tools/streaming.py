from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field

from context.emitter_protocol import Emitter

if TYPE_CHECKING:
    from tools.models import ToolResult


class ToolStreamEvent(BaseModel):
    """Flat, structured event sent to the frontend during tool execution.

    This exact shape is what the client receives — no information loss,
    no type-inference logic, no extra nesting layers.

    STREAMING CONTRACT (non-negotiable):
      - ``tool_started`` MUST include the full tool arguments in ``data.arguments``
      - ``tool_completed`` MUST include the full tool result in ``data.result``
      - These are sent by the executor ONLY — individual tools MUST NOT
        call ``started()`` or ``completed()`` themselves.
      - Individual tools may only call ``progress()`` and ``step()`` for
        intermediate UI updates during long-running operations.
    """
    event: Literal[
        "tool_started",
        "tool_progress",
        "tool_step",
        "tool_result_preview",
        "tool_completed",
        "tool_error",
    ]
    call_id: str
    tool_name: str
    timestamp: float = Field(default_factory=time.time)
    message: str | None = None
    show_spinner: bool = True
    data: dict[str, Any] = Field(default_factory=dict)


class ToolStreamManager:
    """Manages streaming updates during a single tool execution.

    Dual-writes every event to:
      1. The client via ``send_tool_event()`` (real-time, flat payload)
      2. An in-memory buffer for DB persistence in cx_tool_call.execution_events

    STREAMING CONTRACT — enforced here, called from executor.py only:
      - ``started()``   → streams tool name + full arguments to the UI
      - ``completed()`` → streams full result output to the UI
      - ``error()``     → streams error details to the UI

    Individual tool implementations MUST NOT call started/completed/error.
    They may only call progress() and step() for intermediate updates.
    """

    def __init__(self, emitter: Emitter | None, call_id: str, tool_name: str):
        self.emitter = emitter
        self.call_id = call_id
        self.tool_name = tool_name
        self._events: list[ToolStreamEvent] = []

    async def emit(self, event: ToolStreamEvent) -> None:
        self._events.append(event)
        if self.emitter is not None:
            try:
                await self.emitter.send_tool_event(event.model_dump())
            except Exception:
                pass

    # ------------------------------------------------------------------
    # EXECUTOR-ONLY: started / completed / error
    # These carry the full payloads the frontend needs to render tools.
    # Individual tools MUST NOT call these — the executor does.
    # ------------------------------------------------------------------

    async def started(
        self,
        message: str = "Starting...",
        arguments: dict[str, Any] | None = None,
    ) -> None:
        await self.emit(ToolStreamEvent(
            event="tool_started",
            call_id=self.call_id,
            tool_name=self.tool_name,
            message=message,
            data={"arguments": arguments} if arguments else {},
        ))

    async def completed(
        self,
        message: str = "Done",
        result: ToolResult | None = None,
    ) -> None:
        data: dict[str, Any] = {}
        if result is not None:
            output = result.output
            if isinstance(output, dict):
                data["result"] = output
            elif isinstance(output, str):
                try:
                    data["result"] = json.loads(output)
                except (json.JSONDecodeError, TypeError):
                    data["result"] = output
            elif output is not None:
                data["result"] = output

        await self.emit(ToolStreamEvent(
            event="tool_completed",
            call_id=self.call_id,
            tool_name=self.tool_name,
            message=message,
            show_spinner=False,
            data=data,
        ))

    async def error(self, message: str, error_type: str = "execution") -> None:
        
        await self.emit(ToolStreamEvent(
            event="tool_error",
            call_id=self.call_id,
            tool_name=self.tool_name,
            message=message,
            show_spinner=False,
            data={"error_type": error_type},
        ))

    # ------------------------------------------------------------------
    # TOOL-CALLABLE: progress / step / result_preview
    # These are the ONLY methods individual tool implementations may call.
    # ------------------------------------------------------------------

    async def progress(self, message: str, data: dict[str, Any] | None = None) -> None:
        await self.emit(ToolStreamEvent(
            event="tool_progress",
            call_id=self.call_id,
            tool_name=self.tool_name,
            message=message,
            data=data or {},
        ))

    async def step(self, step_name: str, message: str, data: dict[str, Any] | None = None) -> None:
        await self.emit(ToolStreamEvent(
            event="tool_step",
            call_id=self.call_id,
            tool_name=self.tool_name,
            message=message,
            data={"step": step_name, **(data or {})},
        ))

    async def result_preview(self, preview: str) -> None:
        await self.emit(ToolStreamEvent(
            event="tool_result_preview",
            call_id=self.call_id,
            tool_name=self.tool_name,
            message="Preview available",
            data={"preview": preview[:500]},
        ))

    # ------------------------------------------------------------------

    def get_events_for_persistence(self) -> list[dict[str, Any]]:
        return [e.model_dump() for e in self._events]
