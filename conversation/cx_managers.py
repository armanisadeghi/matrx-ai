from typing import Any
from db.managers.cx_agent_memory import CxAgentMemoryBase
from db.managers.cx_request import CxRequestBase
from db.managers.cx_tool_call import CxToolCallBase
from db.managers.cx_user_request import CxUserRequestBase
from db.managers.cx_message import CxMessageBase
from db.managers.cx_media import CxMediaBase
from db.managers.cx_conversation import CxConversationBase
from config.unified_config import UnifiedConfig
from matrx_utils import vcprint
from db.models import (
    CxMessage,
    CxToolCall,
    CxMedia,
    CxUserRequest,
    CxRequest,
    CxAgentMemory,
    CxConversation,
)
from conversation.rebuild import rebuild_conversation_messages


class CxToolCallManager(CxToolCallBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxToolCallManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


class CxConversationManager(CxConversationBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxConversationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


class CxMediaManager(CxMediaBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxMediaManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


class CxMessageManager(CxMessageBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxMessageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


class CxUserRequestManager(CxUserRequestBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxUserRequestManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


class CxRequestManager(CxRequestBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxRequestManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


class CxAgentMemoryManager(CxAgentMemoryBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxAgentMemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def upsert(
        self, data: dict[str, Any], on_conflict: str = "user_id,scope,scope_id,key",
    ) -> dict[str, Any]:
        lookup = {}
        for field in on_conflict.split(","):
            field = field.strip()
            if field in data:
                lookup[field] = data[field]

        if lookup:
            existing = await self.filter_cx_agent_memories(**lookup)
            if existing:
                record = existing[0]
                record_id = record.id if hasattr(record, "id") else record.get("id")
                if record_id:
                    updated = await self.update_cx_agent_memory(record_id, **data)
                    return updated if isinstance(updated, dict) else (updated.to_dict() if hasattr(updated, "to_dict") else {})

        created = await self.create_cx_agent_memory(**data)
        return created if isinstance(created, dict) else (created.to_dict() if hasattr(created, "to_dict") else {})

    async def search_by_content(
        self,
        user_id: str,
        scope: str,
        query: str,
        *,
        memory_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {"user_id": user_id, "scope": scope}
        if memory_type:
            filters["memory_type"] = memory_type

        results = await self.filter_cx_agent_memories(**filters)
        if not results:
            return []

        query_lower = query.lower()
        matched = []
        for item in results:
            content = ""
            if hasattr(item, "content"):
                content = str(item.content)
            elif isinstance(item, dict):
                content = str(item.get("content", ""))
            if query_lower in content.lower():
                matched.append(item if isinstance(item, dict) else (item.to_dict() if hasattr(item, "to_dict") else {}))

        matched.sort(
            key=lambda x: x.get("importance", 0) if isinstance(x, dict) else 0,
            reverse=True,
        )
        return matched[:limit]

    async def recall(
        self,
        user_id: str,
        scope: str,
        *,
        key: str | None = None,
        memory_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {"user_id": user_id, "scope": scope}
        if key:
            filters["key"] = key
        if memory_type:
            filters["memory_type"] = memory_type

        results = await self.filter_cx_agent_memories(**filters)
        if not results:
            return []

        items = [
            item if isinstance(item, dict) else (item.to_dict() if hasattr(item, "to_dict") else {})
            for item in results
        ]
        items.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return items[:limit]

    async def update_access_count(self, memory_id: str, current_count: int) -> None:
        from datetime import datetime, timezone
        try:
            await self.update_cx_agent_memory(
                memory_id,
                access_count=current_count + 1,
                last_accessed_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception:
            pass

    async def delete_by_key(self, user_id: str, scope: str, key: str) -> int:
        results = await self.filter_cx_agent_memories(user_id=user_id, scope=scope, key=key)
        count = 0
        for item in results:
            record_id = item.id if hasattr(item, "id") else item.get("id") if isinstance(item, dict) else None
            if record_id:
                await self.delete_cx_agent_memory(record_id)
                count += 1
        return count

    async def update_by_key(
        self, user_id: str, scope: str, key: str, data: dict[str, Any],
    ) -> int:
        results = await self.filter_cx_agent_memories(user_id=user_id, scope=scope, key=key)
        count = 0
        for item in results:
            record_id = item.id if hasattr(item, "id") else item.get("id") if isinstance(item, dict) else None
            if record_id:
                await self.update_cx_agent_memory(record_id, **data)
                count += 1
        return count


cx_conversation_manager_instance = CxConversationManager()
cx_media_manager_instance = CxMediaManager()
cx_message_manager_instance = CxMessageManager()
cx_user_request_manager_instance = CxUserRequestManager()
cx_request_manager_instance = CxRequestManager()
cx_agent_memory_manager_instance = CxAgentMemoryManager()
cx_tool_call_manager_instance = CxToolCallManager()


class CxManagers:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxManagers, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.conversation: CxConversationManager = cx_conversation_manager_instance
        self.message: CxMessageManager = cx_message_manager_instance
        self.tool_call: CxToolCallManager = cx_tool_call_manager_instance
        self.media: CxMediaManager = cx_media_manager_instance
        self.user_request: CxUserRequestManager = cx_user_request_manager_instance
        self.request: CxRequestManager = cx_request_manager_instance
        self.agent_memory: CxAgentMemoryManager = cx_agent_memory_manager_instance

    async def get_conversation_data(self, conversation_id: str) -> dict[str, Any]:
        all_data = await self.conversation.get_cx_conversation_with_all_related(
            conversation_id
        )
        vcprint(all_data, "[CX MANAGERS] All Data", color="cyan")
        conversation = all_data[0]
        foreign_keys = all_data[1]["foreign_keys"]
        inverse_fks = all_data[1]["inverse_foreign_keys"]
        user_requests = inverse_fks["cx_user_request"]
        requests = inverse_fks["cx_request"]
        messages = inverse_fks["cx_message"]
        tool_calls = inverse_fks["cx_tool_call"]
        media = inverse_fks["cx_media"]

        return {
            "conversation": conversation,
            "foreign_keys": foreign_keys,
            "user_requests": user_requests,
            "requests": requests,
            "messages": messages,
            "tool_calls": tool_calls,
            "media": media,
        }

    async def get_unified_config(self, flat_data: dict[str, Any]) -> UnifiedConfig:
        conversation = flat_data["conversation"]
        messages = flat_data["messages"]
        tool_calls = flat_data["tool_calls"]
        media = flat_data["media"]

        messages_rebuilt = await rebuild_conversation_messages(
            messages, tool_calls, media
        )
        vcprint(messages_rebuilt, "[CX MANAGERS] Messages Rebuilt", color="green")

        config_dict = {
            "model": conversation.ai_model_id,
            "system_instruction": conversation.system_instruction,
            "messages": messages_rebuilt,
            **conversation.config,
        }

        unified_config = UnifiedConfig.from_dict(config_dict)
        vcprint(unified_config, "[CX MANAGERS] Unified Config", color="cyan")

        return unified_config

    async def get_conversation_unified_config(
        self, conversation_id: str
    ) -> UnifiedConfig:
        conversation_data = await self.get_conversation_data(conversation_id)

        vcprint(conversation_data, "[CX MANAGERS] Conversation Data", color="cyan")
        conversation: CxConversation = conversation_data["conversation"]
        messages: list[CxMessage] = conversation_data["messages"]
        tool_calls: list[CxToolCall] = conversation_data["tool_calls"]
        media: list[CxMedia] = conversation_data["media"]

        messages_rebuilt = await rebuild_conversation_messages(
            messages, tool_calls, media
        )

        config_dict = {
            "model": conversation.ai_model_id,
            "system_instruction": conversation.system_instruction,
            "messages": messages_rebuilt,
            **conversation.config,
        }

        return UnifiedConfig.from_dict(config_dict)

    async def get_full_conversation(self, conversation_id: str) -> dict[str, Any]:
        conversation_data = await self.get_conversation_data(conversation_id)
        unified_config: UnifiedConfig = await self.get_unified_config(conversation_data)
        conversation: CxConversation = conversation_data["conversation"]
        user_requests: list[CxUserRequest] = conversation_data["user_requests"]
        requests: list[CxRequest] = conversation_data["requests"]

        result = {
            "conversation_id": conversation.id,
            "variables": conversation.variables,
            "overrides": conversation.overrides,
            "unified_config": unified_config,
            "user_requests": user_requests,
            "requests": requests,
        }

        return result


cxm = CxManagers()
