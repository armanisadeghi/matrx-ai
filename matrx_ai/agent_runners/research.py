from __future__ import annotations

from typing import Any
from uuid import uuid4

from matrx_utils import vcprint
from pydantic import BaseModel, Field

from matrx_ai.agents.definition import Agent
from matrx_ai.config.usage_config import TokenUsage
from matrx_ai.context.app_context import (
    clear_app_context as clear_execution_context,
)
from matrx_ai.context.app_context import (
    get_app_context,
)
from matrx_ai.context.app_context import (
    set_app_context as set_execution_context,
)
from matrx_ai.tools.models import ToolContext


class AgentResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    success: bool
    output: str = ""
    usage: dict[str, Any] = Field(default_factory=dict)
    usage_history: list[TokenUsage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


async def scrape_research_condenser_agent_1(
    instructions: str,
    scraped_content: str,
    queries: str,
    search_results: str,
    ctx: ToolContext,
) -> AgentResult:
    child_ctx = get_app_context().fork_for_child_agent(str(uuid4()))
    token = set_execution_context(child_ctx)
    try:
        agent = await Agent.from_prompt("a5f65b49-f0fa-4d0d-a7ce-e200237ab1b6")
        agent.set_variable("instructions", instructions)
        agent.set_variable("scraped_content", scraped_content)
        agent.set_variable("queries", queries)
        agent.set_variable("search_results", search_results)

        result = await agent.execute()

        vcprint(result.usage, title="[research_condenser_1] Usage", color="pink")

        return AgentResult(
            success=True,
            output=result.output,
            usage=result.usage.to_dict(),
            usage_history=list(result.usage_history),
            metadata=result.metadata,
        )
    except Exception as e:
        vcprint(f"Research condenser agent_1 failed: {e}", color="red")
        return AgentResult(success=False, output=f"Agent failed: {e}")
    finally:
        clear_execution_context(token)


async def scrape_research_condenser_agent_2(
    instructions: str,
    scraped_content: str,
    queries: str,
    search_results: str,
    ctx: ToolContext,
) -> AgentResult:
    child_ctx = get_app_context().fork_for_child_agent(str(uuid4()))
    token = set_execution_context(child_ctx)
    try:
        agent = await Agent.from_prompt("048fb140-8ba4-4a5a-b290-2e657c3785e9")
        agent.set_variable("instructions", instructions)
        agent.set_variable("scraped_content", scraped_content)
        agent.set_variable("queries", queries)
        agent.set_variable("search_results", search_results)

        result = await agent.execute()

        vcprint(result.usage, title="[research_condenser_2] Usage", color="pink")

        return AgentResult(
            success=True,
            output=result.output,
            usage=result.usage.to_dict(),
            usage_history=list(result.usage_history),
            metadata=result.metadata,
        )
    except Exception as e:
        vcprint(f"Research condenser agent_2 failed: {e}", color="red")
        return AgentResult(success=False, output=f"Agent failed: {e}")
    finally:
        clear_execution_context(token)
