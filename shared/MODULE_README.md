# `shared` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `shared` |
| Last generated | 2026-02-28 13:39 |
| Output file | `shared/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py shared --mode signatures \
        --call-graph-scope handle_tool_calls,executor,registry,guardrails
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

> Auto-generated. 5 files across 1 directories.

```
shared/
├── MODULE_README.md
├── __init__.py
├── file_handler.py
├── json_utils.py
├── supabase_client.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: shared/__init__.py  [python]



---
Filepath: shared/json_utils.py  [python]

  def to_matrx_json(data: Any) -> str


---
Filepath: shared/file_handler.py  [python]

  class FileHandler:
      async def save_file(path: str, content: bytes) -> str
      async def read_file(path: str) -> bytes


---
Filepath: shared/supabase_client.py  [python]

  def get_supabase_client() -> Any
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** supabase
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "shared",
  "mode": "signatures",
  "scope": [
    "handle_tool_calls",
    "executor",
    "registry",
    "guardrails"
  ],
  "project_noise": null,
  "include_call_graph": true,
  "entry_points": [
    "handle_tool_calls_v2",
    "initialize_tool_system",
    "initialize_tool_system_sync",
    "cleanup_conversation"
  ],
  "call_graph_exclude": null
}
```
<!-- /AUTO:config -->
