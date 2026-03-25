from __future__ import annotations

import asyncio
import os
import traceback
from typing import Any

import rich
from matrx_utils import vcprint
from openai import AsyncOpenAI
from openai.types.responses import Response as OpenAIResponse

from matrx_ai.config import (
    AudioContent,
    TokenUsage,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
)
from matrx_ai.context.emitter_protocol import Emitter
from matrx_ai.media.media_persistence import save_media

from .translator import OpenAITranslator

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
        self.translator = OpenAITranslator(debug=debug)
        self.debug = debug
        self._event_samples = {}
        self._reasoning_started = {}  # Track reasoning items that have received content

        if DEBUG_OVERRIDE:
            self.debug = True

    def to_provider_config(
        self, config: UnifiedConfig, api_class: str
    ) -> dict[str, Any]:
        return self.translator.to_openai(config, api_class)

    def to_unified_response(self, response: OpenAIResponse, matrx_model_name: str) -> UnifiedResponse:
        """Convert OpenAI API response to unified format"""

        return self.translator.from_openai(response, matrx_model_name)

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context

        emitter = get_app_context().emitter

        self.debug = debug
        if DEBUG_OVERRIDE:
            self.debug = True
        self.translator.debug = debug
        matrx_model_name = unified_config.model

        vcprint(f"[OpenAI Chat] executing api_class={api_class}, debug={self.debug}", color="blue")

        if api_class == "openai_tts":
            return await self._execute_tts(unified_config, emitter, matrx_model_name)

        # Build provider-specific config
        config_data = self.to_provider_config(unified_config, api_class)

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
            from matrx_ai.providers.errors import classify_openai_error

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

    async def _execute_tts(
        self,
        unified_config: UnifiedConfig,
        emitter: Emitter,
        matrx_model_name: str,
    ) -> UnifiedResponse:
        """Execute OpenAI TTS request via client.audio.speech.create."""
        from matrx_ai.config.tts_config import OpenAITTSRegistry

        tts = unified_config.tts_voice_config
        model, voice = OpenAITTSRegistry.resolve(
            model=unified_config.model,
            voice=tts._primary_voice() if tts else None,
        )

        # OpenAI TTS supports: mp3, opus, aac, flac, wav, pcm
        valid_formats = {"mp3", "opus", "aac", "flac", "wav", "pcm"}
        audio_format = (unified_config.audio_format or "mp3").lower()
        if audio_format not in valid_formats:
            audio_format = "mp3"

        text_parts: list[str] = []
        for msg in unified_config.messages:
            if hasattr(msg, "content"):
                for c in msg.content:
                    if hasattr(c, "text") and c.text:
                        text_parts.append(c.text)
        input_text = " ".join(text_parts).strip() or "."

        # Multi-speaker configs collapse to a single voice for OpenAI.
        # Strip speaker labels (e.g. "Alex: ") so they aren't read aloud.
        if tts:
            input_text = tts.strip_speaker_labels(input_text)

        vcprint(f"[OpenAI TTS] model={model} voice={voice} format={audio_format}", color="blue")

        response = await self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=input_text,
            response_format=audio_format,
        )

        audio_bytes = response.content

        mime_map = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "wav": "audio/wav",
            "pcm": "audio/pcm",
        }
        mime_type = mime_map.get(audio_format, "audio/mpeg")

        url = save_media(content=audio_bytes, mime_type=mime_type, audio_format=audio_format)

        audio_content = AudioContent(url=url, mime_type=mime_type)
        msg = UnifiedMessage(role="assistant", content=[audio_content])

        usage = TokenUsage(
            input_tokens=0,
            output_tokens=0,
            matrx_model_name=matrx_model_name,
            provider_model_name=model,
            api="openai",
        )

        unified_response = UnifiedResponse(messages=[msg], usage=usage)

        await emitter.send_data({"type": "audio_output", "url": url, "mime_type": mime_type})
        await asyncio.sleep(0)

        return unified_response

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

        return self.to_unified_response(response, matrx_model_name)

    async def _execute_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        matrx_model_name: str,
    ) -> UnifiedResponse:
        """Execute streaming OpenAI request"""

        accumulated_events = []
        final_response = None

        # Clear reasoning tracking for this stream
        self._reasoning_started = {}

        # Use the streaming context manager
        async with self.client.responses.stream(**config_data) as stream:
            async for event in stream:
                accumulated_events.append(event)
                await self._handle_event(event, emitter)

            # Get the final response with usage data
            final_response: OpenAIResponse = await stream.get_final_response()

        return self.to_unified_response(final_response, matrx_model_name)

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
            vcprint("\n\n[OPENAI API CHAT] Response Stream Started", color="cyan")

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
