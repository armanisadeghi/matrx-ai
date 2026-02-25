from __future__ import annotations

import logging
import time
from typing import Any
from uuid import uuid4

from tools.models import ToolContext, ToolDefinition, ToolError, ToolResult, ToolType

logger = logging.getLogger(__name__)


async def execute_agent_tool(
    tool_def: ToolDefinition,
    args: dict[str, Any],
    ctx: ToolContext,
) -> ToolResult:
    """Execute an agent prompt as a tool call.

    Forks the current ExecutionContext for the child agent so it inherits
    user identity, emitter, and project scope automatically.
    """
    started_at = time.time()

    if not tool_def.prompt_id:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="configuration",
                message=f"Agent tool '{tool_def.name}' has no prompt_id configured.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_def.name,
            call_id=ctx.call_id,
        )

    try:
        from context.app_context import get_app_context, set_app_context as set_execution_context, clear_app_context as clear_execution_context
        from prompts.session import SimpleSession
        from prompts.agent import Agent
    except ImportError as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="import",
                message=f"Cannot import agent modules: {exc}",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_def.name,
            call_id=ctx.call_id,
        )

    child_conversation_id = str(uuid4())
    child_ctx = get_app_context().fork_for_child_agent(child_conversation_id)
    token = set_execution_context(child_ctx)

    try:
        child_session = SimpleSession(conversation_id=child_conversation_id)

        agent = await Agent.from_prompt(
            tool_def.prompt_id,
            session=child_session,
            variables=args.get("variables"),
        )

        user_input = (
            args.get("input")
            or args.get("user_input")
            or args.get("query")
            or args.get("task")
            or ""
        )
        result = await agent.execute(user_input=user_input)

        return ToolResult(
            success=True,
            output=result.output,
            child_usages=list(result.usage_history),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_def.name,
            call_id=ctx.call_id,
        )

    except Exception as exc:
        import traceback as tb
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="agent_execution",
                message=f"Agent '{tool_def.prompt_id}' failed: {exc}",
                traceback=tb.format_exc(),
                is_retryable=False,
                suggested_action="Check the agent prompt configuration and input parameters.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_def.name,
            call_id=ctx.call_id,
        )
    finally:
        clear_execution_context(token)


async def register_agent_as_tool(
    prompt_id: str,
    tool_name: str,
    description: str,
    input_schema: dict[str, Any] | None = None,
    max_calls_per_conversation: int = 5,
    cost_cap_per_call: float = 1.0,
    timeout_seconds: float = 300.0,
) -> ToolDefinition:
    default_schema: dict[str, Any] = {
        "input": {
            "type": "string",
            "description": "The input/query to send to the agent",
            "required": True,
        },
    }

    return ToolDefinition(
        name=tool_name,
        description=description,
        parameters=input_schema or default_schema,
        tool_type=ToolType.AGENT,
        function_path=f"agent:{prompt_id}",
        prompt_id=prompt_id,
        max_calls_per_conversation=max_calls_per_conversation,
        cost_cap_per_call=cost_cap_per_call,
        timeout_seconds=timeout_seconds,
        max_recursion_depth=2,
    )
