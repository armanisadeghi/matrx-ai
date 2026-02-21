from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Role(StrEnum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class Message(BaseModel):
    role: Role
    content: str
    name: str | None = None
    tool_call_id: str | None = None


class StreamMode(StrEnum):
    sse = "sse"
    ndjson = "ndjson"


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)
    model: str = "gpt-4o"
    provider: str = "openai"
    stream: bool = True
    stream_mode: StreamMode = StreamMode.sse
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    system_prompt: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatChunk(BaseModel):
    text: str
    index: int = 0
    finish_reason: str | None = None


class ChatResponse(BaseModel):
    id: str
    model: str
    provider: str
    content: str
    usage: dict[str, int] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
