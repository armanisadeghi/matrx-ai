import asyncio

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.config import get_settings
from app.models.health import HealthStatus

router = APIRouter(prefix="/health", tags=["health"])


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


@router.get("/ready", response_class=ORJSONResponse)
async def readiness() -> ORJSONResponse:
    """Kubernetes-style readiness probe — fast path, no sub-checks."""
    return ORJSONResponse({"status": "ready"})


@router.get("/live", response_class=ORJSONResponse)
async def liveness() -> ORJSONResponse:
    """Kubernetes-style liveness probe."""
    return ORJSONResponse({"status": "alive"})


async def _run_checks() -> dict[str, str]:
    """
    Extend this with real checks (DB ping, cache ping, etc.) as services
    are added. Each check should return "ok" or a short error string.
    """
    results: dict[str, str] = {}

    async def _event_loop_check() -> str:
        await asyncio.sleep(0)
        return "ok"

    results["event_loop"] = await _event_loop_check()
    return results
