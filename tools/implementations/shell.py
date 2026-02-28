from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any

from tools.arg_models.shell_args import ShellExecuteArgs, ShellPythonArgs
from tools.models import ToolContext, ToolError, ToolResult

logger = logging.getLogger(__name__)

WORKSPACE_BASE = os.environ.get("TOOL_WORKSPACE_BASE", "/tmp/workspaces")
MAX_OUTPUT_SIZE = 10_240  # 10 KB

BLOCKED_COMMANDS = {
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=/dev/zero",
    ":(){ :|:& };:",
    "format",
    "fdisk",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
}


def _is_blocked(command: str) -> bool:
    normalized = command.strip().lower()
    for blocked in BLOCKED_COMMANDS:
        if blocked in normalized:
            return True
    return False


def _workspace_dir(ctx: ToolContext, working_dir: str = ".") -> str:
    base = Path(WORKSPACE_BASE) / ctx.user_id
    if ctx.project_id:
        base = base / ctx.project_id
    base.mkdir(parents=True, exist_ok=True)
    resolved = (base / working_dir).resolve()
    if not str(resolved).startswith(str(base.resolve())):
        return str(base)
    resolved.mkdir(parents=True, exist_ok=True)
    return str(resolved)


async def shell_execute(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = ShellExecuteArgs(**args)

    if _is_blocked(parsed.command):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="permission",
                message=f"Command blocked for safety: {parsed.command[:100]}",
                suggested_action="This command is not allowed. Use a different approach.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="shell_execute",
            call_id=ctx.call_id,
        )

    cwd = _workspace_dir(ctx, parsed.working_dir)

    try:
        process = await asyncio.create_subprocess_shell(
            parsed.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=parsed.timeout_seconds,
            )
        except asyncio.TimeoutError:
            process.kill()
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="timeout",
                    message=f"Command timed out after {parsed.timeout_seconds}s",
                    is_retryable=True,
                    suggested_action="Try a simpler command or increase the timeout.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="shell_execute",
                call_id=ctx.call_id,
            )

        stdout_str = stdout.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]
        stderr_str = stderr.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]

        return ToolResult(
            success=process.returncode == 0,
            output={
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode,
            },
            error=ToolError(
                error_type="exit_code",
                message=f"Command exited with code {process.returncode}: {stderr_str[:500]}",
            )
            if process.returncode != 0
            else None,
            started_at=started_at,
            completed_at=time.time(),
            tool_name="shell_execute",
            call_id=ctx.call_id,
        )

    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution", message=f"Shell execution failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="shell_execute",
            call_id=ctx.call_id,
        )


async def shell_python(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = ShellPythonArgs(**args)

    cwd = _workspace_dir(ctx)
    script_path = Path(cwd) / "_tool_exec.py"

    try:
        script_path.write_text(parsed.code)

        process = await asyncio.create_subprocess_exec(
            "python3",
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=parsed.timeout_seconds,
            )
        except asyncio.TimeoutError:
            process.kill()
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="timeout",
                    message=f"Python execution timed out after {parsed.timeout_seconds}s",
                    is_retryable=True,
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="shell_python",
                call_id=ctx.call_id,
            )
        finally:
            try:
                script_path.unlink()
            except Exception:
                pass

        stdout_str = stdout.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]
        stderr_str = stderr.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]

        return ToolResult(
            success=process.returncode == 0,
            output={
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode,
            },
            error=ToolError(
                error_type="python_error",
                message=f"Python exited with code {process.returncode}: {stderr_str[:500]}",
            )
            if process.returncode != 0
            else None,
            started_at=started_at,
            completed_at=time.time(),
            tool_name="shell_python",
            call_id=ctx.call_id,
        )

    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution", message=f"Python execution failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="shell_python",
            call_id=ctx.call_id,
        )
