import asyncio
import os
import traceback
from typing import Any

import rich
from matrx_utils import vcprint
from openai import AsyncOpenAI
from openai.types.responses import Response as OpenAIResponse

from config import (
    UnifiedConfig,
    UnifiedResponse,
)
from context.emitter_protocol import Emitter

from .translator import OpenAITranslator

DEBUG_OVERRIDE = False


class OpenAIChat:
    """OpenAI Responses API-specific endpoint implementation."""

    client: AsyncOpenAI
    endpoint_name: str
    debug: bool

    def __init__(self, debug: bool = False):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.endpoint_name = "[OPENAI CHAT]"
        self.translator = OpenAITranslator()
        self.debug = debug
        self._event_samples = {}
        self._reasoning_started = {}  # Track reasoning items that have received content

        if DEBUG_OVERRIDE:
            self.debug = True

    def to_provider_config(
        self, config: UnifiedConfig, api_class: str
    ) -> dict[str, Any]:
        return self.translator.to_openai(config, api_class)

    def to_unified_response(self, response: OpenAIResponse) -> UnifiedResponse:
        """Convert OpenAI API response to unified format"""

        return self.translator.from_openai(response)

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from context.app_context import get_app_context

        emitter = get_app_context().emitter

        self.debug = debug
        matrx_model_name = unified_config.model

        # Build provider-specific config
        config_data = self.to_provider_config(unified_config, api_class)

        vcprint(f"[OpenAI Chat] executing, with debug: {self.debug}", color="blue")
        if self.debug:
            rich.print(config_data)

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
            from providers.errors import classify_openai_error

            # Classify the error to determine if it's retryable
            error_info = classify_openai_error(e)

            await emitter.send_error(
                error_type=error_info.error_type,
                message=error_info.message,
                user_message=error_info.user_message,
            )
            vcprint(e, "[OpenAI Chat] Error", color="red")
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
        """Execute non-streaming OpenAI request"""

        # Remove stream parameter if present
        config_data_copy = config_data.copy()
        config_data_copy.pop("stream", None)

        # Make API call
        response: OpenAIResponse = await self.client.responses.create(
            **config_data_copy
        )

        content = ""
        for item in response.output:
            item_type = item.type
            if item_type == "reasoning":
                # Collect reasoning text first
                reasoning_text = ""
                for summary_item in item.summary:
                    reasoning_text += summary_item.text
                # Only add tags if there's actual content
                if reasoning_text.strip():
                    content += "\n<reasoning>\n"
                    content += reasoning_text
                    content += "\n</reasoning>\n"
            elif item_type == "message":
                if item.content:
                    for content_item in item.content:
                        if content_item.type == "output_text":
                            content += content_item.text

        await emitter.send_chunk(content)

        return self.translator.from_openai(response, matrx_model_name)

    async def _execute_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        matrx_model_name: str,
    ) -> UnifiedResponse:
        """Execute streaming OpenAI request"""

        accumulated_events = []

        # Clear reasoning tracking for this stream
        self._reasoning_started = {}

        # Use the streaming context manager
        async with self.client.responses.stream(**config_data) as stream:
            async for event in stream:
                accumulated_events.append(event)
                await self._handle_event(event, emitter)

            # Get the final response with usage data
            final_response: OpenAIResponse = await stream.get_final_response()

        return self.translator.from_openai(final_response, matrx_model_name)

    async def _handle_event(self, event: Any, emitter: Emitter):
        """Handle individual streaming event"""
        await asyncio.sleep(0)

        event_type = event.type
        if event_type and event_type not in self._event_samples:
            self._event_samples[event_type] = event

        # Text content streaming
        if event_type == "response.output_text.delta":
            await emitter.send_chunk(event.delta)

        # Reasoning streaming events
        elif (
            event_type == "response.output_item.added"
            and event.item.type == "reasoning"
        ):
            # Don't send opening tag yet - wait for actual content
            if self.debug:
                vcprint(f"Reasoning item added: {event.item.id}", color="blue")

        elif event_type == "response.reasoning_summary_text.delta":
            # Only send opening tag on first actual content
            reasoning_id = getattr(event, "item_id", None)
            if reasoning_id and reasoning_id not in self._reasoning_started:
                await emitter.send_chunk("\n<reasoning>\n")
                self._reasoning_started[reasoning_id] = True
                if self.debug:
                    vcprint(f"Reasoning content started: {reasoning_id}", color="blue")
            await emitter.send_chunk(event.delta)

        elif (
            event_type == "response.output_item.done" and event.item.type == "reasoning"
        ):
            # Only send closing tag if we sent opening tag
            reasoning_id = event.item.id
            if reasoning_id in self._reasoning_started:
                await emitter.send_chunk("\n</reasoning>\n")
                del self._reasoning_started[reasoning_id]
                if self.debug:
                    vcprint(
                        f"Reasoning completed with content: {reasoning_id}",
                        color="blue",
                    )
            elif self.debug:
                vcprint(
                    f"Reasoning completed with no content: {reasoning_id}", color="blue"
                )

        # Function/tool call completed
        elif event_type == "response.output_item.done" and event.item.type == "message":
            for content_item in event.item.content:
                if content_item.type == "function_call":
                    vcprint(content_item, "Function Call", color="magenta")

        # Stream lifecycle events
        elif event_type == "response.created":
            vcprint("OpenAI Response Stream Started", color="cyan")

        elif event_type == "response.completed":
            if self.debug:
                vcprint("OpenAI Response Stream Completed", color="green")
                vcprint(
                    self._event_samples,
                    "Unique Event Types & Samples",
                    color="magenta",
                    verbose=False,
                )
                self._event_samples = {}

        elif event_type == "error":
            error_data = getattr(event, "error", {})
            await emitter.send_error(
                error_type="streaming_error",
                message=str(error_data),
                user_message="An error occurred during streaming.",
            )

    async def _debug_event(self, event: Any):
        """Debug logging for events"""
        event_type = event.type

        if event_type == "response.output_text.delta":
            delta = event.delta
            print(delta, end="", flush=True)
        elif event_type == "response.output_item.added":
            item = event.item
            vcprint(item, "Output Item Added", color="blue")
        elif event_type == "response.created":
            vcprint(
                "=================== RESPONSE STARTED ===================", color="blue"
            )
        elif event_type == "response.completed":
            vcprint(
                "=================== RESPONSE COMPLETED ===================",
                color="green",
            )
        else:
            vcprint(event, f"Event: {event_type}", color="yellow")
