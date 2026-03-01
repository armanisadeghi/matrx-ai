"""
Tool router.

  GET  /api/tools/test/list       — list registered tools
  GET  /api/tools/test/{name}     — get a tool's definition
  POST /api/tools/test/execute    — invoke a tool (returns result)
"""

import time
import uuid
from typing import Any

from fastapi import APIRouter, Path
from fastapi.responses import ORJSONResponse

from matrx_ai.app.core.exceptions import ToolNotFoundError
from matrx_ai.app.models.tool import ToolCallRequest, ToolCallResult, ToolDefinition, ToolParameter

router = APIRouter(prefix="/api/tools/test", tags=["tool"])


# ---------------------------------------------------------------------------
# Tool registry — replace with your dynamic registry when ORM is wired in
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: dict[str, ToolDefinition] = {
    "search": ToolDefinition(
        name="search",
        description="Search the web for up-to-date information",
        parameters=[
            ToolParameter(name="q", type="string", description="Search query", required=True),
            ToolParameter(
                name="limit",
                type="integer",
                description="Max results",
                required=False,
                default=10,
            ),
        ],
    ),
    "calculator": ToolDefinition(
        name="calculator",
        description="Evaluate a mathematical expression",
        parameters=[
            ToolParameter(
                name="expression", type="string", description="Math expression", required=True
            )
        ],
    ),
}


@router.get("/list", response_class=ORJSONResponse)
async def list_tools() -> list[ToolDefinition]:
    return list(_TOOL_REGISTRY.values())


@router.get("/{name}", response_class=ORJSONResponse)
async def get_tool(
    name: str = Path(..., description="Tool name"),
) -> ToolDefinition:
    tool = _TOOL_REGISTRY.get(name)
    if tool is None:
        raise ToolNotFoundError(name)
    return tool


@router.post("/execute", response_class=ORJSONResponse)
async def execute_tool(body: ToolCallRequest) -> ToolCallResult:
    tool = _TOOL_REGISTRY.get(body.tool_name)
    if tool is None:
        raise ToolNotFoundError(body.tool_name)

    call_id = body.call_id or str(uuid.uuid4())
    start = time.perf_counter()
    result = await _dispatch(body.tool_name, body.arguments)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return ToolCallResult(
        call_id=call_id,
        tool_name=body.tool_name,
        result=result,
        elapsed_ms=round(elapsed_ms, 2),
    )


async def _dispatch(tool_name: str, arguments: dict[str, Any]) -> Any:
    """
    Route to the actual tool implementation.
    Replace each branch with your real tool logic.
    """
    match tool_name:
        case "search":
            return {"results": [], "query": arguments.get("q"), "note": "stub — wire real search"}
        case "calculator":
            expr = arguments.get("expression", "")
            try:
                return {"result": eval(expr, {"__builtins__": {}}, {})}  # noqa: S307
            except Exception as exc:
                return {"error": str(exc)}
        case _:
            return {"error": f"No handler for tool '{tool_name}'"}
