"""
AI Agents Module

Core components for agent-based AI interactions:
- Agent: Main class for executing prompts with variable support
- AgentCache: In-memory cache for multi-turn conversations
- AgentVariable: Variable definition for prompt templates
- AgentConfig: Configuration container for agent initialization
- AgentExecuteResult: Return type from Agent.execute()
- ConversationResolver: Resolves UnifiedConfig from conversation_id
- AgentConfigResolver: Resolves UnifiedConfig from agent/prompt id
- pm: PromptManagers aggregator — single access point for prompt/builtin operations

Usage:
    from agents import Agent, pm
    from agents import ConversationResolver, AgentConfigResolver
"""

__all__ = [
    "Agent",
    "AgentCache",
    "AgentConfig",
    "AgentConfigResolver",
    "AgentExecuteResult",
    "AgentVariable",
    "ConversationResolver",
    "PromptManagers",
    "PromptType",
    "pm",
]

def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "Agent":
        from agents.definition import Agent

        return Agent
    elif name == "AgentCache":
        from agents.cache import AgentCache

        return AgentCache
    elif name == "AgentConfig":
        from agents.types import AgentConfig

        return AgentConfig
    elif name == "AgentConfigResolver":
        from agents.resolver import AgentConfigResolver

        return AgentConfigResolver
    elif name == "AgentExecuteResult":
        from agents.definition import AgentExecuteResult

        return AgentExecuteResult
    elif name == "AgentVariable":
        from agents.variables import AgentVariable

        return AgentVariable
    elif name == "ConversationResolver":
        from agents.resolver import ConversationResolver

        return ConversationResolver
    elif name == "PromptManagers":
        from agents.manager import PromptManagers

        return PromptManagers
    elif name == "PromptType":
        from agents.manager import PromptType

        return PromptType
    elif name == "pm":
        from agents.manager import pm

        return pm
    raise AttributeError(f"module 'ai.agents' has no attribute '{name}'")

