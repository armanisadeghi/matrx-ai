"""
Conversation router.

  POST /api/ai/conversations/{conversation_id}       — continue an existing conversation
  POST /api/ai/conversations/{conversation_id}/warm   — pre-warm conversation cache (public)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from matrx_utils import vcprint

from app.core.response import create_streaming_response
from app.models.conversation import ConversationContinueRequest
from context.app_context import AppContext, context_dep
from context.events import CompletionPayload
from context.stream_emitter import StreamEmitter
from prompts.agent import Agent
from prompts.cache import AgentCache
from prompts.session import SimpleSession
from config.unified_config import UnifiedConfig
from conversation.rebuild import rebuild_conversation_messages
from conversation import cx_conversation_manager

# Protected endpoints (require guest auth or above)
router = APIRouter(prefix="/api/ai/conversations", tags=["conversation"])

# Public endpoints (no auth — server-to-server warm calls from Next.js)
public_router = APIRouter(prefix="/api/ai/conversations", tags=["conversation"])




# THIS THING IS COMPLETELY AND ABSOLUTELY WRONG!!!!!!!!!!!!!  IT'S COMPLETELY BYPASSING OUR FULL CONFIG SYSETM TO REBUILD MESSAGES LIKE IT'S OPENAI IN 2022 WITH ROLE AND CONTENT! EVERYTHING ELSE IS BEING SILENTLY LOST!
async def _reconstruct_from_db(conversation_id: str) -> Agent:
    conversation = await cx_conversation_manager.load_and_get_config(
        id=conversation_id,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found.",
        )

    messages = await rebuild_conversation_messages(conversation_id)

    config_dict: dict[str, Any] = dict(conversation["config"])
    
    config_dict["messages"] = [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in messages
    ]

    unified_config = UnifiedConfig.from_dict(config_dict)
    return Agent(config=unified_config, session=SimpleSession(conversation_id=conversation_id))


async def _run_conversation_continue(
    emitter: StreamEmitter,
    request: ConversationContinueRequest,
    conversation_id: str,
):
    agent = AgentCache.get(conversation_id)

    if agent is None:
        vcprint(
            f"{conversation_id[:8]}...",
            "[Conversation] Cache miss — rebuilding from DB",
            color="yellow",
        )
        await emitter.send_status_update(
            status="processing",
            system_message="Restoring conversation from database",
        )
        agent = await _reconstruct_from_db(conversation_id)
    else:
        vcprint(f"{conversation_id[:8]}...", "[Conversation] Cache hit", color="green")

    if request.config_overrides:
        agent.apply_config_overrides(**request.config_overrides)

    await emitter.send_status_update(status="processing", system_message="Executing")

    result = await agent.execute(user_input=request.user_input)
    AgentCache.set(conversation_id, agent)

    vcprint(f"{conversation_id[:8]}...", "[Conversation] Complete", color="green")

    await emitter.send_completion(CompletionPayload(
        status="complete",
        output=result.output,
        total_usage=result.usage.to_dict(),
        metadata=result.metadata,
    ))
    await emitter.send_end()


@router.post("/{conversation_id}")
async def continue_conversation(
    conversation_id: str,
    request: ConversationContinueRequest,
    ctx: AppContext = Depends(context_dep),
) -> Any:
    vcprint(conversation_id, "[Conversation] Continue", color="cyan")
    ctx.extend(conversation_id=conversation_id, debug=request.debug)
    return create_streaming_response(
        ctx,
        _run_conversation_continue,
        request, conversation_id,
        initial_message="Connecting...",
        debug_label="Conversation",
    )


@public_router.post("/{conversation_id}/warm")
async def warm_conversation(conversation_id: str):
    vcprint(conversation_id, "[Conversation Warm] Warming", color="cyan")

    if AgentCache.exists(conversation_id):
        vcprint(
            f"{conversation_id[:8]}...",
            "[Conversation Warm] Already cached",
            color="green",
        )
        return {"status": "already_cached", "conversation_id": conversation_id}

    try:
        agent = await _reconstruct_from_db(conversation_id)
        AgentCache.set(conversation_id, agent)
        vcprint(f"{conversation_id[:8]}...", "[Conversation Warm] Cached", color="green")
        return {"status": "cached", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        vcprint(str(e), f"[Conversation Warm] Error for {conversation_id[:8]}", color="red")
        return {"status": "error", "conversation_id": conversation_id, "message": str(e)}
