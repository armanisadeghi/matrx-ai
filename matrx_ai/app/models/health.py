from typing import Any

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    version: str
    environment: str
    checks: dict[str, Any] = {}
