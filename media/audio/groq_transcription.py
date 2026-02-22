"""
Groq Speech-to-Text Transcription Utility

Fast, cost-effective audio transcription using Groq's Whisper API.
Supports both transcription (any language to text) and translation (any language to English).

Recommended Model: whisper-large-v3-turbo (best price/performance with multilingual support)
"""

import os
import io
import base64
from typing import Dict, Any, Optional, Literal, Union
from dataclasses import dataclass, field
from pathlib import Path
from groq import Groq
from matrx_utils import vcprint


@dataclass
class TranscriptionUsage:
    """Track usage for transcription requests"""
    
    duration_seconds: float
    """Duration of the audio file in seconds"""
    
    model: str
    """Whisper model used for transcription"""
    
    language: Optional[str] = None
    """Language of the audio (ISO-639-1 format like 'en', 'es', 'tr')"""
    
    operation: Literal["transcription", "translation"] = "transcription"
    """Type of operation performed"""
    
    billed_duration: float = 0.0
    """Actual billed duration (minimum 10 seconds)"""
    
    file_size_mb: float = 0.0
    """Size of the audio file in MB"""
    
    response_format: str = "json"
    """Format of the response"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata from the transcription"""
    
    def __post_init__(self):
        """Calculate billed duration (minimum 10 seconds per Groq pricing)"""
        self.billed_duration = max(self.duration_seconds, 10.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "duration_seconds": self.duration_seconds,
            "billed_duration": self.billed_duration,
            "model": self.model,
            "language": self.language,
            "operation": self.operation,
            "file_size_mb": self.file_size_mb,
            "response_format": self.response_format,
            "metadata": self.metadata,
        }


@dataclass
class TranscriptionResult:
    """Result from a transcription or translation request"""
    
    text: str
    """The transcribed/translated text"""
    
    usage: TranscriptionUsage
    """Usage tracking information"""
    
    segments: Optional[list] = None
    """Detailed segment information (if verbose_json was requested)"""
    
    language: Optional[str] = None
    """Detected language (for transcriptions)"""
    
    duration: Optional[float] = None
    """Duration from response metadata"""
    
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    """Quality metrics (avg_logprob, no_speech_prob, compression_ratio)"""
    
    raw_response: Optional[Dict[str, Any]] = None
    """Full raw response from Groq API"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "text": self.text,
            "usage": self.usage.to_dict(),
            "segments": self.segments,
            "language": self.language,
            "duration": self.duration,
            "quality_metrics": self.quality_metrics,
        }


class GroqTranscription:
    """
    Groq Speech-to-Text Transcription Service
    
    Provides fast, cost-effective audio transcription using Groq's Whisper API.
    
    Features:
    - Transcription: Convert audio in any language to text in that language
    - Translation: Convert audio in any language to English text
    - Multiple Whisper models available
    - Automatic audio preprocessing
    - Usage tracking and quality metrics
    
    Recommended Model: whisper-large-v3-turbo
    """
    
    # Supported file formats
    SUPPORTED_FORMATS = ["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"]
    
    # Available Whisper models
    MODELS = {
        "whisper-large-v3": "Most accurate, multilingual, error-sensitive applications",
        "whisper-large-v3-turbo": "Best price/performance, multilingual (RECOMMENDED)",
    }
    
    # File size limits (in MB)
    MAX_FILE_SIZE_FREE = 25  # 25 MB for free tier
    MAX_FILE_SIZE_DEV = 100  # 100 MB for dev tier
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "whisper-large-v3-turbo",
        debug: bool = False,
    ):
        """
        Initialize Groq Transcription client
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            default_model: Default Whisper model to use
            debug: Enable debug logging
        """
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.default_model = default_model
        self.debug = debug
        
        if self.debug:
            vcprint(
                f"Initialized GroqTranscription with model: {self.default_model}",
                "Groq Transcription",
                color="blue"
            )
    
    def transcribe(
        self,
        audio_source: Union[str, bytes, io.BytesIO],
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Literal["json", "verbose_json", "text"] = "verbose_json",
        temperature: float = 0.0,
        timestamp_granularities: Optional[list] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio to text in the same language
        
        Args:
            audio_source: File path, URL, base64 data, or bytes
            model: Whisper model to use (defaults to default_model)
            language: Language of the input audio (ISO-639-1 format, e.g., 'en', 'es')
            prompt: Optional prompt to guide transcription style (max 224 tokens)
            response_format: Output format (json, verbose_json, or text)
            temperature: Sampling temperature (0-1, default 0 for deterministic)
            timestamp_granularities: List of ["word", "segment"] for timestamps
        
        Returns:
            TranscriptionResult with text and metadata
        """
        model = model or self.default_model
        
        if self.debug:
            vcprint(
                f"Starting transcription with model: {model}",
                "Groq Transcription",
                color="cyan"
            )
        
        # Prepare audio file
        file_tuple, file_size_mb = self._prepare_audio_file(audio_source)
        
        # Build request parameters
        request_params = {
            "file": file_tuple,
            "model": model,
            "response_format": response_format,
            "temperature": temperature,
        }
        
        if language:
            request_params["language"] = language
        
        if prompt:
            request_params["prompt"] = prompt
        
        if timestamp_granularities and response_format == "verbose_json":
            request_params["timestamp_granularities"] = timestamp_granularities
        
        # Make API call
        try:
            response = self.client.audio.transcriptions.create(**request_params)
            
            if self.debug:
                vcprint(response, "Groq Transcription Response", color="green")
            
            # Parse response
            return self._parse_response(
                response,
                model=model,
                operation="transcription",
                file_size_mb=file_size_mb,
                response_format=response_format,
            )
        
        except Exception as e:
            vcprint(f"Transcription error: {str(e)}", "Groq Transcription Error", color="red")
            raise
    
    def translate(
        self,
        audio_source: Union[str, bytes, io.BytesIO],
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Literal["json", "text"] = "json",
        temperature: float = 0.0,
    ) -> TranscriptionResult:
        """
        Translate audio to English text
        
        Args:
            audio_source: File path, URL, base64 data, or bytes
            model: Whisper model to use (defaults to default_model)
            prompt: Optional prompt to guide translation style (max 224 tokens)
            response_format: Output format (json or text)
            temperature: Sampling temperature (0-1, default 0 for deterministic)
        
        Returns:
            TranscriptionResult with English text and metadata
        """
        model = model or self.default_model
        
        if self.debug:
            vcprint(
                f"Starting translation with model: {model}",
                "Groq Translation",
                color="cyan"
            )
        
        # Prepare audio file
        file_tuple, file_size_mb = self._prepare_audio_file(audio_source)
        
        # Build request parameters
        request_params = {
            "file": file_tuple,
            "model": model,
            "response_format": response_format,
            "temperature": temperature,
            "language": "en",  # Translation endpoint only supports English
        }
        
        if prompt:
            request_params["prompt"] = prompt
        
        # Make API call
        try:
            response = self.client.audio.translations.create(**request_params)
            
            if self.debug:
                vcprint(response, "Groq Translation Response", color="green")
            
            # Parse response
            return self._parse_response(
                response,
                model=model,
                operation="translation",
                file_size_mb=file_size_mb,
                response_format=response_format,
            )
        
        except Exception as e:
            vcprint(f"Translation error: {str(e)}", "Groq Translation Error", color="red")
            raise
    
    def _prepare_audio_file(
        self, audio_source: Union[str, bytes, io.BytesIO]
    ) -> tuple:
        """
        Prepare audio file for API request
        
        Returns:
            Tuple of (file_tuple, file_size_mb)
        """
        if isinstance(audio_source, str):
            # Could be file path or URL
            if audio_source.startswith(("http://", "https://")):
                # It's a URL - download it first
                from media.persistence import fetch_media
                audio_data = fetch_media(audio_source, target_format="bytes")
                file_tuple = ("audio.wav", audio_data)
                file_size_mb = len(audio_data) / (1024 * 1024)
            elif audio_source.startswith("data:"):
                # It's a base64 data URI
                audio_data = base64.b64decode(audio_source.split(",")[1])
                file_tuple = ("audio.wav", audio_data)
                file_size_mb = len(audio_data) / (1024 * 1024)
            else:
                # It's a file path
                file_path = Path(audio_source)
                if not file_path.exists():
                    raise FileNotFoundError(f"Audio file not found: {audio_source}")
                
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                file_tuple = (file_path.name, open(file_path, "rb"))
        
        elif isinstance(audio_source, bytes):
            # Raw bytes
            file_tuple = ("audio.wav", audio_source)
            file_size_mb = len(audio_source) / (1024 * 1024)
        
        elif isinstance(audio_source, io.BytesIO):
            # BytesIO object
            audio_data = audio_source.getvalue()
            file_tuple = ("audio.wav", audio_data)
            file_size_mb = len(audio_data) / (1024 * 1024)
        
        else:
            raise ValueError(f"Unsupported audio_source type: {type(audio_source)}")
        
        # Check file size
        if file_size_mb > self.MAX_FILE_SIZE_DEV:
            raise ValueError(
                f"Audio file too large ({file_size_mb:.2f} MB). "
                f"Maximum size is {self.MAX_FILE_SIZE_DEV} MB. "
                "Consider chunking the audio file."
            )
        
        if self.debug:
            vcprint(f"Prepared audio file: {file_size_mb:.2f} MB", color="blue")
        
        return file_tuple, file_size_mb
    
    def _parse_response(
        self,
        response: Any,
        model: str,
        operation: Literal["transcription", "translation"],
        file_size_mb: float,
        response_format: str,
    ) -> TranscriptionResult:
        """Parse API response into TranscriptionResult"""
        
        # Extract text
        if isinstance(response, str):
            text = response
            segments = None
            duration = None
            language = None
            quality_metrics = {}
            raw_response = None
        else:
            # Response is an object
            text = response.text if hasattr(response, "text") else str(response)
            
            # Extract verbose_json fields if available
            segments = getattr(response, "segments", None)
            duration = getattr(response, "duration", None)
            language = getattr(response, "language", None)
            
            # Calculate quality metrics from segments
            quality_metrics = {}
            if segments:
                quality_metrics = self._calculate_quality_metrics(segments)
            
            # Store raw response
            raw_response = response.model_dump() if hasattr(response, "model_dump") else None
        
        # Create usage tracking
        usage = TranscriptionUsage(
            duration_seconds=duration or 0.0,
            model=model,
            language=language,
            operation=operation,
            file_size_mb=file_size_mb,
            response_format=response_format,
            metadata={
                "has_segments": segments is not None,
                "segment_count": len(segments) if segments else 0,
            }
        )
        
        return TranscriptionResult(
            text=text,
            usage=usage,
            segments=segments,
            language=language,
            duration=duration,
            quality_metrics=quality_metrics,
            raw_response=raw_response,
        )
    
    def _calculate_quality_metrics(self, segments: list) -> Dict[str, Any]:
        """
        Calculate aggregate quality metrics from segments
        
        Metrics:
        - avg_logprob: Average log probability (closer to 0 = higher confidence)
        - no_speech_prob: Probability of no speech (closer to 0 = definitely speech)
        - compression_ratio: Speech pattern indicator (1.5-2.5 is normal)
        """
        if not segments:
            return {}
        
        total_logprob = 0.0
        total_no_speech = 0.0
        total_compression = 0.0
        count = 0
        
        low_confidence_segments = []
        high_no_speech_segments = []
        unusual_compression_segments = []
        
        for segment in segments:
            if isinstance(segment, dict):
                avg_logprob = segment.get("avg_logprob", 0)
                no_speech_prob = segment.get("no_speech_prob", 0)
                compression_ratio = segment.get("compression_ratio", 0)
            else:
                avg_logprob = getattr(segment, "avg_logprob", 0)
                no_speech_prob = getattr(segment, "no_speech_prob", 0)
                compression_ratio = getattr(segment, "compression_ratio", 0)
            
            total_logprob += avg_logprob
            total_no_speech += no_speech_prob
            total_compression += compression_ratio
            count += 1
            
            # Flag problematic segments
            if avg_logprob < -0.5:  # Low confidence
                low_confidence_segments.append({
                    "id": segment.get("id") if isinstance(segment, dict) else getattr(segment, "id", None),
                    "start": segment.get("start") if isinstance(segment, dict) else getattr(segment, "start", None),
                    "end": segment.get("end") if isinstance(segment, dict) else getattr(segment, "end", None),
                    "avg_logprob": avg_logprob,
                })
            
            if no_speech_prob > 0.5:  # Likely not speech
                high_no_speech_segments.append({
                    "id": segment.get("id") if isinstance(segment, dict) else getattr(segment, "id", None),
                    "start": segment.get("start") if isinstance(segment, dict) else getattr(segment, "start", None),
                    "end": segment.get("end") if isinstance(segment, dict) else getattr(segment, "end", None),
                    "no_speech_prob": no_speech_prob,
                })
            
            if compression_ratio < 1.0 or compression_ratio > 3.0:  # Unusual
                unusual_compression_segments.append({
                    "id": segment.get("id") if isinstance(segment, dict) else getattr(segment, "id", None),
                    "start": segment.get("start") if isinstance(segment, dict) else getattr(segment, "start", None),
                    "end": segment.get("end") if isinstance(segment, dict) else getattr(segment, "end", None),
                    "compression_ratio": compression_ratio,
                })
        
        metrics = {
            "avg_logprob": total_logprob / count if count > 0 else 0,
            "avg_no_speech_prob": total_no_speech / count if count > 0 else 0,
            "avg_compression_ratio": total_compression / count if count > 0 else 0,
            "segment_count": count,
        }
        
        # Add warnings for problematic segments
        if low_confidence_segments:
            metrics["low_confidence_segments"] = low_confidence_segments
            metrics["warning_low_confidence"] = True
        
        if high_no_speech_segments:
            metrics["high_no_speech_segments"] = high_no_speech_segments
            metrics["warning_high_no_speech"] = True
        
        if unusual_compression_segments:
            metrics["unusual_compression_segments"] = unusual_compression_segments
            metrics["warning_unusual_compression"] = True
        
        return metrics
