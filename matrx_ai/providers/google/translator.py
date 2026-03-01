from typing import Any, TypedDict

from google.genai import types
from google.genai.types import (
    Content,
    GenerateContentConfig,
    GenerateContentResponse,
    Part,
)
from matrx_utils import vcprint

from matrx_ai.config import (
    AudioContent,
    CodeExecutionContent,
    CodeExecutionResultContent,
    DocumentContent,
    FinishReason,
    ImageContent,
    TextContent,
    ThinkingConfig,
    ThinkingContent,
    TokenUsage,
    ToolCallContent,
    ToolResultContent,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
    VideoContent,
    YouTubeVideoContent,
)
from matrx_ai.tools.registry import ToolRegistryV2

# ============================================================================
# GEMINI TRANSLATOR
# ============================================================================


class GoogleProviderConfig(TypedDict):
    """Type hint for Google API configuration dictionary"""

    model: str
    contents: list[Content]
    config: GenerateContentConfig


class GoogleTranslator:
    """Translates between unified format and Google Gemini API"""

    from google.genai import types

    def to_google(self, config: UnifiedConfig, api_class: str) -> GoogleProviderConfig:
        """
        Convert unified request to Google provider format efficiently.
        Combines to_gemini and generate_google_config into a single optimized method.

        This method does everything in ONE efficient pass:
        1. Processes messages and builds 'contents' array (from to_gemini)
        2. Directly builds types.GenerateContentConfig object (from generate_google_config)
        3. Returns both in the exact structure needed by execute()

        Args:
            config: UnifiedConfig with request parameters
            api_class: API class identifier ("google_standard", "google_thinking", "google_thinking_3")

        Returns:
            Dict with:
                - contents: List of message contents in Google format
                - config: types.GenerateContentConfig object ready for API call
        """
        # ========================
        # STEP 1: Build contents (from messages)
        # ========================
        contents: list[Content] = []

        for msg in config.messages:
            google_content: dict[str, Any] | None = msg.to_google_content()
            if google_content:
                contents.append(google_content)

        # ========================
        # STEP 2: Build GenerateContentConfig directly
        # ========================
        try:
            # Build generation config kwargs
            generation_config_kwargs = {}

            # System instruction
            if config.system_instruction:
                generation_config_kwargs["system_instruction"] = (
                    config.system_instruction
                )

            # Standard generation parameters
            if config.max_output_tokens:
                generation_config_kwargs["max_output_tokens"] = config.max_output_tokens
            if config.temperature is not None:
                generation_config_kwargs["temperature"] = config.temperature

            # API-class specific parameters
            if api_class == "google_standard":
                if config.top_p is not None:
                    generation_config_kwargs["top_p"] = config.top_p
                if config.top_k is not None:
                    generation_config_kwargs["top_k"] = config.top_k

            # # Thinking config
            # print("TO GOOGLE TRANSLATOR DEBUG")
            # print("API CLASS", api_class)
            # vcprint(config, "CONFIG", color="yellow")
            # print("--------------------------------")
            # print("--------------------------------")

            thinking = ThinkingConfig.from_settings(config)
            if thinking:
                if api_class == "google_thinking":
                    generation_config_kwargs["thinking_config"] = (
                        thinking.to_google_thinking_legacy()
                    )
                elif api_class == "google_thinking_3":
                    generation_config_kwargs["thinking_config"] = (
                        thinking.to_google_thinking_3()
                    )

            # Create the config object
            generated_config: GenerateContentConfig = types.GenerateContentConfig(
                **generation_config_kwargs
            )

            # ========================
            # STEP 3: Process tools directly on config object
            # ========================
            if config.tools:
                raw_tools = ToolRegistryV2.get_instance().get_provider_tools(
                    config.tools, "google"
                )

                # Wrap each tool in types.Tool
                generated_config.tools = [
                    types.Tool(function_declarations=[tool]) for tool in raw_tools
                ]

                # Set tool config if tool_choice is specified
                if config.tool_choice:
                    if config.tool_choice == "none":
                        mode = "NONE"
                    elif config.tool_choice == "required":
                        mode = "ANY"
                    else:
                        mode = "AUTO"

                    generated_config.tool_config = types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(mode=mode)
                    )

            else:
                # Conditionally add built-in Google tools based on config flags
                built_in_tools = []

                if config.internal_url_context:
                    built_in_tools.append(types.Tool(url_context=types.UrlContext()))

                if config.internal_web_search:
                    built_in_tools.append(types.Tool(googleSearch=types.GoogleSearch()))

                if built_in_tools:
                    generated_config.tools = built_in_tools

        except Exception as e:
            vcprint(e, "Error in to_provider_config", color="red")
            raise

        # ========================
        # STEP 4: Return final structure
        # ========================
        return {
            "model": config.model,
            "contents": contents,
            "config": generated_config,
        }

    def from_google(
        self, chunks: list[GenerateContentResponse], matrx_model_name: str
    ) -> UnifiedResponse:
        """Convert Google API response chunks to unified format"""

        content = []
        all_candidates = []
        usage_metadata = None
        finish_reason = None
        accumulated_text = ""  # Accumulator for regular text chunks
        google_thought_signature = None  # Track Google's thought_signature if present
        grounding_metadata = None
        model_version = None
        response_id = None
        last_chunk = None

        # Process all chunks to extract complete response
        for chunk in chunks:
            if chunk.candidates:
                for cand in chunk.candidates:
                    all_candidates.append(cand)
                    # Capture finish reason and usage metadata from final chunk
                    if cand.finish_reason:
                        finish_reason = FinishReason.from_google(cand.finish_reason)
                        usage_metadata = chunk.usage_metadata
                        model_version = chunk.model_version
                        response_id = chunk.response_id
                        last_chunk = chunk

                    if cand.grounding_metadata:
                        grounding_metadata = cand.grounding_metadata

                    # Process content parts - all parts have predictable structure
                    if cand.content and cand.content.parts:
                        for part in cand.content.parts:
                            part: Part

                            # vcprint(part, "PART", color="yellow")

                            # 1. Thinking content (has thought flag set)
                            if part.thought:
                                content.append(ThinkingContent.from_google(part))
                                # print(part.text)

                            # 2. Regular text (has text but no thought flag)
                            elif part.text:
                                accumulated_text += part.text
                                # Capture Google's thought_signature if present
                                if part.thought_signature:
                                    google_thought_signature = part.thought_signature

                            # 4. Tool calls and other content types
                            elif part.function_call:
                                content.append(ToolCallContent.from_google(part))
                            elif part.function_response:
                                content.append(ToolResultContent.from_google(part))
                            elif part.executable_code:
                                content.append(CodeExecutionContent.from_google(part))
                            elif part.code_execution_result:
                                content.append(
                                    CodeExecutionResultContent.from_google(part)
                                )
                            elif part.inline_data:
                                converted = (
                                    ImageContent.from_google(part)
                                    or AudioContent.from_google(part)
                                    or VideoContent.from_google(part)
                                    or DocumentContent.from_google(part)
                                )
                                if converted:
                                    content.append(converted)

                            # Handle file_data (could be YouTube URL or regular file)
                            elif part.file_data:
                                converted = (
                                    YouTubeVideoContent.from_google(part)
                                    or ImageContent.from_google(part)
                                    or AudioContent.from_google(part)
                                    or VideoContent.from_google(part)
                                    or DocumentContent.from_google(part)
                                )
                                if converted:
                                    content.append(converted)

                            # == only if no other part type is found ==
                            elif part.thought_signature:
                                content.append(ThinkingContent.from_google(part))

        # Add accumulated text as a single TextContent object if we have any
        if accumulated_text:
            metadata = {}
            if google_thought_signature:
                metadata["google_thought_signature"] = google_thought_signature
            if grounding_metadata:
                metadata["grounding_metadata"] = grounding_metadata
            content.append(
                TextContent(
                    text=accumulated_text,
                    metadata=metadata,
                )
            )

        # Build unified message from accumulated content
        messages = []
        if content:
            messages.append(
                UnifiedMessage(
                    role="assistant",
                    content=content,
                    metadata={
                        "finish_reason": finish_reason,
                    },
                )
            )

        # Convert usage_metadata to TokenUsage if present
        token_usage = None
        if usage_metadata:
            token_usage = TokenUsage.from_gemini(
                usage_metadata,
                matrx_model_name=matrx_model_name,
                provider_model_name=model_version,
                response_id=response_id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: Gemini response missing usage metadata for model {model_version}",
                color="red",
            )

        assert last_chunk is not None, "No chunks with a finish_reason were received from Google"
        raw_response = last_chunk
        last_chunk.candidates = all_candidates

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            raw_response=raw_response,
        )
