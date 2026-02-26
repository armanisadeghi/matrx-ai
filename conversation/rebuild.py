"""Conversation Rebuild — Reconstruct message lists from the database.

When loading a conversation from the DB, tool-role messages may have empty
content (when saved by the new tool system). This module joins cx_tool_call
rows to rebuild the full ToolResultContent objects.

Usage:
    from conversation.rebuild import rebuild_conversation_messages

    messages = await rebuild_conversation_messages(raw_messages, tool_calls, media)
"""
from __future__ import annotations

from typing import Any

from config.unified_config import UnifiedMessage
from db.models import (
    CxMessage,
    CxToolCall,
    CxMedia,
)


def _rebuild_tool_result_content(
    tool_calls: list[CxToolCall],
) -> list[dict[str, Any]]:
    content_blocks: list[dict[str, Any]] = []

    for tc in tool_calls:
        content_blocks.append(
            {
                "type": "tool_result",
                "tool_use_id": tc.call_id,
                "call_id": tc.call_id,
                "name": tc.tool_name,
                "content": tc.output,
                "is_error": tc.is_error,
            }
        )

    return content_blocks


async def _map_tool_calls_to_messages(
    messages: list[CxMessage],
    tool_calls: list[CxToolCall],
) -> dict[str, list[dict[str, Any]]]:
    message_ids = [msg.id for msg in messages]

    rows = []
    for tc in tool_calls:
        mid = tc.message_id
        if mid and str(mid) in message_ids and not tc.deleted_at:
            rows.append(tc)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        mid = str(row.message_id)
        grouped.setdefault(mid, []).append(row)

    return grouped


async def rebuild_conversation_messages(
    raw_messages: list[CxMessage],
    tool_calls: list[CxToolCall],
    media: list[CxMedia],
) -> list[CxMessage]:
    ordered_messages = sorted(raw_messages, key=lambda x: x.position)

    tool_call_map: dict[str, list[CxToolCall]] = await _map_tool_calls_to_messages(
        ordered_messages,
        tool_calls,
    )

    result: list[dict[str, Any]] = []
    for msg in ordered_messages:
        role = msg.role
        msg_id = msg.id

        if role == "tool" and msg_id in tool_call_map:
            rebuilt_content = _rebuild_tool_result_content(tool_call_map[msg_id])
            msg.content = rebuilt_content

        unified_message = UnifiedMessage.from_cx_message(msg)
        result.append(unified_message)

    return result
