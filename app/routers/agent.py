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
from app.core.ai_task import run_ai_task
from app.models.agent import AgentStartRequest
from context.app_context import AppContext, context_dep
from conversation.conversation_resolver import AgentConfigResolver

# Protected endpoints (require guest auth or above)
router = APIRouter(prefix="/api/ai/agents", tags=["agent"])

# Public endpoints (no auth — used for server-to-server warm calls)
public_router = APIRouter(prefix="/api/ai/agents", tags=["agent"])

# Cancel router (separate prefix)
cancel_router = APIRouter(prefix="/api/ai", tags=["agent"])


@router.post("/{agent_id}")
async def start_agent(
    agent_id: str,
    request: AgentStartRequest,
    ctx: AppContext = Depends(context_dep),
) -> Any:
    """Start a new agent conversation.

    Resolves the agent's UnifiedConfig (with variables/overrides applied),
    then hands off to the AI engine. A new conversation_id is generated here
    and set on AppContext so execution and persistence use the same ID.
    """
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

    config = await AgentConfigResolver.from_id(
        agent_id,
        variables=request.variables,
        overrides=request.config_overrides,
    )

    if request.user_input is not None:
        config.append_or_extend_user_input(request.user_input)

    return create_streaming_response(
        ctx,
        run_ai_task,
        config,
        initial_message="Connecting to agent...",
        debug_label="Agent",
    )


@public_router.post("/{agent_id}/warm")
async def warm_agent(agent_id: str):
    """Pre-load an agent definition into the PromptManager cache."""
    vcprint(agent_id, "[Agent Warm] Warming", color="cyan")
    loaded = await AgentConfigResolver.warm(agent_id)
    status = "cached" if loaded else "error"
    return {"status": status, "agent_id": agent_id}


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
