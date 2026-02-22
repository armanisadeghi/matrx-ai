"""Unified AI Configuration & Types.

Core configuration types for AI requests:
- UnifiedConfig: Configuration dataclass for AI requests
- UnifiedMessage: Message representation across providers
- MessageList: Container for conversation messages
- UnifiedResponse: Standardized response from AI providers
- Role, ContentType, Provider, FinishReason: Enums
"""

__all__ = [
    "UnifiedConfig",
    "UnifiedMessage",
    "MessageList",
    "UnifiedResponse",
    "Role",
    "ContentType",
    "Provider",
    "FinishReason",
]


def __getattr__(name: str):
    if name in ("UnifiedConfig", "UnifiedMessage", "MessageList", "UnifiedResponse",
                "Role", "ContentType", "Provider", "FinishReason"):
        from config import unified_config
        return getattr(unified_config, name)
    raise AttributeError(f"module 'config' has no attribute '{name}'")
