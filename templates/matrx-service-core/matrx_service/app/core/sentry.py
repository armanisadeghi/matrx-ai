"""
Sentry initialisation for Matrx AI (Python / FastAPI).

Call `init_sentry()` as early as possible — before the FastAPI app is
created — so that import-time errors and startup exceptions are captured.

Features enabled:
  - FastAPI integration     → automatic request/response tracing
  - LoggingIntegration      → stdlib `logging` calls → Sentry
  - enable_logs=True        → structured Sentry Logs (SDK ≥ 2.35.0)
  - Performance tracing     → traces_sample_rate
  - Profiling               → profiles_sample_rate
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
    dsn = settings.matrx_engine_sentry_dsn

    if not dsn:
        logger.warning("MATRX_ENGINE_SENTRY_DSN is not set — Sentry disabled")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.environment,
        release=f"matrx-ai@{settings.app_version}",

        # ── Structured logging (SDK ≥ 2.35.0) ───────────────────────────────
        enable_logs=True,

        # ── Performance tracing ──────────────────────────────────────────────
        # 1.0 = capture every request; reduce to 0.1–0.2 in high-traffic prod
        traces_sample_rate=settings.sentry_traces_sample_rate,

        # ── Profiling ────────────────────────────────────────────────────────
        profiles_sample_rate=settings.sentry_profiles_sample_rate,

        # ── Integrations ─────────────────────────────────────────────────────
        integrations=[
            # Captures stdlib logging.WARNING and above → Sentry issues
            # Also bridges them into structured Sentry Logs
            LoggingIntegration(
                level=logging.INFO,           # breadcrumb threshold
                event_level=logging.ERROR,    # creates a Sentry *issue*
                sentry_logs_level=logging.WARNING,  # structured log threshold
            ),
            # Automatic request/response spans for Starlette (FastAPI base)
            StarletteIntegration(transaction_style="url"),
            # FastAPI-specific: captures route handler names, path params
            FastApiIntegration(transaction_style="url"),
        ],

        # ── Filtering ────────────────────────────────────────────────────────
        # Drop noisy health-check endpoints from traces
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
    wsgi_environ = sampling_context.get("wsgi_environ", {})
    path = wsgi_environ.get("PATH_INFO", "")

    asgi_scope = sampling_context.get("asgi_scope", {})
    if not path:
        path = asgi_scope.get("path", "")

    if path.startswith("/health"):
        return 0.0  # never trace health probes

    settings = get_settings()
    return settings.sentry_traces_sample_rate
