"""
Audio Preprocessing for Unified Config

Handles automatic transcription of audio content when the auto_transcribe flag is set
OR when the target API doesn't support native audio input (automatic fallback).
"""

from matrx_utils import vcprint

from config import (
    AudioContent,
    MessageList,
    TextContent,
    TokenUsage,
    UnifiedMessage,
)

from .audio_support import api_class_supports_audio


def preprocess_audio_in_messages(
    messages: MessageList, api_class: str, debug: bool = False
) -> tuple[MessageList, list[TokenUsage]]:
    """
    Preprocess messages to handle auto-transcription of audio content.

    Audio is transcribed when:
    1. auto_transcribe=True (explicitly requested by user)
    2. API doesn't support native audio input (automatic fallback)

    After transcription:
    1. Audio is replaced with TextContent containing the transcription
    2. Metadata about the original audio is preserved
    3. Usage for transcription API calls is tracked

    Args:
        messages: MessageList to preprocess
        api_class: API class identifier (e.g., "openai_standard", "google_standard")
        debug: Enable debug logging

    Returns:
        Tuple of (MessageList with audio transcribed, List of TokenUsage for transcriptions)
    """
    processed_messages = []
    transcription_usage_list = []
    api_supports_audio = api_class_supports_audio(api_class)

    for message in messages.to_list():
        processed_content = []

        for content in message.content:
            # Check if this audio needs transcription
            should_transcribe = False
            transcribe_reason = None

            if isinstance(content, AudioContent):
                if content.auto_transcribe:
                    # User explicitly requested transcription
                    should_transcribe = True
                    transcribe_reason = "explicit"
                elif not api_supports_audio:
                    # API doesn't support audio - automatic fallback
                    should_transcribe = True
                    transcribe_reason = "fallback"
                    # Enable auto_transcribe so get_transcription() works
                    content.auto_transcribe = True

            if should_transcribe:
                # Transcribe audio
                if debug:
                    if transcribe_reason == "explicit":
                        vcprint(
                            f"Auto-transcribing audio from: {content.url or content.file_uri or 'base64 data'}",
                            "Audio Preprocessing",
                            color="cyan",
                        )
                    else:  # fallback
                        vcprint(
                            f"⚠️ API doesn't support audio - transcribing as fallback: {content.url or content.file_uri or 'base64 data'}",
                            "Audio Preprocessing",
                            color="yellow",
                        )

                try:
                    transcription = content.get_transcription()

                    if transcription:
                        # Create text content with transcription
                        text_content = TextContent(
                            text=f"[Audio Transcription]: {transcription}",
                            metadata={
                                "original_type": "audio",
                                "transcription_metadata": content.metadata.get(
                                    "transcription", {}
                                ),
                                "audio_source": content.url
                                or content.file_uri
                                or "base64",
                            },
                        )
                        processed_content.append(text_content)

                        # Track transcription usage (only if not from cache)
                        transcription_metadata = content.metadata.get(
                            "transcription", {}
                        )
                        from_cache = transcription_metadata.get("from_cache", False)
                        usage_data = transcription_metadata.get("usage", {})

                        matrx_model_name = content.transcription_model
                        duration_seconds = 0.0

                        if usage_data and not from_cache:
                            # Create TokenUsage for transcription
                            # Note: Groq transcription is billed by duration, not tokens
                            # We'll represent it as "input tokens" for tracking purposes
                            duration_seconds = usage_data.get("billed_duration", 0)

                            # Convert duration to a token-equivalent for tracking
                            # (e.g., 1 second = 100 "tokens" for reporting purposes)
                            duration_as_tokens = int(duration_seconds * 100)

                            model_from_usage = usage_data.get("model")
                            if not model_from_usage:
                                vcprint(
                                    f"⚠️  WARNING: Groq transcription usage missing model name for response_id: {usage_data.get('response_id')}",
                                    color="red",
                                )
                                vcprint(
                                    "USING FAKE VALUE FOR MODEL: whisper-large-v3-turbo",
                                    color="yellow",
                                )
                                model_from_usage = "whisper-large-v3-turbo"

                            usage = TokenUsage(
                                input_tokens=duration_as_tokens,
                                output_tokens=0,  # Transcription doesn't have "output tokens"
                                cached_input_tokens=0,
                                matrx_model_name=matrx_model_name,
                                provider_model_name=model_from_usage,
                                api="groq_transcription",
                                response_id=None,
                                metadata={
                                    "duration_seconds": usage_data.get(
                                        "duration_seconds", 0
                                    ),
                                    "billed_duration": duration_seconds,
                                    "file_size_mb": usage_data.get("file_size_mb", 0),
                                    "language": usage_data.get("language"),
                                    "operation": usage_data.get(
                                        "operation", "transcription"
                                    ),
                                    "response_format": usage_data.get(
                                        "response_format"
                                    ),
                                    "audio_source": content.url
                                    or content.file_uri
                                    or "base64",
                                },
                            )
                            transcription_usage_list.append(usage)
                        elif from_cache and debug:
                            vcprint(
                                "✓ Using cached transcription (no API call)",
                                "Audio Preprocessing",
                                color="blue",
                            )

                        if debug:
                            vcprint(
                                f"✓ Audio transcribed successfully ({len(transcription)} characters, {duration_seconds:.1f}s)",
                                "Audio Preprocessing",
                                color="green",
                            )
                            print("--------------------------------")
                            print(transcription)
                            print("--------------------------------")
                    else:
                        # Transcription failed, skip audio
                        vcprint(
                            "⚠️ Audio transcription failed - audio will be skipped",
                            "Audio Preprocessing",
                            color="yellow",
                        )

                except Exception as e:
                    vcprint(
                        f"⚠️ Audio transcription error: {str(e)} - audio will be skipped",
                        "Audio Preprocessing",
                        color="yellow",
                    )
            else:
                # Keep content as-is
                processed_content.append(content)

        # Create new message with processed content
        processed_messages.append(
            UnifiedMessage(
                role=message.role,
                content=processed_content,
                id=message.id,
                name=message.name,
                timestamp=message.timestamp,
                metadata=message.metadata,
            )
        )

    return MessageList(_messages=processed_messages), transcription_usage_list


def should_preprocess_audio(messages: MessageList, api_class: str) -> bool:
    """
    Check if any messages contain audio that needs transcription.

    Audio needs transcription if:
    1. auto_transcribe=True (explicitly requested)
    2. API doesn't support native audio input (automatic fallback)

    Args:
        messages: MessageList to check
        api_class: API class identifier

    Returns:
        True if preprocessing is needed, False otherwise
    """
    api_supports_audio = api_class_supports_audio(api_class)

    for message in messages.to_list():
        for content in message.content:
            if isinstance(content, AudioContent):
                # Needs transcription if explicitly requested OR API doesn't support audio
                if content.auto_transcribe or not api_supports_audio:
                    return True
    return False
