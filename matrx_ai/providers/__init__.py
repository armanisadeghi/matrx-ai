"""
AI Providers Module

Provider-specific API implementations for different AI services:
- OpenAIChat: OpenAI API (GPT-4, GPT-3.5, etc.)
- AnthropicChat: Anthropic API (Claude models)
- GoogleChat: Google AI API (Gemini models)
- TogetherChat: Together AI API
- GroqChat: Groq API
- XAIChat: xAI API (Grok models)
- CerebrasChat: Cerebras API
- UnifiedAIClient: Unified client that routes to the appropriate provider
- RetryableError, classify_provider_error: Error handling for provider APIs

Imports are lazy so that importing individual providers (e.g. errors) does not
trigger the DB singleton instantiation inside unified_client.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .anthropic import AnthropicChat, AnthropicTranslator
    from .cerebras import CerebrasChat, CerebrasTranslator
    from .errors import (
        RetryableError,
        classify_anthropic_error,
        classify_google_error,
        classify_openai_error,
        classify_provider_error,
    )
    from .google import GoogleChat, GoogleProviderConfig, GoogleTranslator
    from .groq import GroqChat, GroqTranslator
    from .openai import OpenAIChat, OpenAITranslator
    from .together import TogetherChat, TogetherTranslator
    from .unified_client import UnifiedAIClient
    from .xai import XAIChat, XAITranslator

__all__ = [
    "AnthropicChat",
    "AnthropicTranslator",
    "CerebrasChat",
    "CerebrasTranslator",
    "GoogleChat",
    "GoogleProviderConfig",
    "GoogleTranslator",
    "GroqChat",
    "GroqTranslator",
    "OpenAIChat",
    "OpenAITranslator",
    "RetryableError",
    "TogetherChat",
    "TogetherTranslator",
    "UnifiedAIClient",
    "XAIChat",
    "XAITranslator",
    "classify_anthropic_error",
    "classify_google_error",
    "classify_openai_error",
    "classify_provider_error",
]

_module_map: dict[str, str] = {
    "AnthropicChat": ".anthropic",
    "AnthropicTranslator": ".anthropic",
    "CerebrasChat": ".cerebras",
    "CerebrasTranslator": ".cerebras",
    "RetryableError": ".errors",
    "classify_anthropic_error": ".errors",
    "classify_google_error": ".errors",
    "classify_openai_error": ".errors",
    "classify_provider_error": ".errors",
    "GoogleChat": ".google",
    "GoogleProviderConfig": ".google",
    "GoogleTranslator": ".google",
    "GroqChat": ".groq",
    "GroqTranslator": ".groq",
    "OpenAIChat": ".openai",
    "OpenAITranslator": ".openai",
    "TogetherChat": ".together",
    "TogetherTranslator": ".together",
    "UnifiedAIClient": ".unified_client",
    "XAIChat": ".xai",
    "XAITranslator": ".xai",
}


def __getattr__(name: str) -> object:
    if name in _module_map:
        import importlib

        mod = importlib.import_module(_module_map[name], package=__name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
