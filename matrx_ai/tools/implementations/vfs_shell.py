from __future__ import annotations

import asyncio
import time
from typing import Any

from matrx_ai.tools.arg_models.shell_args import ShellExecuteArgs
from matrx_ai.tools.models import ToolContext, ToolError, ToolResult
from matrx_ai.tools.vfs.commands import VfsCommandRunner, load_all
from matrx_ai.tools.vfs.shell import (
    ShellEnv,
    ShellExpansionError,
    ShellParseError,
    execute,
    parse,
)
from matrx_ai.tools.vfs.workspace import get_workspace_fs

# Register every command implementation so the runner can dispatch them.
load_all()

MAX_OUTPUT_SIZE = 10_240


def _err(
    started_at: float,
    ctx: ToolContext,
    error_type: str,
    message: str,
    *,
    is_retryable: bool = False,
) -> ToolResult:
    return ToolResult(
        success=False,
        error=ToolError(
            error_type=error_type,
            message=message,
            is_retryable=is_retryable,
        ),
        started_at=started_at,
        completed_at=time.time(),
        tool_name="shell_execute",
        call_id=ctx.call_id,
    )


async def shell_execute(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = ShellExecuteArgs(**args)
    vfs = await get_workspace_fs(ctx)
    runner = VfsCommandRunner(vfs)

    cwd = parsed.working_dir if parsed.working_dir.startswith("/") else "/"
    env = ShellEnv(cwd=cwd)

    try:
        node = parse(parsed.command)
    except ShellParseError as exc:
        return _err(
            started_at,
            ctx,
            "validation",
            f"bash: syntax error: {exc.message}",
        )

    try:
        result = await asyncio.wait_for(
            execute(node, env, runner, capture=True),
            timeout=parsed.timeout_seconds,
        )
    except TimeoutError:
        return _err(
            started_at,
            ctx,
            "timeout",
            f"Command timed out after {parsed.timeout_seconds}s",
            is_retryable=True,
        )
    except ShellExpansionError as exc:
        return _err(started_at, ctx, "validation", f"bash: {exc}")

    stdout = result.stdout[:MAX_OUTPUT_SIZE]
    stderr = result.stderr[:MAX_OUTPUT_SIZE]
    output = {
        "stdout": stdout.decode("utf-8", errors="replace"),
        "stderr": stderr.decode("utf-8", errors="replace"),
        "exit_code": result.exit_code,
    }

    if result.exit_code == 0:
        return ToolResult(
            success=True,
            output=output,
            started_at=started_at,
            completed_at=time.time(),
            tool_name="shell_execute",
            call_id=ctx.call_id,
        )

    return ToolResult(
        success=False,
        output=output,
        error=ToolError(
            error_type="exit_code",
            message=f"Command exited with code {result.exit_code}",
            is_retryable=False,
        ),
        started_at=started_at,
        completed_at=time.time(),
        tool_name="shell_execute",
        call_id=ctx.call_id,
    )


__all__ = ["shell_execute"]
