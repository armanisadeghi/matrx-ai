# File: database/main/managers/cx_conversation.py
from typing import Any, TypedDict, cast

from db.managers.cx_conversation import CxConversationBase
from db.models import CxConversation


class CxConversationData(TypedDict):
    id: str
    user_id: str
    title: str | None
    system_instruction: str | None
    config: dict[str, Any]
    status: str
    message_count: int
    metadata: dict[str, Any]
    variables: dict[str, Any]
    overrides: dict[str, Any]


class CxConversationManager(CxConversationBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxConversationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: CxConversation) -> None:
        if not isinstance(item.config, dict):
            item.config = {}
        if not isinstance(item.metadata, dict):
            item.metadata = {}
        if not isinstance(item.variables, dict):
            item.variables = {}
        if not isinstance(item.overrides, dict):
            item.overrides = {}

    async def load_and_get_config(self, id: str) -> CxConversationData | None:
        item = await self.load_item_or_none(id=id)
        if item is None:
            return None
        return CxConversationData(
            id=str(item.id),
            user_id=str(item.user_id),
            title=item.title,
            system_instruction=item.system_instruction,
            config=cast(dict[str, Any], item.config),
            status=item.status or "active",
            message_count=item.message_count or 0,
            metadata=cast(dict[str, Any], item.metadata),
            variables=cast(dict[str, Any], item.variables),
            overrides=cast(dict[str, Any], item.overrides),
        )


cx_conversation_manager_instance = CxConversationManager()