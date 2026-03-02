"""Tests for the event system — build_event, validate_event_dict, StreamEvent."""

from __future__ import annotations

import pytest

from matrx_service.context.events import (
    BrokerPayload,
    ChunkPayload,
    CompletionPayload,
    EndPayload,
    ErrorPayload,
    EventType,
    HeartbeatPayload,
    InvalidEventError,
    StatusUpdatePayload,
    StreamEvent,
    ToolEventPayload,
    build_event,
    validate_event_dict,
)


def test_build_chunk_event() -> None:
    event = build_event(EventType.CHUNK, ChunkPayload(text="hello"))
    assert event.event == EventType.CHUNK
    assert event.data == {"text": "hello"}


def test_build_status_update_event() -> None:
    event = build_event(
        EventType.STATUS_UPDATE,
        StatusUpdatePayload(status="processing", system_message="Running"),
    )
    assert event.event == EventType.STATUS_UPDATE
    assert event.data["status"] == "processing"


def test_build_completion_event() -> None:
    payload = CompletionPayload(status="complete", output="result", iterations=3)
    event = build_event(EventType.COMPLETION, payload)
    assert event.event == EventType.COMPLETION
    assert event.data["status"] == "complete"
    assert event.data["iterations"] == 3


def test_build_error_event() -> None:
    payload = ErrorPayload(error_type="test_error", message="Something failed")
    event = build_event(EventType.ERROR, payload)
    assert event.event == EventType.ERROR
    assert event.data["error_type"] == "test_error"
    assert event.data["user_message"] == "Sorry. An error occurred."


def test_build_end_event() -> None:
    event = build_event(EventType.END, EndPayload(reason="complete"))
    assert event.data["reason"] == "complete"


def test_build_heartbeat_event() -> None:
    event = build_event(EventType.HEARTBEAT, HeartbeatPayload())
    assert "timestamp" in event.data


def test_build_broker_event() -> None:
    payload = BrokerPayload(broker_id="b1", value={"key": "val"}, source="service-a")
    event = build_event(EventType.BROKER, payload)
    assert event.data["broker_id"] == "b1"


def test_build_tool_event() -> None:
    payload = ToolEventPayload(
        event="tool_started",
        call_id="call-1",
        tool_name="web_search",
        message="Searching...",
    )
    event = build_event(EventType.TOOL_EVENT, payload)
    assert event.data["tool_name"] == "web_search"
    assert event.data["event"] == "tool_started"


def test_build_event_wrong_payload_type_raises() -> None:
    with pytest.raises(InvalidEventError, match="expects payload type"):
        build_event(EventType.CHUNK, EndPayload())


def test_stream_event_to_jsonl() -> None:
    event = build_event(EventType.CHUNK, ChunkPayload(text="hello"))
    jsonl = event.to_jsonl()
    assert jsonl.endswith("\n")
    import json
    parsed = json.loads(jsonl)
    assert parsed["event"] == "chunk"
    assert parsed["data"]["text"] == "hello"


def test_validate_event_dict_valid() -> None:
    event = validate_event_dict("chunk", {"text": "world"})
    assert event.event == EventType.CHUNK


def test_validate_event_dict_invalid_type_raises() -> None:
    with pytest.raises(InvalidEventError, match="Unsupported event type"):
        validate_event_dict("nonexistent_event", {})


def test_validate_event_dict_invalid_payload_raises() -> None:
    with pytest.raises(InvalidEventError, match="Invalid payload"):
        validate_event_dict("chunk", {"wrong_field": "value"})


def test_all_event_types_have_registry_entries() -> None:
    from matrx_service.context.events import PAYLOAD_REGISTRY
    for event_type in EventType:
        assert event_type in PAYLOAD_REGISTRY, f"Missing registry entry for {event_type}"
