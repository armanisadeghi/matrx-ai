from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Matrx AI"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # CORS — comma-separated origins
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Streaming
    stream_chunk_size: int = 1024
    stream_keepalive_interval: float = 15.0  # seconds

    # AI Providers (populated via .env)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    together_api_key: str = ""
    cerebras_api_key: str = ""
    xai_api_key: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Sentry — matches MATRX_ENGINE_SENTRY_DSN in .env
    matrx_engine_sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 1.0   # 1.0 = 100% in dev; lower in prod
    sentry_profiles_sample_rate: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
