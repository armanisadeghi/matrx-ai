from typing import Any

from matrx_utils import vcprint

from config import (
    FinishReason,
    ThinkingConfig,
    TokenUsage,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
)
from tools.registry import ToolRegistryV2

# ============================================================================
# ANTHROPIC TRANSLATOR
# ============================================================================


class AnthropicTranslator:
    """Translates between unified format and Anthropic Messages API"""

    def to_anthropic(
        self, config: UnifiedConfig, api_class: str = "anthropic_standard"
    ) -> dict[str, Any]:
        """
        Convert unified config to Anthropic Messages API format.

        System instruction comes from config.system_instruction field.
        Delegates message conversion to UnifiedMessage.to_anthropic_blocks().

        Note: Anthropic only supports "user" and "assistant" roles.
        Tool results (role="tool") are converted to role="user".

        api_class controls which thinking path is used:
          - "anthropic_standard" / "anthropic": extended thinking (budget_tokens)
          - "anthropic_adaptive": adaptive thinking (placeholder — currently identical
            to standard; update when Anthropic stabilises the adaptive API surface)
        """
        messages = []

        for msg in config.messages:
            message_content = msg.to_anthropic_blocks()

            if message_content:
                role = "user" if msg.role == "tool" else msg.role
                messages.append({"role": role, "content": message_content})

        anthropic_request = {
            "model": config.model,
            "messages": messages,
        }

        if config.system_instruction:
            anthropic_request["system"] = config.system_instruction

        if config.tools:
            anthropic_request["tools"] = (
                ToolRegistryV2.get_instance().get_provider_tools(
                    config.tools, "anthropic"
                )
            )

        # Temperature / top_p mutual exclusion: Anthropic returns an error if both
        # are set on claude-opus-4-6 / claude-sonnet-4-6 (anthropic_adaptive models).
        # For safety, apply the guard on all Anthropic calls — temperature takes priority.
        if config.temperature is not None and config.top_p is not None:
            vcprint(
                f"⚠️  Anthropic requires temperature OR top_p, not both. "
                f"Dropping top_p={config.top_p} and keeping temperature={config.temperature}.",
                color="yellow",
            )
            anthropic_request["temperature"] = config.temperature
        elif config.temperature is not None:
            anthropic_request["temperature"] = config.temperature
        elif config.top_p is not None:
            anthropic_request["top_p"] = config.top_p

        if config.top_k is not None:
            anthropic_request["top_k"] = config.top_k

        if config.tool_choice:
            if config.tool_choice == "auto":
                anthropic_request["tool_choice"] = {"type": "auto"}
            elif config.tool_choice == "required":
                anthropic_request["tool_choice"] = {"type": "any"}
            elif config.tool_choice == "none":
                anthropic_request["tool_choice"] = {"type": "none"}

        thinking = ThinkingConfig.from_settings(config)
        if thinking:
            if api_class == "anthropic_adaptive":
                thinking_result = thinking.to_anthropic_adaptive_thinking(
                    current_max_tokens=config.max_output_tokens
                )
                if thinking_result:
                    anthropic_request["thinking"] = thinking_result["thinking"]
                    anthropic_request["output_config"] = thinking_result[
                        "output_config"
                    ]
                    anthropic_request["max_tokens"] = thinking_result["max_tokens"]
                else:
                    anthropic_request["max_tokens"] = (
                        config.max_output_tokens
                        if config.max_output_tokens is not None
                        else 8000
                    )
            else:
                thinking_result = thinking.to_anthropic_thinking(
                    current_max_tokens=config.max_output_tokens
                )
                if thinking_result:
                    anthropic_request["thinking"] = thinking_result["thinking"]
                    anthropic_request["max_tokens"] = thinking_result["max_tokens"]
                else:
                    anthropic_request["max_tokens"] = (
                        config.max_output_tokens
                        if config.max_output_tokens is not None
                        else 8000
                    )
        else:
            anthropic_request["max_tokens"] = (
                config.max_output_tokens
                if config.max_output_tokens is not None
                else 8000
            )

        return anthropic_request

    def from_anthropic(
        self, response: dict[str, Any], matrx_model_name: str
    ) -> UnifiedResponse:
        """Convert Anthropic Messages API response to unified format"""

        message_id = response.get("id")

        message = UnifiedMessage.from_anthropic_content(
            role=response.get("role"),
            content=response.get("content", []),
            id=message_id,
        )

        # Convert usage to TokenUsage if present
        token_usage = TokenUsage.from_anthropic(
            response["usage"], matrx_model_name=matrx_model_name, response_id=message_id
        )

        finish_reason = FinishReason.from_anthropic(response.get("stop_reason"))

        return UnifiedResponse(
            messages=[message],
            usage=token_usage,
            finish_reason=finish_reason,
            raw_response=response,
        )
