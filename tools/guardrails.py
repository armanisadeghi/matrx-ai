from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass

from tools.models import GuardrailResult, ToolContext, ToolDefinition, ToolType

logger = logging.getLogger(__name__)

# Type alias for a tool call coming from unified config
ToolCallLike = dict  # Must have "name" and "arguments" keys at minimum


@dataclass
class _CallRecord:
    tool_name: str
    args_hash: str
    timestamp: float
    iteration: int


class GuardrailEngine:
    """Centralized guardrails that run before every tool execution.

    Checks:
      1. Duplicate detection — identical call within recent history
      2. Rate limiting — max calls per minute per tool
      3. Conversation limit — max total calls per tool per conversation
      4. Cost budget — remaining budget vs estimated cost
      5. Loop detection — same tool called with similar args repeatedly
      6. Recursion depth — prevent runaway agent-in-agent chains
    """

    def __init__(self) -> None:
        # conversation_id → list[_CallRecord]
        self._history: dict[str, list[_CallRecord]] = defaultdict(list)

    async def check(
        self,
        tool_name: str,
        arguments: dict,
        ctx: ToolContext,
        tool_def: ToolDefinition,
    ) -> GuardrailResult:
        checks = [
            self._check_duplicate(tool_name, arguments, ctx),
            self._check_rate_limit(tool_name, ctx, tool_def),
            self._check_conversation_limit(tool_name, ctx, tool_def),
            self._check_cost_budget(ctx, tool_def),
            self._check_loop_detection(tool_name, arguments, ctx),
            self._check_recursion_depth(ctx, tool_def),
        ]
        for check in checks:
            if check.blocked:
                return check
        return GuardrailResult(blocked=False)

    def record_call(self, tool_name: str, arguments: dict, ctx: ToolContext) -> None:
        self._history[ctx.conversation_id].append(
            _CallRecord(
                tool_name=tool_name,
                args_hash=self._hash_args(arguments),
                timestamp=time.time(),
                iteration=ctx.iteration,
            )
        )

    def clear_conversation(self, conversation_id: str) -> None:
        self._history.pop(conversation_id, None)

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_duplicate(
        self,
        tool_name: str,
        arguments: dict,
        ctx: ToolContext,
    ) -> GuardrailResult:
        records = self._history.get(ctx.conversation_id, [])
        current_hash = self._hash_args(arguments)

        for rec in reversed(records[-5:]):
            if rec.tool_name == tool_name and rec.args_hash == current_hash:
                return GuardrailResult(
                    blocked=True,
                    reason=f"Exact duplicate call to '{tool_name}' with identical arguments was already made.",
                    error_type="duplicate",
                    suggested_action="Use different parameters or try a different approach.",
                )
        return GuardrailResult(blocked=False)

    def _check_rate_limit(
        self,
        tool_name: str,
        ctx: ToolContext,
        tool_def: ToolDefinition,
    ) -> GuardrailResult:
        if tool_def.max_calls_per_minute is None:
            return GuardrailResult(blocked=False)

        window_start = time.time() - 60
        records = self._history.get(ctx.conversation_id, [])
        recent = [
            r
            for r in records
            if r.tool_name == tool_name and r.timestamp >= window_start
        ]

        if len(recent) >= tool_def.max_calls_per_minute:
            return GuardrailResult(
                blocked=True,
                reason=f"Rate limit exceeded: '{tool_name}' called {len(recent)} times in the last minute (max {tool_def.max_calls_per_minute}).",
                error_type="rate_limit",
                suggested_action="Wait before calling this tool again, or use a different approach.",
            )
        return GuardrailResult(blocked=False)

    def _check_conversation_limit(
        self,
        tool_name: str,
        ctx: ToolContext,
        tool_def: ToolDefinition,
    ) -> GuardrailResult:
        if tool_def.max_calls_per_conversation is None:
            return GuardrailResult(blocked=False)

        records = self._history.get(ctx.conversation_id, [])
        total = sum(1 for r in records if r.tool_name == tool_name)

        if total >= tool_def.max_calls_per_conversation:
            return GuardrailResult(
                blocked=True,
                reason=f"Conversation limit reached: '{tool_name}' already called {total} times (max {tool_def.max_calls_per_conversation}).",
                error_type="conversation_limit",
                suggested_action="You have used this tool the maximum number of times in this conversation. Try a different approach.",
            )
        return GuardrailResult(blocked=False)

    def _check_cost_budget(
        self,
        ctx: ToolContext,
        tool_def: ToolDefinition,
    ) -> GuardrailResult:
        if ctx.cost_budget_remaining is not None and ctx.cost_budget_remaining <= 0:
            return GuardrailResult(
                blocked=True,
                reason="Cost budget exhausted for this conversation.",
                error_type="cost_budget",
                suggested_action="Inform the user that the cost budget has been reached.",
            )

        if tool_def.cost_cap_per_call is not None:
            if (
                ctx.cost_budget_remaining is not None
                and tool_def.cost_cap_per_call > ctx.cost_budget_remaining
            ):
                return GuardrailResult(
                    blocked=True,
                    reason=(
                        f"Estimated cost for '{tool_def.name}' (${tool_def.cost_cap_per_call:.2f}) "
                        f"exceeds remaining budget (${ctx.cost_budget_remaining:.2f})."
                    ),
                    error_type="cost_budget",
                    suggested_action="Use a less expensive tool or inform the user.",
                )
        return GuardrailResult(blocked=False)

    def _check_loop_detection(
        self,
        tool_name: str,
        arguments: dict,
        ctx: ToolContext,
    ) -> GuardrailResult:
        records = self._history.get(ctx.conversation_id, [])
        recent_same = [r for r in records[-10:] if r.tool_name == tool_name]

        if len(recent_same) < 3:
            return GuardrailResult(blocked=False)

        current_hash = self._hash_args(arguments)
        similar_count = sum(
            1 for r in recent_same if self._similarity(r.args_hash, current_hash) > 0.8
        )

        if similar_count >= 3:
            return GuardrailResult(
                blocked=True,
                reason=(
                    f"Loop detected: '{tool_name}' has been called {similar_count} times recently "
                    f"with very similar arguments. This appears to be a loop."
                ),
                error_type="loop_detected",
                suggested_action=(
                    "You seem to be calling this tool repeatedly with similar parameters. "
                    "Please try a fundamentally different approach or provide a final answer."
                ),
            )
        return GuardrailResult(blocked=False)

    def _check_recursion_depth(
        self,
        ctx: ToolContext,
        tool_def: ToolDefinition,
    ) -> GuardrailResult:
        if tool_def.tool_type == ToolType.AGENT:
            max_depth = tool_def.max_recursion_depth
            if ctx.recursion_depth >= max_depth:
                return GuardrailResult(
                    blocked=True,
                    reason=(
                        f"Maximum agent recursion depth ({max_depth}) reached. "
                        f"Current depth: {ctx.recursion_depth}."
                    ),
                    error_type="recursion_depth",
                    suggested_action="Agent tools cannot spawn further agent tools at this depth. Use direct tools instead.",
                )
        return GuardrailResult(blocked=False)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_args(arguments: dict) -> str:
        normalized = json.dumps(arguments, sort_keys=True, default=str)
        return hashlib.md5(normalized.encode()).hexdigest()

    @staticmethod
    def _similarity(hash_a: str, hash_b: str) -> float:
        if hash_a == hash_b:
            return 1.0
        matching = sum(a == b for a, b in zip(hash_a, hash_b))
        return matching / max(len(hash_a), len(hash_b))
