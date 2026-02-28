from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from db.custom import cxm
from tools.arg_models.memory_args import (
    MemoryForgetArgs,
    MemoryRecallArgs,
    MemorySearchArgs,
    MemoryStoreArgs,
    MemoryUpdateArgs,
)
from tools.models import ToolContext, ToolError, ToolResult

logger = logging.getLogger(__name__)

EXPIRY_MAP = {
    "short": timedelta(hours=1),
    "medium": timedelta(days=7),
    "long": None,
}


def _scope_id(ctx: ToolContext, scope: str) -> str | None:
    if scope == "project":
        return ctx.project_id
    if scope == "organization":
        return ctx.organization_id
    return None


async def memory_store(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = MemoryStoreArgs(**args)

    try:
        expires_delta = EXPIRY_MAP.get(parsed.memory_type)
        expires_at = (
            (datetime.now(timezone.utc) + expires_delta).isoformat()
            if expires_delta
            else None
        )

        data = {
            "user_id": ctx.user_id,
            "memory_type": parsed.memory_type,
            "scope": parsed.scope,
            "scope_id": _scope_id(ctx, parsed.scope),
            "key": parsed.key,
            "content": parsed.content,
            "importance": parsed.importance,
            "expires_at": expires_at,
        }

        await cxm.agent_memory.upsert(data)

        return ToolResult(
            success=True,
            output={"stored": True, "key": parsed.key, "type": parsed.memory_type},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_store",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=f"Memory store failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_store",
            call_id=ctx.call_id,
        )


async def memory_recall(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = MemoryRecallArgs(**args)

    try:
        memories = await cxm.agent_memory.recall(
            user_id=ctx.user_id,
            scope=parsed.scope,
            key=parsed.key,
            memory_type=parsed.memory_type,
            limit=parsed.limit,
        )

        for mem in memories:
            await cxm.agent_memory.update_access_count(
                mem["id"], mem.get("access_count", 0) or 0
            )

        return ToolResult(
            success=True,
            output={"memories": memories, "count": len(memories)},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_recall",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=f"Memory recall failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_recall",
            call_id=ctx.call_id,
        )


async def memory_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = MemorySearchArgs(**args)

    try:
        results = await cxm.agent_memory.search_by_content(
            user_id=ctx.user_id,
            scope=parsed.scope,
            query=parsed.query,
            memory_type=parsed.memory_type,
            limit=parsed.limit,
        )

        return ToolResult(
            success=True,
            output={"results": results, "count": len(results)},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_search",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=f"Memory search failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_search",
            call_id=ctx.call_id,
        )


async def memory_update(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = MemoryUpdateArgs(**args)

    try:
        update_data: dict[str, Any] = {
            "content": parsed.content,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if parsed.importance is not None:
            update_data["importance"] = parsed.importance

        updated = await cxm.agent_memory.update_by_key(
            user_id=ctx.user_id,
            scope=parsed.scope,
            key=parsed.key,
            data=update_data,
        )

        return ToolResult(
            success=updated > 0,
            output={"updated": updated},
            error=ToolError(
                error_type="not_found",
                message=f"Memory with key '{parsed.key}' not found.",
            )
            if updated == 0
            else None,
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_update",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=f"Memory update failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_update",
            call_id=ctx.call_id,
        )


async def memory_forget(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = MemoryForgetArgs(**args)

    try:
        deleted = await cxm.agent_memory.delete_by_key(
            user_id=ctx.user_id,
            scope=parsed.scope,
            key=parsed.key,
        )
        return ToolResult(
            success=True,
            output={"deleted": deleted, "key": parsed.key},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_forget",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=f"Memory forget failed: {exc}"
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="memory_forget",
            call_id=ctx.call_id,
        )
