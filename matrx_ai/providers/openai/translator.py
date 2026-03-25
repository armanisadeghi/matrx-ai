from __future__ import annotations

from typing import Any

import rich
from matrx_utils import vcprint
from openai.types.responses import Response as OpenAIResponse

from matrx_ai.config import (
    FinishReason,
    Role,
    TextContent,
    ThinkingConfig,
    ThinkingContent,
    TokenUsage,
    ToolCallContent,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
    WebSearchCallContent,
)
from matrx_ai.config.message_config import OpenAIResponseOutputItem
from matrx_ai.providers.generic_openai.base_translator import BaseTranslator
from matrx_ai.tools.registry import ToolRegistryV2

# ============================================================================
# OPENAI TRANSLATOR
# ============================================================================

class OpenAITranslator(BaseTranslator):
    """Translates between unified format and OpenAI Responses API"""

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)

    def to_openai(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]:
        """
        Convert unified config to OpenAI Responses API format.

        Creates developer message from config.system_instruction.
        Delegates message conversion to UnifiedMessage.to_openai_items().
        """
        messages = []
        include_items = []

        if self.debug:
            rich.print(config)

        # Add developer message from system_instruction if present
        system_text = self.get_system_text(config)
        if system_text:
            messages.append(
                {
                    "role": "developer",
                    "content": [
                        {"type": "input_text", "text": system_text}
                    ],
                }
            )

        # Process all messages - delegate to message method
        for msg in config.messages:
            converted = msg.to_openai_items_modified()
            if self.debug:
                rich.print(converted)
            messages.extend(converted)

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

        # clear_thinking is a Cerebras-only concept — not applicable to OpenAI.
        # disable_reasoning is normalised to reasoning_effort="none" by ThinkingConfig.from_settings()
        # so the existing to_openai_reasoning() path handles it automatically.
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

        OpenAI returns flat output items (reasoning, function_call, message, etc.)
        as siblings. We must reorganize them into the canonical message structure:

        - If there is reasoning and/or tool calls (but no text message), they go
          into an 'output' role message with [thinking, tool_call, ...] content.
        - If there is reasoning and/or tool calls AND a text message, the non-text
          items go into 'output' and text goes into a separate 'assistant' message.
        - If there are only tool calls (no reasoning), they go into 'assistant'.
        - A text-only response is a single 'assistant' message.

        This normalization ensures OpenAI responses match the same canonical DB
        structure that Anthropic and Google already produce.
        """
        messages = self._build_unified_messages(response.output)
        # vcprint(messages, "[OPENAI TRANSLATOR] Unified Messages", color="pink")

        token_usage = TokenUsage.from_openai(
            response.usage,
            matrx_model_name=matrx_model_name,
            provider_model_name=response.model,
            response_id=response.id,
        )

        finish_reason = None
        if response.status == "completed":
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

    def _build_unified_messages(
        self, output_items: list[OpenAIResponseOutputItem]
    ) -> list[UnifiedMessage]:
        """
        Convert OpenAI's flat output items into canonical UnifiedMessage list.

        Collects thinking, tool_call, web_search, and text content blocks from the
        raw output, then assembles them into properly-roled messages matching the
        DB contract all providers share.
        """
        thinking_blocks: list[ThinkingContent] = []
        tool_call_blocks: list[ToolCallContent] = []
        web_search_blocks: list[WebSearchCallContent] = []
        text_blocks: list[TextContent] = []
        text_message_id: str | None = None

        for item in output_items:
            # vcprint(item, "[OPENAI TRANSLATOR] Output Item", color="cyan")

            if item.type == "reasoning":
                thinking_blocks.append(ThinkingContent.from_openai(item))

            elif item.type == "function_call":
                tool_call_blocks.append(ToolCallContent.from_openai(item))

            elif item.type == "web_search_call":
                web_search_blocks.append(WebSearchCallContent.from_openai(item))

            elif item.type == "message":
                for content_item in item.content:
                    if content_item.type == "output_text":
                        text_blocks.append(
                            TextContent.from_openai(content_item, item.id)
                        )
                        text_message_id = item.id
                    elif content_item.type == "refusal":
                        vcprint(content_item, "[OPENAI TRANSLATOR] Refusal", color="red")
                        text_blocks.append(TextContent(text=content_item.refusal or ""))
                    else:
                        vcprint(content_item, "[OPENAI TRANSLATOR] Unknown content type", color="red")
            else:
                vcprint(item, f"[OPENAI TRANSLATOR] Unknown output item type: {item.type}", color="red")

        has_thinking = bool(thinking_blocks)
        has_tool_calls = bool(tool_call_blocks)
        has_web_search = bool(web_search_blocks)
        has_text = bool(text_blocks)

        messages: list[UnifiedMessage] = []

        non_text_content = [*thinking_blocks, *tool_call_blocks, *web_search_blocks]

        if non_text_content:
            role = Role.OUTPUT if has_thinking else Role.ASSISTANT
            messages.append(UnifiedMessage(
                role=role,
                content=non_text_content,
            ))

        if has_text:
            messages.append(UnifiedMessage(
                id=text_message_id,
                role=Role.ASSISTANT,
                content=text_blocks,
            ))

        return messages