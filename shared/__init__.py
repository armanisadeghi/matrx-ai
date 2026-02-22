"""Shared Utilities.

- supabase_client: Direct Supabase client access
- file_handler: File I/O utilities
- json_utils: JSON serialization helpers
"""

from shared.supabase_client import get_supabase_client

__all__ = [
    "get_supabase_client",
]
