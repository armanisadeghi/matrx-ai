"""
Matrx AI — FastAPI application entry point.

Key design decisions:
  - uvloop replaces the default asyncio event loop for ~2–4× throughput on I/O-heavy workloads
  - ORJSONResponse is the default; ~10× faster than stdlib json
  - Lifespan context manager replaces deprecated on_startup/on_shutdown events
  - CORS is permissive in dev; lock down allowed_origins in production via .env
"""

import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config import get_settings
from app.core.exceptions import MatrxException, matrx_exception_handler, unhandled_exception_handler
from app.core.middleware import RequestContextMiddleware
from app.core.sentry import init_sentry
from app.routers import agent, chat, conversation, health, tool

# Sentry must be initialised before the app is created so that import-time
# errors and startup exceptions are captured.
init_sentry()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
        "loggers": {
            "uvicorn": {"propagate": True},
            "app": {"level": "DEBUG", "propagate": True},
        },
    }
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    logger.info(
        "Starting %s v%s [%s]", settings.app_name, settings.app_version, settings.environment
    )

    # Place async resource initialisation here (DB pools, HTTP clients, etc.)
    # e.g.:  app.state.http_client = httpx.AsyncClient()

    yield

    # Teardown
    logger.info("Shutting down %s", settings.app_name)
    # e.g.:  await app.state.http_client.aclose()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request context (ID + timing) ---
    app.add_middleware(RequestContextMiddleware)

    # --- Exception handlers ---
    app.add_exception_handler(MatrxException, matrx_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

    # --- Routers ---
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(agent.router)
    app.include_router(agent.cancel_router)
    app.include_router(conversation.router)
    app.include_router(tool.router)

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Entry point — installs uvloop before uvicorn takes over
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvloop.install()  # must be called before uvicorn starts the event loop

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        loop="uvloop",
        log_config=None,  # we configure logging ourselves above
        access_log=False,  # handled by RequestContextMiddleware
    )
