"""Sentry initialisation.

Call init_sentry() as early as possible — before the FastAPI app is created —
so that import-time errors and startup exceptions are captured.

Features
--------
- FastAPI integration     → automatic request/response tracing
- LoggingIntegration      → stdlib logging calls → Sentry
- enable_logs=True        → structured Sentry Logs (SDK ≥ 2.35.0)
- Performance tracing     → traces_sample_rate
- Profiling               → profiles_sample_rate
- Health probes excluded  → /health/** routes never create traces
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from matrx_service.app.config import get_settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    settings = get_settings()
    dsn = settings.sentry_dsn

    if not dsn:
        logger.warning("SENTRY_DSN is not set — Sentry disabled")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.environment,
        release=f"{settings.app_name}@{settings.app_version}",

        enable_logs=True,

        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,

        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
                sentry_logs_level=logging.WARNING,
            ),
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
        ],

        traces_sampler=_traces_sampler,
    )

    logger.info(
        "Sentry initialised [env=%s, traces=%.0f%%, profiles=%.0f%%]",
        settings.environment,
        settings.sentry_traces_sample_rate * 100,
        settings.sentry_profiles_sample_rate * 100,
    )


def _traces_sampler(sampling_context: dict) -> float:
    """Drop health-check traces; sample everything else at the configured rate."""
    asgi_scope = sampling_context.get("asgi_scope", {})
    path = asgi_scope.get("path", "")

    if not path:
        wsgi_environ = sampling_context.get("wsgi_environ", {})
        path = wsgi_environ.get("PATH_INFO", "")

    if path.startswith("/health") or path.startswith("/api/health"):
        return 0.0

    return get_settings().sentry_traces_sample_rate
