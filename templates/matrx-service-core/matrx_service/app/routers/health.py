"""Health check endpoints.

All three endpoint flavours are provided:
  /api/health         — full status with component checks (Swagger-visible)
  /api/health/ready   — Kubernetes readiness probe (fast, no sub-checks)
  /api/health/live    — Kubernetes liveness probe

Add real component checks to _run_checks() as your service grows, e.g.:

    async def _db_check() -> str:
        try:
            await db.execute("SELECT 1")
            return "ok"
        except Exception as e:
            return f"error: {e}"

    results["database"] = await _db_check()
"""

import asyncio

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from matrx_service.app.config import get_settings
from matrx_service.app.models.health import HealthStatus

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_class=ORJSONResponse)
async def health() -> HealthStatus:
    settings = get_settings()
    checks = await _run_checks()
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return HealthStatus(
        status=overall,
        version=settings.app_version,
        environment=settings.environment,
        checks=checks,
    )


@router.get("/detailed", response_class=ORJSONResponse)
async def health_detailed() -> HealthStatus:
    settings = get_settings()
    checks = await _run_checks()
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return HealthStatus(
        status=overall,
        version=settings.app_version,
        environment=settings.environment,
        checks=checks,
    )


@router.get("/ready", response_class=ORJSONResponse)
async def readiness() -> ORJSONResponse:
    return ORJSONResponse({"status": "ready"})


@router.get("/live", response_class=ORJSONResponse)
async def liveness() -> ORJSONResponse:
    return ORJSONResponse({"status": "alive"})


async def _run_checks() -> dict[str, str]:
    results: dict[str, str] = {}

    async def _event_loop_check() -> str:
        await asyncio.sleep(0)
        return "ok"

    results["event_loop"] = await _event_loop_check()
    return results
