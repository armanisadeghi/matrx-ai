"""
AI Media Persistence Handler

Handles media upload/download for AI-generated content.
Uses FileHandler for Supabase operations and ExecutionContext for user tracking.
"""

import base64
import uuid
from typing import Literal

from matrx_utils import FileManager

# TODO: Figure out how to manage file handler with supabase buckets from matrx_utils

# ============================================================================
# AI MEDIA HANDLER
# ============================================================================


class AIMediaHandler:
    """Handles media persistence for AI content conversions"""

    _instance = None

    def __init__(self):
        self.file_manager = FileManager.get_instance(
            app_name="ai_media"
        )
        self.file_handler = self.file_manager.file_handler

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
    ) -> str:
        """Save AI-generated media to Supabase.

        Reads ``user_id`` from the current ``ExecutionContext``.
        """
        from matrx_ai.context.app_context import get_app_context
        exec_ctx = get_app_context()

        if isinstance(content, str):
            content = base64.b64decode(content)

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
        """Get file extension from MIME type"""
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
            "application/pdf": ".pdf",
        }
        return mime_map.get(mime_type.lower(), "")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def save_media(content: str | bytes, mime_type: str) -> str:
    """Convenience function to save media using singleton instance"""
    return AIMediaHandler.get_instance().save_response_media(content, mime_type)


def fetch_media(
    url: str, target_format: Literal["base64", "bytes"] = "base64"
) -> str | bytes:
    """Convenience function to fetch media using singleton instance"""
    return AIMediaHandler.get_instance().fetch_media(url, target_format)
