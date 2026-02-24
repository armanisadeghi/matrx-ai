from __future__ import annotations

import traceback
from typing import TYPE_CHECKING
from uuid import uuid4

from matrx_utils import vcprint

from tools.models import ToolContext

if TYPE_CHECKING:
    from config.unified_config import TokenUsage


async def summarize_content(
    content: str,
    instructions: str,
    ctx: ToolContext,
    model_id: str = "gemini-2.5-flash-preview-05-20",
) -> tuple[str, list[TokenUsage]]:
    """Summarize content using the unified AI system.

    Returns ``(summary_text, usage_history)``.
    """
    try:
        from context.app_context import get_app_context, set_app_context, clear_app_context
        from prompts.agent import Agent
        from prompts.session import SimpleSession

        child_ctx = get_app_context().fork_for_child_agent(str(uuid4()))
        token = set_app_context(child_ctx)

        try:
            from config.unified_config import UnifiedConfig

            session = SimpleSession(conversation_id=child_ctx.conversation_id)

            config = UnifiedConfig.from_dict({
                "model": model_id,
                "system_instruction": (
                    "You are a summarization assistant. Summarize the provided content "
                    "following the user's instructions precisely. Be concise and accurate."
                ),
                "messages": [],
            })
            agent = Agent(config=config)
            agent.set_session(session)

            prompt = f"Instructions: {instructions}\n\nContent to summarize:\n{content[:100000]}"
            result = await agent.execute(user_input=prompt)

            return result.output, list(result.usage_history)
        finally:
            clear_app_context(token)

    except ImportError:
        vcprint("Agent modules not available; returning raw content truncated", "[summarize_content] ImportError", color="red")
        return content[:2000], []
    except Exception as exc:
        vcprint(f"Summarization failed: {exc}\n{traceback.format_exc()}", "[summarize_content] Unhandled exception", color="red")
        return f"[Summarization failed: {exc}]", []
