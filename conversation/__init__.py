"""Conversation State & Persistence.

Singleton manager instances for conversation exchange tables.

Usage:
    from conversation import cx_conversation_manager, cx_message_manager, ...
"""

from conversation.cx_conversation import cx_conversation_manager_instance as cx_conversation_manager
from conversation.cx_message import cx_message_manager_instance as cx_message_manager
from conversation.cx_media import cx_media_manager_instance as cx_media_manager
from conversation.cx_user_request import cx_user_request_manager_instance as cx_user_request_manager
from conversation.cx_request import cx_request_manager_instance as cx_request_manager
from database.main.managers.cx_tool_call import cx_tool_call_manager_instance as cx_tool_call_manager
from conversation.cx_agent_memory import cx_agent_memory_manager_instance as cx_agent_memory_manager
from database.main.managers.tools import tools_manager_instance as tools_manager

__all__ = [
    "cx_conversation_manager",
    "cx_message_manager",
    "cx_media_manager",
    "cx_user_request_manager",
    "cx_request_manager",
    "cx_tool_call_manager",
    "cx_agent_memory_manager",
    "tools_manager",
]
