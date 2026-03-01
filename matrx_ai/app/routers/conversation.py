"""
Conversation router.

  POST /api/ai/conversations/{conversation_id}       — continue an existing conversation
  POST /api/ai/conversations/{conversation_id}/warm   — pre-warm conversation cache (public)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from matrx_utils import vcprint

from agents.resolver import ConversationResolver
from app.core.ai_task import run_ai_task
from app.core.response import create_streaming_response
from app.models.conversation import ConversationContinueRequest
from context.app_context import AppContext, context_dep

# Protected endpoints (require guest auth or above)
router = APIRouter(prefix="/api/ai/conversations", tags=["conversation"])

# Public endpoints (no auth — server-to-server warm calls from Next.js)
public_router = APIRouter(prefix="/api/ai/conversations", tags=["conversation"])


@router.post("/{conversation_id}")
async def continue_conversation(
    conversation_id: str,
    request: ConversationContinueRequest,
    ctx: AppContext = Depends(context_dep),
) -> Any:
    """Continue an existing conversation.

    Resolves the UnifiedConfig from cache or DB via ConversationResolver,
    appends the new user_input, then hands off to the AI engine.
    """
    vcprint(conversation_id, "[Conversation] Continue", color="cyan")
    ctx.extend(conversation_id=conversation_id, debug=request.debug)

    config = await ConversationResolver.from_conversation_id(
        conversation_id,
        user_input=request.user_input,
        config_overrides=request.config_overrides,
    )

    return create_streaming_response(
        ctx,
        run_ai_task,
        config,
        initial_message="Connecting...",
        debug_label="Conversation",
    )


@public_router.post("/{conversation_id}/warm")
async def warm_conversation(conversation_id: str):
    """Pre-load a conversation into the in-memory cache.

    Fire-and-forget from the client's perspective — any error is logged
    but never returned as a failure. The sole purpose is to shave latency
    off the next real request.
    """
    vcprint(conversation_id, "[Conversation Warm] Warming", color="cyan")
    cached = await ConversationResolver.warm(conversation_id)
    status = "cached" if cached else "already_cached"
    return {"status": status, "conversation_id": conversation_id}
