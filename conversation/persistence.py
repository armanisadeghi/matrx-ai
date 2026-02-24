"""
CX_ Persistence Service — Writes CompletedRequest data to the database.

This is the single point of truth for persisting AI execution results.
It lives in the core AI layer (not in API routes) so that ANY execution path
(unified chat, agent, internal calls, agent-to-agent) triggers persistence.

The cx_conversation row is guaranteed to exist before this module runs —
it is created by ``ensure_conversation_exists()`` at the start of
``execute_until_complete()`` in ``ai.ai_requests``.  This module only
**updates** the conversation; it never creates one.

Usage:
    from conversation.persistence import persist_completed_request

    completed = await execute_until_complete(...)
    await persist_completed_request(completed)
"""

from typing import Any, Dict, Optional
from datetime import datetime, timezone
from uuid import UUID
from matrx_utils import vcprint
from conversation import (
    cx_conversation_manager,
    cx_message_manager,
    cx_user_request_manager,
    cx_request_manager,
)
from db.custom.ai_model_manager import get_ai_model_manager


def _is_valid_uuid(value: Optional[str]) -> bool:
    if not value:
        return False
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


async def _resolve_ai_model_id(model_name: Optional[str]) -> Optional[str]:
    """Resolve a model name (e.g. 'gemini-3-flash-preview') to its ai_model UUID.

    Uses the cached model manager singleton — no DB hit if already loaded.
    Returns None if the model name is None or not found.
    """
    if not model_name:
        return None
    model_manager = get_ai_model_manager()
    model_data = await model_manager.load_model(model_name)
    if model_data:
        return str(model_data.id)
    vcprint(
        f"[CX Persistence] Could not resolve ai_model_id for: {model_name}",
        color="yellow",
    )
    return None


async def _backfill_tool_call_message_id(
    msg: Dict[str, Any],
    message_id: str,
    conversation_id: str,
) -> None:
    """Set message_id on the corresponding cx_tool_call row.

    Matches on call_id (from the original ToolResultContent) + conversation_id.
    This is fire-and-forget — failures are logged, never fatal.
    """
    from tools.handle_tool_calls import get_executor

    original_content = msg.get("_original_content", msg.get("content", []))
    if not isinstance(original_content, list):
        return

    executor = get_executor()
    tool_logger = executor.execution_logger

    for item in original_content:
        call_id = None
        if isinstance(item, dict):
            call_id = item.get("call_id") or item.get("tool_use_id")
        elif hasattr(item, "call_id"):
            call_id = getattr(item, "call_id", None) or getattr(item, "tool_use_id", None)

        if call_id:
            try:
                await tool_logger.backfill_message_id(call_id, conversation_id, message_id)
            except Exception:
                pass


async def persist_completed_request(
    completed: Any,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist a CompletedRequest to the cx_ database tables.

    The cx_conversation row is guaranteed to exist (created by the
    conversation gate at request entry time).  This function:
        1. Update cx_conversation with all data from the completed config
        2. Write new cx_message rows (only messages produced by this execution)
        3. Create cx_user_request (parent)
        4. Create cx_request rows (one per iteration)

    Args:
        completed: A CompletedRequest instance from execute_until_complete()
        conversation_id: Optional existing conversation UUID. Falls back to
                         completed.request.conversation_id.

    Returns:
        Dict with created record IDs:
            {
                "conversation_id": str,
                "user_request_id": str,
                "message_ids": list[str],
                "request_ids": list[str],
            }
    """
    storage = completed.to_storage_dict()
    conv_data = storage["conversation"]
    msg_list = storage["messages"]
    ur_data = storage["user_request"]
    req_list = storage["requests"]

    result: Dict[str, Any] = {
        "conversation_id": None,
        "user_request_id": None,
        "message_ids": [],
        "request_ids": [],
    }

    user_id = conv_data.get("user_id")
    if not _is_valid_uuid(user_id):
        vcprint(
            f"[CX Persistence] REJECTED — non-UUID user_id: {user_id!r}. "
            f"Cannot persist data without a valid user identity.",
            color="red",
        )
        return result

    try:
        # ============================================================
        # RESOLVE ai_model_id from model name string
        # ============================================================
        primary_ai_model_id = await _resolve_ai_model_id(conv_data.get("ai_model"))

        # ============================================================
        # 1. CONVERSATION — update existing (created by conversation gate)
        #
        # The gate creates a minimal row (just id + user_id + status).
        # This update backfills ALL real data from the completed
        # UnifiedConfig via to_storage_dict().  Every field that
        # to_storage_dict() puts into conv_data MUST be written here.
        # ============================================================
        db_conversation_id = conversation_id or completed.request.conversation_id

        if db_conversation_id and _is_valid_uuid(db_conversation_id):
            exec_status = completed.metadata.get("status")
            conv_status = "error" if exec_status == "failed" else "active"

            update_kwargs: Dict[str, Any] = {
                "ai_model_id": primary_ai_model_id,
                "message_count": conv_data["message_count"],
                "config": conv_data.get("config", {}),
                "status": conv_status,
            }

            # Backfill every optional field that to_storage_dict() provides
            if conv_data.get("system_instruction") is not None:
                update_kwargs["system_instruction"] = conv_data["system_instruction"]
            if conv_data.get("metadata") is not None:
                update_kwargs["metadata"] = conv_data["metadata"]
            if conv_data.get("parent_conversation_id") and _is_valid_uuid(conv_data["parent_conversation_id"]):
                update_kwargs["parent_conversation_id"] = conv_data["parent_conversation_id"]

            await cx_conversation_manager.update_cx_conversation(
                db_conversation_id,
                **update_kwargs,
            )
            result["conversation_id"] = db_conversation_id
        else:
            vcprint(
                f"[CX Persistence] No valid conversation_id to update: {db_conversation_id!r}",
                color="yellow",
            )

        # ============================================================
        # 2. MESSAGES — write trigger message + messages produced by this execution
        # ============================================================
        trigger_pos = completed.trigger_message_position
        start_pos = completed.result_start_position
        end_pos = completed.result_end_position

        if start_pos is not None and end_pos is not None:
            # Include the trigger message (user input) and all execution results
            write_from = trigger_pos if trigger_pos is not None else start_pos
            new_messages = [
                m for m in msg_list
                if write_from <= m["position"] <= end_pos
            ]
        else:
            # Fallback: write all messages (first execution in conversation)
            new_messages = msg_list

        for msg in new_messages:
            role_val = msg["role"]
            role_val = role_val.value if hasattr(role_val, "value") else role_val
            status_val = msg.get("status", "active")
            status_val = status_val.value if hasattr(status_val, "value") else status_val

            # Tool-role message content lives in cx_tool_call.output —
            # cx_message.content is empty for tool messages.
            msg_content = msg["content"]
            is_tool_message = role_val == "tool"

            if is_tool_message:
                msg_content = []

            message = await cx_message_manager.create_cx_message(
                conversation_id=db_conversation_id,
                role=role_val,
                position=msg["position"],
                status=status_val,
                content=msg_content,
            )
            msg_id = str(message.id) if hasattr(message, "id") else str(message)
            result["message_ids"].append(msg_id)

            # Backfill message_id on matching cx_tool_call rows so they
            # can be joined later during conversation rebuild.
            if is_tool_message:
                try:
                    await _backfill_tool_call_message_id(
                        msg, msg_id, db_conversation_id
                    )
                except Exception as backfill_err:
                    vcprint(
                        f"[CX Persistence] cx_tool_call backfill error: {backfill_err}",
                        color="yellow",
                    )

        # ============================================================
        # 3. USER REQUEST — update existing (created as 'pending' by
        #    create_pending_user_request() at the start of
        #    execute_until_complete).  The PK is the request_id from
        #    AIMatrixRequest.
        # ============================================================
        now = datetime.now(timezone.utc)
        user_request_id = ur_data.get("request_id") or completed.request.request_id

        if user_request_id and _is_valid_uuid(user_request_id):
            ur_update_data: Dict[str, Any] = {
                "conversation_id": db_conversation_id,
                "user_id": ur_data["user_id"],
                "ai_model_id": primary_ai_model_id,
                "api_class": ur_data.get("api_class"),
                "total_input_tokens": ur_data.get("total_input_tokens", 0),
                "total_output_tokens": ur_data.get("total_output_tokens", 0),
                "total_cached_tokens": ur_data.get("total_cached_tokens", 0),
                "total_tokens": ur_data.get("total_tokens", 0),
                "total_cost": ur_data.get("total_cost", 0),
                "iterations": ur_data.get("iterations", 1),
                "total_tool_calls": ur_data.get("total_tool_calls", 0),
                "status": ur_data.get("status", "completed"),
                "finish_reason": ur_data.get("finish_reason"),
                "completed_at": now,
                "metadata": ur_data.get("metadata", {}),
            }

            # Optional fields (only set if present)
            if ur_data.get("trigger_message_position") is not None:
                ur_update_data["trigger_message_position"] = ur_data["trigger_message_position"]
            if ur_data.get("result_start_position") is not None:
                ur_update_data["result_start_position"] = ur_data["result_start_position"]
            if ur_data.get("result_end_position") is not None:
                ur_update_data["result_end_position"] = ur_data["result_end_position"]
            if ur_data.get("error"):
                ur_update_data["error"] = ur_data["error"]

            # Timing
            if ur_data.get("total_duration_ms") is not None:
                ur_update_data["total_duration_ms"] = ur_data["total_duration_ms"]
            if ur_data.get("api_duration_ms") is not None:
                ur_update_data["api_duration_ms"] = ur_data["api_duration_ms"]
            if ur_data.get("tool_duration_ms") is not None:
                ur_update_data["tool_duration_ms"] = ur_data["tool_duration_ms"]

            await cx_user_request_manager.update_cx_user_request(
                user_request_id,
                **ur_update_data,
            )
        else:
            vcprint(
                f"[CX Persistence] No valid request_id to update user_request: {user_request_id!r}",
                color="yellow",
            )

        result["user_request_id"] = user_request_id

        # ============================================================
        # 4. REQUEST ROWS — one per iteration
        # ============================================================
        for req in req_list:
            # Resolve per-iteration model (may differ from primary if model switched)
            iter_model_name = req.get("ai_model")
            if iter_model_name and iter_model_name != conv_data.get("ai_model"):
                iter_ai_model_id = await _resolve_ai_model_id(iter_model_name)
            else:
                iter_ai_model_id = primary_ai_model_id

            req_create_data: Dict[str, Any] = {
                "user_request_id": user_request_id,
                "conversation_id": db_conversation_id,
                "ai_model_id": iter_ai_model_id,
                "api_class": req.get("api_class"),
                "iteration": req.get("iteration", 1),
                "input_tokens": req.get("input_tokens"),
                "output_tokens": req.get("output_tokens"),
                "cached_tokens": req.get("cached_tokens"),
                "total_tokens": req.get("total_tokens"),
                "cost": req.get("cost"),
                "api_duration_ms": req.get("api_duration_ms"),
                "tool_duration_ms": req.get("tool_duration_ms"),
                "total_duration_ms": req.get("total_duration_ms"),
                "tool_calls_count": req.get("tool_calls_count", 0),
                "tool_calls_details": req.get("tool_calls_details"),
                "finish_reason": req.get("finish_reason"),
                "response_id": req.get("response_id"),
                "metadata": req.get("metadata", {}),
            }

            request_row = await cx_request_manager.create_cx_request(
                **req_create_data
            )
            req_id = str(request_row.id) if hasattr(request_row, "id") else str(request_row)
            result["request_ids"].append(req_id)

        vcprint(
            f"[CX Persistence] Saved: Conversation ID: {db_conversation_id}\n"
            f"User Request ID: {user_request_id}\n"
            f"{len(result['message_ids'])} messages,\n"
            f"{len(result['request_ids'])} request iterations",
            color="green",
        )

        return result

    except Exception as e:
        vcprint(
            f"[CX Persistence] Error persisting request: {e}",
            color="red",
        )
        import traceback
        traceback.print_exc()
        # Return partial result rather than crashing the caller
        return result
