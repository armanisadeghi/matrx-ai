"""Single source of truth for all LLM configuration parameters.

Every overridable LLM parameter is declared here exactly once. This model is
used by:
  - API request models (config_overrides, ChatRequest inheritance)
  - UnifiedConfig.apply_overrides() for runtime application
  - TypeScript type generation (auto-generated via OpenAPI → openapi-typescript)

When you add a new provider parameter, add it HERE and it propagates
everywhere — Python API validation, TypeScript types, and drift-detection
tests.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator


_DEPRECATED_ALIASES = {
    "max_tokens": "max_output_tokens",
    "n": "count",
}


class LLMParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _remap_deprecated(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        for old_name, new_name in _DEPRECATED_ALIASES.items():
            if old_name in data:
                if new_name not in data or data[new_name] is None:
                    data[new_name] = data.pop(old_name)
                else:
                    data.pop(old_name)
        return data

    model: str | None = None

    max_output_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None

    tool_choice: Literal["none", "auto", "required"] | None = None
    parallel_tool_calls: bool | None = None

    # OpenAI thinking
    reasoning_effort: Literal["auto", "none", "minimal", "low", "medium", "high", "xhigh"] | None = None
    reasoning_summary: Literal["concise", "detailed", "never", "auto", "always"] | None = None

    # Google Gemini thinking
    thinking_level: Literal["minimal", "low", "medium", "high"] | None = None
    include_thoughts: bool | None = None

    # Anthropic thinking & legacy Gemini thinking
    thinking_budget: int | None = None

    # Cerebras-specific thinking controls
    # clear_thinking: remove <thinking> blocks from the final response (Cerebras only)
    # disable_reasoning: when True, suppress reasoning entirely (maps to reasoning_effort="none" on unified side)
    clear_thinking: bool | None = None
    disable_reasoning: bool | None = None

    response_format: dict[str, Any] | None = None
    stop_sequences: list[str] | None = None
    stream: bool | None = None
    store: bool | None = None
    verbosity: str | None = None

    # Provider features
    internal_web_search: bool | None = None
    internal_url_context: bool | None = None

    # Image generation
    size: str | None = None
    quality: str | None = None
    count: int | None = None

    # Audio / TTS
    tts_voice: str | list[dict[str, str]] | None = None
    audio_format: str | None = None

    # Video generation
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
    image_loras: list | None = None
    disable_safety_checker: bool | None = None
