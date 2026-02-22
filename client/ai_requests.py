import asyncio
import traceback
from typing import Any, Dict, List, Optional, Tuple
from client.recovery_logic import handle_finish_reason
from matrx_utils import vcprint
from client.unified_client import UnifiedAIClient, AIMatrixRequest, CompletedRequest
from config.unified_config import ToolCallContent, UnifiedResponse, UnifiedMessage
from client.usage import TokenUsage
from client.timing import TimingUsage
from client.tool_call_tracking import ToolCallUsage
from conversation.persistence import persist_completed_request
from conversation.gate import (
    ensure_conversation_exists,
    update_conversation_status,
    create_pending_user_request,
    update_user_request_status,
)
import time


LOCAL_DEBUG = False


async def handle_tool_calls(
    response: UnifiedResponse, request: AIMatrixRequest, iteration: int
) -> Tuple[Optional[List], Optional[ToolCallUsage], List[TokenUsage]]:
    """Handle tool calls from the response using Tool System V2.

    Returns (tool_results, tool_call_usage, child_token_usages).
    child_token_usages contains TokenUsage objects from any child agent
    executions triggered by the tool calls.
    """
    from tools.handle_tool_calls import handle_tool_calls_v2
    from config.unified_config import ToolResultContent

    tool_calls = []
    messages = response.messages
    if isinstance(messages, UnifiedMessage):
        messages = [messages]

    for message in messages:
        for content in message.content:
            if isinstance(content, ToolCallContent):
                tool_calls.append(content)

    if not tool_calls:
        return None, None, []

    raw_calls = [
        {
            "name": getattr(tc, "name", ""),
            "arguments": getattr(tc, "arguments", {}),
            "call_id": getattr(tc, "call_id", "") or getattr(tc, "id", ""),
        }
        for tc in tool_calls
    ]

    vcprint(tool_calls, "ai_requests.py: Tool Calls", color="yellow")
    vcprint(raw_calls, "ai_requests.py: Raw Calls", color="yellow")
    content_results, child_token_usages = await handle_tool_calls_v2(
        raw_calls,
        iteration=iteration,
    )

    results = [ToolResultContent(**cr) for cr in content_results]

    vcprint(content_results, "ai_requests.py: Content Results", color="yellow")
    tool_call_details = [
        {
            "name": raw_calls[i]["name"],
            "id": raw_calls[i]["call_id"],
            "call_id": raw_calls[i]["call_id"],
            "success": not cr.get("is_error", False),
        }
        for i, cr in enumerate(content_results)
    ]

    tool_call_usage = ToolCallUsage(
        iteration=iteration,
        tool_calls_count=len(tool_calls),
        tool_calls_details=tool_call_details,
    )

    vcprint(tool_call_usage, "ai_requests.py: Tool Call Usage", color="yellow")

    return results, tool_call_usage, child_token_usages



# ============================================================================
# INTERNAL HELPERS
# ============================================================================


async def _finalize_and_persist(
    current_request: AIMatrixRequest,
    iteration: int,
    final_response: UnifiedResponse,
    metadata: Dict[str, Any],
    trigger_position: int,
    pre_execution_message_count: int,
    conversation_id: Optional[str] = None,
) -> CompletedRequest:
    """Build a CompletedRequest and persist it to the database.

    Every exit path from execute_until_complete() MUST call this function.
    This guarantees that no API call, no matter how it was triggered
    (route, test, agent-to-agent, internal service), is ever lost.

    The cx_conversation row already exists (created by the conversation
    gate at request entry time).  Persistence only updates it.

    Persistence is non-blocking to the caller: errors are logged
    but never propagated. The CompletedRequest is always returned.
    """
    post_count = len(current_request.config.messages)
    has_new_messages = post_count > pre_execution_message_count

    completed = CompletedRequest(
        request=current_request,
        total_usage=current_request.total_usage,
        timing_stats=current_request.timing_stats,
        tool_call_stats=current_request.tool_call_stats,
        iterations=iteration,
        final_response=final_response,
        metadata=metadata,
        trigger_message_position=trigger_position,
        result_start_position=pre_execution_message_count if has_new_messages else None,
        result_end_position=post_count - 1 if has_new_messages else None,
    )

    conv_id = conversation_id or current_request.conversation_id or None
    req_id = current_request.request_id or None

    # On failure paths, update both conversation and user_request status
    # immediately so the DB reflects the error even if full persistence
    # below fails.
    if metadata.get("status") == "failed":
        if conv_id:
            await update_conversation_status(conv_id, "error")
        if req_id:
            await update_user_request_status(
                req_id, "failed", error=metadata.get("error"),
            )

    # Persist — never block, never crash the caller
    try:
        await persist_completed_request(completed, conversation_id=conv_id)
    except Exception as persist_err:
        vcprint(f"[CX Persistence] Non-fatal error: {persist_err}", color="yellow")

    return completed


# ============================================================================
# MAIN EXECUTION FUNCTIONS
# ============================================================================


async def execute_until_complete(
    initial_request: AIMatrixRequest,
    client: UnifiedAIClient,
    max_iterations: int = 20,
    max_retries_per_iteration: int = 2,
) -> CompletedRequest:
    """
    Execute AI request autonomously, handling tool calls until completion.

    Args:
        initial_request: The initial request to execute
        client: The unified AI client
        max_iterations: Maximum number of iterations before giving up

    Returns:
        CompletedRequest with full conversation history, usage, and final response

    Raises:
        RuntimeError: If max iterations exceeded or execution fails
    """
    from context.app_context import get_app_context
    exec_ctx = get_app_context()

    current_request = initial_request
    iteration = 0
    debug = current_request.debug
    if LOCAL_DEBUG:
        debug = True

    await ensure_conversation_exists(
        conversation_id=exec_ctx.conversation_id,
        user_id=exec_ctx.user_id,
        parent_conversation_id=exec_ctx.parent_conversation_id,
    )

    await create_pending_user_request(
        request_id=exec_ctx.request_id or current_request.request_id or "",
        conversation_id=exec_ctx.conversation_id,
        user_id=exec_ctx.user_id,
    )

    # Track message positions for cx_user_request
    pre_execution_message_count = len(current_request.config.messages)
    # The trigger is the last user message before execution (position is 0-based)
    trigger_position = pre_execution_message_count - 1 if pre_execution_message_count > 0 else 0

    while iteration < max_iterations:
        iteration += 1
        current_timing = TimingUsage(start_time=time.time(), iteration=iteration)

        vcprint(f"\n{'='*60}\nIteration {iteration}\n{'='*60}", color="cyan", verbose=debug)

        # Retry loop for recoverable errors
        response: Optional[UnifiedResponse] = None
        last_error: Optional[Exception] = None
        
        for retry_attempt in range(max_retries_per_iteration + 1):
            try:
                # Make API call
                t0 = time.time()
                response = await client.execute(current_request)
                current_timing.api_call_duration = time.time() - t0
                current_timing.model = current_request.config.model
                
                # if debug:
                #     print("\n\nDEBUG PRINT Execute Until complete 1\n\n")
                #     rich.print(response)
                
                # Automatically track usage in the request
                current_request.add_usage(response.usage)

                # Handle finish reason
                finish_action = handle_finish_reason(
                    response,
                    current_request,
                    retry_attempt,
                    max_retries_per_iteration,
                    debug
                )
                
                status = {
                    "Iteration": iteration,
                    "Retry Attempt": retry_attempt,
                    "Finish Action": finish_action,
                    "Finish Reason": response.finish_reason,
                }
                await exec_ctx.emitter.send_status_update(
                    status="processing",
                    system_message="Processing update",
                    metadata=status,
                )
                
                vcprint(status, "Request Status", color="magenta", verbose=debug)
                
                if finish_action == "retry":
                    continue  # Retry with updated context
                elif finish_action == "stop":
                    return await _finalize_and_persist(
                        current_request=current_request,
                        iteration=iteration,
                        final_response=response,
                        metadata={
                            "status": "failed",
                            "finish_reason": response.finish_reason,
                            "error": f"Model stopped with finish reason: {response.finish_reason}",
                            "error_type": "finish_reason_error",
                        },
                        trigger_position=trigger_position,
                        pre_execution_message_count=pre_execution_message_count,
                    )
                
                # Success - break out of retry loop
                break
            
            except Exception as e:
                last_error = e
                
                # Check if error has classification info attached
                from client.errors import classify_provider_error, RetryableError
                
                error_info: RetryableError = getattr(e, 'error_info', None)
                if error_info is None:
                    # Classify the error if not already classified
                    # Try to determine provider from model or config
                    provider = "unknown"
                    if current_request.config.model:
                        model_name = current_request.config.model.lower()
                        if "gemini" in model_name or "google" in model_name:
                            provider = "google"
                        elif "gpt" in model_name or "openai" in model_name:
                            provider = "openai"
                        elif "claude" in model_name or "anthropic" in model_name:
                            provider = "anthropic"
                    
                    error_info = classify_provider_error(provider, e)
                
                # Handle retryable errors
                if error_info.is_retryable and retry_attempt < max_retries_per_iteration:
                    backoff_delay = error_info.get_backoff_delay(retry_attempt)
                    
                    vcprint(
                        f"⚠️  {error_info.error_type} (attempt {retry_attempt + 1}/{max_retries_per_iteration + 1}): {error_info.message}",
                        color="yellow"
                    )
                    vcprint(f"↻ Waiting {backoff_delay:.1f}s before retry...", color="yellow")
                    
                    if exec_ctx.emitter:
                        await exec_ctx.emitter.send_status_update(
                            status="retrying",
                            system_message=error_info.user_message,
                            metadata={
                                "error_type": error_info.error_type,
                                "retry_attempt": retry_attempt + 1,
                                "max_retries": max_retries_per_iteration + 1,
                                "retry_delay": backoff_delay,
                            }
                        )
                    
                    # Wait before retry
                    await asyncio.sleep(backoff_delay)
                    continue
                else:
                    # Non-retryable or max retries exceeded
                    if not error_info.is_retryable:
                        vcprint(
                            f"✗ Non-retryable error: {error_info.message}",
                            color="red"
                        )
                    else:
                        vcprint(
                            f"✗ Max retries exceeded after {retry_attempt + 1} attempts",
                            color="red"
                        )
                    
                    if exec_ctx.emitter:
                        await exec_ctx.emitter.send_error(
                            error_type=error_info.error_type,
                            message=error_info.message,
                            user_message=error_info.user_message if not error_info.is_retryable
                                else f"Failed after {retry_attempt + 1} retry attempts. {error_info.user_message}"
                        )
                    
                    # Re-raise to outer exception handler
                    raise

        # After retry loop - check if we have a valid response
        if response is None:
            # All retries failed, handle the last error
            vcprint(f"\n✗ All retries failed in iteration {iteration}", color="red")
            
            if current_timing.end_time is None:
                current_timing.end_time = time.time()
                current_request.add_timing(current_timing)
            
            # Get error info from last_error if available
            from client.errors import RetryableError
            error_info: RetryableError = getattr(last_error, 'error_info', None)
            
            error_message = error_info.message if error_info else str(last_error)
            error_type = error_info.error_type if error_info else type(last_error).__name__
            
            return await _finalize_and_persist(
                current_request=current_request,
                iteration=iteration,
                final_response=UnifiedResponse(messages=[]),
                metadata={
                    "error": error_message,
                    "error_type": error_type,
                    "error_iteration": iteration,
                    "status": "failed",
                    "retries_exhausted": True,
                },
                trigger_position=trigger_position,
                pre_execution_message_count=pre_execution_message_count,
            )
        
        # Process tool calls
        try:
            # Check for tool calls
            t0 = time.time()
            tool_results, tool_call_usage, child_token_usages = await handle_tool_calls(response, current_request, iteration)
            current_timing.tool_execution_duration = time.time() - t0

            # Add child agent usages to parent request so they appear in total_usage
            for child_usage in child_token_usages:
                current_request.add_usage(child_usage)

            # Record completion of this iteration's main work
            current_timing.end_time = time.time()
            current_request.add_timing(current_timing)

            # Track tool calls if any were made
            current_request.add_tool_calls(tool_call_usage)

            # Always update request with the response and tool results (if any)
            current_request = AIMatrixRequest.add_response(
                original_request=current_request,
                response=response,
                tool_results=tool_results,
            )
            
            # if debug:
            #     print("\n\nDEBUG PRINT Execute Until complete 2\n\n")                
            #     rich.print(current_request)

            # Finish - no more tool calls needed
            if tool_results is None:
                # Print accumulated usage for debugging
                vcprint(current_request.usage_history, "Usage History", color="magenta", verbose=debug)
                vcprint(current_request.total_usage, "Total Usage", color="green", verbose=debug)
                vcprint(current_request.tool_call_stats, "Tool Call Stats", color="blue", verbose=debug)

                # Build complete response and persist
                return await _finalize_and_persist(
                    current_request=current_request,
                    iteration=iteration,
                    final_response=response,
                    metadata={
                        "finish_reason": response.finish_reason,
                        "response_id": response.usage.response_id if response.usage else None,
                        "model": response.usage.model if response.usage else None,
                    },
                    trigger_position=trigger_position,
                    pre_execution_message_count=pre_execution_message_count,
                )

            # Continue - loop back for next iteration

        except Exception as e:
            # Ensure we close out the timing for this failed iteration
            if current_timing.end_time is None:
                current_timing.end_time = time.time()
                current_request.add_timing(current_timing)

            vcprint(f"\n✗ Error in iteration {iteration}: {str(e)}", color="red")
            traceback.print_exc()

            # CRITICAL: Preserve all accumulated usage and data even on error
            # Print what we've collected so far
            if current_request.usage_history:
                vcprint(
                    current_request.usage_history,
                    "Usage History (at error)",
                    color="magenta",
                    verbose=debug,
                )
                vcprint(
                    current_request.total_usage,
                    "Total Usage (at error)",
                    color="yellow",
                    verbose=debug,
                )

            # Return a CompletedRequest with error information
            # This ensures the client never loses accumulated data
            error_response = await _finalize_and_persist(
                current_request=current_request,
                iteration=iteration,
                final_response=response if response else UnifiedResponse(messages=[]),
                metadata={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "error_iteration": iteration,
                    "status": "failed",
                },
                trigger_position=trigger_position,
                pre_execution_message_count=pre_execution_message_count,
            )

            vcprint(error_response, "Error Response", color="yellow")

            return error_response

    # Hit max iterations - still return accumulated data
    vcprint("\n⚠️  Max iterations reached - returning accumulated data", color="yellow")
    if current_request.usage_history:
        vcprint(
            current_request.usage_history,
            "Usage History (max iterations)",
            color="magenta",
            verbose=debug,
        )
        vcprint(
            current_request.total_usage, "Total Usage (max iterations)", color="yellow", verbose=debug
        )

    return await _finalize_and_persist(
        current_request=current_request,
        iteration=iteration,
        final_response=response
        if "response" in locals()
        else UnifiedResponse(messages=[]),
        metadata={
            "status": "max_iterations_exceeded",
            "max_iterations": max_iterations,
        },
        trigger_position=trigger_position,
        pre_execution_message_count=pre_execution_message_count,
    )
