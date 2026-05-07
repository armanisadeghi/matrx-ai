from __future__ import annotations

import os
from typing import Any

# Map: original (real-disk) function_path → VFS-backed function_path.
# When VFS routing fires, lookups in this table determine the swap target.
VFS_REMAP_TABLE: dict[str, str] = {
    "matrx_ai.tools.implementations.filesystem.fs_read":
        "matrx_ai.tools.implementations.vfs_filesystem.fs_read",
    "matrx_ai.tools.implementations.filesystem.fs_write":
        "matrx_ai.tools.implementations.vfs_filesystem.fs_write",
    "matrx_ai.tools.implementations.filesystem.fs_list":
        "matrx_ai.tools.implementations.vfs_filesystem.fs_list",
    "matrx_ai.tools.implementations.filesystem.fs_search":
        "matrx_ai.tools.implementations.vfs_filesystem.fs_search",
    "matrx_ai.tools.implementations.filesystem.fs_mkdir":
        "matrx_ai.tools.implementations.vfs_filesystem.fs_mkdir",
    "matrx_ai.tools.implementations.shell.shell_execute":
        "matrx_ai.tools.implementations.vfs_shell.shell_execute",
}

# Sentinel source_app values.
#   matrx_ai   — first-party real-disk implementation (default).
#   matrx_vfs  — first-party VFS implementation, forced regardless of env var.
#   matrx_local / others — external host handler; never remapped here.
NATIVE_SOURCE_APP = "matrx_ai"
VFS_SOURCE_APP = "matrx_vfs"

_TRUTHY: frozenset[str] = frozenset({"1", "true", "yes", "on"})


def is_vfs_globally_enabled() -> bool:
    # Env var is the source of truth so the flip works without touching Settings.
    return os.getenv("MATRX_VFS_ENABLED", "").strip().lower() in _TRUTHY


def should_route_to_vfs(function_path: str, source_app: str | None) -> bool:
    if source_app == VFS_SOURCE_APP:
        return True
    if source_app == NATIVE_SOURCE_APP and is_vfs_globally_enabled():
        return function_path in VFS_REMAP_TABLE
    return False


def remap(function_path: str) -> str:
    return VFS_REMAP_TABLE.get(function_path, function_path)


# Synthetic tool definition for fs_edit. fs_edit only exists in the VFS layer
# (no real-disk equivalent), so we inject it at registry-load time when VFS
# routing is active and no DB row already provides it.
FS_EDIT_TOOL_DEFINITION: dict[str, Any] = {
    "name": "fs_edit",
    "description": (
        "Edit a file by exact string replacement. Requires an exact match of "
        "old_str that is unique within the file unless replace_all is true."
    ),
    "parameters": {
        "path": {
            "type": "string",
            "description": "File path within the workspace.",
            "required": True,
        },
        "old_str": {
            "type": "string",
            "description": "Exact string to find. Must be unique unless replace_all=true.",
            "required": True,
        },
        "new_str": {
            "type": "string",
            "description": "Replacement string.",
            "required": True,
        },
        "replace_all": {
            "type": "boolean",
            "description": "If true, replace every occurrence of old_str.",
            "default": False,
        },
    },
    "function_path": "matrx_ai.tools.implementations.vfs_filesystem.fs_edit",
    "source_app": VFS_SOURCE_APP,
    "is_active": True,
    "version": "1.0.0",
    "category": "filesystem",
    "tags": ["edit", "patch", "vfs"],
}
