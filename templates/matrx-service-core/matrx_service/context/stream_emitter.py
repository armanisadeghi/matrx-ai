from __future__ import annotations

import asyncio
import dataclasses
import datetime
import enum
import json
import uuid
from typing import Any

from matrx_utils import vcprint

from matrx_service.context.events import (
    BrokerPayload,
    ChunkPayload,
    CompletionPayload,
    EndPayload,
    ErrorPayload,
    EventType,
    HeartbeatPayload,
    StatusUpdatePayload,
    StreamEvent,
    ToolEventPayload,
    build_event,
)


class StreamEmitter:
    """Production emitter that serialises events to JSONL for FastAPI StreamingResponse.

    Uses an asyncio.Queue to buffer events and an async generator to yield them.
    Supports client disconnect detection and optional heartbeat keepalive.
    """

    def __init__(self, debug: bool = False, heartbeat_interval: float = 5.0):
        self.queue: asyncio.Queue[str | None] = asyncio.Queue()
        self.debug = debug
        self._ended = False
        self.cancelled = False
        self._task: asyncio.Task[None] | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._heartbeat_interval = heartbeat_interval

    # ------------------------------------------------------------------
    # Task / lifecycle management
    # ------------------------------------------------------------------

    def set_task(self, task: asyncio.Task[None]) -> None:
        self._task = task

    def start_heartbeat(self) -> None:
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def _stop_heartbeat(self) -> None:
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()

    async def _heartbeat_loop(self) -> None:
        try:
            while not self._ended and not self.cancelled:
                await asyncio.sleep(self._heartbeat_interval)
                if not self._ended and not self.cancelled:
                    event = build_event(EventType.HEARTBEAT, HeartbeatPayload())
                    await self.queue.put(event.to_jsonl())
        except asyncio.CancelledError:
            pass

    async def generate(self):
        self.start_heartbeat()
        try:
            while True:
                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except TimeoutError:
                    if self._task and self._task.done():
                        break
                    continue

                if item is None:
                    break
                yield item
        except (GeneratorExit, asyncio.CancelledError):
            self.cancelled = True
            if self._task and not self._task.done():
                self._task.cancel()
        finally:
            self._stop_heartbeat()

    # ------------------------------------------------------------------
    # Internal emit
    # ------------------------------------------------------------------

    def _serialize(self, data: Any) -> Any:
        if data is None or isinstance(data, (bool, int, float, str)):
            return data
        if isinstance(data, (datetime.datetime, datetime.date)):
            return data.isoformat()
        if isinstance(data, uuid.UUID):
            return str(data)
        if isinstance(data, enum.Enum):
            return data.value
        if dataclasses.is_dataclass(data) and not isinstance(data, type):
            return self._serialize(dataclasses.asdict(data))
        if isinstance(data, (set, tuple)):
            return [self._serialize(item) for item in data]
        if isinstance(data, dict):
            return {key: self._serialize(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._serialize(item) for item in data]
        if hasattr(data, "model_dump"):
            return data.model_dump()
        return str(data)

    async def _emit_event(self, event: StreamEvent) -> None:
        if self._ended or self.cancelled:
            return
        await self.queue.put(event.to_jsonl())

    async def _emit_raw(self, event_type: EventType, data: dict[str, Any]) -> None:
        if self._ended or self.cancelled:
            return
        payload = {"event": event_type.value, "data": data}
        await self.queue.put(json.dumps(payload) + "\n")

    # ------------------------------------------------------------------
    # Public API — one method per canonical event type
    # ------------------------------------------------------------------

    async def send_chunk(self, text: str) -> None:
        event = build_event(EventType.CHUNK, ChunkPayload(text=text))
        await self._emit_event(event)

    async def send_status_update(
        self,
        status: str,
        system_message: str | None = None,
        user_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        vcprint(
            {"status": status, "system_message": system_message,
             "user_message": user_message, "metadata": metadata},
            "[Stream Emitter] Status Update", color="blue",
        )
        event = build_event(
            EventType.STATUS_UPDATE,
            StatusUpdatePayload(
                status=status,
                system_message=system_message,
                user_message=user_message,
                metadata=metadata,
            ),
        )
        await self._emit_event(event)

    async def send_data(self, data: Any) -> None:
        serialized = self._serialize(data)
        if not isinstance(serialized, dict):
            serialized = {"value": serialized}
        vcprint(serialized, "[Stream Emitter] Data", color="blue")
        await self._emit_raw(EventType.DATA, serialized)

    async def send_completion(self, payload: CompletionPayload) -> None:
        color = (
            "green" if payload.status == "complete"
            else "red" if payload.status == "failed"
            else "blue"
        )
        vcprint(payload, "[Stream Emitter] Completion", color=color)
        event = build_event(EventType.COMPLETION, payload)
        await self._emit_event(event)

    async def send_error(
        self,
        error_type: str,
        message: str,
        user_message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = build_event(
            EventType.ERROR,
            ErrorPayload(
                error_type=error_type,
                message=message,
                user_message=user_message or "Sorry. An error occurred.",
                code=code,
                details=self._serialize(details) if details else None,
            ),
        )
        await self._emit_event(event)

    async def send_tool_event(self, event_data: ToolEventPayload | dict[str, Any]) -> None:
        if isinstance(event_data, dict):
            payload = ToolEventPayload.model_validate(event_data)
        else:
            payload = event_data
        color = (
            "red" if payload.event == "tool_error"
            else "green" if payload.event == "tool_completed"
            else "blue"
        )
        vcprint(payload, "[Stream Emitter] Tool Event", color=color)
        event = build_event(EventType.TOOL_EVENT, payload)
        await self._emit_event(event)

    async def send_broker(self, broker: BrokerPayload) -> None:
        vcprint(broker, "[Stream Emitter] Broker", color="blue")
        event = build_event(EventType.BROKER, broker)
        await self._emit_event(event)

    async def send_end(self, reason: str = "complete") -> None:
        if not self._ended:
            color = "green" if reason == "complete" else "blue"
            vcprint({"reason": reason}, "[Stream Emitter] End", color=color)
            event = build_event(EventType.END, EndPayload(reason=reason))
            await self._emit_event(event)
            await self.queue.put(None)
            self._ended = True
            self._stop_heartbeat()

    async def send_cancelled(self) -> None:
        await self.send_error(
            error_type="task_cancelled",
            message="Task was cancelled.",
            user_message="Your request was cancelled.",
        )
        await self.send_end(reason="cancelled")

    async def fatal_error(
        self,
        error_type: str,
        message: str,
        user_message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.send_error(error_type, message, user_message, code, details)
        await self.send_end()
