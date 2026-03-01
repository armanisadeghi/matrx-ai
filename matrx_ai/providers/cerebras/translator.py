import json
from typing import Any

from matrx_utils import vcprint

from matrx_ai.config import (
    FinishReason,
    TextContent,
    ThinkingContent,
    TokenUsage,
    ToolCallContent,
    ToolResultContent,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
    YouTubeVideoContent,
)
from matrx_ai.tools.registry import ToolRegistryV2

# ============================================================================
# CEREBRAS TRANSLATOR
# ============================================================================


class CerebrasTranslator:
    """Translates between unified format and Cerebras API (OpenAI-style)"""

    def to_cerebras(self, config: UnifiedConfig) -> dict[str, Any]:
        """
        Convert unified config to Cerebras API format.

        Cerebras uses OpenAI-style messages but with some differences:
        - Uses max_completion_tokens instead of max_output_tokens
        - Tools only work in non-streaming mode
        - Supports reasoning (similar to OpenAI)
        """
        messages = []

        # Add system message if present
        if config.system_instruction:
            messages.append({"role": "system", "content": config.system_instruction})

        # Convert messages to OpenAI-style format
        for msg in config.messages:
            # Cerebras uses OpenAI-style messages with role and content
            if msg.role == "tool":
                # Tool results go as role="tool"
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
                # Regular messages
                message_dict = {"role": msg.role, "content": ""}

                # Combine text content
                text_parts = []
                tool_calls = []

                for content in msg.content:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif isinstance(content, ToolCallContent):
                        # Tool calls are added separately
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
                        # YouTube URLs not supported by Cerebras - show warning
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by Cerebras models and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                # Set content
                if text_parts:
                    message_dict["content"] = "".join(text_parts)

                # Add tool_calls if present
                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                # Only add message if it has content or tool calls
                if message_dict["content"] or tool_calls:
                    messages.append(message_dict)

        # Build request
        cerebras_request = {
            "model": config.model,
            "messages": messages,
        }

        # Add optional parameters
        if config.max_output_tokens:
            cerebras_request["max_completion_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            cerebras_request["temperature"] = config.temperature
        if config.top_p is not None:
            cerebras_request["top_p"] = config.top_p

        # Stop sequences
        if config.stop_sequences:
            cerebras_request["stop"] = config.stop_sequences

        # Response format
        if config.response_format:
            cerebras_request["response_format"] = config.response_format

        # Tools - Cerebras doesn't support streaming with tools
        # If tools are present, we disable streaming at API level (system stays responsive)
        if config.tools:
            cerebras_request["tools"] = (
                ToolRegistryV2.get_instance().get_provider_tools(
                    config.tools, "cerebras"
                )
            )
            if config.tool_choice:
                cerebras_request["tool_choice"] = config.tool_choice

        # Stream setting - disable if tools are present
        if config.stream and not config.tools:
            cerebras_request["stream"] = True

        # Seed
        if config.seed is not None:
            cerebras_request["seed"] = config.seed

        vcprint(
            cerebras_request, "--> Cerebras Request", color="magenta", verbose=False
        )

        return cerebras_request

    def from_cerebras(self, response: Any) -> UnifiedResponse:
        """
        Convert Cerebras API response to unified format.

        Cerebras returns OpenAI-style responses:
        - response.id, response.created, response.model always present
        - response.choices is always a list with one item
        - choice.message has: content, reasoning, role, tool_calls (can be null)
        - response.usage has: prompt_tokens, completion_tokens, prompt_tokens_details
        """
        messages = []

        if not response.choices:
            vcprint(response, "Cerebras Response", color="red")
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # Extract reasoning first (if present)
        if message.reasoning:
            content.append(ThinkingContent(text=message.reasoning, provider="cerebras"))

        # Extract text content
        if message.content:
            content.append(TextContent(text=message.content))

        # Extract tool calls
        if message.tool_calls:
            for tc in message.tool_calls:
                # Parse arguments from JSON string if needed
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

        # Create unified message
        if content:
            messages.append(
                UnifiedMessage(role="assistant", content=content, id=response.id)
            )

        # Convert usage to TokenUsage with cached tokens
        token_usage = None
        if response.usage:
            # Cerebras provides cached_tokens in prompt_tokens_details
            cached_tokens = 0
            if (
                response.usage.prompt_tokens_details
                and response.usage.prompt_tokens_details.cached_tokens
            ):
                cached_tokens = response.usage.prompt_tokens_details.cached_tokens

            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens - cached_tokens,
                output_tokens=response.usage.completion_tokens,
                cached_input_tokens=cached_tokens,
                matrx_model_name=response.model,
                provider_model_name=response.model,
                api="cerebras",
                response_id=response.id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: Cerebras response missing usage data for model {response.model} (response_id: {response.id})",
                color="red",
            )

        # Map finish_reason to unified format
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
