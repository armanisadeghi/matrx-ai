# `app` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `app` |
| Last generated | 2026-03-01 00:10 |
| Output file | `app/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`app/core/MODULE_README.md`](app/core/MODULE_README.md) | last generated 2026-03-01 00:09 |
| [`app/models/MODULE_README.md`](app/models/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`app/routers/MODULE_README.md`](app/routers/MODULE_README.md) | last generated 2026-03-01 00:10 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py app --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 31 files across 6 directories.

```
app/
├── MODULE_README.md
├── __init__.py
├── config.py
├── core/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── ai_task.py
│   ├── cancellation.py
│   ├── exceptions.py
│   ├── middleware.py
│   ├── response.py
│   ├── sentry.py
│   ├── streaming.py
├── dependencies/
│   ├── __init__.py
│   ├── auth.py
├── main.py
├── middleware/
│   ├── __init__.py
│   ├── auth.py
├── models/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── agent.py
│   ├── chat.py
│   ├── conversation.py
│   ├── health.py
│   ├── tool.py
├── routers/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── agent.py
│   ├── chat.py
│   ├── conversation.py
│   ├── health.py
│   ├── tool.py
# excluded: 4 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: app/config.py  [python]

  class Settings(BaseSettings):
  def get_settings() -> Settings



---
Filepath: app/__init__.py  [python]




---
Filepath: app/main.py  [python]

  async def lifespan(app: FastAPI) -> AsyncGenerator[None]
  def create_app() -> FastAPI
  def custom_openapi()



---
Filepath: app/dependencies/__init__.py  [python]




---
Filepath: app/dependencies/auth.py  [python]

  async def require_guest_or_above(request: Request) -> None
  async def require_authenticated(request: Request) -> None
  async def require_admin(request: Request) -> None



---
Filepath: app/middleware/__init__.py  [python]




---
Filepath: app/middleware/auth.py  [python]

  class AuthMiddleware:
      def __init__(self, app: ASGIApp) -> None
      async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None
  def _build_context(request: Request) -> AppContext
  def _validate_token(authorization: str, fingerprint_id: str | None, ctx: AppContext) -> AppContext | None



---
Submodule: app/routers/  [6 files — full detail in app/routers/MODULE_README.md]

---
Submodule: app/models/  [6 files — full detail in app/models/MODULE_README.md]

---
Submodule: app/core/  [8 files — full detail in app/core/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** fastapi, jwt, matrx_utils, orjson, pydantic, pydantic_settings, sentry_sdk, sse_starlette, starlette, uvicorn, uvloop
**Internal modules:** agents.cache, agents.definition, agents.resolver, config.unified_config, context.app_context, context.emitter_protocol, context.events, context.stream_emitter, orchestrator, orchestrator.requests, tools.handle_tool_calls
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "app",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
