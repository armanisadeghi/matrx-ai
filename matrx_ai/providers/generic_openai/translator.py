from __future__ import annotations

import json
from typing import Any

from matrx_utils import vcprint

from matrx_ai.config import (
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
from .base_translator import BaseTranslator
from matrx_ai.tools.registry import ToolRegistryV2


class GenericOpenAITranslator(BaseTranslator):
    """Translates between unified format and any OpenAI-compatible API."""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)

    def to_generic_openai(self, config: UnifiedConfig, provider_name: str = "generic_openai") -> dict[str, Any]:
        """
        Convert unified config to OpenAI-compatible chat completion format.

        Works with any OpenAI-compatible endpoint (HuggingFace TGI, llama.cpp server,
        vLLM, LocalAI, Ollama, etc.)
        """
        messages = []

        system_text = self.get_system_text(config)
        if system_text:
            messages.append({"role": "system", "content": system_text})

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
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by generic OpenAI-compatible endpoints and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                if text_parts:
                    message_dict["content"] = "".join(text_parts)
                elif tool_calls:
                    message_dict["content"] = None
                else:
                    message_dict["content"] = ""

                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                if text_parts or tool_calls or message_dict["content"] == "":
                    messages.append(message_dict)

        # clear_thinking is a Cerebras-only concept — not forwarded to generic OpenAI providers.
        # disable_reasoning has no generic equivalent — dropped.

        request: dict[str, Any] = {
            "model": config.model,
            "messages": messages,
        }

        if config.max_output_tokens:
            request["max_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            request["temperature"] = config.temperature
        if config.top_p is not None:
            request["top_p"] = config.top_p
        if config.stop_sequences:
            request["stop"] = config.stop_sequences
        if config.response_format:
            request["response_format"] = config.response_format
        if config.stream:
            request["stream"] = True

        if config.tools:
            request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(
                config.tools, "generic_openai"
            )
            if config.tool_choice:
                request["tool_choice"] = config.tool_choice

        vcprint(request, f"--> {provider_name} Request", color="magenta", verbose=False)
        return request

    def from_generic_openai(self, response: Any, provider_name: str = "generic_openai") -> UnifiedResponse:
        """Convert OpenAI-compatible response to unified format."""
        messages = []

        if not response.choices:
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # llama.cpp / Qwen3-thinking puts chain-of-thought in reasoning_content and the
        # final answer in content. Surface both when present so the caller sees the full
        # picture; fall back to just the reasoning if content is empty (hit max_tokens).
        reasoning = getattr(message, "reasoning_content", None)
        main_text = message.content or ""

        if reasoning and main_text:
            content.append(TextContent(text=f"<reasoning>{reasoning}</reasoning>\n{main_text}"))
        elif main_text:
            content.append(TextContent(text=main_text))
        elif reasoning:
            # No final answer (e.g. hit max_tokens mid-reasoning) — surface what we have
            content.append(TextContent(text=f"<reasoning>{reasoning}</reasoning>"))

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

        token_usage = None
        if response.usage:
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                matrx_model_name=getattr(response, "model", ""),
                provider_model_name=getattr(response, "model", ""),
                api=provider_name,
                response_id=response.id,
            )

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
