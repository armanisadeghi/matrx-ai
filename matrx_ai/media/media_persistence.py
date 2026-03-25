"""
AI Media Persistence Handler

Handles media upload/download for AI-generated content.
Uses FileHandler for Supabase operations and ExecutionContext for user tracking.
"""

import base64
import struct
import uuid
from typing import Literal

from matrx_utils import FileHandler, vcprint


class AIMediaHandler:
    """Handles media persistence for AI content conversions"""

    _instance = None

    def __init__(self):
        self.file_handler = FileHandler.get_instance(
            app_name="ai_media"
        )

    @classmethod
    def get_instance(cls):
        """Singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_response_media(
        self,
        content: str | bytes,
        mime_type: str,
        audio_format: str | None = None,
    ) -> str:
        """Save AI-generated media to Supabase.

        Pipeline for audio content:
          1. Decode base64 if needed
          2. Normalize raw PCM (audio/L16, audio/pcm) → WAV with RIFF header
          3. Transcode to target format if audio_format is specified (e.g. "mp3", "ogg")
          4. Upload with the correct mime type and file extension

        audio_format options: "wav" (default for audio), "mp3", "ogg"
        Non-audio content is uploaded as-is.

        Reads ``user_id`` from the current ``ExecutionContext``.
        """
        from matrx_ai.context.app_context import get_app_context
        exec_ctx = get_app_context()

        if isinstance(content, str):
            content = base64.b64decode(content)

        # Step 1: Normalize raw PCM → WAV
        content, mime_type = self._normalize_audio(content, mime_type)

        # Step 2: Transcode audio if a specific output format is requested
        if audio_format and mime_type.startswith("audio/"):
            content, mime_type = self._transcode_audio(content, mime_type, audio_format)

        file_id = str(uuid.uuid4())
        ext = self._get_extension_from_mime(mime_type)

        path = f"{exec_ctx.user_id}/{file_id}{ext}"

        url = self.file_handler.write_to_supabase(
            path=path,
            content=content,
            file_options={
                "content-type": mime_type,
                "cache-control": "3600",
                "upsert": "false",
            },
        )

        return url

    @staticmethod
    def _transcode_audio(
        content: bytes, source_mime: str, target_format: str
    ) -> tuple[bytes, str]:
        """Transcode audio bytes to the requested format using pydub.

        Args:
            content: WAV bytes (PCM normalization must already be done)
            source_mime: current mime type (e.g. "audio/wav")
            target_format: desired format string, e.g. "mp3", "ogg", "wav"

        Returns:
            (transcoded_bytes, new_mime_type)
        """
        format_to_mime = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "ogg": "audio/ogg",
        }

        target_format = target_format.lower().strip()
        target_mime = format_to_mime.get(target_format)

        if not target_mime:
            vcprint(
                f"Unsupported audio_format '{target_format}' — supported: {list(format_to_mime)}. Keeping current format.",
                "AIMediaHandler",
                color="yellow",
            )
            return content, source_mime

        # No-op if already in the desired format
        source_base = source_mime.split(";")[0].strip().lower()
        if source_base == target_mime:
            return content, source_mime

        try:
            from pydub import AudioSegment
            import io

            source_format = source_base.split("/")[-1]
            if source_format == "mpeg":
                source_format = "mp3"

            audio = AudioSegment.from_file(io.BytesIO(content), format=source_format)
            output = io.BytesIO()
            audio.export(output, format=target_format)
            return output.getvalue(), target_mime

        except Exception as e:
            vcprint(
                f"Audio transcoding to '{target_format}' failed: {e}. Keeping WAV.",
                "AIMediaHandler",
                color="red",
            )
            return content, source_mime

    def fetch_media(
        self, url: str, target_format: Literal["base64", "bytes"] = "base64"
    ) -> str | bytes:
        """
        Fetch media from URL and convert to requested format.

        Args:
            url: URL to fetch from
            target_format: "base64" or "bytes"

        Returns:
            Media content in requested format
        """
        import requests

        response = requests.get(url)
        response.raise_for_status()

        content = response.content

        if target_format == "base64":
            return base64.b64encode(content).decode("utf-8")
        return content

    def _get_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type.

        For raw PCM types (audio/L16, audio/pcm) the caller should have already
        converted to WAV; we return .wav here as the normalized extension.
        """
        base = mime_type.split(";")[0].strip().lower()
        mime_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "audio/mpeg": ".mp3",
            "audio/mp3": ".mp3",
            "audio/wav": ".wav",
            "audio/ogg": ".ogg",
            "audio/l16": ".wav",  # raw PCM — saved as WAV after header is prepended
            "audio/pcm": ".wav",  # raw PCM — saved as WAV after header is prepended
            "application/pdf": ".pdf",
        }
        return mime_map.get(base, "")

    @staticmethod
    def _parse_pcm_mime_params(mime_type: str) -> tuple[int, int]:
        """Extract (bits_per_sample, sample_rate) from a raw PCM MIME type.

        Handles formats like:
          audio/L16;rate=24000
          audio/L16;codec=pcm;rate=24000
          audio/pcm;rate=24000
        """
        bits_per_sample = 16
        sample_rate = 24000

        for part in mime_type.split(";"):
            part = part.strip()
            if part.lower().startswith("rate="):
                try:
                    sample_rate = int(part.split("=", 1)[1])
                except (ValueError, IndexError):
                    pass
            elif part.lower().startswith("audio/l"):
                try:
                    bits_per_sample = int(part.split("l", 1)[1])
                except (ValueError, IndexError):
                    pass

        return bits_per_sample, sample_rate

    @staticmethod
    def _pcm_to_wav(audio_data: bytes, bits_per_sample: int, sample_rate: int) -> bytes:
        """Prepend a standard WAV/RIFF header to raw PCM data."""
        num_channels = 1
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        data_size = len(audio_data)
        chunk_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            chunk_size,
            b"WAVE",
            b"fmt ",
            16,              # PCM chunk size
            1,               # AudioFormat = PCM
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size,
        )
        return header + audio_data

    def _normalize_audio(
        self, content: bytes, mime_type: str
    ) -> tuple[bytes, str]:
        """Convert raw PCM audio to WAV if needed.

        Returns (content, effective_mime_type) where effective_mime_type is
        'audio/wav' for any PCM input, otherwise the original mime_type.
        """
        base = mime_type.split(";")[0].strip().lower()
        if base in ("audio/l16", "audio/pcm") or base.startswith("audio/l"):
            bits_per_sample, sample_rate = self._parse_pcm_mime_params(mime_type)
            content = self._pcm_to_wav(content, bits_per_sample, sample_rate)
            return content, "audio/wav"
        return content, mime_type


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def save_media(
    content: str | bytes,
    mime_type: str,
    audio_format: str | None = None,
) -> str:
    """Convenience function to save media using singleton instance.

    audio_format: optional target format for audio content ("wav", "mp3", "ogg").
    If None, audio is normalized to WAV but not further transcoded.
    """
    return AIMediaHandler.get_instance().save_response_media(
        content, mime_type, audio_format=audio_format
    )


def fetch_media(
    url: str, target_format: Literal["base64", "bytes"] = "base64"
) -> str | bytes:
    """Convenience function to fetch media using singleton instance"""
    return AIMediaHandler.get_instance().fetch_media(url, target_format)
