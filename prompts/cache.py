"""
Agent cache — thin wrapper around the centralized TTLCache.
Keyed by conversation_id for multi-turn conversation support.

Default: 30-minute TTL, max 200 cached agents.
"""

from typing import Optional
from client.cache import TTLCache
from prompts.agent import Agent

# Shared cache instance for all agent interactions
_agent_cache: TTLCache[Agent] = TTLCache(ttl_seconds=1800, max_size=200)


class AgentCache:
    """In-memory cache for Agent instances keyed by conversation_id.

    Backed by TTLCache with automatic TTL expiration and LRU eviction.
    """

    @classmethod
    def get(cls, conversation_id: str) -> Optional[Agent]:
        return _agent_cache.get(conversation_id)

    @classmethod
    def set(cls, conversation_id: str, agent: Agent) -> None:
        _agent_cache.set(conversation_id, agent)

    @classmethod
    def remove(cls, conversation_id: str) -> None:
        _agent_cache.remove(conversation_id)

    @classmethod
    def exists(cls, conversation_id: str) -> bool:
        return _agent_cache.exists(conversation_id)

    @classmethod
    def clear(cls) -> None:
        _agent_cache.clear()

    @classmethod
    @property
    def size(cls) -> int:
        return _agent_cache.size
