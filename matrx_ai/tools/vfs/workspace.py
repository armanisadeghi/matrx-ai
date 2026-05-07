from __future__ import annotations

import os
from typing import TYPE_CHECKING

from matrx_ai.tools.vfs.backends.memory import MemoryBackend
from matrx_ai.tools.vfs.cache import CachingBackend
from matrx_ai.tools.vfs.core import AbstractBackend, MatrxAsyncFS

if TYPE_CHECKING:
    from matrx_ai.tools.models import ToolContext


_BACKEND: AbstractBackend | None = None
_FS_CACHE: dict[str, MatrxAsyncFS] = {}


def get_backend() -> AbstractBackend:
    global _BACKEND
    if _BACKEND is None:
        backend_type = os.getenv("MATRX_VFS_BACKEND", "memory")
        inner: AbstractBackend
        if backend_type == "postgres":
            from matrx_ai.tools.vfs.backends.postgres import PostgresBackend

            inner = PostgresBackend()
        else:
            inner = MemoryBackend()
        _BACKEND = CachingBackend(inner)
    return _BACKEND


def workspace_id_for(ctx: ToolContext) -> str:
    # Conversation-scoped: every tool call within a conversation shares state,
    # but separate conversations (or anonymous "default" lanes) stay isolated.
    user_id = ctx.user_id or "anonymous"
    conversation_id = ctx.conversation_id or "default"
    return f"{user_id}:{conversation_id}"


async def get_workspace_fs(ctx: ToolContext) -> MatrxAsyncFS:
    workspace_id = workspace_id_for(ctx)
    fs = _FS_CACHE.get(workspace_id)
    if fs is None:
        backend = get_backend()
        await backend.ensure_workspace_root(workspace_id)
        fs = MatrxAsyncFS(backend=backend, workspace_id=workspace_id, asynchronous=True)
        _FS_CACHE[workspace_id] = fs
    return fs


def clear_workspace_cache() -> None:
    global _BACKEND
    _FS_CACHE.clear()
    _BACKEND = None
