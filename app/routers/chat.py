"""
Chat router — streaming-first LLM completions.

  POST /api/ai/chat — one-shot or managed chat

Wired to the real AI engine via execute_until_complete().
"""

from __future__ import annotations

import uuid
from dataclasses import fields
from typing import Any

from fastapi import APIRouter, Depends
from matrx_utils import vcprint

from app.core.response import create_streaming_response
from app.models.chat import ChatRequest
from context.app_context import AppContext, context_dep
from context.events import CompletionPayload
from context.stream_emitter import StreamEmitter
from client.unified_client import UnifiedAIClient, AIMatrixRequest, CompletedRequest
from config.unified_config import UnifiedConfig
from client.ai_requests import execute_until_complete

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


async def _run_chat(
    emitter: StreamEmitter,
    request: ChatRequest,
    conversation_id: str,
):
    if request.debug:
        vcprint(request.model_dump(), "[Chat] Request", color="light_blue")

    config, unrecognized = _build_unified_config(request)

    if unrecognized:
        await emitter.send_status_update(
            status="warning",
            system_message=f"Unrecognized config keys: {', '.join(sorted(unrecognized))}",
            user_message=f"The following configurations are not used: "
                         f"{', '.join(sorted(unrecognized))}",
        )

    metadata = request.metadata or {}
    metadata["ai_model_id"] = request.ai_model_id

    ai_request = AIMatrixRequest(
        conversation_id=conversation_id,
        config=config,
        debug=request.debug,
        metadata=metadata,
    )

    if request.debug:
        vcprint(ai_request.to_dict(), "[Chat] AIMatrixRequest", color="cyan")

    await emitter.send_status_update(status="processing", system_message="Starting chat execution")

    client = UnifiedAIClient()
    completed: CompletedRequest = await execute_until_complete(
        initial_request=ai_request,
        client=client,
        max_iterations=request.max_iterations,
        max_retries_per_iteration=request.max_retries_per_iteration,
    )

    cx_status = completed.metadata.get("status", "complete")
    if cx_status == "complete" or cx_status != "failed":
        completion = CompletionPayload(
            status="complete",
            iterations=completed.iterations,
            total_usage=completed.total_usage.to_dict(),
            timing_stats={
                "total_duration": completed.timing_stats.get("total_duration"),
                "api_duration": completed.timing_stats.get("api_duration"),
                "tool_duration": completed.timing_stats.get("tool_duration"),
                "iterations": completed.timing_stats.get("iterations"),
                "avg_iteration_duration": completed.timing_stats.get("avg_iteration_duration"),
            },
            tool_call_stats=completed.tool_call_stats,
            finish_reason=(
                str(completed.metadata.get("finish_reason", ""))
                if completed.metadata.get("finish_reason") else None
            ),
        )
        await emitter.send_completion(completion)
        vcprint(completion.model_dump(), "[Chat] Completion", color="green")
    else:
        error_msg = completed.metadata.get("error", "Unknown error")
        vcprint(error_msg, "[Chat] Execution failed", color="red")
        await emitter.send_error(
            error_type=completed.metadata.get("error_type", "execution_error"),
            message=str(error_msg),
            user_message="Execution completed with errors. Please check the results.",
            details={
                "error": str(error_msg),
                "error_type": completed.metadata.get("error_type", "execution_error"),
                "error_iteration": completed.metadata.get("error_iteration"),
                "status": "failed",
            },
        )

    await emitter.send_end()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    ctx: AppContext = Depends(context_dep),
) -> Any:
    conversation_id = request.conversation_id or str(uuid.uuid4())
    vcprint(f"conversation_id={conversation_id}", "[Chat]", color="cyan")

    ctx.extend(conversation_id=conversation_id, debug=request.debug)
    return create_streaming_response(
        ctx,
        _run_chat,
        request, conversation_id,
        initial_message="Connecting...",
        debug_label="Chat",
    )
