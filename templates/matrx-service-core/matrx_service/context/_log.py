"""Logging compatibility shim.

Tries to use matrx_utils.vcprint (rich pretty-printing with colour support).
Falls back to stdlib logging so the template works without matrx-utils installed.

Internal to the context package — do not import this from outside.
"""

from __future__ import annotations

import logging
from typing import Any

_logger = logging.getLogger("matrx_service.emitter")

try:
    from matrx_utils import vcprint as _vcprint  # type: ignore[import-untyped]

    def log(
        data: Any,
        title: str = "",
        color: str = "white",
        verbose: bool = True,
        chunks: bool = False,
        inline: bool = False,
    ) -> None:
        _vcprint(data=data, title=title, color=color, verbose=verbose, chunks=chunks, inline=inline)

except ImportError:
    def log(
        data: Any,
        title: str = "",
        color: str = "white",
        verbose: bool = True,
        chunks: bool = False,
        inline: bool = False,
    ) -> None:
        prefix = f"[{title}] " if title else ""
        _logger.debug("%s%s", prefix, data)
