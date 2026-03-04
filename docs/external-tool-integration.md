# Integrating External Tools with matrx-ai

This guide is for developers building applications (such as Matrx Local) that consume
`matrx-ai` as a Python package and need to expose their own tools to the AI model.

---

## How it works

Tools are defined in the shared Supabase database.  Each tool row has a `source_app`
column that says which application owns its implementation:

| `source_app` | Who executes it |
|---|---|
| `matrx_ai` | matrx-ai itself — no action needed from you |
| `matrx_local` | Your application — you must register a handler |
| *(any future app)* | That application — same pattern |

When the AI model decides to call a tool, matrx-ai looks up that tool in the registry.
If the tool's `source_app` is not `matrx_ai`, it routes the call to a handler that
**your application registered at startup**.  The result comes back through the exact
same pipeline — guardrails, streaming events, DB logging, model feedback — as if the
tool had run inside matrx-ai.  The model cannot tell the difference.

---

## Startup order

```python
import matrx_ai
from matrx_ai.tools import initialize_tool_system   # already called by the server

# 1. Initialize matrx-ai (connects the DB)
matrx_ai.initialize()

# 2. Register your tool handlers  ← your code goes here
#    (see the three patterns below)

# 3. Load tools from the database (this is where source_app is read)
await initialize_tool_system()
```

> **Important:** Register your handlers **before** `initialize_tool_system()` is
> awaited, or at minimum before the first AI request that could trigger one of your
> tools.  The registry is a process-level singleton, so registrations persist for the
> lifetime of the process.

---

## Pattern 1 — `ExternalToolAdapter` (recommended)

The cleanest integration.  Subclass `ExternalToolAdapter`, decorate methods with
`@external_tool`, and call `register()` once.  The adapter handles everything else.

```python
from matrx_ai.tools import ExternalToolAdapter, external_tool, ToolContext

class MatrxLocalTools(ExternalToolAdapter):
    # Must match the source_app value in the database for your tools.
    source_app = "matrx_local"

    @external_tool("screenshot")
    async def take_screenshot(self, args: dict, ctx: ToolContext) -> dict:
        """Capture a screenshot and return it as base64."""
        region = args.get("region")
        image_b64 = await capture_screen(region)
        return {"image_base64": image_b64}

    @external_tool("open_file")
    async def open_file(self, args: dict, ctx: ToolContext) -> dict:
        """Open and return the contents of a local file."""
        path = args["path"]
        content = await read_local_file(path)
        return {"content": content, "path": path}

    @external_tool("list_directory")
    async def list_directory(self, args: dict, ctx: ToolContext) -> dict:
        """List files in a local directory."""
        entries = await scan_dir(args["path"])
        return {"entries": entries}


# Call once at application startup, before any AI requests.
MatrxLocalTools().register()
```

### What `@external_tool` does

- Marks the method as the handler for a specific tool name.
- The adapter auto-discovers all decorated methods and registers each one as a
  per-tool handler (exact-name match — highest priority).
- The adapter also registers itself as the app-level fallback dispatcher for
  `source_app`, so any tool from your app that doesn't have a specific handler falls
  through to `dispatch()` (see below).

### Return values

Your methods can return any of these — all are normalised automatically:

| Return value | What the model receives |
|---|---|
| `ToolResult` | Passed through as-is (gives you full control) |
| `dict` | `ToolResult(success=True, output=dict)` |
| `dict` with `"status": "error"` | `ToolResult(success=False, error=...)` |
| `str` / any other value | `ToolResult(success=True, output=value)` |

You only need to return a `ToolResult` directly when you want to set specific fields
like `should_persist_output`, `child_usages`, or custom `error` details.

### Using `ctx` (ToolContext)

`ctx` gives you runtime context for the call:

```python
ctx.tool_name          # name of the tool being called (str)
ctx.call_id            # unique ID for this specific call (str)
ctx.user_id            # authenticated user ID (str)
ctx.conversation_id    # current conversation ID (str)
ctx.request_id         # current request ID (str)
ctx.iteration          # which tool-call loop iteration (int)
ctx.recursion_depth    # agent nesting depth (int)
ctx.emitter            # stream emitter (for sending events mid-execution)
ctx.api_keys           # any API keys from the user's context (dict)
```

### Handling tools not covered by `@external_tool`

Override `dispatch()` to handle any tool from your `source_app` that doesn't have a
dedicated decorated method:

```python
class MatrxLocalTools(ExternalToolAdapter):
    source_app = "matrx_local"

    @external_tool("screenshot")
    async def take_screenshot(self, args: dict, ctx: ToolContext) -> dict:
        ...

    async def dispatch(self, args: dict, ctx: ToolContext) -> ToolResult:
        # ctx.tool_name tells you which tool was called.
        # This is your custom router for everything else.
        match ctx.tool_name:
            case "open_file":
                return ToolResult(success=True, output=await read_file(args["path"]),
                                  tool_name=ctx.tool_name, call_id=ctx.call_id)
            case _:
                # Let the default error propagate for truly unknown tools.
                return await super().dispatch(args, ctx)
```

---

## Pattern 2 — Per-tool function registration

For simpler cases or when you don't want a class, register async functions directly.

```python
from matrx_ai.tools import register_external_tool_handler, ToolContext, ToolResult

async def handle_screenshot(args: dict, ctx: ToolContext) -> ToolResult:
    image_b64 = await capture_screen(args.get("region"))
    return ToolResult(
        success=True,
        output={"image_base64": image_b64},
        tool_name=ctx.tool_name,
        call_id=ctx.call_id,
    )

async def handle_open_file(args: dict, ctx: ToolContext) -> ToolResult:
    content = await read_local_file(args["path"])
    return ToolResult(
        success=True,
        output={"content": content},
        tool_name=ctx.tool_name,
        call_id=ctx.call_id,
    )

# Register each tool individually.
register_external_tool_handler("screenshot", handle_screenshot)
register_external_tool_handler("open_file", handle_open_file)
```

> Per-tool registrations have higher priority than app-level registrations.
> Registering the same tool name again replaces the previous handler.

---

## Pattern 3 — Single app-level dispatcher

If you want one function that receives every call for your `source_app`:

```python
from matrx_ai.tools import register_external_app_handler, ToolContext, ToolResult

async def matrx_local_dispatcher(args: dict, ctx: ToolContext) -> ToolResult:
    # ctx.tool_name tells you which specific tool was called.
    match ctx.tool_name:
        case "screenshot":
            image_b64 = await capture_screen(args.get("region"))
            return ToolResult(success=True, output={"image_base64": image_b64},
                              tool_name=ctx.tool_name, call_id=ctx.call_id)
        case "open_file":
            content = await read_local_file(args["path"])
            return ToolResult(success=True, output={"content": content},
                              tool_name=ctx.tool_name, call_id=ctx.call_id)
        case _:
            return ToolResult(
                success=False,
                error=ToolError(error_type="not_implemented",
                                message=f"Tool '{ctx.tool_name}' is not implemented."),
                tool_name=ctx.tool_name,
                call_id=ctx.call_id,
            )

register_external_app_handler("matrx_local", matrx_local_dispatcher)
```

---

## Handler resolution order

For every tool call, matrx-ai resolves the handler in this order:

```
1. Per-tool handler   →  register_external_tool_handler("tool_name", ...)
                         or @external_tool("tool_name") on an adapter method
                         ↓ (if not found)
2. App-level handler  →  register_external_app_handler("source_app", ...)
                         or ExternalToolAdapter.dispatch()
                         ↓ (if not found)
3. No handler         →  structured error returned to the model — not a crash
```

This means you can use Pattern 1 for most tools and Pattern 2 for specific overrides,
and they compose naturally.

---

## Error handling

If your handler raises an exception, matrx-ai catches it and returns a structured
`ToolResult` with `success=False` and `error_type="external_handler_error"`.  The
model receives the error message and may try a different approach.  Your process does
not crash.

For expected errors (e.g. file not found), return a `ToolResult` with `success=False`
explicitly:

```python
from matrx_ai.tools import ToolResult, ToolError

async def handle_open_file(args: dict, ctx: ToolContext) -> ToolResult:
    path = args.get("path", "")
    if not path:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="invalid_arguments",
                message="The 'path' argument is required.",
                suggested_action="Provide a valid file path and try again.",
            ),
            tool_name=ctx.tool_name,
            call_id=ctx.call_id,
        )
    content = await read_local_file(path)
    return ToolResult(success=True, output={"content": content},
                      tool_name=ctx.tool_name, call_id=ctx.call_id)
```

---

## What you do NOT need to worry about

The following are all handled by matrx-ai automatically, regardless of which pattern
you use:

- **Guardrails** — rate limits, cost caps, duplicate detection, loop detection
- **Streaming events** — "tool started" / "tool completed" sent to the client
- **DB logging** — two-phase write to `cx_tool_call` (INSERT on start, UPDATE on finish)
- **Model feedback** — your result is formatted and inserted into the conversation
- **Timeouts** — the `timeout_seconds` value from the DB row is enforced by the executor
- **Error normalisation** — any exception is caught and turned into a model-readable error

---

## Complete startup example (Matrx Local)

```python
# matrx_local/startup.py

import matrx_ai
from matrx_ai.tools import (
    ExternalToolAdapter,
    ExternalToolHandler,
    ToolContext,
    ToolResult,
    external_tool,
    initialize_tool_system,
)


class MatrxLocalTools(ExternalToolAdapter):
    source_app = "matrx_local"

    def __init__(self, config: dict) -> None:
        self.config = config   # any app state you need in handlers

    @external_tool("screenshot")
    async def take_screenshot(self, args: dict, ctx: ToolContext) -> dict:
        from local.screen import capture
        return {"image_base64": await capture(args.get("region"))}

    @external_tool("open_file")
    async def open_file(self, args: dict, ctx: ToolContext) -> dict:
        from local.fs import read_file
        return {"content": await read_file(args["path"])}

    @external_tool("run_shell_command")
    async def run_shell_command(self, args: dict, ctx: ToolContext) -> dict:
        from local.shell import run
        stdout, stderr, code = await run(args["command"])
        return {"stdout": stdout, "stderr": stderr, "exit_code": code}


async def startup(config: dict) -> None:
    # 1. Connect the database.
    matrx_ai.initialize()

    # 2. Register your tool handlers.
    MatrxLocalTools(config).register()

    # 3. Load tools from the database (reads source_app, builds the registry).
    count = await initialize_tool_system()
    print(f"Tool system ready: {count} tools loaded")
```

---

## Reference

### `ExternalToolAdapter`

| Member | Description |
|---|---|
| `source_app` | Class attribute — set to your DB `source_app` value |
| `register(registry=None)` | Call once at startup to register all handlers |
| `dispatch(args, ctx)` | Override for custom routing of unregistered tools |

### `@external_tool(tool_name)`

Decorator for `ExternalToolAdapter` methods. `tool_name` must exactly match the `name`
column in the `tools` database table.

### `register_external_tool_handler(tool_name, handler)`

Register a standalone async function for a specific tool. Handler signature:
`async (args: dict, ctx: ToolContext) -> ToolResult | dict | Any`

### `register_external_app_handler(source_app, handler)`

Register a standalone async function as the catch-all for all tools from `source_app`.
Same handler signature as above.

### `ExternalHandlerRegistry`

The underlying singleton. Use `ExternalHandlerRegistry.get_instance()` for advanced
introspection or testing. Not needed for normal integration.
