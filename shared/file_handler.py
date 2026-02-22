# Placeholder: FileHandler — used by ai.media.media_persistence
from typing import Any


class FileHandler:
    @staticmethod
    async def save_file(path: str, content: bytes) -> str:
        return path

    @staticmethod
    async def read_file(path: str) -> bytes:
        return b""
