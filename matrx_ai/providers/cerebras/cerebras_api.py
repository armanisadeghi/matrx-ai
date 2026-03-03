import asyncio
import os
import traceback
from typing import Any

from cerebras.cloud.sdk import AsyncCerebras, AsyncStream
from cerebras.cloud.sdk.types.chat import ChatCompletion as CerebrasCompletion
from matrx_utils import vcprint

from matrx_ai.config import (
    TextContent,
    ThinkingContent,
    ToolCallContent,
    UnifiedConfig,
    UnifiedResponse,
)
from matrx_ai.context.emitter_protocol import Emitter

from .translator import CerebrasTranslator

DEBUG_OVERRIDE = False


class CerebrasChat:
    """Cerebras API-specific endpoint implementation (OpenAI-style)."""

    client: AsyncCerebras
    endpoint_name: str
    debug: bool

    def __init__(self, debug: bool = False):
        self.client = AsyncCerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
        self.endpoint_name = "[CEREBRAS CHAT]"
        self.translator = CerebrasTranslator()
        self.debug = debug

        if DEBUG_OVERRIDE:
            self.debug = True

    def to_provider_config(
        self, config: UnifiedConfig, api_class: str
    ) -> dict[str, Any]:
        return self.translator.to_cerebras(config)

    def to_unified_response(self, response: Any, model: str = "") -> UnifiedResponse:
        """Convert Cerebras response to unified format"""
        return self.translator.from_cerebras(response)

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context

        emitter = get_app_context().emitter
        self.debug = debug

        # Build provider-specific config
        config_data = self.to_provider_config(unified_config, api_class)

        vcprint(config_data, "Cerebras API Config Data", color="blue", verbose=debug)

        try:
            # Translator has already set stream correctly based on tools
            if config_data.get("stream", False):
                return await self._execute_streaming(
                    config_data, emitter, unified_config.model
                )
            else:
                return await self._execute_non_streaming(
                    config_data, emitter, unified_config.model
                )

        except Exception as e:
            # Import here to avoid circular dependency
            from matrx_ai.providers.errors import classify_provider_error

            # Classify the error to determine if it's retryable
            error_info = classify_provider_error("cerebras", e)

            await emitter.send_error(
                error_type=error_info.error_type,
                message=error_info.message,
                user_message=error_info.user_message,
            )
            vcprint(e, "[Cerebras Chat] Error", color="red")
            traceback.print_exc()

            # Re-raise with error classification attached
            e.error_info = error_info
            raise

    async def _execute_non_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        model: str,
    ) -> UnifiedResponse:
        """Execute non-streaming Cerebras request"""

        vcprint("[Cerebras] Starting API call (non-streaming)...", color="cyan")

        # Native async API call - no executor needed!
        response = await self.client.chat.completions.create(**config_data)

        vcprint("[Cerebras] API call completed, processing response...", color="cyan")
        vcprint(response, "Cerebras Response", color="green", verbose=self.debug)

        from tests.ai.translation_tests.response_capture import capture_provider_response
        vcprint("\nCAPTURING PROVIDER RESPONSE - REMOVE AFTER TESTING\n", color="yellow")

        capture_provider_response(
            "cerebras",
            model,
            response.model_dump(),
            {"stream": False, "has_tools": bool(config_data.get("tools"))},
        )

        # Convert to unified format first
        vcprint("[Cerebras] Converting to unified format...", color="cyan")
        converted_response = self.to_unified_response(response, model)
        vcprint(
            f"[Cerebras] Conversion complete. {len(converted_response.messages)} messages",
            color="cyan",
        )

        # Send content through emitter
        vcprint("[Cerebras] Sending content to stream handler...", color="cyan")
        for message in converted_response.messages:
            for content in message.content:
                if isinstance(content, ThinkingContent):
                    # Wrap reasoning in XML tags
                    await emitter.send_chunk(
                        f"\n<reasoning>\n{content.text}\n</reasoning>\n"
                    )
                elif isinstance(content, TextContent):
                    await emitter.send_chunk(content.text)
                elif isinstance(content, ToolCallContent):
                    await emitter.send_status_update(
                        status="processing",
                        system_message=f"Executing {content.name}",
                        user_message=f"Using tool {content.name}",
                        metadata={"tool_call": content.name},
                    )

        vcprint(
            "[Cerebras] Non-streaming execution completed successfully", color="green"
        )
        return converted_response

    async def _execute_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        model: str,
    ) -> UnifiedResponse:
        """Execute streaming Cerebras request"""

        vcprint("[Cerebras] Starting API call (streaming)...", color="cyan")

        # Native async streaming - stream=True already in config_data from translator
        stream: AsyncStream[CerebrasCompletion] = await self.client.chat.completions.create(**config_data)  # type: ignore[assignment]

        vcprint(
            "[Cerebras] Stream connection established, processing chunks...",
            color="cyan",
        )

        # Accumulate response data to reconstruct full response object
        accumulated_content = ""
        accumulated_reasoning = ""
        accumulated_tool_calls = []
        usage_data = None
        finish_reason = None
        response_id = None
        response_created = None
        response_model = None

        first_reasoning_chunk = True

        # Process stream chunks
        # Chunk structure is 100% predictable:
        # - chunk.id, chunk.created, chunk.model always present
        # - chunk.choices is always a list with one item (index 0)
        # - choice.delta has: content, reasoning, role, tokens, tool_calls (all can be null)
        # - choice.finish_reason is null except final chunk
        # - chunk.usage is null except final chunk
        async for chunk in stream:
            response_id = chunk.id  # Always present
            response_created = chunk.created  # Always present
            response_model = chunk.model  # Always present

            # Choices is always a list with one item
            assert chunk.choices, "Cerebras streaming chunk missing choices"
            choice = chunk.choices[0]
            assert choice.delta is not None, "Cerebras streaming choice missing delta"
            delta = choice.delta

            # Handle reasoning chunks (delta.reasoning can be null or string)
            if delta.reasoning:
                accumulated_reasoning += delta.reasoning

                if first_reasoning_chunk:
                    await emitter.send_chunk("\n<reasoning>\n")
                    first_reasoning_chunk = False

                await emitter.send_chunk(delta.reasoning)
                await asyncio.sleep(0)

            # Handle content chunks (delta.content can be null or string)
            if delta.content:
                # Close reasoning tag if we were in reasoning
                if accumulated_reasoning and not first_reasoning_chunk:
                    await emitter.send_chunk("\n</reasoning>\n")
                    first_reasoning_chunk = True  # Reset for potential future reasoning

                accumulated_content += delta.content
                await emitter.send_chunk(delta.content)
                await asyncio.sleep(0)

            # Handle tool calls (delta.tool_calls can be null or list)
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    # Accumulate tool call data
                    while len(accumulated_tool_calls) <= tc.index:
                        accumulated_tool_calls.append(
                            {"id": "", "name": "", "arguments": ""}
                        )

                    if tc.id:
                        accumulated_tool_calls[tc.index]["id"] = tc.id
                    if tc.function.name:
                        accumulated_tool_calls[tc.index]["name"] = tc.function.name
                    if tc.function.arguments:
                        accumulated_tool_calls[tc.index]["arguments"] += (
                            tc.function.arguments
                        )

            # Capture finish reason (only in final chunk)
            if choice.finish_reason:
                finish_reason = choice.finish_reason

            # Capture usage from final chunk
            if chunk.usage:
                usage_data = chunk.usage

        # Close reasoning tag if still open
        if accumulated_reasoning and not first_reasoning_chunk:
            await emitter.send_chunk("\n</reasoning>\n")

        from tests.ai.translation_tests.response_capture import capture_provider_response
        vcprint("\nCAPTURING PROVIDER RESPONSE - REMOVE AFTER TESTING\n", color="yellow")
        
        capture_provider_response(
            "cerebras",
            model,
            {
                "id": response_id,
                "created": response_created,
                "model": response_model,
                "content": accumulated_content,
                "reasoning": accumulated_reasoning,
                "tool_calls": accumulated_tool_calls,
                "finish_reason": finish_reason,
                "usage": usage_data.model_dump() if usage_data else None,
            },
            {"stream": True},
        )

        # Reconstruct a ChatCompletion-like response object to pass through translator
        # This ensures consistency with non-streaming path and keeps conversion logic in one place
        from types import SimpleNamespace

        # Build tool_calls list if we have any
        tool_calls_list = []
        for tc_data in accumulated_tool_calls:
            if tc_data["name"]:  # Only add if we have a name
                tool_calls_list.append(
                    SimpleNamespace(
                        id=tc_data["id"],
                        type="function",
                        function=SimpleNamespace(
                            name=tc_data["name"], arguments=tc_data["arguments"]
                        ),
                    )
                )

        # Create message object matching Cerebras response structure
        message = SimpleNamespace(
            role="assistant",
            content=accumulated_content or None,
            reasoning=accumulated_reasoning or None,
            tool_calls=tool_calls_list if tool_calls_list else None,
        )

        # Create choice object
        choice = SimpleNamespace(index=0, message=message, finish_reason=finish_reason)

        # Create full response object matching ChatCompletion structure
        mock_response = SimpleNamespace(
            id=response_id,
            created=response_created,
            model=response_model,
            choices=[choice],
            usage=usage_data,
        )

        vcprint(
            "[Cerebras] Stream accumulated, converting through translator...",
            color="cyan",
        )

        # Convert through translator (same path as non-streaming)
        converted_response = self.to_unified_response(mock_response, model)

        vcprint("[Cerebras] Streaming execution completed successfully", color="green")

        return converted_response
