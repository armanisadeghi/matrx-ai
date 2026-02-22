from __future__ import annotations

import math
import time
from typing import Any

from tools.arg_models.math_args import CalculateArgs
from tools.models import ToolContext, ToolError, ToolResult


SAFE_MATH_NAMES: dict[str, Any] = {
    k: getattr(math, k) for k in dir(math) if not k.startswith("_")
}
SAFE_MATH_NAMES.update({
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "int": int,
    "float": float,
})


async def calculate(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = CalculateArgs(**args)

    try:
        result = eval(parsed.expression, {"__builtins__": {}}, SAFE_MATH_NAMES)
        return ToolResult(
            success=True,
            output=str(result),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="calculate",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="evaluation",
                message=f"Failed to evaluate expression: {exc}",
                suggested_action="Check the expression syntax. Use standard math operations and functions.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="calculate",
            call_id=ctx.call_id,
        )
