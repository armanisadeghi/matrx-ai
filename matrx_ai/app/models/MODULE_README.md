# `app.models` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `app/models` |
| Last generated | 2026-03-01 00:10 |
| Output file | `app/models/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py app/models --mode signatures
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

> Auto-generated. 7 files across 1 directories.

```
app/models/
├── MODULE_README.md
├── __init__.py
├── agent.py
├── chat.py
├── conversation.py
├── health.py
├── tool.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: app/models/__init__.py  [python]



---
Filepath: app/models/health.py  [python]

  class HealthStatus(BaseModel):
      # fields: status: str, version: str, environment: str, checks: dict[str, Any] = {}


---
Filepath: app/models/tool.py  [python]

  class ToolParameter(BaseModel):
      # fields: name: str, type: str, description: str, required: bool = True, default: Any = None
  class ToolDefinition(BaseModel):
      # fields: name: str, description: str, parameters: list[ToolParameter] = list(), metadata: dict[str, Any] = dict()
  class ToolCallRequest(BaseModel):
      # fields: tool_name: str, arguments: dict[str, Any] = dict(), call_id: str | None = None, metadata: dict[str, Any] = dict()
  class ToolCallResult(BaseModel):
      # fields: call_id: str | None = None, tool_name: str, result: Any, error: str | None = None, elapsed_ms: float | None = None


---
Filepath: app/models/chat.py  [python]

  class ChatRequest(BaseModel):
      # fields: ai_model_id: str, messages: list[dict[str, Any]], conversation_id: str | None = None, max_iterations: int = 20, max_retries_per_iteration: int = 2, stream: bool = True, debug: bool = False, system_instruction: str | None = None, max_output_tokens: int | None = None, temperature: float | None = None, top_p: float | None = None, top_k: int | None = None, tools: list[str] | None = None, tool_choice: Any | None = None, parallel_tool_calls: bool = True, reasoning_effort: str | None = None, reasoning_summary: str | None = None, thinking_level: str | None = None, include_thoughts: bool | None = None, thinking_budget: int | None = None, response_format: dict[str, Any] | None = None, stop_sequences: list[str] | None = None, internal_web_search: bool | None = None, internal_url_context: bool | None = None, size: str | None = None, quality: str | None = None, count: int = 1, audio_voice: str | None = None, audio_format: str | None = None, seconds: str | None = None, fps: int | None = None, steps: int | None = None, seed: int | None = None, guidance_scale: int | None = None, output_quality: int | None = None, negative_prompt: str | None = None, output_format: str | None = None, width: int | None = None, height: int | None = None, frame_images: list | None = None, reference_images: list | None = None, disable_safety_checker: bool | None = None, metadata: dict[str, Any] | None = None, store: bool = True
      def coerce_response_format(cls, v: Any) -> Any


---
Filepath: app/models/conversation.py  [python]

  class ConversationContinueRequest(BaseModel):
      # fields: user_input: str | list[dict[str, Any]], config_overrides: dict[str, Any] | None = None, stream: bool = True, debug: bool = False


---
Filepath: app/models/agent.py  [python]

  class AgentStatus(StrEnum):
  class AgentStartRequest(BaseModel):
      # fields: user_input: str | list[dict[str, Any]] | None = None, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None, stream: bool = True, debug: bool = False
  class AgentInfo(BaseModel):
      # fields: agent_id: str, status: AgentStatus, created_at: str, metadata: dict[str, Any] = dict()
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `app/routers/agent.py` | `AgentStartRequest()` |
| `app/routers/chat.py` | `ChatRequest()` |
| `app/routers/conversation.py` | `ConversationContinueRequest()` |
| `app/routers/health.py` | `HealthStatus()` |
| `app/routers/tool.py` | `ToolCallRequest()` |
| `app/routers/tool.py` | `ToolCallResult()` |
| `app/routers/tool.py` | `ToolDefinition()` |
| `app/routers/tool.py` | `ToolParameter()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_utils, pydantic
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "app/models",
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
