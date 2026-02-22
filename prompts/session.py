from __future__ import annotations

from typing import Optional


class SimpleSession:
    def __init__(
        self,
        conversation_id: str | None = None,
        debug: bool = False,
        # Legacy params accepted for backward compat but ignored;
        # the canonical source is ExecutionContext.
        user_id: str | None = None,
        project_id: str | None = None,
        emitter: object | None = None,
        parent_conversation_id: str | None = None,
        parent_request_id: str | None = None,
        is_internal_agent: bool = False,
    ):
        from context.app_context import get_app_context
        ctx = get_app_context()

        self._conversation_id = conversation_id or ctx.conversation_id
        self.debug = debug

    @property
    def user_id(self) -> str:
        from context.app_context import get_app_context
        return get_app_context().user_id

    @property
    def emitter(self):
        from context.app_context import get_app_context
        return get_app_context().emitter

    @emitter.setter
    def emitter(self, value: object) -> None:
        pass

    @property
    def conversation_id(self) -> str:
        return self._conversation_id

    @conversation_id.setter
    def conversation_id(self, value: str) -> None:
        self._conversation_id = value

    @property
    def project_id(self) -> Optional[str]:
        from context.app_context import get_app_context
        return get_app_context().project_id

    @property
    def parent_conversation_id(self) -> Optional[str]:
        from context.app_context import get_app_context
        return get_app_context().parent_conversation_id

    @parent_conversation_id.setter
    def parent_conversation_id(self, value: str | None) -> None:
        pass

    @property
    def parent_request_id(self) -> Optional[str]:
        from context.app_context import get_app_context
        return get_app_context().parent_request_id

    @parent_request_id.setter
    def parent_request_id(self, value: str | None) -> None:
        pass

    @property
    def is_internal_agent(self) -> bool:
        from context.app_context import get_app_context
        return get_app_context().is_internal_agent

    @is_internal_agent.setter
    def is_internal_agent(self, value: bool) -> None:
        pass
