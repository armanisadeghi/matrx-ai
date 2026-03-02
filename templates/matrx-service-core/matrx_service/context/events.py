"""Streaming event contract — identical across all Matrx services.

All services emit and consume this exact set of event types. Never add
service-specific event types here; extend by adding fields to existing
payloads or by using the `metadata` / `data` dict fields.
"""

from __future__ import annotations

import time
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Event type registry
# ---------------------------------------------------------------------------


class EventType(StrEnum):
    CHUNK = "chunk"
    STATUS_UPDATE = "status_update"
    DATA = "data"
    COMPLETION = "completion"
    ERROR = "error"
    TOOL_EVENT = "tool_event"
    BROKER = "broker"
    HEARTBEAT = "heartbeat"
    END = "end"


VALID_EVENT_TYPES: frozenset[str] = frozenset(e.value for e in EventType)


# ---------------------------------------------------------------------------
# Payload models — one per EventType, validated on emit
# ---------------------------------------------------------------------------


class ChunkPayload(BaseModel):
    """Streaming text chunk — emitted as the LLM generates tokens."""

    model_config = {"extra": "forbid"}
    text: str


class StatusUpdatePayload(BaseModel):
    """Human-readable status update. system_message is for logs; user_message for UI."""

    model_config = {"extra": "forbid"}
    status: str
    system_message: str | None = None
    user_message: str | None = None
    metadata: dict[str, Any] | None = None


class DataPayload(BaseModel):
    """Arbitrary structured data payload. Extra fields allowed — use for service-specific data."""

    model_config = {"extra": "allow"}


class CompletionPayload(BaseModel):
    """Final completion event. Sent once per request, immediately before END."""

    model_config = {"extra": "forbid"}
    status: Literal["complete", "failed", "max_iterations_exceeded"] = "complete"
    output: Any = None
    iterations: int | None = None
    total_usage: dict[str, Any] | None = None
    timing_stats: dict[str, Any] | None = None
    tool_call_stats: dict[str, Any] | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] | None = None


class ErrorPayload(BaseModel):
    """Structured error. user_message is safe to display to end users."""

    model_config = {"extra": "forbid"}
    error_type: str
    message: str
    user_message: str = "Sorry. An error occurred."
    code: str | None = None
    details: dict[str, Any] | None = None


ToolEventType = Literal[
    "tool_started",
    "tool_progress",
    "tool_step",
    "tool_result_preview",
    "tool_completed",
    "tool_error",
]


class ToolEventPayload(BaseModel):
    """Tool lifecycle event. Emitted by the tool executor during tool calls."""

    model_config = {"extra": "forbid"}
    event: ToolEventType
    call_id: str
    tool_name: str
    timestamp: float = Field(default_factory=time.time)
    message: str | None = None
    show_spinner: bool = True
    data: dict[str, Any] = Field(default_factory=dict)


class BrokerPayload(BaseModel):
    """Cross-service value delivery. broker_id identifies the subscriber."""

    model_config = {"extra": "forbid"}
    broker_id: str
    value: Any
    source: str | None = None
    source_id: str | None = None


class HeartbeatPayload(BaseModel):
    """Keepalive ping sent on idle connections to prevent proxy timeouts."""

    model_config = {"extra": "forbid"}
    timestamp: float = Field(default_factory=time.time)


class EndPayload(BaseModel):
    """Stream termination signal. Always the last event in a stream."""

    model_config = {"extra": "forbid"}
    reason: str = "complete"


# ---------------------------------------------------------------------------
# Registry — maps EventType → expected payload class
# ---------------------------------------------------------------------------

PAYLOAD_REGISTRY: dict[EventType, type[BaseModel]] = {
    EventType.CHUNK: ChunkPayload,
    EventType.STATUS_UPDATE: StatusUpdatePayload,
    EventType.DATA: DataPayload,
    EventType.COMPLETION: CompletionPayload,
    EventType.ERROR: ErrorPayload,
    EventType.TOOL_EVENT: ToolEventPayload,
    EventType.BROKER: BrokerPayload,
    EventType.HEARTBEAT: HeartbeatPayload,
    EventType.END: EndPayload,
}


# ---------------------------------------------------------------------------
# StreamEvent — the wire format
# ---------------------------------------------------------------------------


class StreamEvent(BaseModel):
    model_config = {"extra": "forbid"}
    event: EventType
    data: dict[str, Any]

    def to_jsonl(self) -> str:
        return self.model_dump_json() + "\n"


# ---------------------------------------------------------------------------
# Builder + validator
# ---------------------------------------------------------------------------


class InvalidEventError(Exception):
    pass


def build_event(event_type: EventType, payload: BaseModel) -> StreamEvent:
    """Construct a StreamEvent, validating that payload matches the event type."""
    expected_cls = PAYLOAD_REGISTRY.get(event_type)
    if expected_cls is None:
        raise InvalidEventError(
            f"[EMITTER ERROR] Unknown event type: '{event_type}'. "
            f"Valid types: {', '.join(VALID_EVENT_TYPES)}"
        )

    if not isinstance(payload, expected_cls):
        raise InvalidEventError(
            f"[EMITTER ERROR] Event '{event_type}' expects payload type "
            f"'{expected_cls.__name__}', got '{type(payload).__name__}'"
        )

    return StreamEvent(event=event_type, data=payload.model_dump())


def validate_event_dict(event_name: str, data: dict[str, Any]) -> StreamEvent:
    """Parse and validate a raw event dict (e.g. from an inbound stream)."""
    if event_name not in VALID_EVENT_TYPES:
        raise InvalidEventError(
            f"[EMITTER ERROR] Unsupported event type: '{event_name}'. "
            f"Valid types: {', '.join(sorted(VALID_EVENT_TYPES))}"
        )

    event_type = EventType(event_name)
    payload_cls = PAYLOAD_REGISTRY[event_type]

    try:
        payload_cls.model_validate(data)
    except Exception as e:
        raise InvalidEventError(
            f"[EMITTER ERROR] Invalid payload for event '{event_name}': {e}"
        ) from e

    return StreamEvent(event=event_type, data=data)
