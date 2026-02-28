"""Replicated handle_tool_calls integration point.

This module shows exactly how the new tool system plugs into the existing
``execute_until_complete`` loop in ``ai/executor.py``.

When rolling out, the single change needed in ``ai/executor.py`` is to:
  1. Import from this module
  2. Replace the current ``handle_tool_calls`` call with ``handle_tool_calls_v2``
  3. Feature-flag it for gradual rollout

This file is self-contained — it can be tested independently.
"""

from __future__ import annotations

import logging
from typing import Any

from matrx_utils import vcprint

from config.usage_config import TokenUsage
from .guardrails import GuardrailEngine
from .lifecycle import ToolLifecycleManager
from .logger import ToolExecutionLogger
from .models import ToolContext
from .registry import ToolRegistryV2
from .executor import ToolExecutor

logger = logging.getLogger(__name__)

# Module-level singleton — initialized once at app startup
_executor: ToolExecutor | None = None


def get_executor() -> ToolExecutor:
    global _executor
    if _executor is None:
        registry = ToolRegistryV2.get_instance()
        if not registry.loaded:
            vcprint(
                "[Tool System] Creating executor but registry was never initialized. "
                "Did initialize_tool_system() run at startup?",
                color="red",
            )
        elif registry.count == 0:
            vcprint(
                "[Tool System] Creating executor but registry has 0 tools loaded.",
                color="red",
            )
        _executor = ToolExecutor(
            registry=registry,
            guardrails=GuardrailEngine(),
            execution_logger=ToolExecutionLogger(),
            lifecycle=ToolLifecycleManager.get_instance(),
        )
    return _executor


async def initialize_tool_system() -> int:
    """Call once at app startup to load tools from the database (async).

    Returns the number of tools loaded.
    """
    registry = ToolRegistryV2.get_instance()
    count = await registry.load_from_database()

    if count == 0:
        vcprint(
            "[Tool System] WARNING: 0 tools loaded from database. "
            "Tool calls will fail. Check the 'tools' table and is_active flags.",
            color="red",
        )
    else:
        vcprint(f"[Tool System] Initialized: {count} tools loaded", color="green")

    get_executor()

    lifecycle = ToolLifecycleManager.get_instance()
    lifecycle.start_background_sweep()

    return count


def initialize_tool_system_sync() -> int:
    """Call once at app startup to load tools from the database (sync).

    Use this when the caller does not have an active event loop
    (e.g. module-level code in asgi.py).
    """
    registry = ToolRegistryV2.get_instance()
    count = registry.load_from_database_sync()

    if count == 0:
        vcprint(
            "[Tool System] WARNING: 0 tools loaded from database. "
            "Tool calls will fail. Check the 'tools' table and is_active flags.",
            color="red",
        )
    else:
        vcprint(
            f"[Tool System] Initialized (sync): {count} tools loaded", color="green"
        )

    get_executor()

    return count


async def handle_tool_calls_v2(
    tool_calls_raw: list[dict[str, Any]],
    *,
    iteration: int,
    recursion_depth: int = 0,
    cost_budget_remaining: float | None = None,
) -> tuple[list[dict[str, Any]], list["TokenUsage"]]:
    """Execute tool calls using the current ExecutionContext.

    All user/emitter/project context is read from the ContextVar.

    Returns
    -------
    (content_results, child_token_usages)
        - content_results: list of dicts matching ToolResultContent fields
        - child_token_usages: list of TokenUsage objects from child agent executions
    """
    executor = get_executor()

    lifecycle = ToolLifecycleManager.get_instance()
    if not lifecycle.sweep_running:
        lifecycle.start_background_sweep()

    ctx = ToolContext(
        call_id="",
        tool_name="",
        iteration=iteration,
        recursion_depth=recursion_depth,
        cost_budget_remaining=cost_budget_remaining,
    )

    content_results, full_results = await executor.execute_batch(tool_calls_raw, ctx)

    all_child_usages: list[TokenUsage] = []
    for result in full_results:
        all_child_usages.extend(result.child_usages)

    return content_results, all_child_usages


async def cleanup_conversation(conversation_id: str) -> None:
    """Call when a conversation ends to clean up resources."""
    lifecycle = ToolLifecycleManager.get_instance()
    await lifecycle.cleanup_conversation(conversation_id)

    guardrails = get_executor().guardrails
    guardrails.clear_conversation(conversation_id)
