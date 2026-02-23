"""
Conversation router.

  POST /api/ai/conversations/{conversation_id}       — continue an existing conversation
  POST /api/ai/conversations/{conversation_id}/warm   — pre-warm conversation cache
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Path
from fastapi.responses import ORJSONResponse

from app.core.streaming import make_ndjson_response
from app.models.conversation import ConversationContinueRequest

router = APIRouter(prefix="/api/ai/conversations", tags=["conversation"])


@router.post("/{conversation_id}")
async def continue_conversation(
    conversation_id: str = Path(..., description="Existing conversation ID"),
    body: ConversationContinueRequest = ...,
) -> Any:
    """Continue an existing conversation. Only user_input is needed."""
    stream = _mock_conversation_stream(conversation_id, body)

    async def _to_ndjson() -> AsyncGenerator[dict[str, Any]]:
        async for chunk in stream:
            yield chunk

    return make_ndjson_response(_to_ndjson())


@router.post("/{conversation_id}/warm")
async def warm_conversation(
    conversation_id: str = Path(..., description="Conversation ID to pre-warm"),
) -> ORJSONResponse:
    """Pre-warm the conversation so it's cached for the next message."""
    # TODO: wire real cache-warming logic here
    return ORJSONResponse({"status": "ok", "conversation_id": conversation_id})


# ---------------------------------------------------------------------------
# Stand-in implementation — replace with your real conversation engine
# ---------------------------------------------------------------------------


async def _mock_conversation_stream(
    conversation_id: str,
    body: ConversationContinueRequest,
) -> AsyncGenerator[dict[str, Any]]:
    """
    Placeholder conversation continuation.
    Replace with your real conversation engine.
    """
    reply = f"Continuing conversation {conversation_id}: received '{body.user_input}'"
    for word in reply.split():
        await asyncio.sleep(0.05)
        yield {"event": "chunk", "data": {"text": word + " "}}
    yield {"event": "done", "data": {"message": "Complete"}}
