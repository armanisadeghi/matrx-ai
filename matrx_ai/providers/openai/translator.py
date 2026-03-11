from __future__ import annotations

from typing import Any

import rich
from matrx_utils import vcprint
from openai.types.responses import Response as OpenAIResponse

from matrx_ai.config import (
    FinishReason,
    ThinkingConfig,
    TokenUsage,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
)
from matrx_ai.tools.registry import ToolRegistryV2

# ============================================================================
# OPENAI TRANSLATOR
# ============================================================================

class OpenAITranslator:
    """Translates between unified format and OpenAI Responses API"""

    def to_openai(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]:
        """
        Convert unified config to OpenAI Responses API format.

        Creates developer message from config.system_instruction.
        Delegates message conversion to UnifiedMessage.to_openai_items().
        """
        messages = []
        include_items = []

        rich.print(config)

        # Add developer message from system_instruction if present
        if config.system_instruction:
            messages.append(
                {
                    "role": "developer",
                    "content": [
                        {"type": "input_text", "text": config.system_instruction}
                    ],
                }
            )

        # Process all messages - delegate to message method
        for msg in config.messages:
            converted = msg.to_openai_items()
            rich.print(converted)

            if converted:
                # If it's a list (OUTPUT/TOOL role), extend messages with all items
                if isinstance(converted, list):
                    messages.extend(converted)
                # Otherwise it's a single wrapped message, append it
                else:
                    messages.append(converted)

        # Build request
        openai_request = {"model": config.model, "input": messages}

        tools = []
        if config.tools:
            tools.extend(
                ToolRegistryV2.get_instance().get_provider_tools(config.tools, "openai")
            )
        if config.internal_web_search:
            tools.append({"type": "web_search"})
            include_items.append("web_search_call.action.sources")

        if tools:
            openai_request["tools"] = tools

        # Add optional parameters
        if config.max_output_tokens:
            openai_request["max_output_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            openai_request["temperature"] = config.temperature

        if config.top_p is not None:
            if api_class == "openai_standard":
                openai_request["top_p"] = config.top_p

        # Response format
        if config.response_format:
            if config.response_format == "text":
                openai_request["text"] = {"format": {"type": "text"}}
            elif config.response_format == "json_schema":
                openai_request["text"] = {
                    "format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": config.response_format.get("name"),
                            "schema": config.response_format.get("schema"),
                        },
                    }
                }
            elif config.response_format == "json_object":
                openai_request["text"] = {
                    "format": {
                        "type": "json_object",
                        "json_object": {
                            "name": config.response_format.get("name"),
                            "schema": config.response_format.get("schema"),
                        },
                    }
                }
            else:
                vcprint(
                    config.response_format,
                    "WARNING: Unknown response format type",
                    color="red",
                )
                openai_request["text"] = {"format": {"type": "text"}}

        # Tool choice
        if config.tool_choice:
            openai_request["tool_choice"] = config.tool_choice

        # Parallel tool calls
        if not config.parallel_tool_calls:
            openai_request["parallel_tool_calls"] = False

        # Stream - Stream is not included in the request and is handled be the execution logic
        # if config.stream:
        #     openai_request["stream"] = True

        thinking = ThinkingConfig.from_settings(config)
        if api_class == "openai_reasoning" and thinking:
            openai_request["reasoning"] = thinking.to_openai_reasoning()
            include_items.append("reasoning.encrypted_content")

        if include_items:
            openai_request["include"] = include_items

        return openai_request

    def from_openai(
        self, response: OpenAIResponse, matrx_model_name: str
    ) -> UnifiedResponse:
        """
        Convert OpenAI Responses API response to unified format.

        """
        vcprint(response, "OpenAI Response", color="blue", verbose=False)

        # messages = self._from_openai_messages(response.output)
        messages = []
        for item in response.output:
            messages.append(UnifiedMessage.from_openai_item(item))

        # Convert usage to TokenUsage if present
        token_usage = TokenUsage.from_openai(
            response.usage,
            matrx_model_name=matrx_model_name,
            provider_model_name=response.model,
            response_id=response.id,
        )

        # # Map OpenAI status/finish_reason to unified format
        finish_reason = None

        if response.status == "completed":
            # If there are tool calls, set finish reason to TOOL_CALLS
            finish_reason = FinishReason.STOP
        elif response.status == "incomplete":
            finish_reason = FinishReason.MAX_TOKENS
        elif response.status == "failed":
            finish_reason = FinishReason.ERROR

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            raw_response=response,
        )
