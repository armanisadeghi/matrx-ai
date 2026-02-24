from __future__ import annotations

import logging
import re
import time
from typing import Any

from tools.arg_models.db_args import DbInsertArgs, DbQueryArgs, DbSchemaArgs, DbUpdateArgs
from tools.models import ToolContext, ToolError, ToolResult

logger = logging.getLogger(__name__)


def _get_async_supabase():
    from common.supabase.supabase_client import get_async_supabase_client
    return get_async_supabase_client()

BLOCKED_TABLES = {"auth", "cx_conversation", "cx_message", "cx_user_request", "cx_request"}
READ_ONLY_TABLES = {"ai_models", "tools", "prompt_builtins"}

DANGEROUS_KEYWORDS = {"DROP", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE"}
MAX_QUERY_TIMEOUT = 10


def _is_blocked_table(table: str) -> bool:
    normalized = table.lower().strip().replace('"', "").replace("'", "")
    if normalized in BLOCKED_TABLES:
        return True
    if normalized.startswith("auth."):
        return True
    return False


def _is_read_only(table: str) -> bool:
    return table.lower().strip() in READ_ONLY_TABLES


def _is_safe_select(query: str) -> bool:
    upper = query.strip().upper()
    if not upper.startswith("SELECT"):
        return False
    for kw in DANGEROUS_KEYWORDS:
        if re.search(rf'\b{kw}\b', upper):
            return False
    return True


async def db_query(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = DbQueryArgs(**args)

    if not _is_safe_select(parsed.query):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="permission",
                message="Only SELECT queries are allowed. Mutations must use db_insert or db_update.",
                suggested_action="Rewrite your query as a SELECT statement.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_query",
            call_id=ctx.call_id,
        )

    query_with_limit = parsed.query.rstrip().rstrip(";")
    if "LIMIT" not in parsed.query.upper():
        query_with_limit += f" LIMIT {parsed.limit}"

    try:
        client = _get_async_supabase()
        response = await client.rpc(
            "execute_safe_query",
            {"query": query_with_limit},
        ).execute()

        raw = response.data
        rows = raw if isinstance(raw, list) else (raw.get("result", []) if isinstance(raw, dict) else [])
        if len(rows) > parsed.limit:
            rows = rows[:parsed.limit]

        return ToolResult(
            success=True,
            output={"rows": rows, "count": len(rows)},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_query",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database",
                message=f"Query failed: {exc}",
                suggested_action="Check your SQL syntax and try again.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_query",
            call_id=ctx.call_id,
        )


async def db_insert(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = DbInsertArgs(**args)

    if _is_blocked_table(parsed.table):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="permission",
                message=f"Table '{parsed.table}' is blocked for direct writes.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_insert",
            call_id=ctx.call_id,
        )

    if _is_read_only(parsed.table):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="permission",
                message=f"Table '{parsed.table}' is read-only.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_insert",
            call_id=ctx.call_id,
        )

    try:
        data = parsed.data if isinstance(parsed.data, list) else [parsed.data]
        for row in data:
            row.setdefault("user_id", ctx.user_id)

        client = _get_async_supabase()
        response = await client.table(parsed.table).insert(data).execute()
        return ToolResult(
            success=True,
            output={"inserted": len(response.data) if response.data else 0, "data": response.data},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_insert",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="database", message=f"Insert failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_insert",
            call_id=ctx.call_id,
        )


async def db_update(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = DbUpdateArgs(**args)

    if _is_blocked_table(parsed.table):
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=f"Table '{parsed.table}' is blocked."),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_update",
            call_id=ctx.call_id,
        )

    if _is_read_only(parsed.table):
        return ToolResult(
            success=False,
            error=ToolError(error_type="permission", message=f"Table '{parsed.table}' is read-only."),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_update",
            call_id=ctx.call_id,
        )

    try:
        client = _get_async_supabase()
        query = client.table(parsed.table).update(parsed.data)
        for col, val in parsed.match.items():
            query = query.eq(col, val)
        response = await query.execute()

        return ToolResult(
            success=True,
            output={"updated": len(response.data) if response.data else 0, "data": response.data},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_update",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="database", message=f"Update failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_update",
            call_id=ctx.call_id,
        )


async def db_schema(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = DbSchemaArgs(**args)

    try:
        client = _get_async_supabase()
        if parsed.table:
            safe_table = parsed.table.replace("'", "''")
            response = await client.rpc(
                "execute_safe_query",
                {
                    "query": (
                        "SELECT column_name, data_type, is_nullable, column_default "
                        "FROM information_schema.columns "
                        f"WHERE table_schema = 'public' AND table_name = '{safe_table}' "
                        "ORDER BY ordinal_position"
                    ),
                },
            ).execute()

            raw = response.data
            columns = raw if isinstance(raw, list) else (raw.get("result", []) if isinstance(raw, dict) else [])

            return ToolResult(
                success=True,
                output={"table": parsed.table, "columns": columns},
                started_at=started_at,
                completed_at=time.time(),
                tool_name="db_schema",
                call_id=ctx.call_id,
            )
        else:
            response = await client.rpc(
                "execute_safe_query",
                {
                    "query": (
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public' ORDER BY table_name"
                    ),
                },
            ).execute()

            raw = response.data
            rows = raw if isinstance(raw, list) else (raw.get("result", []) if isinstance(raw, dict) else [])
            tables = [r.get("table_name", r) for r in rows]

            return ToolResult(
                success=True,
                output={"tables": tables},
                started_at=started_at,
                completed_at=time.time(),
                tool_name="db_schema",
                call_id=ctx.call_id,
            )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="database", message=f"Schema query failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="db_schema",
            call_id=ctx.call_id,
        )
