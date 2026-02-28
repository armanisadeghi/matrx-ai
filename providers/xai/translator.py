import json
from typing import Any

from matrx_utils import vcprint

from config import (
    FinishReason,
    TextContent,
    TokenUsage,
    ToolCallContent,
    ToolResultContent,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
    YouTubeVideoContent,
)
from tools.registry import ToolRegistryV2

# ============================================================================
# XAI TRANSLATOR
# ============================================================================


class XAITranslator:
    """Translates between unified format and xAI Grok API (OpenAI-compatible)"""

    def to_xai(self, config: UnifiedConfig) -> dict[str, Any]:
        """
        Convert unified config to xAI API format.

        xAI uses OpenAI-compatible API with full streaming + tools support.
        """
        messages = []

        # Add system message if present
        if config.system_instruction:
            messages.append({"role": "system", "content": config.system_instruction})

        # Convert messages to OpenAI-style format
        for msg in config.messages:
            if msg.role == "tool":
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": content.tool_use_id or content.call_id,
                                "content": json.dumps(content.content)
                                if isinstance(content.content, (dict, list))
                                else str(content.content),
                            }
                        )
            else:
                message_dict = {"role": msg.role}
                text_parts = []
                tool_calls = []

                for content in msg.content:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif isinstance(content, ToolCallContent):
                        tool_calls.append(
                            {
                                "id": content.id,
                                "type": "function",
                                "function": {
                                    "name": content.name,
                                    "arguments": json.dumps(content.arguments),
                                },
                            }
                        )
                    elif isinstance(content, YouTubeVideoContent):
                        # YouTube URLs not supported by xAI - show warning
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by xAI models and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                # Set content based on what we have
                if text_parts:
                    # Has text content
                    message_dict["content"] = "".join(text_parts)
                elif tool_calls:
                    # Has tool calls but no text - set content to null for OpenAI compatibility
                    message_dict["content"] = None
                else:
                    # No text and no tool calls - set empty string
                    message_dict["content"] = ""

                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                # Append message if it has content or tool calls
                if text_parts or tool_calls or message_dict["content"] == "":
                    messages.append(message_dict)

        # Build request
        xai_request = {
            "model": config.model,
            "messages": messages,
        }

        # Add optional parameters
        if config.max_output_tokens:
            xai_request["max_completion_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            xai_request["temperature"] = config.temperature
        if config.top_p is not None:
            xai_request["top_p"] = config.top_p
        if config.stop_sequences:
            xai_request["stop"] = config.stop_sequences
        if config.response_format:
            xai_request["response_format"] = config.response_format
        if config.stream:
            xai_request["stream"] = True

        # Tools - xAI supports streaming with tools
        if config.tools:
            xai_request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(
                config.tools, "xai"
            )
            if config.tool_choice:
                xai_request["tool_choice"] = config.tool_choice

        vcprint(xai_request, "--> xAI Request", color="magenta", verbose=False)
        return xai_request

    def from_xai(self, response: Any) -> UnifiedResponse:
        """Convert xAI API response to unified format"""
        messages = []

        if not response.choices:
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # Extract text content
        if message.content:
            content.append(TextContent(text=message.content))

        # Extract tool calls
        if message.tool_calls:
            for tc in message.tool_calls:
                arguments = (
                    json.loads(tc.function.arguments)
                    if isinstance(tc.function.arguments, str)
                    else tc.function.arguments
                )
                content.append(
                    ToolCallContent(
                        id=tc.id, name=tc.function.name, arguments=arguments
                    )
                )

        if content:
            messages.append(
                UnifiedMessage(role="assistant", content=content, id=response.id)
            )

        # Convert usage to TokenUsage
        token_usage = None
        if response.usage:
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                matrx_model_name=response.model,
                provider_model_name=response.model,
                api="xai",
                response_id=response.id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: xAI response missing usage data for model {response.model} (response_id: {response.id})",
                color="red",
            )

        # Map finish_reason
        finish_reason = None
        if choice.finish_reason == "stop":
            finish_reason = FinishReason.STOP
        elif choice.finish_reason == "length":
            finish_reason = FinishReason.MAX_TOKENS
        elif choice.finish_reason == "tool_calls":
            finish_reason = FinishReason.TOOL_CALLS
        elif choice.finish_reason == "content_filter":
            finish_reason = FinishReason.CONTENT_FILTER

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            stop_reason=choice.finish_reason,
            raw_response=response,
        )
