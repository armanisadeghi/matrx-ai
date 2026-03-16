"""
Client mode configuration — the single source of truth for all client-mode requirements.

When matrx-ai is used as a library inside a desktop app (no direct PostgreSQL access),
the host app calls:

    import matrx_ai
    matrx_ai.initialize(
        client_mode=True,
        client_config=ClientModeConfig(
            server_url=os.environ["AIDREAM_SERVER_URL_LIVE"],
            supabase_url=...,
            supabase_anon_key=...,
            get_jwt=lambda: auth_manager.current_token,
            conversation_handler=MyConversationHandler(),
        ),
    )

Every requirement for client mode is declared here. If any field is missing,
initialize() raises ClientModeConfigError listing every problem before doing
anything else. There is no partial initialization.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    pass


class ClientModeConfigError(Exception):
    """Raised at initialize() time when client_mode=True config is incomplete."""


@runtime_checkable
class ConversationHandler(Protocol):
    """
    Protocol that the host app must implement to handle conversation persistence
    in client mode. The library calls these methods instead of writing to the
    cloud database directly.

    The host app is responsible for how data is stored — SQLite, in-memory,
    a local file, or even forwarding to a remote API. We do not prescribe the
    storage mechanism.
    """

    async def ensure_conversation_exists(
        self,
        conversation_id: str,
        user_id: str,
        parent_conversation_id: str | None = None,
        variables: dict[str, Any] | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> None:
        """Create the conversation record if it does not already exist."""
        ...

    async def create_pending_user_request(
        self,
        request_id: str,
        conversation_id: str,
        user_id: str,
    ) -> None:
        """Insert a user request record with status='pending'."""
        ...

    async def persist_completed_request(
        self,
        completed: Any,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Persist all data from a completed AI execution.
        Must return a dict with keys: conversation_id, user_request_id,
        message_ids (list), request_ids (list).
        """
        ...

    async def log_tool_call_start(
        self,
        row_id: str,
        data: dict[str, Any],
    ) -> None:
        """Insert a tool call record with status='running'."""
        ...

    async def log_tool_call_update(
        self,
        row_id: str,
        data: dict[str, Any],
    ) -> None:
        """Update an existing tool call record (completion or error)."""
        ...

    async def get_conversation_config(
        self,
        conversation_id: str,
    ) -> dict[str, Any]:
        """
        Return the stored conversation config dict for the given conversation_id.
        Called by ConversationResolver when rebuilding state from local storage.
        """
        ...


@dataclass
class ClientModeConfig:
    """
    All configuration required when matrx-ai runs in client (desktop) mode.

    server_url:
        Base URL of the AIDream server. Must be set from the
        AIDREAM_SERVER_URL_LIVE environment variable — never hard-coded.
        e.g. "https://server.app.matrxserver.com"

    supabase_url:
        Supabase project URL for PostgREST access.
        e.g. "https://abc123.supabase.co"

    supabase_anon_key:
        Supabase publishable anon key. Safe to embed in desktop apps —
        RLS policies on the database enforce per-user data isolation.

    get_jwt:
        A callable (no arguments) that returns the current user's JWT string,
        or None if the user is not authenticated. Called at request time, not
        at initialization time, so the token can rotate between calls.

    conversation_handler:
        An object implementing the ConversationHandler protocol. All
        conversation persistence (gate, persistence, tool logging) is
        delegated to this object instead of writing to the cloud DB directly.

    source_app:
        Optional. When set, only tools with this source_app value are fetched
        from the server via GET /api/ai-tools/app/{source_app}. When None,
        all tools are fetched via GET /api/ai-tools.
        e.g. "matrx_local" to fetch only tools belonging to the desktop app.
        This prevents the registry from attempting to import server-side tool
        modules (like mcp_server.*) that don't exist in the desktop environment.
    """

    server_url: str = field(default_factory=lambda: os.environ.get("AIDREAM_SERVER_URL_LIVE", ""))
    supabase_url: str = ""
    supabase_anon_key: str = ""
    get_jwt: Any = None  # Callable[[], str | None]
    conversation_handler: Any = None  # ConversationHandler
    source_app: str | None = None  # e.g. "matrx_local" — filters tools fetched from API

    def validate(self) -> None:
        """Validate all required fields. Raises ClientModeConfigError if anything is missing."""
        errors: list[str] = []

        if not self.server_url:
            errors.append(
                "server_url is required. Set AIDREAM_SERVER_URL_LIVE in your environment "
                "or pass server_url explicitly to ClientModeConfig."
            )

        if not self.supabase_url:
            errors.append("supabase_url is required (Supabase project URL).")

        if not self.supabase_anon_key:
            errors.append("supabase_anon_key is required (Supabase publishable anon key).")

        if self.get_jwt is None or not callable(self.get_jwt):
            errors.append(
                "get_jwt must be a callable with no arguments that returns str | None "
                "(the current user's JWT, or None if unauthenticated)."
            )

        if self.conversation_handler is None:
            errors.append(
                "conversation_handler is required. Provide an object implementing "
                "the ConversationHandler protocol to handle local conversation persistence."
            )
        elif not isinstance(self.conversation_handler, ConversationHandler):
            errors.append(
                "conversation_handler does not implement the ConversationHandler protocol. "
                "It must define: ensure_conversation_exists, create_pending_user_request, "
                "persist_completed_request, log_tool_call_start, log_tool_call_update, "
                "get_conversation_config."
            )

        if errors:
            raise ClientModeConfigError(
                "client_mode=True requires a fully configured ClientModeConfig.\n"
                "The following are missing or invalid:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )
