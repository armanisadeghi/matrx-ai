from __future__ import annotations

import fnmatch
import re
import time
from typing import Any

from matrx_ai.tools.arg_models.fs_args import (
    FsEditArgs,
    FsListArgs,
    FsMkdirArgs,
    FsReadArgs,
    FsSearchArgs,
    FsWriteArgs,
)
from matrx_ai.tools.models import ToolContext, ToolError, ToolResult
from matrx_ai.tools.vfs.mimicry import claude_tool
from matrx_ai.tools.vfs.paths import dirname, join, normalize
from matrx_ai.tools.vfs.workspace import get_workspace_fs

MAX_READ_SIZE = 1_048_576  # 1 MB
MAX_LIST_ENTRIES = 500


def _abs(path: str) -> str:
    return path if path.startswith("/") else "/" + path


def _err(
    started_at: float,
    ctx: ToolContext,
    tool_name: str,
    error_type: str,
    message: str,
) -> ToolResult:
    return ToolResult(
        success=False,
        error=ToolError(error_type=error_type, message=message),
        started_at=started_at,
        completed_at=time.time(),
        tool_name=tool_name,
        call_id=ctx.call_id,
    )


def _ok(
    started_at: float,
    ctx: ToolContext,
    tool_name: str,
    output: Any,
) -> ToolResult:
    return ToolResult(
        success=True,
        output=output,
        started_at=started_at,
        completed_at=time.time(),
        tool_name=tool_name,
        call_id=ctx.call_id,
    )


async def fs_read(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsReadArgs(**args)
    vfs = await get_workspace_fs(ctx)
    path = _abs(parsed.path)

    try:
        data = await vfs._cat_file(path)
    except FileNotFoundError:
        return _err(started_at, ctx, "fs_read", "not_found", f"File not found: {parsed.path}")
    except IsADirectoryError:
        return _err(started_at, ctx, "fs_read", "filesystem", f"Is a directory: {parsed.path}")
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_read", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_read", "filesystem", f"Read failed: {exc}")

    full_size = len(data)
    if parsed.offset:
        data = data[parsed.offset :]

    read_limit = parsed.limit if parsed.limit > 0 else MAX_READ_SIZE
    truncated = len(data) > read_limit
    if truncated:
        data = data[:read_limit]

    text = data.decode("utf-8", errors="replace")
    return _ok(
        started_at,
        ctx,
        "fs_read",
        {
            "content": text,
            "size": full_size,
            "truncated": truncated,
            "path": parsed.path,
        },
    )


async def fs_write(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsWriteArgs(**args)
    vfs = await get_workspace_fs(ctx)
    path = _abs(parsed.path)

    try:
        if parsed.create_dirs:
            parent = dirname(path)
            if parent and parent != "/":
                await vfs._makedirs(parent, exist_ok=True)

        content_bytes = parsed.content.encode("utf-8")
        if parsed.append:
            try:
                existing = await vfs._cat_file(path)
            except FileNotFoundError:
                existing = b""
            content_bytes = existing + content_bytes

        await vfs._pipe_file(path, content_bytes)
    except IsADirectoryError:
        return _err(started_at, ctx, "fs_write", "filesystem", f"Is a directory: {parsed.path}")
    except NotADirectoryError as exc:
        return _err(started_at, ctx, "fs_write", "filesystem", str(exc))
    except FileNotFoundError as exc:
        # Parent missing and create_dirs=False
        return _err(started_at, ctx, "fs_write", "not_found", str(exc))
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_write", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_write", "filesystem", f"Write failed: {exc}")

    return _ok(
        started_at,
        ctx,
        "fs_write",
        {
            "path": parsed.path,
            "bytes_written": len(parsed.content.encode("utf-8")),
            "mode": "append" if parsed.append else "write",
        },
    )


async def fs_list(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsListArgs(**args)
    vfs = await get_workspace_fs(ctx)
    path = _abs(parsed.path)

    try:
        if not await vfs._isdir(path):
            return _err(
                started_at,
                ctx,
                "fs_list",
                "not_found",
                f"Directory not found: {parsed.path}",
            )

        entries: list[dict[str, Any]] = []
        pattern = parsed.pattern or None

        if parsed.recursive:
            async for root, _dirs, files in vfs._walk(path, topdown=True):
                rel_root = _relative(root, path)
                # Include subdirectories themselves
                listing = await vfs._ls(root, detail=True)
                for info in listing:
                    name = info["name"].rsplit("/", 1)[-1]
                    if pattern and not fnmatch.fnmatch(name, pattern):
                        continue
                    rel_path = name if rel_root in ("", ".") else f"{rel_root}/{name}"
                    entries.append(
                        {
                            "name": name,
                            "path": rel_path,
                            "is_dir": info["type"] == "directory",
                            "size": info["size"] if info["type"] == "file" else 0,
                        }
                    )
                    if len(entries) >= MAX_LIST_ENTRIES:
                        break
                _ = files  # used by _walk filter — not needed here
                if len(entries) >= MAX_LIST_ENTRIES:
                    break
        else:
            listing = await vfs._ls(path, detail=True)
            for info in listing:
                name = info["name"].rsplit("/", 1)[-1]
                if pattern and not fnmatch.fnmatch(name, pattern):
                    continue
                entries.append(
                    {
                        "name": name,
                        "path": name,
                        "is_dir": info["type"] == "directory",
                        "size": info["size"] if info["type"] == "file" else 0,
                    }
                )
                if len(entries) >= MAX_LIST_ENTRIES:
                    break
    except NotADirectoryError as exc:
        return _err(started_at, ctx, "fs_list", "filesystem", str(exc))
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_list", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_list", "filesystem", f"List failed: {exc}")

    return _ok(
        started_at,
        ctx,
        "fs_list",
        {"entries": entries, "count": len(entries), "path": parsed.path},
    )


def _relative(absolute: str, base: str) -> str:
    a = normalize(absolute)
    b = normalize(base)
    if a == b:
        return "."
    if b == "/":
        return a[1:] if a.startswith("/") else a
    if a.startswith(b + "/"):
        return a[len(b) + 1 :]
    return a


async def fs_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsSearchArgs(**args)
    vfs = await get_workspace_fs(ctx)
    base = _abs(parsed.path)

    try:
        if not await vfs._isdir(base):
            return _err(
                started_at,
                ctx,
                "fs_search",
                "not_found",
                f"Directory not found: {parsed.path}",
            )

        results: list[dict[str, Any]] = []

        if parsed.content_search:
            try:
                content_re = re.compile(parsed.pattern)
            except re.error as exc:
                return _err(
                    started_at,
                    ctx,
                    "fs_search",
                    "validation",
                    f"Invalid regex: {exc}",
                )
            async for root, _dirs, files in vfs._walk(base, topdown=True):
                for fname in files:
                    if len(results) >= parsed.max_results:
                        break
                    full = join(root, fname)
                    try:
                        data = await vfs._cat_file(full)
                    except OSError:
                        continue
                    text = data.decode("utf-8", errors="replace")[:50000]
                    matches = [m.group() for m in content_re.finditer(text)]
                    if matches:
                        results.append(
                            {
                                "path": _relative(full, base),
                                "matches": matches[:10],
                            }
                        )
                if len(results) >= parsed.max_results:
                    break
        else:
            async for root, _dirs, files in vfs._walk(base, topdown=True):
                for fname in files:
                    if len(results) >= parsed.max_results:
                        break
                    if not fnmatch.fnmatch(fname, parsed.pattern):
                        continue
                    full = join(root, fname)
                    try:
                        info = await vfs._info(full)
                    except OSError:
                        continue
                    results.append(
                        {
                            "path": _relative(full, base),
                            "size": info["size"],
                        }
                    )
                if len(results) >= parsed.max_results:
                    break
    except NotADirectoryError as exc:
        return _err(started_at, ctx, "fs_search", "filesystem", str(exc))
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_search", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_search", "filesystem", f"Search failed: {exc}")

    return _ok(
        started_at,
        ctx,
        "fs_search",
        {"results": results, "count": len(results)},
    )


async def fs_mkdir(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsMkdirArgs(**args)
    vfs = await get_workspace_fs(ctx)
    path = _abs(parsed.path)

    try:
        if parsed.parents:
            await vfs._makedirs(path, exist_ok=True)
        else:
            await vfs._mkdir(path, create_parents=False)
    except FileExistsError:
        return _err(
            started_at,
            ctx,
            "fs_mkdir",
            "filesystem",
            f"Directory already exists: {parsed.path}",
        )
    except FileNotFoundError as exc:
        return _err(started_at, ctx, "fs_mkdir", "not_found", str(exc))
    except NotADirectoryError as exc:
        return _err(started_at, ctx, "fs_mkdir", "filesystem", str(exc))
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_mkdir", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_mkdir", "filesystem", f"Mkdir failed: {exc}")

    return _ok(started_at, ctx, "fs_mkdir", {"created": parsed.path})


async def fs_edit(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsEditArgs(**args)
    vfs = await get_workspace_fs(ctx)
    path = _abs(parsed.path)

    try:
        data = await vfs._cat_file(path)
    except FileNotFoundError:
        return _err(started_at, ctx, "fs_edit", "not_found", claude_tool.edit_not_found())
    except IsADirectoryError:
        return _err(started_at, ctx, "fs_edit", "filesystem", f"Is a directory: {parsed.path}")
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_edit", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_edit", "filesystem", f"Read failed: {exc}")

    text = data.decode("utf-8", errors="replace")
    count = text.count(parsed.old_str)

    if count == 0:
        return _err(started_at, ctx, "fs_edit", "validation", claude_tool.edit_string_not_found())

    if count > 1 and not parsed.replace_all:
        return _err(started_at, ctx, "fs_edit", "validation", claude_tool.edit_n_matches(count))

    if parsed.replace_all:
        new_text = text.replace(parsed.old_str, parsed.new_str)
        replaced = count
    else:
        new_text = text.replace(parsed.old_str, parsed.new_str, 1)
        replaced = 1

    try:
        await vfs._pipe_file(path, new_text.encode("utf-8"))
    except PermissionError as exc:
        return _err(started_at, ctx, "fs_edit", "permission", str(exc))
    except OSError as exc:
        return _err(started_at, ctx, "fs_edit", "filesystem", f"Write failed: {exc}")

    return _ok(
        started_at,
        ctx,
        "fs_edit",
        {
            "path": parsed.path,
            "old_str_count": count,
            "replaced": replaced,
        },
    )


__all__ = [
    "fs_edit",
    "fs_list",
    "fs_mkdir",
    "fs_read",
    "fs_search",
    "fs_write",
]
