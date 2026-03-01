"""
Audio Support Detection

Tracks which AI providers/APIs support native audio input.
Used to determine when audio needs to be transcribed vs. sent directly.
"""

# APIs that support native audio input
AUDIO_SUPPORTED_APIS: set[str] = {
    "google",  # Google Gemini supports audio natively
    # Add others as they add audio support
}

# API classes that support native audio input
AUDIO_SUPPORTED_API_CLASSES: set[str] = {
    "google_standard",
    "google_thinking",
    "google_thinking_3",
    "google_image_generation",
    # Add others as they add audio support
}


def api_supports_audio(api: str) -> bool:
    """
    Check if an API supports native audio input.
    
    Args:
        api: API provider name (e.g., "google", "openai", "anthropic")
    
    Returns:
        True if the API supports audio natively, False otherwise
    """
    return api.lower() in AUDIO_SUPPORTED_APIS


def api_class_supports_audio(api_class: str) -> bool:
    """
    Check if an API class supports native audio input.
    
    Args:
        api_class: API class identifier (e.g., "google_standard", "openai_standard")
    
    Returns:
        True if the API class supports audio natively, False otherwise
    """
    return api_class.lower() in AUDIO_SUPPORTED_API_CLASSES


def should_transcribe_audio(
    audio_auto_transcribe: bool,
    api_class: str,
    explicit_flag: bool = True
) -> bool:
    """
    Determine if audio should be transcribed based on settings and API support.
    
    Logic:
    - If auto_transcribe=True: Always transcribe (user explicitly requested it)
    - If auto_transcribe=False AND API supports audio: Don't transcribe (send audio directly)
    - If auto_transcribe=False AND API doesn't support audio: Transcribe (fallback)
    - If auto_transcribe not set AND API doesn't support audio: Transcribe (fallback)
    
    Args:
        audio_auto_transcribe: Value of the auto_transcribe flag
        api_class: API class identifier
        explicit_flag: Whether auto_transcribe was explicitly set by user
    
    Returns:
        True if audio should be transcribed, False if it should be sent directly
    """
    # If user explicitly requested transcription, honor it
    if audio_auto_transcribe:
        return True
    
    # If API doesn't support audio, must transcribe (fallback)
    if not api_class_supports_audio(api_class):
        return True
    
    # API supports audio and user didn't request transcription
    return False
