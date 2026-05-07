from __future__ import annotations

import importlib.util
import inspect

import pytest

from matrx_ai.tools.models import ToolDefinition, ToolType
from matrx_ai.tools.registry import ToolRegistryV2
from matrx_ai.tools.vfs_routing import (
    FS_EDIT_TOOL_DEFINITION,
    VFS_REMAP_TABLE,
    is_vfs_globally_enabled,
    remap,
    should_route_to_vfs,
)

VFS_ADAPTERS_PRESENT = (
    importlib.util.find_spec("matrx_ai.tools.implementations.vfs_filesystem")
    is not None
    and importlib.util.find_spec("matrx_ai.tools.implementations.vfs_shell")
    is not None
)


# ---------------------------------------------------------------------------
# Pure-function unit tests for the routing module
# ---------------------------------------------------------------------------


def test_remap_table_covers_expected_paths() -> None:
    expected = {
        "matrx_ai.tools.implementations.filesystem.fs_read",
        "matrx_ai.tools.implementations.filesystem.fs_write",
        "matrx_ai.tools.implementations.filesystem.fs_list",
        "matrx_ai.tools.implementations.filesystem.fs_search",
        "matrx_ai.tools.implementations.filesystem.fs_mkdir",
        "matrx_ai.tools.implementations.shell.shell_execute",
    }
    assert expected.issubset(VFS_REMAP_TABLE.keys())


def test_globally_enabled_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    assert is_vfs_globally_enabled()


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on", " On "])
def test_truthy_env_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", value)
    assert is_vfs_globally_enabled()


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "garbage"])
def test_falsy_env_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", value)
    assert not is_vfs_globally_enabled()


def test_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATRX_VFS_ENABLED", raising=False)
    assert not is_vfs_globally_enabled()


def test_remap_known_path() -> None:
    p = "matrx_ai.tools.implementations.filesystem.fs_read"
    assert remap(p) == "matrx_ai.tools.implementations.vfs_filesystem.fs_read"


def test_remap_unknown_passthrough() -> None:
    p = "matrx_ai.tools.implementations.browser.browser_open"
    assert remap(p) == p


def test_should_route_when_globally_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    assert should_route_to_vfs(
        "matrx_ai.tools.implementations.filesystem.fs_read", "matrx_ai"
    )


def test_should_route_explicit_source_app(monkeypatch: pytest.MonkeyPatch) -> None:
    # Even with VFS off globally, explicit "matrx_vfs" routes.
    monkeypatch.delenv("MATRX_VFS_ENABLED", raising=False)
    assert should_route_to_vfs("anything", "matrx_vfs")


def test_should_not_route_unknown_with_global_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    assert not should_route_to_vfs(
        "matrx_ai.tools.implementations.browser.browser_open", "matrx_ai"
    )


def test_should_not_route_external_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    assert not should_route_to_vfs("anything", "matrx_local")


def test_should_not_route_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATRX_VFS_ENABLED", raising=False)
    assert not should_route_to_vfs(
        "matrx_ai.tools.implementations.filesystem.fs_read", "matrx_ai"
    )


def test_should_not_route_when_source_app_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    assert not should_route_to_vfs(
        "matrx_ai.tools.implementations.filesystem.fs_read", None
    )


# ---------------------------------------------------------------------------
# Integration tests against ToolRegistryV2
# ---------------------------------------------------------------------------


def _fs_read_definition() -> ToolDefinition:
    return ToolDefinition(
        name="fs_read",
        description="Read a file",
        parameters={"path": {"type": "string", "required": True}},
        tool_type=ToolType.LOCAL,
        function_path="matrx_ai.tools.implementations.filesystem.fs_read",
        source_app="matrx_ai",
        is_active=True,
    )


def _module_of(callable_obj: object) -> str:
    mod = inspect.getmodule(callable_obj)
    return mod.__name__ if mod is not None else getattr(callable_obj, "__module__", "")


@pytest.mark.skipif(
    not VFS_ADAPTERS_PRESENT, reason="Phase E (vfs_filesystem/vfs_shell) not ready"
)
def test_registry_routes_fs_read_when_vfs_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    registry = ToolRegistryV2()
    registry.load_from_definitions([_fs_read_definition()])
    entry = registry.get("fs_read")
    assert entry is not None
    assert entry._routed_to_vfs is True
    assert entry._original_function_path == (
        "matrx_ai.tools.implementations.filesystem.fs_read"
    )
    assert entry.function_path == (
        "matrx_ai.tools.implementations.vfs_filesystem.fs_read"
    )
    assert entry._callable is not None
    assert "vfs_filesystem" in _module_of(entry._callable)


def test_registry_passthrough_when_vfs_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MATRX_VFS_ENABLED", raising=False)
    registry = ToolRegistryV2()
    registry.load_from_definitions([_fs_read_definition()])
    entry = registry.get("fs_read")
    assert entry is not None
    assert entry._routed_to_vfs is False
    assert entry._original_function_path is None
    assert entry.function_path == (
        "matrx_ai.tools.implementations.filesystem.fs_read"
    )
    assert entry._callable is not None
    assert "vfs_filesystem" not in _module_of(entry._callable)


def test_registry_does_not_inject_fs_edit_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MATRX_VFS_ENABLED", raising=False)
    registry = ToolRegistryV2()
    registry.load_from_definitions([])
    assert registry.get("fs_edit") is None


@pytest.mark.skipif(
    not VFS_ADAPTERS_PRESENT, reason="Phase E (vfs_filesystem/vfs_shell) not ready"
)
def test_fs_edit_synthetic_added_when_vfs_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    registry = ToolRegistryV2()
    registry.load_from_definitions([])
    entry = registry.get("fs_edit")
    assert entry is not None
    assert entry.source_app == "matrx_vfs"
    assert entry.function_path == FS_EDIT_TOOL_DEFINITION["function_path"]


@pytest.mark.skipif(
    not VFS_ADAPTERS_PRESENT, reason="Phase E (vfs_filesystem/vfs_shell) not ready"
)
def test_fs_edit_not_double_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MATRX_VFS_ENABLED", "1")
    registry = ToolRegistryV2()
    pre_existing = ToolDefinition(
        name="fs_edit",
        description="DB-provided fs_edit",
        parameters={},
        tool_type=ToolType.LOCAL,
        function_path="matrx_ai.tools.implementations.vfs_filesystem.fs_edit",
        source_app="matrx_vfs",
        is_active=True,
    )
    registry.load_from_definitions([pre_existing])
    entry = registry.get("fs_edit")
    assert entry is not None
    assert entry.description == "DB-provided fs_edit"


def test_registry_explicit_vfs_source_app_routes_without_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # source_app=matrx_vfs forces routing even with the env var off, which is
    # the per-tool override path.
    monkeypatch.delenv("MATRX_VFS_ENABLED", raising=False)
    tool_def = ToolDefinition(
        name="fs_read_forced",
        description="x",
        parameters={},
        tool_type=ToolType.LOCAL,
        function_path="matrx_ai.tools.implementations.filesystem.fs_read",
        source_app="matrx_vfs",
        is_active=True,
    )
    # We want to verify the routing decision fires, not that the import
    # succeeds (Phase E may be missing). Inspect after _apply_vfs_routing.
    ToolRegistryV2._apply_vfs_routing(tool_def)
    assert tool_def._routed_to_vfs is True
    assert tool_def.function_path == (
        "matrx_ai.tools.implementations.vfs_filesystem.fs_read"
    )
