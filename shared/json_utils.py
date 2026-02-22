# Placeholder: json_matrx — used by ai.tests.execution_test
import json
from typing import Any


def to_matrx_json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)
