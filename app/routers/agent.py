"""
Agent router.

  POST /api/ai/agents/{agent_id}        — start a new agent conversation (streaming)
  POST /api/ai/agents/{agent_id}/warm   — pre-warm / cache agent (public, no auth)
  POST /api/ai/cancel/{request_id}      — request graceful cancellation
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from matrx_utils import vcprint

from app.core.cancellation import CancellationRegistry
from app.core.response import create_streaming_response
from app.models.agent import AgentStartRequest
from context.app_context import AppContext, context_dep
from context.events import CompletionPayload
from context.stream_emitter import StreamEmitter
from prompts.agent import Agent
from prompts.session import SimpleSession
from prompts.cache import AgentCache

# Protected endpoints (require guest auth or above)
router = APIRouter(prefix="/api/ai/agents", tags=["agent"])

# Public endpoints (no auth — used for server-to-server warm calls)
public_router = APIRouter(prefix="/api/ai/agents", tags=["agent"])

# Cancel router (separate prefix)
cancel_router = APIRouter(prefix="/api/ai", tags=["agent"])


async def _run_agent_start(
    emitter: StreamEmitter,
    request: AgentStartRequest,
    agent_id: str,
    conversation_id: str,
):
    vcprint(
        f"agent={agent_id} conversation={conversation_id[:8]}...",
        "[Agent] Starting",
        color="cyan",
    )

    agent = await Agent.from_id(
        agent_id,
        variables=request.variables,
        config_overrides=request.config_overrides,
    )

    session = SimpleSession(conversation_id=conversation_id, debug=request.debug)
    agent.set_session(session)
    agent.request_metadata = {"agent_id": agent_id}

    await emitter.send_status_update(
        status="processing",
        system_message="Agent execution started",
    )

    result = await agent.execute(user_input=request.user_input)
    AgentCache.set(conversation_id, agent)

    vcprint(agent.name, "[Agent] Complete", color="green")

    await emitter.send_completion(CompletionPayload(
        status="complete",
        output=result.output,
        total_usage=result.usage.to_dict(),
        metadata=result.metadata,
    ))
    await emitter.send_end()


@router.post("/{agent_id}")
async def start_agent(
    agent_id: str,
    request: AgentStartRequest,
    ctx: AppContext = Depends(context_dep),
) -> Any:
    conversation_id = str(uuid.uuid4())
    vcprint(f"agent_id={agent_id} conversation_id={conversation_id}", "[Agent]", color="cyan")

    initial_variables = dict(request.variables or {})
    if request.user_input is not None:
        initial_variables["__agent_user_input__"] = request.user_input

    ctx.extend(
        conversation_id=conversation_id,
        debug=request.debug,
        initial_variables=initial_variables,
        initial_overrides=request.config_overrides or {},
    )
    return create_streaming_response(
        ctx,
        _run_agent_start,
        request, agent_id, conversation_id,
        initial_message="Connecting to agent...",
        debug_label="Agent",
    )


@public_router.post("/{agent_id}/warm")
async def warm_agent(agent_id: str):
    vcprint(agent_id, "[Agent Warm] Warming", color="cyan")
    try:
        agent = await Agent.from_id(agent_id)
        vcprint(f"{agent_id} ({agent.name})", "[Agent Warm] Cached", color="green")
        return {"status": "cached", "agent_id": agent_id}
    except Exception as e:
        vcprint(str(e), f"[Agent Warm] Error for {agent_id}", color="red")
        return {"status": "error", "agent_id": agent_id, "message": str(e)}


# ---------------------------------------------------------------------------
# Cancel — POST /api/ai/cancel/{request_id}
# ---------------------------------------------------------------------------


@cancel_router.post("/cancel/{request_id}")
async def cancel_request(
    request_id: str,
    ctx: AppContext = Depends(context_dep),
):
    registry = CancellationRegistry.get_instance()
    await registry.cancel(request_id)

    vcprint(
        f"request_id={request_id} user={ctx.user_id}",
        "[Cancel] Cancellation requested",
        color="yellow",
    )

    return {
        "status": "cancelled",
        "request_id": request_id,
    }
