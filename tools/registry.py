from __future__ import annotations

import importlib
import logging
import traceback
from typing import Any, Awaitable, Callable

from matrx_utils import vcprint
from pydantic import BaseModel

from tools.models import ToolDefinition, ToolType

logger = logging.getLogger(__name__)


class ToolRegistryV2:
    """Singleton registry: loads tool definitions from the database and
    resolves ``function_path`` → actual callables at startup.

    Design principles:
      - Database is the *metadata* authority (name, description, params, etc.)
      - Code is the *execution* authority (the actual callable)
      - No hardcoded ``register_*`` blocks
    """

    _instance: ToolRegistryV2 | None = None

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._loaded: bool = False

    @classmethod
    def get_instance(cls) -> ToolRegistryV2:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    async def load_from_database(self) -> int:
        """Load all active tools from the ``tools`` table (async entry point).

        Returns the number of tools loaded.
        """
        rows = await self._fetch_tools_async()
        return self._load_rows(rows)

    def load_from_database_sync(self) -> int:
        """Load all active tools from the ``tools`` table (sync entry point).

        Uses the ORM's synchronous wrappers when no event loop is running.
        """
        rows = self._fetch_tools_via_orm_sync()
        return self._load_rows(rows)

    def _load_rows(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            vcprint(
                "[ToolRegistryV2] Database returned 0 tool rows. No tools will be available.",
                color="red",
            )
            self._loaded = True
            return 0

        count = 0
        failed: list[str] = []
        for row in rows:
            tool_name = row.get("name", "?")
            try:
                tool_def = self._row_to_definition(row)
                if tool_def.tool_type == ToolType.LOCAL:
                    tool_def._callable = self._resolve_callable(tool_def.function_path)
                self._tools[tool_def.name] = tool_def
                count += 1
            except Exception as exc:
                failed.append(tool_name)
                vcprint(
                    {
                        "tool": tool_name,
                        "function_path": row.get("function_path", ""),
                        "error": str(exc),
                    },
                    f"[ToolRegistryV2] Failed to load tool: {tool_name}",
                    color="red",
                )
                print(traceback.format_exc())

        if failed:
            vcprint(
                failed,
                f"[ToolRegistryV2] {len(failed)} tool(s) failed to load",
                color="red",
            )

        self._loaded = True
        return count

    def load_from_definitions(self, definitions: list[ToolDefinition]) -> int:
        """Load tool definitions directly (for testing without a database)."""
        count = 0
        for tool_def in definitions:
            if tool_def.tool_type == ToolType.LOCAL and tool_def._callable is None:
                try:
                    tool_def._callable = self._resolve_callable(tool_def.function_path)
                except Exception as exc:
                    logger.warning("Could not resolve callable for '%s': %s", tool_def.name, exc)
                    continue
            self._tools[tool_def.name] = tool_def
            count += 1
        self._loaded = True
        return count

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_local(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        description: str = "",
        category: str | None = None,
        tags: list[str] | None = None,
        **overrides: Any,
    ) -> ToolDefinition:
        """Register a local tool from a Python function.

        If the function's first parameter is a Pydantic ``BaseModel``, its
        JSON Schema is auto-generated for the ``parameters`` field.
        """
        import inspect

        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        parameters: dict[str, Any] = overrides.pop("parameters", {})
        if not parameters and params:
            first_param = params[0]
            annotation = first_param.annotation
            if annotation is not inspect.Parameter.empty:
                try:
                    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                        parameters = self._pydantic_to_param_dict(annotation)
                except TypeError:
                    pass

        tool_def = ToolDefinition(
            name=name,
            description=description or func.__doc__ or "",
            parameters=parameters,
            tool_type=ToolType.LOCAL,
            function_path=f"{func.__module__}.{func.__qualname__}",
            category=category,
            tags=tags or [],
            **overrides,
        )
        tool_def._callable = func
        self._tools[name] = tool_def
        return tool_def

    def register(self, tool_def: ToolDefinition) -> None:
        """Register a pre-built ToolDefinition (e.g. from agent-as-tool setup)."""
        self._tools[tool_def.name] = tool_def

    def unregister(self, name: str) -> bool:
        return self._tools.pop(name, None) is not None

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def get_provider_tools(self, tool_names: list[str], provider: str) -> list[dict[str, Any]]:
        if not self._loaded:
            vcprint(
                {
                    "requested_tools": tool_names,
                    "provider": provider,
                    "registry_loaded": self._loaded,
                    "registry_count": len(self._tools),
                },
                "[ToolRegistryV2] Registry was never loaded! Tools will not be included in the request.",
                color="red",
            )

        missing = [n for n in tool_names if n not in self._tools]
        if missing:
            vcprint(
                {
                    "missing_tools": missing,
                    "requested_tools": tool_names,
                    "provider": provider,
                    "available_tools": list(self._tools.keys())[:20],
                    "registry_count": len(self._tools),
                },
                f"[ToolRegistryV2] {len(missing)} requested tool(s) not found in registry",
                color="red",
            )

        return [
            self._tools[n].get_provider_format(provider)
            for n in tool_names
            if n in self._tools
        ]

    def list_tools(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        tool_type: ToolType | None = None,
        active_only: bool = True,
    ) -> list[ToolDefinition]:
        result: list[ToolDefinition] = []
        for t in self._tools.values():
            if active_only and not t.is_active:
                continue
            if category and t.category != category:
                continue
            if tags and not set(tags).issubset(set(t.tags)):
                continue
            if tool_type is not None and t.tool_type != tool_type:
                continue
            result.append(t)
        return result

    def list_tool_names(self) -> list[str]:
        return list(self._tools.keys())

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def count(self) -> int:
        return len(self._tools)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _fetch_tools_async() -> list[dict[str, Any]]:
        try:
            from conversation import tools_manager
            items = await tools_manager.filter_tool(is_active=True)
            return [item.to_dict() for item in items]
        except Exception as exc:
            vcprint(
                str(exc),
                "[ToolRegistryV2] Failed to fetch tools from database. No tools will be available",
                color="red",
            )
            print(traceback.format_exc())
            return []

    @staticmethod
    def _fetch_tools_via_orm_sync() -> list[dict[str, Any]]:
        try:
            from conversation import tools_manager
            items = tools_manager.filter_items_sync(is_active=True)
            return [item.to_dict() if hasattr(item, "to_dict") else item for item in items]
        except Exception as exc:
            vcprint(
                str(exc),
                "[ToolRegistryV2] Failed to fetch tools from database (sync). No tools will be available",
                color="red",
            )
            print(traceback.format_exc())
            return []

    @staticmethod
    def _normalize_function_path(function_path: str) -> str:
        """Remap legacy ``ai.tool_system.*`` paths from the database to ``tools.*``.

        The DB ``tools`` table stores function_path values like
        ``ai.tool_system.implementations.code.code_fetch_tree``.  In the
        matrx-ai project the equivalent module lives under ``tools/``, so we
        strip the ``ai.tool_system.`` prefix and replace it with ``tools.``.

        TODO: Remove this once all DB rows are updated to use ``tools.*``
              paths directly across all projects.
        """
        if function_path.startswith("ai.tool_system."):
            return "tools." + function_path[len("ai.tool_system."):]
        return function_path

    @staticmethod
    def _row_to_definition(row: dict[str, Any]) -> ToolDefinition:
        tool_type = ToolType.LOCAL
        function_path = row.get("function_path", "")

        # Normalize legacy paths before anything else
        function_path = ToolRegistryV2._normalize_function_path(function_path)

        prompt_id: str | None = None
        if function_path.startswith("agent:"):
            tool_type = ToolType.AGENT
            prompt_id = function_path.split(":", 1)[1]
        elif function_path.startswith("mcp:"):
            tool_type = ToolType.EXTERNAL_MCP

        guardrails = row.get("annotations") or []
        guardrail_config: dict[str, Any] = {}
        if isinstance(guardrails, list):
            for ann in guardrails:
                if isinstance(ann, dict):
                    guardrail_config.update(ann)

        raw_params = row.get("parameters") or {}
        if isinstance(raw_params, dict) and raw_params.get("type") == "object" and "properties" in raw_params:
            params = raw_params["properties"]
            db_required = set(raw_params.get("required", []))
            for pname, pschema in params.items():
                if isinstance(pschema, dict) and "required" not in pschema:
                    pschema["required"] = pname in db_required
        else:
            params = raw_params

        return ToolDefinition(
            name=row["name"],
            description=row.get("description", ""),
            parameters=params,
            output_schema=row.get("output_schema"),
            annotations=row.get("annotations") or [],
            tool_type=tool_type,
            function_path=function_path,
            category=row.get("category"),
            tags=row.get("tags") or [],
            icon=row.get("icon"),
            is_active=row.get("is_active", True),
            version=row.get("version", "1.0.0"),
            prompt_id=prompt_id,
            max_calls_per_conversation=guardrail_config.get("max_calls_per_conversation"),
            max_calls_per_minute=guardrail_config.get("max_calls_per_minute"),
            cost_cap_per_call=guardrail_config.get("cost_cap_per_call"),
            timeout_seconds=guardrail_config.get("timeout_seconds", 120.0),
        )

    @staticmethod
    def _resolve_callable(function_path: str) -> Callable[..., Awaitable[Any]]:
        if not function_path or function_path.startswith("agent:") or function_path.startswith("mcp:"):
            raise ValueError(f"Cannot resolve non-local function_path: {function_path}")
        # Normalize legacy paths in case _row_to_definition was bypassed
        function_path = ToolRegistryV2._normalize_function_path(function_path)
        module_path, func_name = function_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        return func

    @staticmethod
    def _pydantic_to_param_dict(model_cls: type[BaseModel]) -> dict[str, Any]:
        """Convert a Pydantic model into the internal parameter dict format."""
        schema = model_cls.model_json_schema()
        params: dict[str, Any] = {}
        required_fields = set(schema.get("required", []))
        properties = schema.get("properties", {})

        for field_name, field_schema in properties.items():
            param: dict[str, Any] = {
                "type": field_schema.get("type", "string"),
                "description": field_schema.get("description", ""),
                "required": field_name in required_fields,
            }
            for prop in ("items", "enum", "default", "minimum", "maximum", "minItems", "maxItems", "properties"):
                if prop in field_schema:
                    param[prop] = field_schema[prop]
            params[field_name] = param
        return params

    # ------------------------------------------------------------------
    # MCP Server registration
    # ------------------------------------------------------------------

    async def register_mcp_server(
        self,
        server_url: str,
        server_name: str,
        mcp_client: Any | None = None,
    ) -> list[str]:
        """Connect to a remote MCP server, discover tools, register them."""
        if mcp_client is None:
            from tools.external_mcp import ExternalMCPClient
            mcp_client = ExternalMCPClient()

        remote_tools = await mcp_client.discover_tools(server_url)
        registered: list[str] = []
        for tool_def in remote_tools:
            tool_def.tool_type = ToolType.EXTERNAL_MCP
            tool_def.mcp_server_url = server_url
            namespaced = f"{server_name}_{tool_def.name}"
            tool_def.name = namespaced
            self._tools[namespaced] = tool_def
            registered.append(namespaced)

        return registered
