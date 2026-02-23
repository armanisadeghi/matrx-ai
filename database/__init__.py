from dotenv import load_dotenv

load_dotenv()

from matrx_orm import register_database_from_env

register_database_from_env(
    name="supabase_automation_matrix",
    env_prefix="SUPABASE_MATRIX",
    alias="main",
    additional_schemas=["auth"],
)
