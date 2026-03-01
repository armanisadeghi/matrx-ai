"""
AI Media — MIME detection and persistence for AI-generated content.

Usage:
    from matrx_ai.media import detect_mime_type, save_media, fetch_media
    from matrx_ai.media import AIMediaHandler, EXTENSION_MIME_MAP
"""

from .media_persistence import AIMediaHandler, fetch_media, save_media
from .mime_utils import EXTENSION_MIME_MAP, detect_mime_type

__all__ = [
    "AIMediaHandler",
    "EXTENSION_MIME_MAP",
    "detect_mime_type",
    "fetch_media",
    "save_media",
]
