from __future__ import annotations

import traceback
from typing import Any

from tools.models import ToolContext, ToolError, ToolResult


async def usertable_create(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from user_data.table_creator import UserTableCreator

    table_name = args.get("table_name", "")
    description = args.get("description", "")
    data = args.get("data")

    if not table_name:
        return ToolResult(success=False, error=ToolError(error_type="validation", message="table_name is required."))
    if not data or not isinstance(data, list):
        return ToolResult(success=False, error=ToolError(
            error_type="validation",
            message="data must be a non-empty list of dictionaries, each representing a row.",
        ))

    try:
        creator = UserTableCreator(user_id=ctx.user_id)
        table_id = creator.create_table_from_data(data=data, table_name=table_name, description=description)
        return ToolResult(success=True, output={
            "table_id": str(table_id),
            "table_name": table_name,
            "description": description,
            "row_count": len(data),
        })
    except Exception as e:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution",
                message=f"Ensure you provide a table name and a list of dictionaries for data. {e}",
                traceback=traceback.format_exc(),
            ),
        )
