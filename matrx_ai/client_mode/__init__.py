"""
Client mode state module.

Holds the validated ClientModeConfig and an initialized ApiClient after
matrx_ai.initialize(client_mode=True, client_config=...) has been called.

All subsystems that need to behave differently in client mode import from here:

    from matrx_ai.client_mode import get_api_client, get_conversation_handler

These accessors raise RuntimeError if called before initialization, giving a
clear error instead of a confusing AttributeError deep in the call stack.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_ai.client_mode.api_client import ApiClient
    from matrx_ai.client_mode.config import ClientModeConfig, ConversationHandler

_config: ClientModeConfig | None = None
_api_client: ApiClient | None = None


def _activate(config: ClientModeConfig) -> None:
    """Called once by matrx_ai.db._setup_client_mode after validation passes."""
    global _config, _api_client
    from matrx_ai.client_mode.api_client import ApiClient

    _config = config
    _api_client = ApiClient(base_url=config.server_url)


def get_config() -> ClientModeConfig:
    if _config is None:
        raise RuntimeError(
            "matrx-ai client mode is not initialized. "
            "Call matrx_ai.initialize(client_mode=True, client_config=...) first."
        )
    return _config


def get_api_client() -> ApiClient:
    if _api_client is None:
        raise RuntimeError(
            "matrx-ai client mode is not initialized. "
            "Call matrx_ai.initialize(client_mode=True, client_config=...) first."
        )
    return _api_client


def get_conversation_handler() -> ConversationHandler:
    cfg = get_config()
    return cfg.conversation_handler


def get_jwt() -> str | None:
    """Return the current user's JWT by calling the host app's get_jwt callable."""
    cfg = get_config()
    return cfg.get_jwt()
