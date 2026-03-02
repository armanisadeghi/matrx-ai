"""Service configuration — loaded once at startup via pydantic-settings.

All values are read from environment variables (case-insensitive) or a
.env file in the working directory. See .env.example for the full list.

Add service-specific settings by subclassing Settings in your service:

    from matrx_service.app.config import Settings as BaseSettings

    class Settings(BaseSettings):
        my_api_key: str = ""

    @lru_cache
    def get_settings() -> Settings:
        return Settings()

Then replace the get_settings import in main.py, config.py, sentry.py, etc.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Matrx Service"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # --- CORS ---
    # Comma-separated list of allowed origins (used in production).
    # Development automatically allows all origins.
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # --- Streaming ---
    stream_chunk_size: int = 1024
    stream_keepalive_interval: float = 15.0

    # --- Supabase ---
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    # JWT secret for validating Supabase-issued tokens.
    # In Supabase: Project Settings → API → JWT Secret
    supabase_jwt_secret: str = ""

    # --- Admin auth ---
    # Static token for internal service-to-service calls and dev tooling.
    # Must be a long random string — never a real user token.
    admin_api_token: str = ""
    admin_user_id: str = ""

    # --- Sentry ---
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 1.0
    sentry_profiles_sample_rate: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
