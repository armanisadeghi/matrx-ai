from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from matrx_ai.tools.models import ToolContext, ToolDefinition, ToolError, ToolResult, ToolType

logger = logging.getLogger(__name__)


class ExternalMCPClient:
    """Client for calling tools on remote MCP servers.

    Supports the SSE/HTTP transport (JSON-RPC 2.0 over HTTP POST).
    Stdio transport can be added later for local subprocess MCPs.
    """

    def __init__(self, timeout: float = 120.0):
        self._timeout = timeout
        self._request_id = 0

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    async def discover_tools(
        self, server_url: str, auth: dict[str, Any] | None = None
    ) -> list[ToolDefinition]:
        """Call ``tools/list`` on a remote MCP server and parse into ToolDefinitions."""
        request_payload = self._build_request("tools/list", {})
        raw = await self._send(server_url, request_payload, auth)

        tools: list[ToolDefinition] = []
        for tool_data in raw.get("result", {}).get("tools", []):
            td = ToolDefinition(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                parameters=self._schema_to_params(
                    tool_data.get("inputSchema") or tool_data.get("input_schema", {})
                ),
                output_schema=tool_data.get("outputSchema")
                or tool_data.get("output_schema"),
                tool_type=ToolType.EXTERNAL_MCP,
            )
            tools.append(td)

        return tools

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def call_tool(
        self,
        tool_def: ToolDefinition,
        args: dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        """Call a tool on the remote MCP server and return a ToolResult."""
        started_at = time.time()
        server_url = tool_def.mcp_server_url
        if not server_url:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="configuration",
                    message=f"No MCP server URL configured for tool '{tool_def.name}'",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )

        request_payload = self._build_request(
            "tools/call",
            {
                "name": self._strip_namespace(tool_def.name),
                "arguments": args,
            },
        )

        try:
            raw = await self._send(
                server_url, request_payload, tool_def.mcp_server_auth
            )
            result_data = raw.get("result", {})

            content_list = result_data.get("content", [])
            text_parts = [
                item.get("text", "")
                for item in content_list
                if item.get("type") == "text"
            ]
            output = "\n".join(text_parts) if text_parts else json.dumps(content_list)

            is_error = result_data.get("isError", False)
            return ToolResult(
                success=not is_error,
                output=output,
                error=ToolError(error_type="mcp_remote", message=output)
                if is_error
                else None,
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )

        except httpx.TimeoutException:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="timeout",
                    message=f"MCP server at {server_url} timed out after {self._timeout}s",
                    is_retryable=True,
                    suggested_action="Try again or check the MCP server status.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="mcp_connection",
                    message=f"Failed to call MCP server: {exc}",
                    is_retryable=True,
                    suggested_action="Check MCP server connectivity.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    async def _send(
        self,
        server_url: str,
        payload: dict[str, Any],
        auth: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if auth:
            if "bearer" in auth:
                headers["Authorization"] = f"Bearer {auth['bearer']}"
            elif "api_key" in auth:
                headers["X-API-Key"] = auth["api_key"]

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(server_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            err = data["error"]
            raise RuntimeError(
                f"MCP error {err.get('code', '?')}: {err.get('message', 'Unknown')}"
            )

        return data

    def _build_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._request_id += 1
        return {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params,
        }

    @staticmethod
    def _strip_namespace(name: str) -> str:
        """Remove the ``servername_`` prefix from a namespaced tool name."""
        parts = name.split("_", 1)
        return parts[1] if len(parts) > 1 else name

    @staticmethod
    def _schema_to_params(input_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert a JSON Schema ``inputSchema`` from MCP into the internal param dict."""
        if not input_schema:
            return {}
        properties = input_schema.get("properties", {})
        required_set = set(input_schema.get("required", []))
        params: dict[str, Any] = {}
        for key, prop in properties.items():
            params[key] = {
                "type": prop.get("type", "string"),
                "description": prop.get("description", ""),
                "required": key in required_set,
            }
            for f in ("items", "enum", "default", "minimum", "maximum"):
                if f in prop:
                    params[key][f] = prop[f]
        return params
