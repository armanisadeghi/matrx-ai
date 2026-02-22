"""Conversation Rebuild — Reconstruct message lists from the database.

When loading a conversation from the DB, tool-role messages may have empty
content (when saved by the new tool system). This module joins cx_tool_call
rows to rebuild the full ToolResultContent objects.

Usage:
    from conversation.rebuild import rebuild_conversation_messages

    messages = await rebuild_conversation_messages(conversation_id)
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def rebuild_conversation_messages(
    conversation_id: str,
    supabase_client: Any | None = None,
) -> list[dict[str, Any]]:
    """Load cx_message rows and enrich tool-role messages with cx_tool_call data.

    Returns a list of message dicts ready for UnifiedMessage.from_dict(),
    ordered by position ASC.

    The ``supabase_client`` parameter is deprecated and ignored — tool call
    loading now goes through the ORM manager.
    """
    from conversation import cx_message_manager, cx_tool_call_manager

    raw_messages = await cx_message_manager.filter_cx_messages(
        conversation_id=conversation_id,
    )

    if not raw_messages:
        return []

    rows = []
    for msg in raw_messages:
        row = _msg_to_dict(msg)
        rows.append(row)

    rows.sort(key=lambda m: m.get("position", 0))

    tool_message_ids = [
        r["id"] for r in rows
        if r.get("role") == "tool" and _is_empty_content(r.get("content"))
    ]

    tool_call_map: dict[str, list[dict[str, Any]]] = {}

    if tool_message_ids:
        tool_call_map = await _load_tool_calls_for_messages(
            tool_message_ids, conversation_id, cx_tool_call_manager,
        )

    result: list[dict[str, Any]] = []
    for row in rows:
        role = row.get("role")
        msg_id = row.get("id")

        if role == "tool" and msg_id in tool_call_map:
            rebuilt_content = _rebuild_tool_result_content(tool_call_map[msg_id])
            row["content"] = rebuilt_content

        result.append(row)

    return result


def _msg_to_dict(msg: Any) -> dict[str, Any]:
    if isinstance(msg, dict):
        return msg
    d: dict[str, Any] = {}
    for fld in ("id", "conversation_id", "role", "position", "status", "content", "metadata", "created_at"):
        val = getattr(msg, fld, None)
        if val is not None:
            d[fld] = str(val) if fld == "id" else val
    return d


def _is_empty_content(content: Any) -> bool:
    if content is None:
        return True
    if isinstance(content, list) and len(content) == 0:
        return True
    if isinstance(content, str) and content.strip() in ("", "[]", "null"):
        return True
    return False


async def _load_tool_calls_for_messages(
    message_ids: list[str],
    conversation_id: str,
    tool_call_manager: Any,
) -> dict[str, list[dict[str, Any]]]:
    """Fetch cx_tool_call rows grouped by message_id."""
    try:
        all_tc_items = await tool_call_manager.filter_cx_tool_calls(
            conversation_id=conversation_id,
        )

        rows = []
        for item in all_tc_items:
            tc_dict = item.to_dict() if hasattr(item, "to_dict") else item
            mid = tc_dict.get("message_id")
            if mid and str(mid) in message_ids and not tc_dict.get("deleted_at"):
                rows.append(tc_dict)
    except Exception as exc:
        logger.warning("Failed to load cx_tool_call rows: %s", exc)
        return {}

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        mid = str(row.get("message_id"))
        grouped.setdefault(mid, []).append(row)

    return grouped


def _rebuild_tool_result_content(tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert cx_tool_call rows into ToolResultContent-compatible dicts."""
    content_blocks: list[dict[str, Any]] = []

    for tc in tool_calls:
        content_blocks.append({
            "type": "tool_result",
            "tool_use_id": tc.get("call_id", ""),
            "call_id": tc.get("call_id", ""),
            "name": tc.get("tool_name", ""),
            "content": tc.get("output", ""),
            "is_error": tc.get("is_error", False),
        })

    return content_blocks
