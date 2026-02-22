"""
Test Groq Speech-to-Text Transcription

Tests the Groq Whisper API transcription functionality.
"""

import asyncio
from pathlib import Path
from media.audio.groq_transcription import GroqTranscription, TranscriptionResult
from config.unified_config import UnifiedMessage, AudioContent, TextContent
from matrx_utils import vcprint, clear_terminal
from initialize_systems import initialize

initialize()
clear_terminal()


def test_basic_transcription():
    """Test basic transcription with a local audio file"""
    vcprint("=" * 80, color="cyan")
    vcprint("TEST 1: Basic Transcription", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    # Initialize transcription service
    transcriber = GroqTranscription(debug=True)
    
    # Path to your audio file (replace with actual path)
    audio_file = "/path/to/your/audio.wav"
    
    # Check if file exists
    if not Path(audio_file).exists():
        vcprint(
            f"Skipping test - audio file not found: {audio_file}",
            "Test Skipped",
            color="yellow"
        )
        return
    
    # Transcribe
    result = transcriber.transcribe(
        audio_source=audio_file,
        language="en",
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"],
    )
    
    # Display results
    vcprint(result.text, "Transcription Text", color="green")
    vcprint(result.usage.to_dict(), "Usage Tracking", color="blue")
    vcprint(result.quality_metrics, "Quality Metrics", color="yellow")
    
    # Check for quality warnings
    if result.quality_metrics.get("warning_low_confidence"):
        vcprint(
            "⚠️ Warning: Some segments have low confidence",
            color="yellow"
        )
        vcprint(
            result.quality_metrics["low_confidence_segments"],
            "Low Confidence Segments",
            color="yellow"
        )


def test_translation():
    """Test translation (convert any language audio to English)"""
    vcprint("\n" + "=" * 80, color="cyan")
    vcprint("TEST 2: Translation to English", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    # Initialize transcription service
    transcriber = GroqTranscription(debug=True)
    
    # Path to your non-English audio file
    audio_file = "/path/to/your/spanish_audio.wav"
    
    # Check if file exists
    if not Path(audio_file).exists():
        vcprint(
            f"Skipping test - audio file not found: {audio_file}",
            "Test Skipped",
            color="yellow"
        )
        return
    
    # Translate to English
    result = transcriber.translate(
        audio_source=audio_file,
        response_format="json",
    )
    
    # Display results
    vcprint(result.text, "Translated Text (English)", color="green")
    vcprint(result.usage.to_dict(), "Usage Tracking", color="blue")


def test_audio_content_integration():
    """Test AudioContent with auto_transcribe flag"""
    vcprint("\n" + "=" * 80, color="cyan")
    vcprint("TEST 3: AudioContent Auto-Transcription", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    # Create audio content with auto-transcribe enabled
    audio = AudioContent(
        url="https://example.com/audio.mp3",  # Replace with actual audio URL
        auto_transcribe=True,
        transcription_model="whisper-large-v3-turbo",
        transcription_language="en",
    )
    
    vcprint(f"Auto-transcribe enabled: {audio.auto_transcribe}", color="blue")
    vcprint(f"Model: {audio.transcription_model}", color="blue")
    
    # Note: Actual transcription requires a valid audio URL
    # This is just demonstrating the configuration
    
    # To actually transcribe:
    # transcription = audio.get_transcription()
    # vcprint(transcription, "Transcribed Text", color="green")


def test_unified_message_with_audio():
    """Test UnifiedMessage with audio that gets auto-transcribed"""
    vcprint("\n" + "=" * 80, color="cyan")
    vcprint("TEST 4: UnifiedMessage with Auto-Transcribe Audio", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    # Create a message with audio content
    message = UnifiedMessage(
        role="user",
        content=[
            AudioContent(
                url="https://example.com/audio.mp3",  # Replace with actual URL
                auto_transcribe=True,
                transcription_model="whisper-large-v3-turbo",
                transcription_language="en",
            ),
            TextContent(
                text="Please analyze this audio and tell me what you think."
            ),
        ]
    )
    
    vcprint(f"Message has {len(message.content)} content items", color="blue")
    
    # Access audio content
    audio_content = message.content[0]
    if isinstance(audio_content, AudioContent):
        vcprint(f"Audio auto-transcribe: {audio_content.auto_transcribe}", color="green")
        
        # To actually transcribe (requires valid audio URL):
        # transcription = audio_content.get_transcription()
        # vcprint(transcription, "Transcribed Audio", color="green")


def test_url_transcription():
    """Test transcription from a public URL"""
    vcprint("\n" + "=" * 80, color="cyan")
    vcprint("TEST 5: URL-Based Transcription", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    transcriber = GroqTranscription(debug=True)
    
    # Example: Use a public audio URL (replace with actual URL)
    audio_url = "https://example.com/sample-audio.wav"
    
    vcprint(f"Attempting to transcribe from URL: {audio_url}", color="blue")
    
    # Note: This requires a valid, publicly accessible audio URL
    # For testing purposes, this will likely fail unless you provide a real URL
    
    try:
        result = transcriber.transcribe(
            audio_source=audio_url,
            language="en",
            response_format="verbose_json",
        )
        
        vcprint(result.text, "Transcription from URL", color="green")
    except Exception as e:
        vcprint(f"Expected: {str(e)}", "URL Test (Expected to Fail)", color="yellow")


def test_quality_metrics_analysis():
    """Test quality metrics calculation and warnings"""
    vcprint("\n" + "=" * 80, color="cyan")
    vcprint("TEST 6: Quality Metrics Analysis", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    transcriber = GroqTranscription(debug=True)
    
    audio_file = "/path/to/your/audio.wav"
    
    if not Path(audio_file).exists():
        vcprint(
            f"Skipping test - audio file not found: {audio_file}",
            "Test Skipped",
            color="yellow"
        )
        return
    
    result = transcriber.transcribe(
        audio_source=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )
    
    # Analyze quality metrics
    metrics = result.quality_metrics
    
    vcprint("Quality Analysis:", color="cyan")
    vcprint(f"Average Log Probability: {metrics.get('avg_logprob', 'N/A')}", color="blue")
    vcprint(f"Average No-Speech Probability: {metrics.get('avg_no_speech_prob', 'N/A')}", color="blue")
    vcprint(f"Average Compression Ratio: {metrics.get('avg_compression_ratio', 'N/A')}", color="blue")
    vcprint(f"Total Segments: {metrics.get('segment_count', 'N/A')}", color="blue")
    
    # Check for warnings
    if metrics.get("warning_low_confidence"):
        vcprint("⚠️ Low confidence detected in some segments", color="red")
    
    if metrics.get("warning_high_no_speech"):
        vcprint("⚠️ High no-speech probability in some segments (possible silence)", color="yellow")
    
    if metrics.get("warning_unusual_compression"):
        vcprint("⚠️ Unusual compression ratios detected", color="yellow")


def test_model_comparison():
    """Compare different Whisper models"""
    vcprint("\n" + "=" * 80, color="cyan")
    vcprint("TEST 7: Model Comparison", color="cyan")
    vcprint("=" * 80, color="cyan")
    
    audio_file = "/path/to/your/audio.wav"
    
    if not Path(audio_file).exists():
        vcprint(
            f"Skipping test - audio file not found: {audio_file}",
            "Test Skipped",
            color="yellow"
        )
        return
    
    models = ["whisper-large-v3-turbo", "whisper-large-v3"]
    
    for model in models:
        vcprint(f"\nTesting model: {model}", color="cyan")
        
        transcriber = GroqTranscription(default_model=model, debug=False)
        
        result = transcriber.transcribe(
            audio_source=audio_file,
            language="en",
            response_format="json",
        )
        
        vcprint(f"Model: {model}", color="blue")
        vcprint(f"Duration: {result.usage.duration_seconds:.2f}s", color="blue")
        vcprint(f"Billed Duration: {result.usage.billed_duration:.2f}s", color="blue")
        vcprint(f"Text: {result.text[:100]}...", color="green")


if __name__ == "__main__":
    vcprint("\n" + "=" * 80, color="magenta")
    vcprint("GROQ SPEECH-TO-TEXT TRANSCRIPTION TESTS", color="magenta")
    vcprint("=" * 80 + "\n", color="magenta")
    
    # Run tests
    test_basic_transcription()
    test_translation()
    test_audio_content_integration()
    test_unified_message_with_audio()
    test_url_transcription()
    test_quality_metrics_analysis()
    test_model_comparison()
    
    vcprint("\n" + "=" * 80, color="magenta")
    vcprint("ALL TESTS COMPLETED", color="magenta")
    vcprint("=" * 80 + "\n", color="magenta")
    
    vcprint("\nNOTE:", color="yellow")
    vcprint("Most tests are skipped because they require actual audio files.", color="yellow")
    vcprint("To run full tests, replace file paths with actual audio files.", color="yellow")
