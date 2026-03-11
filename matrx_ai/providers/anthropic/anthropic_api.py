from __future__ import annotations

import asyncio
import os
import traceback
from typing import Any

from anthropic import AsyncAnthropic
from matrx_utils import vcprint

from matrx_ai.config import (
    UnifiedConfig,
    UnifiedResponse,
)
from matrx_ai.context.emitter_protocol import Emitter

from .translator import AnthropicTranslator

DEBUG_OVERRIDE = False

class AnthropicChat:
    """Anthropic Messages API-specific endpoint implementation."""

    client: AsyncAnthropic
    endpoint_name: str
    debug: bool

    def __init__(self, debug: bool = False):
        self.client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.endpoint_name = "[ANTHROPIC CHAT]"
        self.translator = AnthropicTranslator()
        self.debug = debug

        if DEBUG_OVERRIDE:
            self.debug = True

    def to_provider_config(
        self, config: UnifiedConfig, api_class: str
    ) -> dict[str, Any]:
        return self.translator.to_anthropic(config, api_class)

    def to_unified_response(
        self, response: Any, matrx_model_name: str = ""
    ) -> UnifiedResponse:

        if hasattr(response, "model_dump"):
            response_dict = response.model_dump()
        else:
            # If for some reason it's not a Pydantic model, debug it
            vcprint(
                f"Unexpected response type: {type(response)}",
                "Warning: Response is not a Pydantic model",
                color="yellow"
            )
            vcprint(response, "Full Response Object", color="yellow")
            # Try to convert to dict as fallback
            if isinstance(response, dict):
                response_dict = response
            else:
                raise TypeError(f"Unexpected response type: {type(response)}. Expected Pydantic model with model_dump()")

        # Ensure model is set
        if not response_dict.get("model"):
            response_dict["model"] = matrx_model_name

        return self.translator.from_anthropic(response_dict, matrx_model_name)

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context
        emitter = get_app_context().emitter

        self.debug = debug
        matrx_model_name = unified_config.model
        # Build provider-specific config
        config_data = self.to_provider_config(unified_config, api_class)
        
        vcprint(config_data, "Anthropic API Config Data", color="blue", verbose=debug)
        
        try:
            if unified_config.stream:
                return await self._execute_streaming(
                    config_data, emitter, matrx_model_name
                )
            else:
                return await self._execute_non_streaming(
                    config_data, emitter, matrx_model_name
                )

        except Exception as e:
            # Import here to avoid circular dependency
            from matrx_ai.providers.errors import classify_anthropic_error
            
            # Classify the error to determine if it's retryable
            error_info = classify_anthropic_error(e)
            
            await emitter.send_error(
                error_type=error_info.error_type,
                message=error_info.message,
                user_message=error_info.user_message,
            )
            vcprint(e, "[Anthropic Chat] Error", color="red")
            traceback.print_exc()
            
            # Re-raise with error classification attached
            e.error_info = error_info
            raise

    async def _execute_non_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        matrx_model_name: str,
    ) -> UnifiedResponse:
        """Execute non-streaming Anthropic request"""

        # Remove stream parameter if present
        config_data_copy = config_data.copy()
        config_data_copy.pop("stream", None)

        # Make API call
        response = await self.client.messages.create(**config_data_copy)

        vcprint(response, "Anthropic Response", color="green", verbose=self.debug)

        # Send content through emitter
        if hasattr(response, "content"):
            for block in response.content:
                await self._handle_content_block(block, emitter)

        # Convert to unified format
        converted_response = self.to_unified_response(response, matrx_model_name)

        return converted_response

    async def _execute_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        matrx_model_name: str,
    ) -> UnifiedResponse:
        """Execute streaming Anthropic request"""

        # Use the streaming context manager
        async with self.client.messages.stream(**config_data) as stream:
            async for event in stream:
                await self._handle_event(event, emitter)

            # Get the final message with usage data
            final_message = await stream.get_final_message()

        vcprint(
            final_message, "Anthropic Final Message", color="green", verbose=self.debug
        )

        # Convert to unified format
        converted_response = self.to_unified_response(final_message, matrx_model_name)

        return converted_response

    async def _handle_event(self, event: Any, emitter: Emitter):
        """
        Handle individual streaming event.
        
        Note: Using getattr for streaming events is acceptable since event structures vary.
        If you need to see the actual event structure, set DEBUG_OVERRIDE = True at the top
        of this file to print raw events.
        """
        await asyncio.sleep(0)

        # Debug: Print raw event structure to understand what we're dealing with
        if DEBUG_OVERRIDE and self.debug:
            vcprint(event, f"Raw Event: {event.type if hasattr(event, 'type') else 'unknown'}", color="cyan")

        event_type = getattr(event, "type", None)

        if event_type == "content_block_delta":
            # Text, thinking, or input delta
            delta = getattr(event, "delta", None)
            if delta:
                delta_type = getattr(delta, "type", None)
                
                if delta_type == "text_delta":
                    text = getattr(delta, "text", "")
                    if text:
                        await emitter.send_chunk(text)
                        await asyncio.sleep(0)
                
                elif delta_type == "thinking_delta":
                    # Thinking content being streamed
                    thinking = getattr(delta, "thinking", "")
                    if thinking:
                        await emitter.send_chunk(thinking)
                        await asyncio.sleep(0)
                
                elif delta_type == "input_json_delta":
                    # Tool input being streamed (usually not needed for display)
                    pass

        elif event_type == "content_block_start":
            # New content block starting
            content_block = getattr(event, "content_block", None)
            if content_block:
                block_type = getattr(content_block, "type", None)
                
                if block_type == "tool_use":
                    name = getattr(content_block, "name", "")
                    await emitter.send_status_update(
                        status="processing",
                        system_message=f"Executing {name}",
                        user_message=f"Using tool {name}",
                        metadata={"tool_use": content_block},
                    )
                
                elif block_type == "thinking":
                    # Thinking block started - wrap in XML tags like OpenAI
                    await emitter.send_chunk("\n<reasoning>\n")

        elif event_type == "content_block_stop":
            # Content block finished
            content_block = getattr(event, "content_block", None)
            if content_block:
                block_type = getattr(content_block, "type", None)
                if block_type == "thinking":
                    # Thinking block ended - close XML tag
                    await emitter.send_chunk("\n</reasoning>\n")

        elif event_type == "message_start":
            # Message started
            vcprint("Anthropic Message Stream Started", color="cyan")

        elif event_type == "message_delta":
            # Message-level updates (usage, stop_reason)
            delta = getattr(event, "delta", None)
            if delta and self.debug:
                stop_reason = getattr(delta, "stop_reason", None)
                if stop_reason:
                    vcprint(f"Stop reason: {stop_reason}", color="yellow")

        elif event_type == "message_stop":
            # Message finished
            vcprint("Anthropic Message Stream Completed", color="green")

        elif event_type == "error":
            # Error occurred
            error = getattr(event, "error", {})
            await emitter.send_error(
                error_type="streaming_error",
                message=str(error),
                user_message="An error occurred during streaming.",
            )

        if self.debug:
            await self._debug_event(event)

    async def _handle_content_block(self, block: Any, emitter: Emitter):
        """Handle a content block from the response"""
        await asyncio.sleep(0)

        block_type = getattr(block, "type", None)

        if block_type == "text":
            # Text content
            text = getattr(block, "text", "")
            if text:
                await emitter.send_chunk(text)

        elif block_type == "tool_use":
            # Tool/function call
            name = getattr(block, "name", "")
            await emitter.send_status_update(
                status="processing",
                system_message=f"Executing {name}",
                user_message=f"Using tool {name}",
                metadata={"tool_use": block},
            )

        elif block_type == "thinking":
            # Thinking block
            text = getattr(block, "text", "")
            if text:
                await emitter.send_chunk(
                    f"\n<reasoning>\n{text}\n</reasoning>\n"
                )

    async def _debug_event(self, event: Any):
        """Debug logging for events - only aggregate/bigger events, not individual chunks"""
        event_type = getattr(event, "type", "unknown")

        # Only log significant events, not individual chunks
        if event_type == "content_block_start":
            content_block = getattr(event, "content_block", None)
            if content_block:
                block_type = getattr(content_block, "type", None)
                # Only log tool_use and thinking blocks
                if block_type in ("tool_use", "thinking"):
                    vcprint(f"Content Block Start. Type: {block_type}", color="blue")
        
        elif event_type == "content_block_stop":
            content_block = getattr(event, "content_block", None)
            if content_block:
                block_type = getattr(content_block, "type", None)
                # Only log completion of tool_use and thinking blocks
                if block_type in ("tool_use", "thinking"):
                    vcprint(content_block, "Content Block Stop", color="green")
        
        elif event_type == "message_start":
            vcprint("=================== MESSAGE STARTED ===================", color="blue")
        
        elif event_type == "message_stop":
            vcprint("=================== MESSAGE COMPLETED ===================", color="green")
        
        elif event_type == "message_delta":
            # Log usage and stop_reason updates
            delta = getattr(event, "delta", None)
            if delta:
                stop_reason = getattr(delta, "stop_reason", None)
                if stop_reason:
                    vcprint(f"Stop reason: {stop_reason}", color="yellow")
                usage = getattr(event, "usage", None)
                if usage:
                    vcprint(usage, "Usage Update", color="cyan")

