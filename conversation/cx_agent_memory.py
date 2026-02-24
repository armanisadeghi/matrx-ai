from __future__ import annotations

from typing import Any

from db.managers.cx_agent_memory import (
    CxAgentMemoryBase,
    cx_agent_memory_manager_instance,
)


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


cx_agent_memory_manager_instance = CxAgentMemoryManager()
