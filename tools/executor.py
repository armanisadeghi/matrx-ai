from __future__ import annotations

import asyncio
import logging
import time
import traceback as tb
from typing import Any
from uuid import uuid4

from matrx_utils import vcprint

from tools.guardrails import GuardrailEngine
from tools.lifecycle import ToolLifecycleManager
from tools.logger import ToolExecutionLogger
from tools.models import (
    ToolContext,
    ToolDefinition,
    ToolError,
    ToolResult,
    ToolType,
)
from tools.registry import ToolRegistryV2
from tools.streaming import ToolStreamManager

logger = logging.getLogger(__name__)


class ToolExecutor:
    """The single entry point for all tool executions.

    Replaces:
      - tool_registry.execute_tool_call()
      - tool_registry.execute_tool()
      - All thin wrapper functions in mcp_server/tools/

    Every tool — local, external MCP, agent — goes through the same pipeline:
      1. Resolve tool definition from registry
      2. Build ToolContext
      3. Validate arguments
      4. Check guardrails
      5. Stream "started" to client
      6. Execute (dispatch by tool type)
      7. Stream "completed" or "error" to client
      8. Log execution (fire-and-forget)
      9. Persist output if flagged
      10. Return result
    """

    def __init__(
        self,
        registry: ToolRegistryV2,
        guardrails: GuardrailEngine | None = None,
        execution_logger: ToolExecutionLogger | None = None,
        lifecycle: ToolLifecycleManager | None = None,
    ):
        self.registry = registry
        self.guardrails = guardrails or GuardrailEngine()
        self.execution_logger = execution_logger or ToolExecutionLogger()
        self.lifecycle = lifecycle or ToolLifecycleManager.get_instance()

    # ------------------------------------------------------------------
    # Context builder
    # ------------------------------------------------------------------

    @staticmethod
    def build_context(
        *,
        call_id: str,
        tool_name: str,
        iteration: int = 0,
        recursion_depth: int = 0,
        cost_budget_remaining: float | None = None,
        calls_remaining: int | None = None,
    ) -> ToolContext:
        return ToolContext(
            call_id=call_id,
            tool_name=tool_name,
            iteration=iteration,
            recursion_depth=recursion_depth,
            cost_budget_remaining=cost_budget_remaining,
            calls_remaining_this_conversation=calls_remaining,
        )

    # ------------------------------------------------------------------
    # Single execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        ctx: ToolContext,
    ) -> tuple[dict[str, Any], ToolResult]:
        """Execute a single tool call through the full pipeline.

        Two-phase logging:
          1. INSERT cx_tool_call with status='running' immediately
          2. UPDATE with output/error when done

        Returns ``(tool_result_content_dict, full_result)``.
        """
        started_at = time.time()

        # --- Resolve tool ---
        tool_def = self.registry.get(tool_name)
        if tool_def is None:
            vcprint(
                {
                    "tool_name": tool_name,
                    "call_id": ctx.call_id,
                    "registry_loaded": self.registry.loaded,
                    "registry_count": self.registry.count,
                    "available_tools": self.registry.list_tool_names()[:20],
                },
                f"[ToolExecutor] Tool '{tool_name}' not found in registry",
                color="red",
            )
            result = self._unknown_tool_result(tool_name, ctx.call_id, started_at)
            return result.to_tool_result_content(), result

        # --- Phase 1: log attempt (fire-and-forget INSERT) ---
        row_id = await self.execution_logger.log_started(ctx, tool_def, arguments)

        stream = ToolStreamManager(ctx.emitter, ctx.call_id, tool_name)

        # --- Guardrails ---
        guardrail_result = await self.guardrails.check(tool_name, arguments, ctx, tool_def)
        if guardrail_result.blocked:
            error_result = ToolResult(
                success=False,
                error=ToolError(
                    error_type=guardrail_result.error_type,
                    message=guardrail_result.reason or "Blocked by guardrail",
                    suggested_action=guardrail_result.suggested_action,
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_name,
                call_id=ctx.call_id,
            )
            error_result.compute_duration()
            await stream.error(guardrail_result.reason or "Blocked", guardrail_result.error_type)
            events = stream.get_events_for_persistence()
            asyncio.create_task(self.execution_logger.log_error(row_id, error_result, events))
            return error_result.to_tool_result_content(), error_result

        self.guardrails.record_call(tool_name, arguments, ctx)

        # --- Stream started (with full arguments — non-negotiable) ---
        user_message = tool_def.format_user_message(arguments)
        await stream.started(user_message, arguments=arguments)

        # Touch lifecycle
        self.lifecycle.touch(ctx.conversation_id)

        # --- Execute ---
        try:
            result = await asyncio.wait_for(
                self._dispatch(tool_def, arguments, ctx, stream),
                timeout=tool_def.timeout_seconds,
            )
        except asyncio.TimeoutError:
            result = ToolResult(
                success=False,
                error=ToolError(
                    error_type="timeout",
                    message=f"Tool '{tool_name}' timed out after {tool_def.timeout_seconds}s",
                    is_retryable=True,
                    suggested_action="Try with simpler parameters or break the task into smaller parts.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_name,
                call_id=ctx.call_id,
            )
        except Exception as exc:
            result = ToolResult(
                success=False,
                error=ToolError(
                    error_type="execution",
                    message=str(exc),
                    traceback=tb.format_exc(),
                    is_retryable=False,
                    suggested_action="Check the error details and try with different parameters.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_name,
                call_id=ctx.call_id,
            )

        result.compute_duration()

        # --- Stream completed / error (with full result — non-negotiable) ---
        if result.success:
            await stream.completed("Done", result=result)
        else:
            msg = result.error.message if result.error else "Unknown error"
            await stream.error(msg, result.error.error_type if result.error else "execution")

        # --- Phase 2: log result (fire-and-forget UPDATE) ---
        events = stream.get_events_for_persistence()
        if result.success:
            asyncio.create_task(self.execution_logger.log_completed(row_id, result, events))
        else:
            asyncio.create_task(self.execution_logger.log_error(row_id, result, events))

        return result.to_tool_result_content(), result

    # ------------------------------------------------------------------
    # Batch execution
    # ------------------------------------------------------------------

    async def execute_batch(
        self,
        tool_calls: list[dict[str, Any]],
        ctx_base: ToolContext,
    ) -> tuple[list[dict[str, Any]], list[ToolResult]]:
        """Execute multiple tool calls concurrently.

        Each item in ``tool_calls`` must have:
          - ``name``: tool name
          - ``arguments``: dict of arguments
          - ``call_id`` or ``id``: the tool call id
        """
        tasks = []
        for tc in tool_calls:
            name = tc.get("name", "")
            arguments = tc.get("arguments", {})
            call_id = tc.get("call_id") or tc.get("id") or str(uuid4())

            child_ctx = ctx_base.model_copy(update={
                "call_id": call_id,
                "tool_name": name,
            })
            tasks.append(self.execute(name, arguments, child_ctx))

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        content_results: list[dict[str, Any]] = []
        full_results: list[ToolResult] = []

        for idx, r in enumerate(raw_results):
            if isinstance(r, Exception):
                tc = tool_calls[idx]
                call_id = tc.get("call_id") or tc.get("id") or ""
                err_result = ToolResult(
                    success=False,
                    error=ToolError(
                        error_type="unhandled",
                        message=str(r),
                        traceback=tb.format_exc(),
                    ),
                    started_at=time.time(),
                    completed_at=time.time(),
                    tool_name=tc.get("name", ""),
                    call_id=call_id,
                )
                content_results.append(err_result.to_tool_result_content())
                full_results.append(err_result)
            else:
                content_dict, full_result = r
                content_results.append(content_dict)
                full_results.append(full_result)

        return content_results, full_results

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    async def _dispatch(
        self,
        tool_def: ToolDefinition,
        args: dict[str, Any],
        ctx: ToolContext,
        stream: ToolStreamManager,
    ) -> ToolResult:
        match tool_def.tool_type:
            case ToolType.LOCAL:
                return await self._execute_local(tool_def, args, ctx, stream)
            case ToolType.EXTERNAL_MCP:
                return await self._execute_external_mcp(tool_def, args, ctx)
            case ToolType.AGENT:
                return await self._execute_agent(tool_def, args, ctx)
            case _:
                return ToolResult(
                    success=False,
                    error=ToolError(
                        error_type="configuration",
                        message=f"Unknown tool type: {tool_def.tool_type}",
                    ),
                    started_at=time.time(),
                    completed_at=time.time(),
                    tool_name=tool_def.name,
                    call_id=ctx.call_id,
                )

    async def _execute_local(
        self,
        tool_def: ToolDefinition,
        args: dict[str, Any],
        ctx: ToolContext,
        stream: ToolStreamManager,
    ) -> ToolResult:
        func = tool_def._callable
        if func is None:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="configuration",
                    message=f"No callable resolved for local tool '{tool_def.name}'",
                ),
                started_at=time.time(),
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )

        started_at = time.time()
        raw_result = await func(args, ctx)

        if isinstance(raw_result, ToolResult):
            raw_result.started_at = raw_result.started_at or started_at
            raw_result.completed_at = raw_result.completed_at or time.time()
            raw_result.tool_name = raw_result.tool_name or tool_def.name
            raw_result.call_id = raw_result.call_id or ctx.call_id
            return raw_result

        # Legacy compatibility: dict with "status" / "result"
        if isinstance(raw_result, dict):
            is_error = raw_result.get("status") == "error"
            return ToolResult(
                success=not is_error,
                output=(
                    raw_result.get("result")
                    if not is_error
                    else raw_result.get("error", raw_result.get("result"))
                ),
                error=ToolError(
                    error_type="execution",
                    message=str(raw_result.get("error", raw_result.get("result", ""))),
                ) if is_error else None,
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )

        return ToolResult(
            success=True,
            output=raw_result,
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_def.name,
            call_id=ctx.call_id,
        )

    async def _execute_external_mcp(
        self,
        tool_def: ToolDefinition,
        args: dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        from tools.external_mcp import ExternalMCPClient
        client = ExternalMCPClient(timeout=tool_def.timeout_seconds)
        return await client.call_tool(tool_def, args, ctx)

    async def _execute_agent(
        self,
        tool_def: ToolDefinition,
        args: dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        from tools.agent_tool import execute_agent_tool

        child_ctx = ctx.model_copy(update={
            "recursion_depth": ctx.recursion_depth + 1,
        })
        return await execute_agent_tool(tool_def, args, child_ctx)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unknown_tool_result(tool_name: str, call_id: str, started_at: float) -> ToolResult:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Tool '{tool_name}' is not registered.",
                suggested_action="Check the tool name and try again. Use a valid tool from the available set.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_name,
            call_id=call_id,
        )

    # _persist_output is no longer needed — persist_key and output are stored
    # directly in the cx_tool_call row via the unified logger.log() call.
