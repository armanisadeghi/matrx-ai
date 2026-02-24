from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from matrx_utils import vcprint


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    ai_model_id: str
    messages: list[dict[str, Any]]

    # Optional label for storage/tracking — server never fetches prior state from this.
    conversation_id: str | None = None

    max_iterations: int = 20
    max_retries_per_iteration: int = 2
    stream: bool = True
    debug: bool = False

    system_instruction: str | None = None
    max_output_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None

    tools: list[str] | None = None
    tool_choice: Any | None = None
    parallel_tool_calls: bool = True

    reasoning_effort: str | None = None
    reasoning_summary: str | None = None
    thinking_level: str | None = None
    include_thoughts: bool | None = None
    thinking_budget: int | None = None

    response_format: dict[str, Any] | None = None
    stop_sequences: list[str] | None = None

    internal_web_search: bool | None = None
    internal_url_context: bool | None = None

    size: str | None = None
    quality: str | None = None
    count: int = 1
    audio_voice: str | None = None
    audio_format: str | None = None

    seconds: str | None = None
    fps: int | None = None
    steps: int | None = None
    seed: int | None = None
    guidance_scale: int | None = None
    output_quality: int | None = None
    negative_prompt: str | None = None
    output_format: str | None = None
    width: int | None = None
    height: int | None = None
    frame_images: list | None = None
    reference_images: list | None = None
    disable_safety_checker: bool | None = None

    metadata: dict[str, Any] | None = None
    store: bool = True

    @field_validator("response_format", mode="before")
    @classmethod
    def coerce_response_format(cls, v: Any) -> Any:
        if isinstance(v, str):
            vcprint(
                f"[FRONTEND BUG] response_format must be a dict or null — received string: {v!r}. "
                f'Pass a proper dict like {{"type": "json_object"}} or omit it. Coercing to None.',
                color="red",
            )
            return None
        return v
