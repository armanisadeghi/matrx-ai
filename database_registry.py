from dotenv import load_dotenv

load_dotenv()
from matrx_utils.conf import settings, NotConfiguredError
from matrx_utils import vcprint
from matrx_orm import DatabaseProjectConfig, register_database

try:
    ADMIN_SAVE_DIRECT_ROOT = settings.ADMIN_SAVE_DIRECT_ROOT
except (AttributeError, NotConfiguredError):
    ADMIN_SAVE_DIRECT_ROOT = ""
    vcprint("ADMIN_SAVE_DIRECT_ROOT not found in settings or environment. Defaulting to : '' ", color="red")

try:
    ADMIN_PYTHON_ROOT = settings.ADMIN_PYTHON_ROOT
except (AttributeError, NotConfiguredError):
    ADMIN_PYTHON_ROOT = ""
    vcprint("ADMIN_PYTHON_ROOT not found in settings or environment. Defaulting to : '' ", color="red")

# If this environmental variable is set to your actual project root, auto-generated typescript files will overwrite the live, existing files
try:
    ADMIN_TS_ROOT = settings.ADMIN_TS_ROOT
except (AttributeError, NotConfiguredError):
    ADMIN_TS_ROOT = ""
    vcprint("ADMIN_TS_ROOT not found in settings or environment. Defaulting to : '' ", color="red")

data_input_component_overrides = {
    "relations": ["message_broker", "broker", "data_broker"],
    "filter_fields": [
        "options",
        "component",
    ],
}

ai_model_overrides = {
    "relations": ["ai_provider", "ai_model_endpoint", "ai_settings", "recipe_model"],
    "filter_fields": [
        "name",
        "common_name",
        "provider",
        "model_class",
        "model_provider",
    ],
}

compiled_recipe_overrides = {
    "relations": ["recipe", "applet"],
    "filter_fields": ["recipe_id", "user_id", "version"],
    "include_core_relations": True,
    "include_filter_fields": True,
}

MANAGER_CONFIG_OVERRIDES = {
    "ai_model": ai_model_overrides,
    "data_input_component": data_input_component_overrides,
    "compiled_recipe": compiled_recipe_overrides,
}

# Tables for which Python models and managers are auto-generated.
# Add a table name here (exact PostgreSQL snake_case name) then run:
#   uv run python makemigrations.py
# See SCHEMA_GENERATION.md for full instructions.
MANAGED_TABLES = {
    "cx_conversation",
    "cx_messages",
    "cx_agent_memory",
    "cx_media",
    "cx_request",
    "cx_tool_call",
    "cx_user_request",
    "ai_model",
    "tools",
    "prompts",
    "prompt_builtins",
    "content_blocks",
    "table_data",
    "ai_provider",
    "shortcut_categories",
    "user_tables",
}

config = DatabaseProjectConfig(name="supabase_automation_matrix",
                               alias="main",
                               user=settings.SUPABASE_MATRIX_USER,
                               password=settings.SUPABASE_MATRIX_PASSWORD,
                               host=settings.SUPABASE_MATRIX_HOST,
                               port=settings.SUPABASE_MATRIX_PORT,
                               database_name=settings.SUPABASE_MATRIX_DATABASE_NAME,
                               manager_config_overrides=MANAGER_CONFIG_OVERRIDES)

register_database(config)
