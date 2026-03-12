"""
CX_ Database Layer — Singleton manager instances for conversation exchange tables.

Usage:
    from matrx_ai.db.custom import cxm, rebuild_conversation_messages, persist_completed_request
    from matrx_ai.db.custom import ensure_conversation_exists, create_pending_user_request
"""

from .conversation_gate import (
    ConversationGateError,
    create_new_conversation,
    create_pending_user_request,
    ensure_conversation_exists,
    ensure_user_request_exists,
    launch_conversation_gate,
    update_conversation_status,
    update_user_request_status,
    verify_existing_conversation,
)
from .conversation_rebuild import rebuild_conversation_messages
from .cx_managers import (
    CxAgentMemoryManager,
    CxConversationManager,
    CxManagers,
    CxMediaManager,
    CxMessageManager,
    CxRequestManager,
    CxToolCallManager,
    CxUserRequestManager,
    cxm,
)

__all__ = [
    "ConversationGateError",
    "CxAgentMemoryManager",
    "CxConversationManager",
    "CxManagers",
    "CxMediaManager",
    "CxMessageManager",
    "CxRequestManager",
    "CxToolCallManager",
    "CxUserRequestManager",
    "create_new_conversation",
    "create_pending_user_request",
    "cxm",
    "ensure_conversation_exists",
    "ensure_user_request_exists",
    "launch_conversation_gate",
    "rebuild_conversation_messages",
    "update_conversation_status",
    "update_user_request_status",
    "verify_existing_conversation",
]
