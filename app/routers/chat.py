"""
Chat router — streaming-first LLM completions.

  POST /api/ai/chat — one-shot or managed chat

Both SSE and NDJSON modes are supported. The mock generator here is a
stand-in for your real provider integrations; replace `_mock_stream` with
calls to your ORM / provider layer when you wire those in.
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from app.core.streaming import make_ndjson_response, make_sse_response, text_chunks_to_sse
from app.models.chat import ChatRequest, ChatResponse, StreamMode

router = APIRouter(prefix="/api/ai", tags=["chat"])


@router.post("/chat")
async def chat(request: Request, body: ChatRequest) -> Any:
    if not body.stream:
        return await _chat_blocking(body)

    stream = _mock_stream(body)

    if body.stream_mode == StreamMode.sse:
        sse_source = text_chunks_to_sse(stream)
        return make_sse_response(sse_source)

    async def _dict_stream() -> AsyncGenerator[dict[str, Any]]:
        async for text in _mock_stream(body):
            yield {"text": text, "done": False}
        yield {"text": "", "done": True}

    return make_ndjson_response(_dict_stream())


async def _chat_blocking(body: ChatRequest) -> ORJSONResponse:
    chunks: list[str] = []
    async for text in _mock_stream(body):
        chunks.append(text)
    content = "".join(chunks)
    response = ChatResponse(
        id=str(uuid.uuid4()),
        model=body.model,
        provider=body.provider,
        content=content,
        usage={"prompt_tokens": 0, "completion_tokens": len(content.split()), "total_tokens": 0},
    )
    return ORJSONResponse(response.model_dump())


# ---------------------------------------------------------------------------
# Replace this with your real provider call
# ---------------------------------------------------------------------------


async def _mock_stream(body: ChatRequest) -> AsyncGenerator[str]:
    """
    Placeholder: yields word-by-word from a canned response.
    Wire in your actual provider SDK calls here.
    """
    last_user_msg = next(
        (m.content for m in reversed(body.messages) if m.role == "user"),
        "Hello",
    )
    reply = f"[{body.provider}/{body.model}] Received: {last_user_msg!r}"
    for word in reply.split():
        await asyncio.sleep(0.05)
        yield word + " "
