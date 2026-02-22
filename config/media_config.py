import dataclasses
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Union
from google.genai.types import Part
from matrx_utils import vcprint
from media.mime_utils import detect_mime_type


# Unified storage kind discriminator for all media types
MediaKind = Literal["image", "audio", "video", "document", "youtube"]


@dataclass
class ImageContent:
    type: Literal["image", "input_image"] = "image"
    url: Optional[str] = None
    base64_data: Optional[str] = None
    file_uri: Optional[str] = None
    mime_type: Optional[str] = None
    media_resolution: Optional[str] = None
    alt: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-detect mime_type if not provided, and move alt to metadata"""
        if self.mime_type is None:
            self.mime_type = detect_mime_type(
                url=self.url, base64_data=self.base64_data, file_uri=self.file_uri
            )
        # Move alt to metadata if provided
        if self.alt is not None:
            self.metadata["alt"] = self.alt
            self.alt = None

        vcprint(f"--> ImageContent MIME Type: {self.mime_type}")

    def get_output(self) -> Optional[str]:
        if self.url:
            return self.url
        elif self.base64_data:
            return self.base64_data
        elif self.file_uri:
            return self.file_uri
        return None

    def to_google(self) -> Optional[dict[str, Any]]:
        """Convert to Google Gemini format"""
        from media.persistence import fetch_media

        # Google prefers file_uri, then inline_data
        if self.file_uri:
            part = {
                "fileData": {
                    "fileUri": self.file_uri,
                    "mimeType": self.mime_type,
                }
            }
        elif self.base64_data:
            part = {
                "inlineData": {
                    "data": self.base64_data,
                    "mimeType": self.mime_type,
                }
            }
        elif self.url:
            # Fetch from URL and convert to base64 for inline_data
            base64_data = fetch_media(self.url, target_format="base64")
            part = {
                "inlineData": {
                    "data": base64_data,
                    "mimeType": self.mime_type,
                }
            }
        else:
            return None

        if self.media_resolution:
            part["mediaResolution"] = {"level": self.media_resolution}
        return part

    def to_openai(self) -> Optional[dict[str, Any]]:
        """Convert to OpenAI format"""
        if self.url:
            return {"type": "input_image", "image_url": self.url}
        elif self.base64_data:
            return {
                "type": "input_image",
                "image": {
                    "data": self.base64_data,
                    "mime_type": self.mime_type,
                },
            }
        return None

    def to_anthropic(self) -> Optional[dict[str, Any]]:
        """Convert to Anthropic format"""
        if self.url:
            return {"type": "image", "source": {"type": "url", "url": self.url}}
        elif self.base64_data:
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": self.mime_type,
                    "data": self.base64_data,
                },
            }
        return None

    @classmethod
    def from_google(cls, part: Part) -> Optional["ImageContent"]:
        """Create ImageContent from Google Part object"""
        from media.persistence import save_media

        # Google can return images via inline_data or file_data
        if part.inline_data:
            # Save base64 data to Supabase to prevent data loss
            url = save_media(
                content=part.inline_data.data, mime_type=part.inline_data.mime_type
            )
            return cls(url=url, mime_type=part.inline_data.mime_type)
        elif part.file_data:
            # File URI is already persistent, just use it
            return cls(
                file_uri=part.file_data.file_uri, mime_type=part.file_data.mime_type
            )
        return None

    def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]:
        """Convert to dict with optional base64 truncation"""
        result = dataclasses.asdict(self)
        if truncate_base64 and result.get("base64_data"):
            result["base64_data"] = f"<{len(self.base64_data)} chars>"
        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to unified media storage format for database persistence."""
        result: dict[str, Any] = {
            "type": "media",
            "kind": "image",
        }
        if self.url:
            result["url"] = self.url
        if self.base64_data:
            result["base64_data"] = self.base64_data
        if self.file_uri:
            result["file_uri"] = self.file_uri
        if self.mime_type:
            result["mime_type"] = self.mime_type
        # Kind-specific extras go into metadata
        storage_metadata = {**self.metadata}
        if self.media_resolution:
            storage_metadata["media_resolution"] = self.media_resolution
        if storage_metadata:
            result["metadata"] = storage_metadata
        return result

    def __repr__(self) -> str:
        """Custom repr that only truncates base64_data"""
        base64_display = (
            f"<{len(self.base64_data)} chars>" if self.base64_data else None
        )
        return (
            f"ImageContent("
            f"type={self.type!r}, "
            f"url={self.url!r}, "
            f"base64_data={base64_display}, "
            f"file_uri={self.file_uri!r}, "
            f"mime_type={self.mime_type!r}, "
            f"media_resolution={self.media_resolution!r}, "
            f"alt={self.alt!r}, "
            f"metadata={self.metadata!r}"
        )


@dataclass
class AudioContent:
    type: Literal["audio", "input_audio"] = "audio"
    url: Optional[str] = None
    base64_data: Optional[str] = None
    file_uri: Optional[str] = None
    mime_type: Optional[str] = None

    # Transcription settings
    auto_transcribe: bool = False
    """If True, automatically transcribe audio to text using Groq Whisper API"""

    transcription_model: str = "whisper-large-v3-turbo"
    """Whisper model to use for transcription"""

    transcription_language: Optional[str] = None
    """Language of the audio (ISO-639-1 format like 'en', 'es'). Auto-detected if None."""

    transcription_result: Optional[str] = None
    """Cached transcription result (set after transcription)"""

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-detect mime_type if not provided"""
        if self.mime_type is None:
            self.mime_type = detect_mime_type(
                url=self.url, base64_data=self.base64_data, file_uri=self.file_uri
            )

    def get_output(self) -> Optional[str]:
        """Get the output of the audio."""
        if self.transcription_result:
            return self.transcription_result
        elif self.url:
            return self.url
        elif self.base64_data:
            return self.base64_data
        elif self.file_uri:
            return self.file_uri
        return None

    def get_transcription(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get transcription of the audio content using Groq Whisper API.

        Uses a global cache to avoid re-transcribing the same audio across
        different requests. Cache is keyed by (audio_source, model, language).

        Args:
            force_refresh: If True, re-transcribe even if cached result exists

        Returns:
            Transcribed text or None if transcription fails
        """
        # Return cached result from instance if available and not forcing refresh
        if self.transcription_result and not force_refresh:
            return self.transcription_result

        # Determine audio source
        audio_source = self.url or self.file_uri or self.base64_data
        if not audio_source:
            vcprint("No audio source available for transcription", color="yellow")
            return None

        # Check global cache (unless forcing refresh)
        if not force_refresh:
            from media.audio.transcription_cache import get_cache

            cache = get_cache()
            cached = cache.get(
                audio_source=audio_source,
                model=self.transcription_model,
                language=self.transcription_language,
            )

            if cached:
                # Use cached transcription
                self.transcription_result = cached.text
                self.metadata["transcription"] = cached.metadata
                self.metadata["transcription"]["from_cache"] = True

                vcprint(
                    f"Using cached transcription for audio ({len(cached.text)} characters)",
                    "Audio Transcription",
                    color="green",
                )
                return self.transcription_result

        # Perform transcription
        try:
            from media.audio.groq_transcription import GroqTranscription
            from media.audio.transcription_cache import get_cache

            transcriber = GroqTranscription(default_model=self.transcription_model)

            # Transcribe
            result = transcriber.transcribe(
                audio_source=audio_source,
                language=self.transcription_language,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

            # Cache result in instance
            self.transcription_result = result.text

            # Store usage metadata
            metadata = {
                "usage": result.usage.to_dict(),
                "quality_metrics": result.quality_metrics,
                "language": result.language,
                "duration": result.duration,
                "from_cache": False,
            }
            self.metadata["transcription"] = metadata

            # Store in global cache
            cache = get_cache()
            cache.set(
                audio_source=audio_source,
                model=self.transcription_model,
                language=self.transcription_language,
                text=result.text,
                metadata=metadata,
            )

            return self.transcription_result

        except Exception as e:
            vcprint(
                f"Transcription failed: {str(e)}",
                "Audio Transcription Error",
                color="red",
            )
            return None

    def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]:
        """Convert to dict with optional base64 truncation"""
        result = dataclasses.asdict(self)
        if truncate_base64 and result.get("base64_data"):
            result["base64_data"] = f"<{len(self.base64_data)} chars>"
        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to unified media storage format for database persistence."""
        result: dict[str, Any] = {
            "type": "media",
            "kind": "audio",
        }
        if self.url:
            result["url"] = self.url
        if self.base64_data:
            result["base64_data"] = self.base64_data
        if self.file_uri:
            result["file_uri"] = self.file_uri
        if self.mime_type:
            result["mime_type"] = self.mime_type
        # Kind-specific extras go into metadata
        storage_metadata = {**self.metadata}
        if self.auto_transcribe:
            storage_metadata["auto_transcribe"] = self.auto_transcribe
        if self.transcription_model != "whisper-large-v3-turbo":
            storage_metadata["transcription_model"] = self.transcription_model
        if self.transcription_language:
            storage_metadata["transcription_language"] = self.transcription_language
        if self.transcription_result:
            storage_metadata["transcription_result"] = self.transcription_result
        if storage_metadata:
            result["metadata"] = storage_metadata
        return result

    def __repr__(self) -> str:
        """Custom repr that only truncates base64_data"""
        base64_display = (
            f"<{len(self.base64_data)} chars>" if self.base64_data else None
        )
        return (
            f"AudioContent("
            f"type={self.type!r}, "
            f"url={self.url!r}, "
            f"base64_data={base64_display}, "
            f"file_uri={self.file_uri!r}, "
            f"mime_type={self.mime_type!r}, "
            f"auto_transcribe={self.auto_transcribe!r}, "
            f"transcription_model={self.transcription_model!r}, "
            f"transcription_language={self.transcription_language!r}, "
            f"transcription_result={self.transcription_result!r}, "
            f"metadata={self.metadata!r})"
        )

    def to_google(self) -> Optional[dict[str, Any]]:
        """Convert to Google Gemini format"""
        from media.persistence import fetch_media

        if self.file_uri:
            return {
                "fileData": {
                    "fileUri": self.file_uri,
                    "mimeType": self.mime_type,
                }
            }
        elif self.base64_data:
            return {
                "inlineData": {
                    "data": self.base64_data,
                    "mimeType": self.mime_type,
                }
            }
        elif self.url:
            # Fetch from URL and convert to base64
            base64_data = fetch_media(self.url, target_format="base64")
            return {
                "inlineData": {
                    "data": base64_data,
                    "mimeType": self.mime_type,
                }
            }
        return None

    def to_openai(self) -> Optional[dict[str, Any]]:
        """Convert to OpenAI format - not yet supported"""
        # OpenAI doesn't have audio input in Responses API yet
        return None

    def to_anthropic(self) -> Optional[dict[str, Any]]:
        """Convert to Anthropic format - not yet supported"""
        # Anthropic doesn't support audio input yet
        return None

    @classmethod
    def from_google(cls, part: Part) -> Optional["AudioContent"]:
        """Create AudioContent from Google Part object"""
        from media.persistence import save_media

        if hasattr(part, "inline_data") and part.inline_data:
            # Save to Supabase to prevent data loss
            url = save_media(
                content=part.inline_data.data, mime_type=part.inline_data.mime_type
            )
            return cls(url=url, mime_type=part.inline_data.mime_type)
        elif hasattr(part, "file_data") and part.file_data:
            return cls(
                file_uri=part.file_data.file_uri, mime_type=part.file_data.mime_type
            )
        return None


@dataclass
class VideoContent:
    type: Literal["video", "input_video"] = "video"
    url: Optional[str] = None
    base64_data: Optional[str] = None
    file_uri: Optional[str] = None
    mime_type: Optional[str] = None
    video_metadata: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-detect mime_type if not provided"""
        if self.mime_type is None:
            self.mime_type = detect_mime_type(
                url=self.url, base64_data=self.base64_data, file_uri=self.file_uri
            )

    def get_output(self) -> Optional[str]:
        """Get the output of the video."""
        if self.url:
            return self.url
        elif self.base64_data:
            return self.base64_data
        elif self.file_uri:
            return self.file_uri
        return None

    def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]:
        """Convert to dict with optional base64 truncation"""
        result = dataclasses.asdict(self)
        if truncate_base64 and result.get("base64_data"):
            result["base64_data"] = f"<{len(self.base64_data)} chars>"
        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to unified media storage format for database persistence."""
        result: dict[str, Any] = {
            "type": "media",
            "kind": "video",
        }
        if self.url:
            result["url"] = self.url
        if self.base64_data:
            result["base64_data"] = self.base64_data
        if self.file_uri:
            result["file_uri"] = self.file_uri
        if self.mime_type:
            result["mime_type"] = self.mime_type
        # Kind-specific extras go into metadata
        storage_metadata = {**self.metadata}
        if self.video_metadata:
            storage_metadata["video_metadata"] = self.video_metadata
        if storage_metadata:
            result["metadata"] = storage_metadata
        return result

    def __repr__(self) -> str:
        """Custom repr that only truncates base64_data"""
        base64_display = (
            f"<{len(self.base64_data)} chars>" if self.base64_data else None
        )
        return (
            f"VideoContent("
            f"type={self.type!r}, "
            f"url={self.url!r}, "
            f"base64_data={base64_display}, "
            f"file_uri={self.file_uri!r}, "
            f"mime_type={self.mime_type!r}, "
            f"video_metadata={self.video_metadata!r}, "
            f"metadata={self.metadata!r})"
        )

    def to_google(self) -> Optional[dict[str, Any]]:
        """Convert to Google Gemini format"""
        from media.persistence import fetch_media

        if self.file_uri:
            part = {
                "fileData": {
                    "fileUri": self.file_uri,
                    "mimeType": self.mime_type,
                }
            }
        elif self.base64_data:
            part = {
                "inlineData": {
                    "data": self.base64_data,
                    "mimeType": self.mime_type,
                }
            }
        elif self.url:
            # Fetch from URL and convert to base64
            base64_data = fetch_media(self.url, target_format="base64")
            part = {
                "inlineData": {
                    "data": base64_data,
                    "mimeType": self.mime_type,
                }
            }
        else:
            return None

        if self.video_metadata:
            part["videoMetadata"] = self.video_metadata
        return part

    def to_openai(self) -> Optional[dict[str, Any]]:
        """Convert to OpenAI format - not yet supported"""
        # OpenAI doesn't support video input yet
        return None

    def to_anthropic(self) -> Optional[dict[str, Any]]:
        """Convert to Anthropic format - not yet supported"""
        # Anthropic doesn't support video input yet
        return None

    @classmethod
    def from_google(cls, part: Part) -> Optional["VideoContent"]:
        """Create VideoContent from Google Part object"""
        from media.persistence import save_media

        video_metadata = None
        if hasattr(part, "video_metadata") and part.video_metadata:
            video_metadata = {
                "start_offset": getattr(part.video_metadata, "start_offset", None),
                "end_offset": getattr(part.video_metadata, "end_offset", None),
                "fps": getattr(part.video_metadata, "fps", None),
            }

        if hasattr(part, "inline_data") and part.inline_data:
            # Save to Supabase to prevent data loss
            url = save_media(
                content=part.inline_data.data, mime_type=part.inline_data.mime_type
            )
            return cls(
                url=url,
                mime_type=part.inline_data.mime_type,
                video_metadata=video_metadata,
            )
        elif hasattr(part, "file_data") and part.file_data:
            # File URI is already persistent
            return cls(
                file_uri=part.file_data.file_uri,
                mime_type=part.file_data.mime_type,
                video_metadata=video_metadata,
            )
        return None


@dataclass
class YouTubeVideoContent:
    """
    YouTube video content that can ONLY be processed by Google Gemini.

    Google Gemini accepts YouTube URLs directly via fileData.fileUri.
    All other providers will skip this content with a warning.

    Example YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    """

    type: Literal["youtube_video"] = "youtube_video"
    url: str = ""
    video_metadata: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_output(self) -> str:
        """Get the output of the YouTube video."""
        return self.url

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to unified media storage format for database persistence."""
        result: dict[str, Any] = {
            "type": "media",
            "kind": "youtube",
            "url": self.url,
        }
        # Kind-specific extras go into metadata
        storage_metadata = {**self.metadata}
        if self.video_metadata:
            storage_metadata["video_metadata"] = self.video_metadata
        if storage_metadata:
            result["metadata"] = storage_metadata
        return result

    def to_google(self) -> Optional[dict[str, Any]]:
        """Convert to Google Gemini format - YouTube URLs supported via fileData"""
        if not self.url:
            return None

        # Google accepts YouTube URLs directly in fileUri
        part = {
            "fileData": {
                "fileUri": self.url,
            }
        }

        if self.video_metadata:
            part["videoMetadata"] = self.video_metadata

        return part

    def to_openai(self) -> Optional[dict[str, Any]]:
        """OpenAI doesn't support YouTube URLs - skip with warning"""
        from matrx_utils import vcprint

        vcprint(
            f"YouTube URL '{self.url}' is not supported by OpenAI models and will be skipped.",
            "YouTube URL Warning",
            color="yellow",
        )
        return None

    def to_anthropic(self) -> Optional[dict[str, Any]]:
        """Anthropic doesn't support YouTube URLs - skip with warning"""
        from matrx_utils import vcprint

        vcprint(
            f"YouTube URL '{self.url}' is not supported by Anthropic models and will be skipped.",
            "YouTube URL Warning",
            color="yellow",
        )
        return None

    @classmethod
    def from_google(cls, part: Part) -> Optional["YouTubeVideoContent"]:
        """
        Create YouTubeVideoContent from Google Part object.

        Only creates if the file_uri is a YouTube URL.
        """
        if not hasattr(part, "file_data") or not part.file_data:
            return None

        file_uri = getattr(part.file_data, "file_uri", "")

        # Check if it's a YouTube URL
        if not file_uri or not ("youtube.com" in file_uri or "youtu.be" in file_uri):
            return None

        video_metadata = None
        if hasattr(part, "video_metadata") and part.video_metadata:
            video_metadata = {
                "start_offset": getattr(part.video_metadata, "start_offset", None),
                "end_offset": getattr(part.video_metadata, "end_offset", None),
                "fps": getattr(part.video_metadata, "fps", None),
            }

        return cls(
            url=file_uri,
            video_metadata=video_metadata,
        )


@dataclass
class DocumentContent:
    type: Literal["document", "input_document"] = "document"
    url: Optional[str] = None
    base64_data: Optional[str] = None
    file_uri: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-detect mime_type if not provided"""
        if self.mime_type is None:
            self.mime_type = detect_mime_type(
                url=self.url, base64_data=self.base64_data, file_uri=self.file_uri
            )

    def get_output(self) -> Optional[str]:
        """Get the output of the document."""
        if self.url:
            return self.url
        elif self.base64_data:
            return self.base64_data
        elif self.file_uri:
            return self.file_uri
        return None

    def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]:
        """Convert to dict with optional base64 truncation"""
        result = dataclasses.asdict(self)
        if truncate_base64 and result.get("base64_data"):
            result["base64_data"] = f"<{len(self.base64_data)} chars>"
        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to unified media storage format for database persistence."""
        result: dict[str, Any] = {
            "type": "media",
            "kind": "document",
        }
        if self.url:
            result["url"] = self.url
        if self.base64_data:
            result["base64_data"] = self.base64_data
        if self.file_uri:
            result["file_uri"] = self.file_uri
        if self.mime_type:
            result["mime_type"] = self.mime_type
        if self.metadata:
            result["metadata"] = {**self.metadata}
        return result

    def __repr__(self) -> str:
        """Custom repr that only truncates base64_data"""
        base64_display = (
            f"<{len(self.base64_data)} chars>" if self.base64_data else None
        )
        return (
            f"DocumentContent("
            f"type={self.type!r}, "
            f"url={self.url!r}, "
            f"base64_data={base64_display}, "
            f"file_uri={self.file_uri!r}, "
            f"mime_type={self.mime_type!r}, "
            f"metadata={self.metadata!r})"
        )

    def to_google(self) -> Optional[dict[str, Any]]:
        """Convert to Google Gemini format"""
        from media.persistence import fetch_media

        if self.file_uri:
            return {
                "fileData": {
                    "fileUri": self.file_uri,
                    "mimeType": self.mime_type,
                }
            }
        elif self.base64_data:
            return {
                "inlineData": {
                    "data": self.base64_data,
                    "mimeType": self.mime_type,
                }
            }
        elif self.url:
            # Fetch from URL and convert to base64
            base64_data = fetch_media(self.url, target_format="base64")
            return {
                "inlineData": {
                    "data": base64_data,
                    "mimeType": self.mime_type,
                }
            }
        return None

    def to_openai(self) -> Optional[dict[str, Any]]:
        """Convert to OpenAI format"""
        # file_url
        return {
            "type": "input_file",
            "file_url": self.url,
        }

    def to_anthropic(self) -> Optional[dict[str, Any]]:
        """Convert to Anthropic format"""
        if self.base64_data:
            return {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": self.mime_type,
                    "data": self.base64_data,
                },
            }
        elif self.url:
            return {"type": "document", "source": {"type": "url", "url": self.url}}
        return None

    @classmethod
    def from_google(cls, part: Part) -> Optional["DocumentContent"]:
        """Create DocumentContent from Google Part object"""
        from media.persistence import save_media

        if hasattr(part, "inline_data") and part.inline_data:
            # Save to Supabase to prevent data loss
            url = save_media(
                content=part.inline_data.data, mime_type=part.inline_data.mime_type
            )
            return cls(url=url, mime_type=part.inline_data.mime_type)
        elif hasattr(part, "file_data") and part.file_data:
            # File URI is already persistent
            return cls(
                file_uri=part.file_data.file_uri, mime_type=part.file_data.mime_type
            )
        return None


# ============================================================================
# UNIFIED MEDIA STORAGE RECONSTRUCTION
# ============================================================================

# Union of all media content types
MediaContent = Union[ImageContent, AudioContent, VideoContent, YouTubeVideoContent, DocumentContent]


def reconstruct_media_content(
    block: dict[str, Any],
) -> Optional[MediaContent]:
    """
    Reconstruct the correct media content class from a unified storage dict.

    Reads the 'kind' field from a block with type="media" and constructs the
    appropriate original class (ImageContent, AudioContent, etc.).

    This is the deserialization counterpart to each class's to_storage_dict() method.

    Args:
        block: Dict with type="media", kind=<MediaKind>, and common/kind-specific fields.

    Returns:
        The appropriate media content instance, or None if kind is unknown.
    """
    kind = block.get("kind")
    meta = block.get("metadata", {})

    if kind == "image":
        return ImageContent(
            url=block.get("url"),
            base64_data=block.get("base64_data"),
            file_uri=block.get("file_uri"),
            mime_type=block.get("mime_type"),
            media_resolution=meta.get("media_resolution"),
            metadata=meta,
        )
    elif kind == "audio":
        return AudioContent(
            url=block.get("url"),
            base64_data=block.get("base64_data"),
            file_uri=block.get("file_uri"),
            mime_type=block.get("mime_type"),
            auto_transcribe=meta.get("auto_transcribe", False),
            transcription_model=meta.get("transcription_model", "whisper-large-v3-turbo"),
            transcription_language=meta.get("transcription_language"),
            transcription_result=meta.get("transcription_result"),
            metadata=meta,
        )
    elif kind == "video":
        return VideoContent(
            url=block.get("url"),
            base64_data=block.get("base64_data"),
            file_uri=block.get("file_uri"),
            mime_type=block.get("mime_type"),
            video_metadata=meta.get("video_metadata"),
            metadata=meta,
        )
    elif kind == "youtube":
        return YouTubeVideoContent(
            url=block.get("url", ""),
            video_metadata=meta.get("video_metadata"),
            metadata=meta,
        )
    elif kind == "document":
        return DocumentContent(
            url=block.get("url"),
            base64_data=block.get("base64_data"),
            file_uri=block.get("file_uri"),
            mime_type=block.get("mime_type"),
            metadata=meta,
        )
    else:
        vcprint(
            block,
            f"WARNING: Unknown media kind: {kind}",
            color="red",
        )
        return None
