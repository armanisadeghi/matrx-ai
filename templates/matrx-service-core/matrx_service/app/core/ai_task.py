"""Shared AI execution task for all streaming AI routes.

Every AI route (chat, agent, conversation) uses the same run_ai_task and
_emit_completion helper. The router's only job is to resolve a UnifiedConfig,
set AppContext, and hand off to create_streaming_response().

Usage:
    from matrx_ai.app.core.ai_task import run_ai_task

    return create_streaming_response(
        ctx, run_ai_task, config,
        initial_message="Connecting...", debug_label="Chat",
    )
"""

from __future__ import annotations

import traceback

from matrx_utils import vcprint

from matrx_ai.config.unified_config import UnifiedConfig
from matrx_service.context.events import CompletionPayload
from matrx_service.context.stream_emitter import StreamEmitter
from matrx_ai.orchestrator.requests import CompletedRequest


async def run_ai_task(
    emitter: StreamEmitter,
    config: UnifiedConfig,
    max_iterations: int = 20,
    max_retries_per_iteration: int = 2,
) -> None:
    """Single shared task function for all AI streaming routes.

    Delegates execution entirely to execute_ai_request(), which reads all
    identity and scoping data from AppContext. After execution:
        1. Writes the completed config back into AgentCache so follow-up
           requests hit the cache instead of going to the DB.
        2. Sends the completion event and closes the stream.

    This function is passed as task_fn to create_streaming_response().
    The emitter argument is injected by the streaming infrastructure.
    """
    from matrx_ai.orchestrator import execute_ai_request

    await emitter.send_status_update(status="processing", system_message="Starting execution")

    completed = await execute_ai_request(
        config,
        max_iterations=max_iterations,
        max_retries_per_iteration=max_retries_per_iteration,
    )

    _update_cache(completed)

    await _emit_completion(emitter, completed)
    await emitter.send_end()


def _update_cache(completed: CompletedRequest) -> None:
    """Write the completed conversation config into AgentCache."""
    try:
        from matrx_ai.agents.cache import AgentCache
        from matrx_ai.agents.definition import Agent
        from matrx_service.context.app_context import get_app_context

        ctx = get_app_context()
        conversation_id = ctx.conversation_id
        if not conversation_id:
            return

        agent = Agent(config=completed.request.config)
        AgentCache.set(conversation_id, agent)
        vcprint(f"[AI Task] Cache updated: {conversation_id}", color="green")
    except Exception as exc:
        vcprint(f"[AI Task] Cache update failed (non-fatal): {exc}\n{traceback.format_exc()}", color="yellow")


async def _emit_completion(emitter: StreamEmitter, completed: CompletedRequest) -> None:
    """Send the correct completion or error event based on execution outcome."""
    exec_status = completed.metadata.get("status", "complete")

    if exec_status == "failed":
        error_msg = completed.metadata.get("error", "Unknown error")
        vcprint(f"[AI Task] Execution failed: {error_msg}", color="red")
        await emitter.send_error(
            error_type=completed.metadata.get("error_type", "execution_error"),
            message=str(error_msg),
            user_message="Execution completed with errors. Please try again.",
            details={
                "error": str(error_msg),
                "error_type": completed.metadata.get("error_type", "execution_error"),
                "error_iteration": completed.metadata.get("error_iteration"),
                "status": exec_status,
            },
        )
        return

    last_output = completed.request.config.get_last_output() if completed.request else None
    completion = CompletionPayload(
        status="complete",
        output=last_output,
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
        finish_reason=str(completed.metadata.get("finish_reason", "")) if completed.metadata.get("finish_reason") else None,
    )
    await emitter.send_completion(completion)
    vcprint(completion.model_dump(), "[AI Task] Completion", color="green", verbose=True)
