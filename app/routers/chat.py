"""
Chat router — streaming-first LLM completions.

  POST /api/ai/chat — one-shot or managed chat

Wired to the real AI engine via run_ai_task().
"""

from __future__ import annotations

import uuid
from dataclasses import fields
from typing import Any

from fastapi import APIRouter, Depends
from matrx_utils import vcprint

from app.core.response import create_streaming_response
from app.core.ai_task import run_ai_task
from app.models.chat import ChatRequest
from context.app_context import AppContext, context_dep
from config.unified_config import UnifiedConfig

router = APIRouter(prefix="/api/ai", tags=["chat"])

_EXCLUDE_FROM_CONFIG = {
    "ai_model_id",
    "conversation_id",
    "max_iterations",
    "max_retries_per_iteration",
    "debug",
    "metadata",
    "store",
}


def _build_unified_config(request: ChatRequest) -> tuple[UnifiedConfig, set]:
    """Translate a ChatRequest into a UnifiedConfig.

    Returns (config, unrecognized_keys) so the router can warn the client
    about any fields that were passed but are not valid config options.
    """
    valid_config_fields = {f.name for f in fields(UnifiedConfig)}

    config_data: dict[str, Any] = {
        "model": request.ai_model_id,
        "messages": request.messages,
        "stream": request.stream,
    }

    for key, value in request.model_dump().items():
        if key not in _EXCLUDE_FROM_CONFIG and key not in config_data and value is not None:
            config_data[key] = value

    unrecognized = set(config_data.keys()) - valid_config_fields
    return UnifiedConfig.from_dict(config_data), unrecognized


@router.post("/chat")
async def chat(
    request: ChatRequest,
    ctx: AppContext = Depends(context_dep),
) -> Any:
    """Direct chat endpoint — client supplies the full message history.

    Builds a UnifiedConfig from the request, sets conversation scope on
    AppContext, and hands off to the AI engine via run_ai_task.
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())
    vcprint(f"conversation_id={conversation_id}", "[Chat]", color="cyan")

    ctx.extend(conversation_id=conversation_id, debug=request.debug)

    config, unrecognized = _build_unified_config(request)

    if unrecognized:
        vcprint(f"[Chat] Unrecognized config keys (ignored): {unrecognized}", color="yellow")

    return create_streaming_response(
        ctx,
        run_ai_task,
        config,
        request.max_iterations,
        request.max_retries_per_iteration,
        initial_message="Connecting...",
        debug_label="Chat",
    )
