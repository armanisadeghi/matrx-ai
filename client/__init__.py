"""Unified AI Client & Execution Engine.

Core Components:
- UnifiedConfig: Configuration dataclass for AI requests
- UnifiedAIClient: Main client for executing AI requests
- AIMatrixRequest: Request container with tracking
- CompletedRequest: Result of autonomous execution
- execute_until_complete: Main execution loop

Usage:
    from client.unified_client import UnifiedAIClient, AIMatrixRequest
    from client.ai_requests import execute_until_complete
"""

__all__ = [
    "UnifiedAIClient",
    "AIMatrixRequest",
    "CompletedRequest",
    "execute_until_complete",
    "TokenUsage",
    "TimingUsage",
    "ToolCallUsage",
]


def __getattr__(name: str):
    if name in ("UnifiedAIClient", "AIMatrixRequest", "CompletedRequest"):
        from client import unified_client
        return getattr(unified_client, name)
    elif name == "execute_until_complete":
        from client.ai_requests import execute_until_complete
        return execute_until_complete
    elif name == "TokenUsage":
        from client.usage import TokenUsage
        return TokenUsage
    elif name == "TimingUsage":
        from client.timing import TimingUsage
        return TimingUsage
    elif name == "ToolCallUsage":
        from client.tool_call_tracking import ToolCallUsage
        return ToolCallUsage
    raise AttributeError(f"module 'client' has no attribute '{name}'")
