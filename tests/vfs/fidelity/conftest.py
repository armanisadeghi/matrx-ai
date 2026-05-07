from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest_asyncio

from .fixtures import BASIC_TREE, ERROR_TREE, GREP_TREE
from .harness import FidelityHarness


async def _make_harness(tree: dict[str, Any]) -> AsyncIterator[FidelityHarness]:
    h = FidelityHarness(tree)
    await h.setup()
    try:
        yield h
    finally:
        h.cleanup()


@pytest_asyncio.fixture
async def basic_harness() -> AsyncIterator[FidelityHarness]:
    async for h in _make_harness(BASIC_TREE):
        yield h


@pytest_asyncio.fixture
async def grep_harness() -> AsyncIterator[FidelityHarness]:
    async for h in _make_harness(GREP_TREE):
        yield h


@pytest_asyncio.fixture
async def error_harness() -> AsyncIterator[FidelityHarness]:
    async for h in _make_harness(ERROR_TREE):
        yield h
