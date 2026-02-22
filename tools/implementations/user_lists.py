from __future__ import annotations

from typing import Any
from tools.models import ToolContext, ToolError, ToolResult
from matrx_utils import vcprint


async def create_user_list(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from user_data.user_list_creator import UserListCreator

    list_name = args.get("list_name", "")
    description = args.get("description", "")
    items = args.get("items", [])

    if not list_name:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="list_name is required."),
        )
    if not items:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation", message="items must be a non-empty list."
            ),
        )

    for idx, item in enumerate(items):
        if not isinstance(item, dict) or not item.get("label"):
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="validation",
                    message=f"Item at index {idx} must be an object with a 'label' field.",
                ),
            )

    try:
        creator = UserListCreator(ctx.user_id)
        result = creator.create_list_with_items(items, list_name, description)
        return ToolResult(
            success=True,
            output={
                "list_id": str(result) if result else None,
                "list_name": list_name,
                "item_count": len(items),
                "message": f"List '{list_name}' created with {len(items)} items.",
            },
        )
    except Exception as e:
        error_mesage=str(e)
        vcprint(error_mesage, "error_mesage", color="red")
        return ToolResult(
            success=False, error=ToolError(error_type="execution", message=str(e))
        )


async def create_simple_list(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from user_data.user_list_creator import UserListCreator

    list_name = args.get("list_name", "")
    description = args.get("description", "")
    labels = args.get("labels", [])
    group_name = args.get("group_name")

    if not list_name:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="list_name is required."),
        )
    if not labels or not isinstance(labels, list):
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation",
                message="labels must be a non-empty list of strings.",
            ),
        )

    for idx, label in enumerate(labels):
        if not isinstance(label, str) or not label.strip():
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="validation",
                    message=f"Label at index {idx} must be a non-empty string.",
                ),
            )

    try:
        creator = UserListCreator(ctx.user_id)
        result = creator.create_simple_list(labels, list_name, description, group_name)
        return ToolResult(
            success=True,
            output={
                "list_id": str(result) if result else None,
                "list_name": list_name,
                "item_count": len(labels),
                "message": f"Simple list '{list_name}' created with {len(labels)} items.",
            },
        )
    except Exception as e:
        error_mesage=str(e)
        vcprint(error_mesage, "error_mesage", color="red")
        return ToolResult(
            success=False, error=ToolError(error_type="execution", message=str(e))
        )


def _make_serializable(obj: Any) -> Any:
    import uuid
    from datetime import date, datetime

    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_serializable(i) for i in obj]
    return obj


async def get_user_lists(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from matrx_orm.sql_executor import execute_standard_query

    page = max(1, args.get("page", 1))
    page_size = min(100, max(1, args.get("page_size", 50)))
    search_term = args.get("search_term")

    try:
        if search_term:
            offset = (page - 1) * page_size
            result = execute_standard_query(
                "user_lists_search_lists",
                {
                    "user_id": ctx.user_id,
                    "search_term": f"%{search_term}%",
                    "limit": page_size,
                    "offset": offset,
                },
            )
        else:
            raw = execute_standard_query(
                "user_lists_get_user_lists", {"user_id": ctx.user_id}
            )
            all_lists = _make_serializable(raw) if raw else []
            offset = (page - 1) * page_size
            result = (
                all_lists[offset : offset + page_size]
                if isinstance(all_lists, list)
                else all_lists
            )

        lists = _make_serializable(result) if result else []
        return ToolResult(
            success=True,
            output={
                "lists": lists,
                "page": page,
                "page_size": page_size,
                "count": len(lists) if isinstance(lists, list) else 0,
            },
        )
    except Exception as e:
        error_mesage=str(e)
        vcprint(error_mesage, "error_mesage", color="red")
        return ToolResult(
            success=False, error=ToolError(error_type="execution", message=error_mesage)
        )


async def get_list_details(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from matrx_orm.sql_executor import execute_standard_query

    list_id = args.get("list_id")
    group_by = args.get("group_by", False)

    if not list_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="list_id is required."),
        )

    try:
        list_data = execute_standard_query("user_lists_get_list", {"list_id": list_id})
        if not list_data:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found", message=f"List '{list_id}' not found."
                ),
            )

        query_name = (
            "user_lists_get_list_items_grouped"
            if group_by
            else "user_lists_get_list_items"
        )
        items = execute_standard_query(query_name, {"list_id": list_id})

        return ToolResult(
            success=True,
            output=_make_serializable(
                {
                    "list": list_data,
                    "items": items or [],
                    "is_grouped": group_by,
                }
            ),
        )
    except Exception as e:
        error_mesage=str(e)
        vcprint(error_mesage, "error_mesage", color="red")
        return ToolResult(
            success=False, error=ToolError(error_type="execution", message=str(e))
        )


async def update_list_item(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from matrx_orm.sql_executor import execute_standard_query

    item_id = args.get("item_id")
    if not item_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="item_id is required."),
        )

    update_fields = {
        k: args[k]
        for k in ("label", "description", "help_text", "group_name")
        if k in args
    }
    if not update_fields:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation",
                message="At least one field to update is required.",
            ),
        )

    try:
        execute_standard_query(
            "user_lists_update_list_item",
            {
                "item_id": item_id,
                "user_id": ctx.user_id,
                **{
                    k: update_fields.get(k)
                    for k in ("label", "description", "help_text", "group_name")
                },
            },
        )
        return ToolResult(
            success=True,
            output={"item_id": item_id, "message": "Item updated successfully."},
        )
    except Exception as e:
        error_mesage=str(e)
        vcprint(error_mesage, "error_mesage", color="red")
        return ToolResult(
            success=False, error=ToolError(error_type="execution", message=str(e))
        )


async def batch_update_list_items(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from matrx_orm.sql_executor import execute_standard_query

    list_id = args.get("list_id")
    items = args.get("items", [])

    if not list_id:
        return ToolResult(
            success=False,
            error=ToolError(error_type="validation", message="list_id is required."),
        )
    if not items:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation", message="items must be a non-empty list."
            ),
        )

    success_count = 0
    failed_items: list[dict[str, Any]] = []

    for item in items:
        item_id = item.get("id")
        if not item_id:
            failed_items.append({"item": item, "error": "Missing 'id' field."})
            continue
        try:
            execute_standard_query(
                "user_lists_update_list_item",
                {
                    "item_id": item_id,
                    "user_id": ctx.user_id,
                    "label": item.get("label"),
                    "description": item.get("description"),
                    "help_text": item.get("help_text"),
                    "group_name": item.get("group_name"),
                },
            )
            success_count += 1
        except Exception as e:
            error_mesage=str(e)
            vcprint(error_mesage, "error_mesage", color="red")
            failed_items.append({"item_id": item_id, "error": error_mesage})

    return ToolResult(
        success=True,
        output={
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items,
            "message": f"Updated {success_count} items, {len(failed_items)} failed.",
        },
    )
