"""Conversation and Agent config resolution.

Single responsibility: given an ID (or raw config), return a UnifiedConfig
ready for execution. Owns the resolution order — in-memory cache first,
database second — so nothing outside this module needs to know how config
is sourced.

Usage:
    from conversation.conversation_resolver import ConversationResolver, AgentConfigResolver

    # Continuing an existing conversation:
    config = await ConversationResolver.from_conversation_id(
        conversation_id, user_input=request.user_input
    )

    # Starting an agent:
    config = await AgentConfigResolver.from_id(
        agent_id, variables=request.variables, overrides=request.config_overrides
    )
"""

from __future__ import annotations

import traceback
from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status
from matrx_utils import vcprint

from config.unified_config import UnifiedConfig


# ---------------------------------------------------------------------------
# Conversation resolver
# ---------------------------------------------------------------------------


class ConversationResolver:
    """Resolves a UnifiedConfig from a conversation_id.

    Resolution order:
        1. AgentCache (in-memory, instant — already converted, zero reconstruction)
        2. Database via cxm (auto-cached by the ORM layer)
        3. HTTP 404 if not found

    The in-memory AgentCache is the primary cache. It stores Agent objects
    whose .config is the fully-reconstructed UnifiedConfig (media already
    processed, tool content already rebuilt). Hitting the cache means zero
    DB queries and zero reconstruction work.
    """

    @staticmethod
    async def from_conversation_id(
        conversation_id: str,
        user_input: Union[str, List[Dict[str, Any]], None] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ) -> UnifiedConfig:
        """Return a UnifiedConfig ready for execution.

        Appends user_input (if provided) and applies config_overrides before
        returning. Updates AgentCache after a DB load so subsequent calls
        within the same process are instant.

        Raises HTTPException(404) if the conversation cannot be found.
        """
        from prompts.agent import Agent
        from prompts.cache import AgentCache
        from conversation import cxm

        agent = AgentCache.get(conversation_id)

        if agent is not None:
            vcprint(f"[ConversationResolver] Cache hit: {conversation_id}", color="green")
            config = deepcopy(agent.config)
        else:
            vcprint(f"[ConversationResolver] Cache miss — loading from DB: {conversation_id}", color="yellow")
            try:
                config = await cxm.get_conversation_unified_config(conversation_id)
            except Exception as exc:
                tb_str = traceback.format_exc()
                vcprint(
                    f"[ConversationResolver] DB load FAILED for {conversation_id}\n"
                    f"  Exception type : {type(exc).__name__}\n"
                    f"  Exception      : {exc}\n"
                    f"  Traceback:\n{tb_str}",
                    color="red",
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation not found: {conversation_id}",
                ) from exc

            agent = Agent(config=deepcopy(config))
            AgentCache.set(conversation_id, agent)

        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        if user_input:
            config.append_or_extend_user_input(user_input)

        return config

    @staticmethod
    async def warm(conversation_id: str) -> bool:
        """Pre-load a conversation into AgentCache. Returns True if newly cached.

        Called by the warm endpoint. Fire-and-forget safe — errors are logged
        but never raised.
        """
        from prompts.agent import Agent
        from prompts.cache import AgentCache
        from conversation import cxm

        if AgentCache.exists(conversation_id):
            vcprint(f"[ConversationResolver] Already cached: {conversation_id}", color="green")
            return False

        try:
            config = await cxm.get_conversation_unified_config(conversation_id)
            AgentCache.set_warm(conversation_id, Agent(config=config))
            vcprint(f"[ConversationResolver] Warmed: {conversation_id}", color="green")
            return True
        except Exception as exc:
            vcprint(f"[ConversationResolver] Warm failed: {exc}", color="red")
            return False


# ---------------------------------------------------------------------------
# Agent config resolver
# ---------------------------------------------------------------------------


class AgentConfigResolver:
    """Resolves a UnifiedConfig from an agent_id (prompt ID).

    Loads the agent definition from the database (via PromptManager), applies
    variables and config overrides, and returns the resulting UnifiedConfig.

    The PromptManager already caches prompt definitions in-memory, so repeated
    calls for the same agent_id are fast after the first load.
    """

    @staticmethod
    async def from_id(
        agent_id: str,
        variables: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> UnifiedConfig:
        """Return a UnifiedConfig for the given agent prompt ID.

        Raises HTTPException(404) if the agent cannot be found.
        """
        from prompts.agent import Agent

        try:
            agent = await Agent.from_id(agent_id, variables=variables, config_overrides=overrides)
        except Exception as exc:
            vcprint(f"[AgentConfigResolver] Load failed for {agent_id!r}: {exc}", color="red")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}",
            ) from exc

        return agent.config

    @staticmethod
    async def warm(agent_id: str) -> bool:
        """Pre-load an agent definition into PromptManager cache. Returns True if loaded.

        The act of calling Agent.from_id() causes the PromptManager to cache
        the prompt definition. Subsequent calls within the same process skip
        the DB query entirely.

        Fire-and-forget safe — errors are logged but never raised.
        """
        from prompts.agent import Agent

        try:
            await Agent.from_id(agent_id)
            vcprint(f"[AgentConfigResolver] Warmed: {agent_id}", color="green")
            return True
        except Exception as exc:
            vcprint(f"[AgentConfigResolver] Warm failed for {agent_id!r}: {exc}", color="red")
            return False
