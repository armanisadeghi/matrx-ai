from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(StrEnum):
    idle = "idle"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"


class AgentStartRequest(BaseModel):
    """Body for POST /api/ai/agents/{agent_id} — start a new agent conversation."""
    user_input: str | list[dict[str, Any]] | None = None
    variables: dict[str, Any] | None = None
    config_overrides: dict[str, Any] | None = None
    stream: bool = True
    debug: bool = False


class AgentInfo(BaseModel):
    agent_id: str
    status: AgentStatus
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)
