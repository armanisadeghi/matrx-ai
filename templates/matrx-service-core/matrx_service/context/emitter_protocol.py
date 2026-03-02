from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from matrx_service.context.events import BrokerPayload, CompletionPayload, ToolEventPayload


@runtime_checkable
class Emitter(Protocol):
    """Runtime-checkable protocol defining the full emitter API surface.

    Both StreamEmitter (production) and ConsoleEmitter (dev/test) satisfy
    this protocol. Service code always depends on Emitter, never on a
    concrete implementation.

    All methods are async — every emit queues a JSON line to the stream.
    """

    async def send_chunk(self, text: str) -> None: ...

    async def send_status_update(
        self,
        status: str,
        system_message: str | None = None,
        user_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

    async def send_data(self, data: Any) -> None: ...

    async def send_completion(self, payload: CompletionPayload) -> None: ...

    async def send_error(
        self,
        error_type: str,
        message: str,
        user_message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...

    async def send_tool_event(self, event_data: ToolEventPayload) -> None: ...

    async def send_broker(self, broker: BrokerPayload) -> None: ...

    async def send_end(self, reason: str = "complete") -> None: ...

    async def send_cancelled(self) -> None: ...

    async def fatal_error(
        self,
        error_type: str,
        message: str,
        user_message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...
