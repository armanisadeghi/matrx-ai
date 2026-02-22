from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from tools.models import ToolContext, ToolDefinition, ToolResult

logger = logging.getLogger(__name__)


class ToolExecutionLogger:
    """Two-phase logging to the ``cx_tool_call`` table via the ORM manager.

    Phase 1 — ``log_started()``:
        INSERT a row with ``status='running'`` the moment execution begins.

    Phase 2 — ``log_completed()`` / ``log_error()``:
        UPDATE that row with output, cost, events, and final status.

    Both phases are fire-and-forget — failures are logged but never block
    the execution pipeline.
    """

    def _get_manager(self) -> Any:
        from conversation import cx_tool_call_manager
        return cx_tool_call_manager

    # ------------------------------------------------------------------
    # Phase 1: log_started (INSERT)
    # ------------------------------------------------------------------

    async def log_started(
        self,
        ctx: ToolContext,
        tool_def: ToolDefinition,
        arguments: dict[str, Any],
    ) -> str:
        row_id = str(uuid4())
        now = datetime.now(timezone.utc)

        safe_arguments = self._truncate_arguments(arguments)

        data: dict[str, Any] = {
            "id": row_id,
            "conversation_id": ctx.conversation_id,
            "user_id": ctx.user_id,
            "request_id": ctx.request_id if ctx.request_id else None,
            "tool_name": tool_def.name,
            "tool_type": tool_def.tool_type.value,
            "call_id": ctx.call_id,
            "status": "running",
            "arguments": safe_arguments,
            "iteration": ctx.iteration,
            "started_at": now.isoformat(),
            "completed_at": now.isoformat(),
            "created_at": now.isoformat(),
            "metadata": {},
        }

        try:
            mgr = self._get_manager()
            await mgr.create_cx_tool_call(**data)
        except Exception as exc:
            logger.warning("Failed to INSERT cx_tool_call (started): %s", exc)

        return row_id

    # ------------------------------------------------------------------
    # Phase 2a: log_completed (UPDATE)
    # ------------------------------------------------------------------

    async def log_completed(
        self,
        row_id: str,
        result: ToolResult,
        execution_events: list[dict[str, Any]] | None = None,
    ) -> None:
        output_str, output_type = self._serialize_output(result.output)

        input_tokens, output_tokens, cost_usd = self._aggregate_usage(result)
        total_tokens = input_tokens + output_tokens

        update_data: dict[str, Any] = {
            "status": "completed",
            "success": True,
            "is_error": False,
            "output": output_str,
            "output_type": output_type,
            "duration_ms": result.duration_ms,
            "completed_at": datetime.fromtimestamp(result.completed_at, tz=timezone.utc).isoformat() if result.completed_at else datetime.now(timezone.utc).isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
            "retry_count": result.retry_count,
            "execution_events": execution_events or [],
            "persist_key": result.persist_key if result.should_persist_output else None,
        }

        await self._update_row(row_id, update_data)

    # ------------------------------------------------------------------
    # Phase 2b: log_error (UPDATE)
    # ------------------------------------------------------------------

    async def log_error(
        self,
        row_id: str,
        result: ToolResult,
        execution_events: list[dict[str, Any]] | None = None,
    ) -> None:
        input_tokens, output_tokens, cost_usd = self._aggregate_usage(result)
        total_tokens = input_tokens + output_tokens

        update_data: dict[str, Any] = {
            "status": "error",
            "success": False,
            "is_error": True,
            "error_type": result.error.error_type if result.error else "unknown",
            "error_message": result.error.message if result.error else "Unknown error",
            "duration_ms": result.duration_ms,
            "completed_at": datetime.fromtimestamp(result.completed_at, tz=timezone.utc).isoformat() if result.completed_at else datetime.now(timezone.utc).isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
            "retry_count": result.retry_count,
            "execution_events": execution_events or [],
        }

        await self._update_row(row_id, update_data)

    # ------------------------------------------------------------------
    # Link message_id after persistence creates the cx_message row
    # ------------------------------------------------------------------

    async def link_message(self, row_id: str, message_id: str) -> None:
        await self._update_row(row_id, {"message_id": message_id})

    # ------------------------------------------------------------------
    # Backfill message_id by call_id + conversation_id
    # ------------------------------------------------------------------

    async def backfill_message_id(
        self, call_id: str, conversation_id: str, message_id: str,
    ) -> None:
        try:
            mgr = self._get_manager()
            matches = await mgr.filter_cx_tool_calls(
                call_id=call_id, conversation_id=conversation_id,
            )
            for item in matches:
                await mgr.update_cx_tool_call(str(item.id), message_id=message_id)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _update_row(self, row_id: str, data: dict[str, Any]) -> None:
        try:
            mgr = self._get_manager()
            await mgr.update_cx_tool_call(row_id, **data)
        except Exception as exc:
            logger.warning("Failed to UPDATE cx_tool_call %s: %s", row_id, exc)

    _MAX_ARG_STRING_CHARS = 10_000

    @staticmethod
    def _truncate_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        limit = ToolExecutionLogger._MAX_ARG_STRING_CHARS
        for key, value in arguments.items():
            if isinstance(value, str) and len(value) > limit:
                result[key] = value[:limit] + f"…[truncated {len(value):,} chars]"
            else:
                result[key] = value
        return result

    _MAX_OUTPUT_CHARS = 100_000

    @staticmethod
    def _serialize_output(output: Any) -> tuple[str | None, str]:
        if output is None:
            return None, "text"
        if isinstance(output, str):
            serialized, output_type = output, "text"
        elif isinstance(output, (dict, list)):
            serialized, output_type = json.dumps(output, default=str), "json"
        else:
            serialized, output_type = str(output), "text"

        if len(serialized) > ToolExecutionLogger._MAX_OUTPUT_CHARS:
            truncated = serialized[: ToolExecutionLogger._MAX_OUTPUT_CHARS]
            suffix = f"\n\n[TRUNCATED — {len(serialized):,} chars total, showing first {ToolExecutionLogger._MAX_OUTPUT_CHARS:,}]"
            serialized = truncated + suffix

        return serialized, output_type

    @staticmethod
    def _aggregate_usage(result: ToolResult) -> tuple[int, int, float]:
        input_tokens = 0
        output_tokens = 0
        cost_usd = 0.0

        if result.usage:
            input_tokens = result.usage.get("input_tokens", 0)
            output_tokens = result.usage.get("output_tokens", 0)
            cost_usd = result.usage.get("cost_usd", 0.0)

        for child in result.child_usages:
            if isinstance(child, dict):
                input_tokens += child.get("input_tokens", 0)
                output_tokens += child.get("output_tokens", 0)
                cost_usd += child.get("cost_usd", 0.0)
            else:
                input_tokens += getattr(child, "input_tokens", 0)
                output_tokens += getattr(child, "output_tokens", 0)
                child_cost = child.calculate_cost()
                cost_usd += child_cost if child_cost is not None else 0.0

        return input_tokens, output_tokens, cost_usd
