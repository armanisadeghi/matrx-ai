from typing import Any

from pydantic import BaseModel


class ConversationContinueRequest(BaseModel):
    """Body for POST /api/ai/conversations/{conversation_id}"""
    user_input: str | list[dict[str, Any]]
    config_overrides: dict[str, Any] | None = None
    stream: bool = True
    debug: bool = False
