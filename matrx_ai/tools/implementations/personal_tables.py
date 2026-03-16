"""Personal Tables tool implementations.

Provides full CRUD access to a user's personal data tables
(stored in public.user_tables / public.table_fields / public.table_data).

These tables are user-owned structured datasets created by the AI on behalf
of the user. All operations are scoped to ctx.user_id automatically.

# CLIENT_MODE_DEFERRED
#
# This tool uses direct asyncpg / matrx-orm queries that require a live
# PostgreSQL connection. In client mode (desktop app), no DB connection is
# available. A future implementation could proxy these operations through a
# JWT-scoped server endpoint that enforces user ownership server-side.
# Until that endpoint exists, all personal_tables tools are disabled in
# client mode and raise NotImplementedError.
"""

from __future__ import annotations

import asyncio
import json
import traceback
from typing import Any

from matrx_ai.tools.models import ToolContext, ToolError, ToolResult

# ---------------------------------------------------------------------------
# Client mode guard
# ---------------------------------------------------------------------------


def _raise_if_client_mode(tool_name: str) -> None:
    from matrx_ai.db import is_client_mode
    if is_client_mode():
        raise NotImplementedError(
            f"The '{tool_name}' tool is not available in client mode. "
            "Personal tables require direct database access which is unavailable "
            "in a desktop application. A JWT-scoped server proxy endpoint is needed "
            "before this tool can run client-side. (CLIENT_MODE_DEFERRED)"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_query(query_name: str, params: dict[str, Any]) -> list[dict]:
    from matrx_orm.sql_executor import execute_query

    result = execute_query(query_name, params)
    return result if isinstance(result, list) else []


def _run_batch(
    query_name: str, batch_params: list[dict], batch_size: int = 50
) -> list[dict]:
    from matrx_orm.sql_executor import execute_query

    result = execute_query(query_name, batch_params=batch_params, batch_size=batch_size)
    return result if isinstance(result, list) else []


# ---------------------------------------------------------------------------
# get_personal_tables
# ---------------------------------------------------------------------------


async def usertable_get_all(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_get_all")
    try:
        rows = await asyncio.to_thread(
            _run_query,
            "user_tables_get_user_tables",
            {"user_id": ctx.user_id},
        )
        tables = [
            {
                "table_id": str(r.get("id", "")),
                "table_name": r.get("table_name", ""),
                "description": r.get("description", ""),
                "row_count": r.get("row_count", 0),
                "created_at": str(r.get("created_at", "")),
            }
            for r in rows
        ]
        return ToolResult(success=True, output={"tables": tables, "count": len(tables)})
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# get_personal_table_metadata
# ---------------------------------------------------------------------------


async def usertable_get_metadata(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_get_metadata")
    table_id = args.get("table_id", "").strip()
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )

    try:
        rows = await asyncio.to_thread(
            _run_query,
            "user_tables_get_table_metadata",
            {"table_id": table_id},
        )
        if not rows:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found",
                    message=f"No table found with id '{table_id}'.",
                ),
            )
        r = rows[0]
        return ToolResult(
            success=True,
            output={
                "table_id": str(r.get("id", "")),
                "table_name": r.get("table_name", ""),
                "description": r.get("description", ""),
                "version": r.get("version", 1),
                "is_public": r.get("is_public", False),
                "authenticated_read": r.get("authenticated_read", False),
                "row_count": r.get("row_count", 0),
                "created_at": str(r.get("created_at", "")),
                "updated_at": str(r.get("updated_at", "")),
            },
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# get_personal_table_fields
# ---------------------------------------------------------------------------


async def usertable_get_fields(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_get_fields")
    table_id = args.get("table_id", "").strip()
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )

    try:
        rows = await asyncio.to_thread(
            _run_query,
            "user_tables_get_table_fields",
            {"table_id": table_id},
        )
        fields = [
            {
                "field_id": str(r.get("id", "")),
                "field_name": r.get("field_name", ""),
                "display_name": r.get("display_name", ""),
                "data_type": r.get("data_type", "string"),
                "field_order": r.get("field_order", 0),
                "is_required": r.get("is_required", False),
            }
            for r in rows
        ]
        return ToolResult(success=True, output={"fields": fields, "count": len(fields)})
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# get_personal_table_data
# ---------------------------------------------------------------------------


async def usertable_get_data(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_get_data")
    table_id = args.get("table_id", "").strip()
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )

    limit = int(args.get("limit", 50))
    offset = int(args.get("offset", 0))
    sort_field = args.get("sort_field") or None
    sort_direction = (args.get("sort_direction") or "asc").lower()

    if sort_field:
        query_name = (
            "user_tables_get_table_data_sorted_asc"
            if sort_direction != "desc"
            else "user_tables_get_table_data_sorted_desc"
        )
        params: dict[str, Any] = {
            "table_id": table_id,
            "limit": limit,
            "offset": offset,
            "sort_field": sort_field,
        }
    else:
        query_name = "user_tables_get_table_data"
        params = {"table_id": table_id, "limit": limit, "offset": offset}

    try:
        rows = await asyncio.to_thread(
            _run_query,
            query_name,
            params,
        )
        data = [
            {
                "row_id": str(r.get("id", "")),
                "data": r.get("data", {}),
                "created_at": str(r.get("created_at", "")),
            }
            for r in rows
        ]
        return ToolResult(
            success=True,
            output={"rows": data, "count": len(data), "offset": offset, "limit": limit},
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# search_personal_table_data
# ---------------------------------------------------------------------------


async def usertable_search_data(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_search_data")
    table_id = args.get("table_id", "").strip()
    search_term = args.get("search_term", "").strip()
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )
    if not search_term:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation", message="search_term is required."
            ),
        )

    limit = int(args.get("limit", 50))
    offset = int(args.get("offset", 0))

    wildcard_term = f"%{search_term}%" if "%" not in search_term else search_term

    try:
        rows = await asyncio.to_thread(
            _run_query,
            "user_tables_search_table_data",
            {
                "table_id": table_id,
                "search_term": wildcard_term,
                "limit": limit,
                "offset": offset,
            },
        )
        data = [
            {
                "row_id": str(r.get("id", "")),
                "data": r.get("data", {}),
                "created_at": str(r.get("created_at", "")),
            }
            for r in rows
        ]
        return ToolResult(
            success=True,
            output={
                "rows": data,
                "count": len(data),
                "search_term": search_term,
            },
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# add_personal_table_rows
# ---------------------------------------------------------------------------


async def usertable_add_rows(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_add_rows")
    table_id = args.get("table_id", "").strip()
    rows_input = args.get("rows")
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )
    if not rows_input or not isinstance(rows_input, list):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation",
                message="rows must be a non-empty list of dicts.",
            ),
        )

    batch_params = [
        {"table_id": table_id, "data": json.dumps(row), "user_id": ctx.user_id}
        for row in rows_input
    ]

    try:
        inserted = await asyncio.to_thread(
            _run_batch,
            "user_tables_add_table_data_batch",
            batch_params,
        )
        return ToolResult(
            success=True,
            output={
                "inserted": len(inserted),
                "table_id": table_id,
                "row_ids": [str(r.get("id", "")) for r in inserted],
            },
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# update_personal_table_row
# ---------------------------------------------------------------------------


async def usertable_update_row(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_update_row")
    row_id = args.get("row_id", "").strip()
    table_id = args.get("table_id", "").strip()
    data = args.get("data")
    if not row_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="row_id is required."),
        )
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )
    if not data or not isinstance(data, dict):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation", message="data must be a dict of field values."
            ),
        )

    try:
        result = await asyncio.to_thread(
            _run_query,
            "user_tables_update_table_data",
            {
                "id": row_id,
                "table_id": table_id,
                "data": json.dumps(data),
                "user_id": ctx.user_id,
            },
        )
        if not result:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found",
                    message=f"Row '{row_id}' not found in table '{table_id}' or you do not own it.",
                ),
            )
        return ToolResult(
            success=True, output={"updated_row_id": str(result[0].get("id", row_id))}
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# delete_personal_table_row
# ---------------------------------------------------------------------------


async def usertable_delete_row(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    _raise_if_client_mode("usertable_delete_row")
    row_id = args.get("row_id", "").strip()
    table_id = args.get("table_id", "").strip()
    if not row_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="row_id is required."),
        )
    if not table_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_id is required."),
        )

    try:
        from matrx_ai.utils.supabase_client import get_async_supabase_client

        client = get_async_supabase_client()
        response = await (
            client.table("table_data")
            .delete()
            .eq("id", row_id)
            .eq("table_id", table_id)
            .eq("user_id", ctx.user_id)
            .execute()
        )
        deleted = response.data if response.data else []
        if not deleted:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found",
                    message=f"Row '{row_id}' not found or you do not own it.",
                ),
            )
        return ToolResult(success=True, output={"deleted_row_id": row_id})
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="database", message=str(e), traceback=traceback.format_exc()
            ),
        )


# ---------------------------------------------------------------------------
# create_personal_table  (alias of old create_user_generated_table)
# ---------------------------------------------------------------------------


async def usertable_create_advanced(
    args: dict[str, Any], ctx: ToolContext
) -> ToolResult:
    _raise_if_client_mode("usertable_create_advanced")
    from user_data.table_creator import UserTableCreator

    table_name = args.get("table_name", "").strip()
    description = args.get("description", "")
    data = args.get("data")

    if not table_name:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="table_name is required."),
        )
    if not data or not isinstance(data, list):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation",
                message="data must be a non-empty list of dicts, each representing a row.",
            ),
        )

    try:
        creator = UserTableCreator(user_id=ctx.user_id)
        result = await asyncio.to_thread(
            creator.create_table_from_data,
            data,
            table_name,
            description,
        )
        if not result.get("success"):
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="execution",
                    message=result.get("error", "Unknown error."),
                ),
            )
        return ToolResult(
            success=True,
            output={
                "table_id": str(result.get("table_id", "")),
                "table_name": result.get("table_name", table_name),
                "description": description,
                "row_count": result.get("row_count", len(data)),
                "field_count": result.get("field_count", 0),
                "already_existed": result.get("existing", False),
            },
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution", message=str(e), traceback=traceback.format_exc()
            ),
        )
