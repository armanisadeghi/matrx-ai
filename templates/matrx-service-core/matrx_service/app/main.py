"""FastAPI application factory for Matrx microservices.

Key design decisions
--------------------
- uvloop replaces the default asyncio event loop (~2–4× throughput on I/O-heavy workloads)
- ORJSONResponse is the default response class (~10× faster than stdlib json)
- Lifespan context manager replaces deprecated on_startup/on_shutdown events
- CORS is permissive in dev; lock down ALLOWED_ORIGINS in production via .env
- AuthMiddleware runs on every request → creates AppContext with emitter + auth info
- Middleware add order is reverse of execution order (last added = outermost = first to run):
    CORS → RequestContext → Auth → handler
  so we add: Auth, RequestContext, CORS (in that order)
- CORS MUST be outermost — Auth must not run before CORS handles OPTIONS preflight

Rename 'matrx_service' to your service package name throughout this file.
"""

import logging
import logging.config
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]

import uvloop
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from matrx_service.app.config import get_settings
from matrx_service.app.core.exceptions import (
    MatrxException,
    http_exception_handler,
    matrx_exception_handler,
    unhandled_exception_handler,
)
from matrx_service.app.core.middleware import RequestContextMiddleware
from matrx_service.app.core.sentry import init_sentry
from matrx_service.app.dependencies.auth import (
    require_authenticated,
    require_guest_or_above,
)
from matrx_service.app.middleware.auth import AuthMiddleware
from matrx_service.app.routers import health

# Sentry must be initialised before the app is created so import-time errors
# and startup exceptions are captured.
init_sentry()

# ---------------------------------------------------------------------------
# Logging — full takeover of uvicorn's default handlers.
#
# uvicorn CLI installs its own handlers before our code runs. We must:
#   1. disable_existing_loggers=True  — kill every handler uvicorn already set
#   2. Re-add a StreamHandler to root so everything propagates to it
#   3. Explicitly re-configure uvicorn's loggers to avoid duplication
#   4. Write to sys.stderr (not stdout) — never buffered by pipes
# ---------------------------------------------------------------------------

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            }
        },
        "handlers": {
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["stderr"]},
        "loggers": {
            "uvicorn": {"level": "WARNING", "propagate": True, "handlers": []},
            "uvicorn.error": {"level": "WARNING", "propagate": True, "handlers": []},
            "uvicorn.access": {"level": "WARNING", "propagate": True, "handlers": []},
            "fastapi": {"level": "DEBUG", "propagate": True, "handlers": []},
        },
    }
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup / teardown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    logger.info(
        "Starting %s v%s [%s]", settings.app_name, settings.app_version, settings.environment
    )

    # ---------------------------------------------------------------------------
    # TODO: Add service-specific startup logic here, for example:
    #
    #   from matrx_service.db import initialize_db
    #   await initialize_db()
    #
    #   from matrx_service.some_system import initialize
    #   await initialize()
    # ---------------------------------------------------------------------------

    yield

    logger.info("Shutting down %s", settings.app_name)


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
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_init_oauth={},
    )

    # --- OpenAPI security scheme (Swagger Authorize button) ---
    from fastapi.openapi.utils import get_openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        schema["components"] = schema.get("components", {})
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT or API Token",
            }
        }
        schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

    # --- Middleware (added in reverse execution order) ---
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RequestContextMiddleware)

    cors_origins = (
        ["*"]
        if settings.environment in ("development", "dev", "local")
        else settings.allowed_origins
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=cors_origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Conversation-ID"],
    )

    # --- Exception handlers ---
    from fastapi import HTTPException  # noqa: PLC0415

    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(MatrxException, matrx_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

    # --- Routers ---

    # Public — no auth required
    app.include_router(health.router)

    # ---------------------------------------------------------------------------
    # TODO: Register your service routers here. Examples:
    #
    # Guest OK (fingerprint or token):
    #   from matrx_service.app.routers import my_feature
    #   guest_router = APIRouter()
    #   guest_router.include_router(my_feature.router)
    #   app.include_router(guest_router, dependencies=[Depends(require_guest_or_above)])
    #
    # Authenticated (valid JWT required):
    #   from matrx_service.app.routers import admin_feature
    #   app.include_router(admin_feature.router, dependencies=[Depends(require_authenticated)])
    # ---------------------------------------------------------------------------

    logger.info("FastAPI app initialized: %s", settings.app_name)

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Entry point — installs uvloop before uvicorn takes over
# ---------------------------------------------------------------------------


def start() -> None:
    """CLI entry point. Register as a script in pyproject.toml:

        [project.scripts]
        my-service = "matrx_service.app.main:start"
    """
    import uvicorn

    uvloop.install()

    settings = get_settings()
    uvicorn.run(
        "matrx_service.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        loop="uvloop",
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    start()
