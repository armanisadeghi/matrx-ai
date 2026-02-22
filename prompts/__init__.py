"""Prompt Management & Agent System.

Core components for agent-based AI interactions:
- Agent: Main class for executing prompts with variable support
- AgentCache: In-memory cache for multi-turn conversations
- SimpleSession: Session context for agent execution
- AgentVariable: Variable definition for prompt templates
- AgentConfig: Configuration container for agent initialization
- pm: PromptManagers aggregator — single access point for prompt/builtin operations
"""

__all__ = [
    "Agent",
    "AgentCache",
    "SimpleSession",
    "AgentConfig",
    "AgentVariable",
    "PromptManagers",
    "PromptType",
    "pm",
]


def __getattr__(name: str):
    if name == "Agent":
        from prompts.agent import Agent
        return Agent
    elif name == "AgentCache":
        from prompts.cache import AgentCache
        return AgentCache
    elif name == "SimpleSession":
        from prompts.session import SimpleSession
        return SimpleSession
    elif name == "AgentConfig":
        from prompts.types import AgentConfig
        return AgentConfig
    elif name == "AgentVariable":
        from prompts.variables import AgentVariable
        return AgentVariable
    elif name == "PromptManagers":
        from prompts.manager import PromptManagers
        return PromptManagers
    elif name == "PromptType":
        from prompts.manager import PromptType
        return PromptType
    elif name == "pm":
        from prompts.manager import pm
        return pm
    raise AttributeError(f"module 'prompts' has no attribute '{name}'")
