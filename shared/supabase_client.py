# Placeholder: Supabase client — used by ai.db.cx_agent_memory for direct queries.
# The real implementation uses the supabase-py SDK.
import os
from typing import Any


_client: Any = None


def get_supabase_client() -> Any:
    global _client
    if _client is None:
        try:
            from supabase import create_client

            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
            if url and key:
                _client = create_client(url, key)
        except ImportError:
            pass
    return _client
