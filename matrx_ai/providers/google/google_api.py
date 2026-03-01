import asyncio
import os
import traceback
from collections.abc import Iterator

import rich
from google import genai
from google.genai.types import (
    Candidate,
    GenerateContentResponse,
    Part,
)
from matrx_utils import vcprint

from matrx_ai.config import (
    UnifiedConfig,
    UnifiedResponse,
)
from matrx_ai.context.emitter_protocol import Emitter

from .translator import GoogleProviderConfig, GoogleTranslator

LOCAL_DEBUG = False


class GoogleChat:
    """Google Gemini-specific endpoint implementation."""

    client: genai.Client
    endpoint_name: str
    translator: GoogleTranslator
    debug: bool

    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.endpoint_name = "[GOOGLE CHAT]"
        self.translator = GoogleTranslator()
        self.debug = LOCAL_DEBUG

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context

        emitter = get_app_context().emitter

        config_data: GoogleProviderConfig = self.translator.to_google(
            unified_config, api_class
        )
        self.debug = debug or LOCAL_DEBUG
        matrx_model_name = unified_config.model

        vcprint(f"[Google Chat] executing, with debug: {self.debug}", color="blue")
        # rich.print(config_data)

        if self.debug:
            rich.print(config_data)

        response: Iterator[GenerateContentResponse] | GenerateContentResponse | None = None
        accumulated_chunks: list[GenerateContentResponse]

        try:

            if unified_config.stream:
                response = self.client.models.generate_content_stream(**config_data)

                accumulated_chunks = []

                chunk: GenerateContentResponse
                for chunk in response:
                    accumulated_chunks.append(chunk)

                    # vcprint(chunk, "CHUNK", color="cyan")

                    if chunk.candidates:
                        cand: Candidate
                        for cand in chunk.candidates:
                            if cand.content and cand.content.parts:
                                part: Part
                                for part in cand.content.parts:
                                    await self._handle_part(part, emitter)

                converted_response = self.translator.from_google(
                    accumulated_chunks, matrx_model_name
                )
            else:
                # Non-streaming mode - returns single GenerateContentResponse
                response = self.client.models.generate_content(**config_data)

                # Wrap the single response in a list to maintain consistency with to_unified_config
                accumulated_chunks = [response]

                # Send all content through emitter (same as streaming, but all at once)
                if response.candidates:
                    for cand in response.candidates:
                        if cand.content and cand.content.parts:
                            for part in cand.content.parts:
                                await self._handle_part(part, emitter)

                converted_response = self.translator.from_google(
                    accumulated_chunks, matrx_model_name
                )

            return converted_response

        except Exception as e:
            vcprint(e, "[Google Chat] Error", color="red")
            # Import here to avoid circular dependency
            from matrx_ai.providers.errors import classify_google_error

            # Classify the error to determine if it's retryable
            error_info = classify_google_error(e)

            if emitter:
                await emitter.send_error(
                    error_type=error_info.error_type,
                    message=error_info.message,
                    user_message=error_info.user_message,
                )

            vcprint(e, "[Google Chat] Error", color="red")
            if "response" in locals():
                vcprint(response, "Response", color="red")
            traceback.print_exc()

            # Re-raise with error classification attached
            e.error_info = error_info
            raise

    async def _handle_part(self, part: Part, emitter: Emitter):
        await asyncio.sleep(0)

        # vcprint(part, "PART", color="green")

        if part.thought:
            if emitter:
                await emitter.send_chunk(
                    f"\n<reasoning>\n {part.text} \n</reasoning>\n"
                )
                # print(part.text)
                await asyncio.sleep(0)
            else:
                print(f"\n<reasoning>\n {part.text} \n</reasoning>\n")

        elif part.text:
            if emitter:
                await emitter.send_chunk(part.text)
                await asyncio.sleep(0)
            else:
                print(part.text)

        elif part.function_call:
            pass

        elif part.thought_signature:
            pass

        else:
            pass

        if LOCAL_DEBUG:
            await self._debug_part(part)

    async def _debug_part(self, part: Part):
        if part.thought:
            vcprint("=================== THOUGHT ===================", color="blue")
            print(part.text)
            vcprint("================================================", color="blue")
        elif part.text:
            print(part.text)
        elif part.function_call:
            vcprint(part.function_call, "Function Call", color="blue")
        elif part.thought_signature:
            vcprint("Empty Thought Signature", color="blue")
        else:
            vcprint(part, "Empty Part", color="blue")
