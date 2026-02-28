#!/usr/bin/env python3
"""One-shot import rewriter for the matrx-ai restructuring.

Rewrites all `from ai.*`, `from aidream.*`, `from matrix.*`, `from common.*`
imports to the new domain-centric package layout.

Run once, then delete this script.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Directories that contain files to rewrite (new locations only)
TARGET_DIRS = [
    "providers",
    "tools",
    "prompts",
    "config",
    "conversation",
    "client",
    "media",
    "context",
    "models",
    "shared",
    "tests",
    "app",
]

# ─── Replacement rules ───
# Order matters! More specific patterns first to avoid partial matches.
# Each tuple: (old_pattern, new_pattern)
# These are exact string replacements on import lines.

REPLACEMENTS = [
    # ── aidream → context ──
    ("from aidream.api.utils.console_emitter import", "from context.console_emitter import"),
    ("from context.emitter_protocol import", "from context.emitter_protocol import"),
    ("from aidream.api.context import", "from context.app_context import"),
    ("from aidream.api.events import", "from context.events import"),

    # ── matrix → models ──
    ("from matrix.ai_models.ai_model_manager import", "from models.ai_model_manager import"),
    ("from matrix.ai_models.ai_model_base import", "from models.ai_model_base import"),

    # ── common → shared ──
    ("from common.utils.file_handlers.file_handler import", "from shared.file_handler import"),
    ("from common.utils.json_matrx import", "from shared.json_utils import"),
    ("from common.supabase.supabase_client import", "from shared.supabase_client import"),
    ("from common import vcprint", "from matrx_utils import vcprint"),

    # ── ai.tool_system.arg_models → tools.arg_models ──
    ("from ai.tool_system.arg_models.browser_args import", "from tools.arg_models.browser_args import"),
    ("from ai.tool_system.arg_models.db_args import", "from tools.arg_models.db_args import"),
    ("from ai.tool_system.arg_models.fs_args import", "from tools.arg_models.fs_args import"),
    ("from ai.tool_system.arg_models.math_args import", "from tools.arg_models.math_args import"),
    ("from ai.tool_system.arg_models.memory_args import", "from tools.arg_models.memory_args import"),
    ("from ai.tool_system.arg_models.shell_args import", "from tools.arg_models.shell_args import"),
    ("from ai.tool_system.arg_models.text_args import", "from tools.arg_models.text_args import"),
    ("from ai.tool_system.arg_models.web_args import", "from tools.arg_models.web_args import"),

    # ── ai.tool_system.implementations → tools.implementations ──
    ("from ai.tool_system.implementations._summarize_helper import", "from tools.implementations._summarize_helper import"),
    ("from ai.tool_system.implementations.browser import", "from tools.implementations.browser import"),
    ("from ai.tool_system.implementations.code import", "from tools.implementations.code import"),
    ("from ai.tool_system.implementations.database import", "from tools.implementations.database import"),
    ("from ai.tool_system.implementations.filesystem import", "from tools.implementations.filesystem import"),
    ("from ai.tool_system.implementations.math import", "from tools.implementations.math import"),
    ("from ai.tool_system.implementations.memory import", "from tools.implementations.memory import"),
    ("from ai.tool_system.implementations.news import", "from tools.implementations.news import"),
    ("from ai.tool_system.implementations.questionnaire import", "from tools.implementations.questionnaire import"),
    ("from ai.tool_system.implementations.seo import", "from tools.implementations.seo import"),
    ("from ai.tool_system.implementations.shell import", "from tools.implementations.shell import"),
    ("from ai.tool_system.implementations.text import", "from tools.implementations.text import"),
    ("from ai.tool_system.implementations.travel import", "from tools.implementations.travel import"),
    ("from ai.tool_system.implementations.user_lists import", "from tools.implementations.user_lists import"),
    ("from ai.tool_system.implementations.user_tables import", "from tools.implementations.user_tables import"),
    ("from ai.tool_system.implementations.web import", "from tools.implementations.web import"),
    ("from ai.tool_system.implementations import", "from tools.implementations import"),

    # ── ai.tool_system → tools ──
    ("from ai.tool_system.tests.mimic_model_tests import", "from tools.tests.mimic_model_tests import"),
    ("from ai.tool_system.handle_tool_calls import", "from tools.handle_tool_calls import"),
    ("from ai.tool_system.external_mcp import", "from tools.external_mcp import"),
    ("from ai.tool_system.agent_tool import", "from tools.agent_tool import"),
    ("from ai.tool_system.guardrails import", "from tools.guardrails import"),
    ("from ai.tool_system.lifecycle import", "from tools.lifecycle import"),
    ("from ai.tool_system.streaming import", "from tools.streaming import"),
    ("from ai.tool_system.executor import", "from tools.executor import"),
    ("from ai.tool_system.registry import", "from tools.registry import"),
    ("from ai.tool_system.logger import", "from tools.logger import"),
    ("from ai.tool_system.models import", "from tools.models import"),

    # ── ai.instructions → prompts.instructions ──
    ("from instructions.tests.variable_recognition_test import", "from prompts.instructions.tests.variable_recognition_test import"),
    ("from instructions.tests.integration_test import", "from prompts.instructions.tests.integration_test import"),
    ("from instructions.content_blocks_manager import", "from prompts.instructions.content_blocks_manager import"),
    ("from instructions.system_instructions import", "from prompts.instructions.system_instructions import"),
    ("from instructions.pattern_parser import", "from prompts.instructions.pattern_parser import"),
    ("from instructions.matrx_fetcher import", "from prompts.instructions.matrx_fetcher import"),

    # ── ai.prompts.tests → prompts.tests ──
    ("from ai.prompts.tests.agent_old import", "from prompts.tests.agent_old import"),
    ("from ai.prompts.tests.agent_example import", "from prompts.tests.agent_example import"),

    # ── ai.prompts → prompts ──
    ("from ai.prompts.variables import", "from prompts.variables import"),
    ("from ai.prompts.session import", "from prompts.session import"),
    ("from ai.prompts.manager import", "from prompts.manager import"),
    ("from ai.prompts.agent import", "from prompts.agent import"),
    ("from ai.prompts.cache import", "from prompts.cache import"),
    ("from ai.prompts.types import", "from prompts.types import"),

    # ── ai.config → config ──
    ("from config.unified_config import", "from config.unified_config import"),
    ("from config.finish_reason import", "from config.finish_reason import"),
    ("from config.tools_config import", "from config.tools_config import"),
    ("from config.media_config import", "from config.media_config import"),
    ("from config.extra_config import", "from config.extra_config import"),
    ("from config.config_utils import", "from config.config_utils import"),
    ("from config.enums import", "from config.enums import"),

    # ── ai.db → conversation ──
    ("from db.custom.conversation_gate import", "from conversation.gate import"),
    ("from db.custom.conversation_rebuild import", "from conversation.rebuild import"),
    ("from db.custom.cx_conversation import", "from conversation.cx_conversation import"),
    ("from db.custom.cx_agent_memory import", "from conversation.cx_agent_memory import"),
    ("from db.custom.cx_user_request import", "from conversation.cx_user_request import"),
    ("from db.custom.cx_message import", "from conversation.cx_message import"),
    ("from db.custom.cx_request import", "from conversation.cx_request import"),
    ("from db.custom.cx_media import", "from conversation.cx_media import"),
    ("from db.custom.persistence import", "from conversation.persistence import"),
    ("from db.custom import", "from conversation import"),

    # ── ai.providers → providers ──
    ("from providers.anthropic_api import", "from providers.anthropic_api import"),
    ("from providers.cerebras_api import", "from providers.cerebras_api import"),
    ("from providers.google_api import", "from providers.google_api import"),
    ("from providers.groq_api import", "from providers.groq_api import"),
    ("from providers.openai_api import", "from providers.openai_api import"),
    ("from providers.together_api import", "from providers.together_api import"),
    ("from providers.xai_api import", "from providers.xai_api import"),

    # ── ai.audio → media.audio ──
    ("from ai.audio.audio_preprocessing import", "from media.audio.audio_preprocessing import"),
    ("from ai.audio.audio_support import", "from media.audio.audio_support import"),
    ("from ai.audio.groq_transcription import", "from media.audio.groq_transcription import"),
    ("from ai.audio.transcription_cache import", "from media.audio.transcription_cache import"),

    # ── ai.media → media ──
    ("from media.media_persistence import", "from media.persistence import"),
    ("from media.mime_utils import", "from media.mime_utils import"),

    # ── ai.tests → tests.ai ──
    ("from ai.tests.test_context import", "from tests.ai.test_context import"),
    ("from ai.tests.openai.", "from tests.openai."),
    ("from ai.tests.prompts.", "from tests.prompts."),

    # ── ai.<file> → client.<file> ──
    ("from ai.unified_client import", "from client.unified_client import"),
    ("from ai.ai_requests import", "from client.ai_requests import"),
    ("from ai.translators import", "from client.translators import"),
    ("from ai.recovery_logic import", "from client.recovery_logic import"),
    ("from ai.errors import", "from client.errors import"),
    ("from ai.stream_protocol import", "from client.stream_protocol import"),
    ("from ai.cache import", "from client.cache import"),
    ("from ai.system_agents import", "from client.system_agents import"),
    ("from ai.usage_config import", "from client.usage import"),
    ("from ai.timing import", "from client.timing import"),
    ("from ai.tool_call_tracking import", "from client.tool_call_tracking import"),
    ("from ai.thinking_config import", "from client.thinking_config import"),

    # ── Catch-all for lazy import references in __init__.py ──
    ("from ai import unified_config", "from config import unified_config"),
    ("from ai import unified_client", "from client import unified_client"),
]

# Also handle comment/docstring references
COMMENT_REPLACEMENTS = [
    ("from db.custom import cx_conversation_manager, cx_message_manager, ...",
     "from conversation import cx_conversation_manager, cx_message_manager, ..."),
    ("from config.unified_config import UnifiedConfig",
     "from config.unified_config import UnifiedConfig"),
    ("from ai.unified_client import UnifiedAIClient",
     "from client.unified_client import UnifiedAIClient"),
    ("from ai.prompts.agent import Agent",
     "from prompts.agent import Agent"),
    ("from ai.prompts.manager import pm",
     "from prompts.manager import pm"),
    ("from db.custom.conversation_rebuild import rebuild_conversation_messages",
     "from conversation.rebuild import rebuild_conversation_messages"),
    ("from db.custom.persistence import persist_completed_request",
     "from conversation.persistence import persist_completed_request"),
    ("from ai.cache import TTLCache",
     "from client.cache import TTLCache"),
]


def rewrite_file(filepath: Path) -> int:
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return 0

    original = content

    # Apply all replacements
    for old, new in REPLACEMENTS + COMMENT_REPLACEMENTS:
        content = content.replace(old, new)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        changes = sum(1 for old, new in REPLACEMENTS + COMMENT_REPLACEMENTS
                     if old in original)
        return changes
    return 0


def main():
    total_files = 0
    total_changes = 0

    for dir_name in TARGET_DIRS:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            continue
        for py_file in sorted(dir_path.rglob("*.py")):
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue
            changes = rewrite_file(py_file)
            if changes > 0:
                total_files += 1
                total_changes += changes
                print(f"  ✓ {py_file.relative_to(PROJECT_ROOT)} ({changes} replacements)")

    print(f"\nDone: {total_changes} replacements across {total_files} files")


if __name__ == "__main__":
    main()
