"""
Matrx AI — FastAPI application entry point.

Key design decisions:
  - uvloop replaces the default asyncio event loop for ~2–4× throughput on I/O-heavy workloads
  - ORJSONResponse is the default; ~10× faster than stdlib json
  - Lifespan context manager replaces deprecated on_startup/on_shutdown events
  - CORS is permissive in dev; lock down allowed_origins in production via .env
  - AuthMiddleware on every request → creates AppContext with emitter + auth info
"""

import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvloop
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config import get_settings
from app.core.exceptions import MatrxException, matrx_exception_handler, unhandled_exception_handler
from app.core.middleware import RequestContextMiddleware
from app.core.sentry import init_sentry
from app.dependencies.auth import require_admin, require_authenticated, require_guest_or_above
from app.middleware.auth import AuthMiddleware
from app.routers import agent, chat, conversation, health, tool
from matrx_utils import vcprint

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

    # Initialize tool system
    try:
        from tools.handle_tool_calls import initialize_tool_system
        tool_count = await initialize_tool_system()
        vcprint(f"{tool_count} tools loaded", "[FastAPI] Tool System V2 initialized", color="green")
    except Exception as e:
        import traceback
        vcprint(str(e), "[FastAPI] Tool System V2 init FAILED. Tools will not work", color="red")
        print(traceback.format_exc())

    yield

    # Teardown
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
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        swagger_ui_init_oauth={},
    )

    # --- OpenAPI security scheme ---
    # This makes Swagger show the Authorize button.
    # Click it and paste:  Bearer <your ADMIN_API_TOKEN>
    from fastapi.openapi.utils import get_openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
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

    # --- Middleware ---
    # Last added = outermost (runs first on request).
    # Execution order: CORS → RequestContext → Auth → handler
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Conversation-ID"],
    )

    # --- Exception handlers ---
    app.add_exception_handler(MatrxException, matrx_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

    # --- Routers ---

    # Public — no auth required
    app.include_router(health.router)
    app.include_router(agent.public_router, tags=["AI"])
    app.include_router(conversation.public_router, tags=["AI"])

    # Guest OK — fingerprint or token
    ai_router = APIRouter()
    ai_router.include_router(chat.router)
    ai_router.include_router(agent.router)
    ai_router.include_router(agent.cancel_router)
    ai_router.include_router(conversation.router)

    app.include_router(
        ai_router,
        dependencies=[Depends(require_guest_or_above)],
    )

    # Authenticated — valid JWT required
    app.include_router(
        tool.router,
        dependencies=[Depends(require_authenticated)],
    )

    vcprint("FastAPI app initialized with routes", "[FastAPI]", color="green")

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
