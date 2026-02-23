"""
Agent router.

  POST /api/ai/agents/{agent_id}        — start a new agent conversation (streaming)
  POST /api/ai/agents/{agent_id}/warm   — pre-warm / cache agent (no body, fire-and-forget)
  GET  /api/ai/agents/{agent_id}        — fetch agent status / metadata
  POST /api/ai/cancel/{request_id}      — request graceful cancellation

The `agent_id` path parameter is dynamic and opaque; your ORM layer will
resolve it to a concrete agent implementation.
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Path
from fastapi.responses import ORJSONResponse

from app.core.exceptions import AgentNotFoundError
from app.core.streaming import make_ndjson_response, make_sse_response
from app.models.agent import AgentEvent, AgentInfo, AgentRunRequest, AgentStatus, StreamMode

router = APIRouter(prefix="/api/ai/agents", tags=["agent"])


@router.post("/{agent_id}")
async def start_agent(
    agent_id: str = Path(..., description="Unique agent identifier"),
    body: AgentRunRequest = ...,
) -> Any:
    """Start a new agent conversation. The server generates the conversation_id."""
    _assert_agent_exists(agent_id)

    stream = _mock_agent_stream(agent_id, body)

    if body.stream_mode == StreamMode.sse:

        async def _to_sse() -> AsyncGenerator[dict[str, Any]]:
            async for event in stream:
                yield {
                    "event": event.event,
                    "data": json.dumps(event.model_dump()),
                }

        return make_sse_response(_to_sse())

    async def _to_ndjson() -> AsyncGenerator[dict[str, Any]]:
        async for event in stream:
            yield event.model_dump()

    return make_ndjson_response(_to_ndjson())


@router.post("/{agent_id}/warm")
async def warm_agent(
    agent_id: str = Path(..., description="Unique agent identifier"),
) -> ORJSONResponse:
    """Pre-warm / cache the agent so the first real request is faster."""
    # TODO: wire real cache-warming logic here
    return ORJSONResponse({"status": "ok", "agent_id": agent_id})


@router.get("/{agent_id}", response_class=ORJSONResponse)
async def get_agent(
    agent_id: str = Path(..., description="Unique agent identifier"),
) -> AgentInfo:
    _assert_agent_exists(agent_id)
    return AgentInfo(
        agent_id=agent_id,
        status=AgentStatus.idle,
        created_at=datetime.now(UTC).isoformat(),
    )


# ---------------------------------------------------------------------------
# Cancel — POST /api/ai/cancel/{request_id}
# ---------------------------------------------------------------------------

cancel_router = APIRouter(prefix="/api/ai", tags=["agent"])


@cancel_router.post("/cancel/{request_id}", response_class=ORJSONResponse)
async def cancel_request(
    request_id: str = Path(..., description="Request ID to cancel"),
) -> ORJSONResponse:
    """Request graceful cancellation of a running agent/conversation request."""
    # TODO: wire real cancellation logic here
    return ORJSONResponse({"request_id": request_id, "status": "cancel_requested"})


# ---------------------------------------------------------------------------
# Stand-in implementations — replace with your real agent orchestration
# ---------------------------------------------------------------------------

_KNOWN_AGENTS: set[str] = {"*"}  # "*" = accept any ID; restrict when real registry is wired


def _assert_agent_exists(agent_id: str) -> None:
    if "*" not in _KNOWN_AGENTS and agent_id not in _KNOWN_AGENTS:
        raise AgentNotFoundError(agent_id)


async def _mock_agent_stream(
    agent_id: str,
    body: AgentRunRequest,
) -> AsyncGenerator[AgentEvent]:
    """
    Placeholder multi-step agent loop.
    Replace with your real orchestration engine.
    """
    steps = [
        ("thinking", {"thought": "Analysing the request…"}),
        ("tool_call", {"tool": "search", "args": {"q": "placeholder"}}),
        ("chunk", {"text": "Here is a response for agent "}),
        ("chunk", {"text": agent_id}),
        ("done", {"message": "Agent run complete"}),
    ]
    for step_idx, (event_name, data) in enumerate(steps):
        await asyncio.sleep(0.1)
        yield AgentEvent(event=event_name, agent_id=agent_id, data=data, step=step_idx)
