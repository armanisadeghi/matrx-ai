from __future__ import annotations

import fnmatch
import logging
import os
import time
from pathlib import Path
from typing import Any

from tools.arg_models.fs_args import (
    FsListArgs,
    FsMkdirArgs,
    FsReadArgs,
    FsSearchArgs,
    FsWriteArgs,
)
from tools.models import ToolContext, ToolError, ToolResult

logger = logging.getLogger(__name__)

MAX_READ_SIZE = 1_048_576  # 1 MB
WORKSPACE_BASE = os.environ.get("TOOL_WORKSPACE_BASE", "/tmp/workspaces")


def _resolve_path(relative: str, ctx: ToolContext) -> Path:
    base = Path(WORKSPACE_BASE) / ctx.user_id
    if ctx.project_id:
        base = base / ctx.project_id
    resolved = (base / relative).resolve()
    if not str(resolved).startswith(str(base.resolve())):
        raise PermissionError(f"Path escapes workspace: {relative}")
    return resolved


async def fs_read(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsReadArgs(**args)

    try:
        filepath = _resolve_path(parsed.path, ctx)
        if not filepath.exists():
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found", message=f"File not found: {parsed.path}"
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="fs_read",
                call_id=ctx.call_id,
            )

        size = filepath.stat().st_size
        read_limit = parsed.limit if parsed.limit > 0 else MAX_READ_SIZE
        truncated = size > read_limit

        with open(filepath, "r", errors="replace") as f:
            if parsed.offset:
                f.seek(parsed.offset)
            content = f.read(read_limit)

        return ToolResult(
            success=True,
            output={
                "content": content,
                "size": size,
                "truncated": truncated,
                "path": parsed.path,
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_read",
            call_id=ctx.call_id,
        )
    except PermissionError as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=str(exc)),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_read",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="filesystem", message=f"Read failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_read",
            call_id=ctx.call_id,
        )


async def fs_write(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsWriteArgs(**args)

    try:
        filepath = _resolve_path(parsed.path, ctx)
        if parsed.create_dirs:
            filepath.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if parsed.append else "w"
        with open(filepath, mode) as f:
            f.write(parsed.content)

        return ToolResult(
            success=True,
            output={
                "path": parsed.path,
                "bytes_written": len(parsed.content.encode()),
                "mode": "append" if parsed.append else "write",
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_write",
            call_id=ctx.call_id,
        )
    except PermissionError as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=str(exc)),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_write",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="filesystem", message=f"Write failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_write",
            call_id=ctx.call_id,
        )


async def fs_list(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsListArgs(**args)

    try:
        dirpath = _resolve_path(parsed.path, ctx)
        if not dirpath.is_dir():
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found",
                    message=f"Directory not found: {parsed.path}",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="fs_list",
                call_id=ctx.call_id,
            )

        entries: list[dict[str, Any]] = []
        iterator = dirpath.rglob("*") if parsed.recursive else dirpath.iterdir()
        for entry in iterator:
            if parsed.pattern and not fnmatch.fnmatch(entry.name, parsed.pattern):
                continue
            entries.append(
                {
                    "name": entry.name,
                    "path": str(entry.relative_to(dirpath)),
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if entry.is_file() else 0,
                }
            )
            if len(entries) >= 500:
                break

        return ToolResult(
            success=True,
            output={"entries": entries, "count": len(entries), "path": parsed.path},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_list",
            call_id=ctx.call_id,
        )
    except PermissionError as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=str(exc)),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_list",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="filesystem", message=f"List failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_list",
            call_id=ctx.call_id,
        )


async def fs_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsSearchArgs(**args)

    try:
        basepath = _resolve_path(parsed.path, ctx)
        if not basepath.is_dir():
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found",
                    message=f"Directory not found: {parsed.path}",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="fs_search",
                call_id=ctx.call_id,
            )

        results: list[dict[str, Any]] = []
        import re

        for entry in basepath.rglob("*"):
            if len(results) >= parsed.max_results:
                break
            if entry.is_dir():
                continue

            if parsed.content_search:
                try:
                    content = entry.read_text(errors="replace")[:50000]
                    matches = [m.group() for m in re.finditer(parsed.pattern, content)]
                    if matches:
                        results.append(
                            {
                                "path": str(entry.relative_to(basepath)),
                                "matches": matches[:10],
                            }
                        )
                except Exception:
                    continue
            else:
                if fnmatch.fnmatch(entry.name, parsed.pattern):
                    results.append(
                        {
                            "path": str(entry.relative_to(basepath)),
                            "size": entry.stat().st_size,
                        }
                    )

        return ToolResult(
            success=True,
            output={"results": results, "count": len(results)},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_search",
            call_id=ctx.call_id,
        )
    except PermissionError as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=str(exc)),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_search",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="filesystem", message=f"Search failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_search",
            call_id=ctx.call_id,
        )


async def fs_mkdir(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = FsMkdirArgs(**args)

    try:
        dirpath = _resolve_path(parsed.path, ctx)
        dirpath.mkdir(parents=parsed.parents, exist_ok=True)

        return ToolResult(
            success=True,
            output={"created": str(parsed.path)},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_mkdir",
            call_id=ctx.call_id,
        )
    except PermissionError as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=str(exc)),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_mkdir",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="filesystem", message=f"Mkdir failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="fs_mkdir",
            call_id=ctx.call_id,
        )
