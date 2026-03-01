# `tools.arg_models` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tools/arg_models` |
| Last generated | 2026-03-01 00:10 |
| Output file | `tools/arg_models/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tools/arg_models --mode signatures
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

> Auto-generated. 10 files across 1 directories.

```
tools/arg_models/
├── MODULE_README.md
├── __init__.py
├── browser_args.py
├── db_args.py
├── fs_args.py
├── math_args.py
├── memory_args.py
├── shell_args.py
├── text_args.py
├── web_args.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tools/arg_models/__init__.py  [python]



---
Filepath: tools/arg_models/shell_args.py  [python]

  class ShellExecuteArgs(BaseModel):
      # fields: command: str, working_dir: str = '.', timeout_seconds: int = 30, allow_network: bool = True
  class ShellPythonArgs(BaseModel):
      # fields: code: str, timeout_seconds: int = 30


---
Filepath: tools/arg_models/browser_args.py  [python]

  class BrowserNavigateArgs(BaseModel):
      # fields: url: str, wait_for: str = 'load', extract_text: bool = True, session_id: str = ''
  class BrowserClickArgs(BaseModel):
      # fields: selector: str, session_id: str, wait_after_ms: int = 1000
  class BrowserTypeArgs(BaseModel):
      # fields: selector: str, text: str, session_id: str, clear_first: bool = True, press_enter: bool = False
  class BrowserScreenshotArgs(BaseModel):
      # fields: session_id: str, selector: str = '', width: int = 1280, height: int = 720
  class BrowserSelectOptionArgs(BaseModel):
      # fields: session_id: str, selector: str, value: str = '', label: str = ''
  class BrowserWaitForArgs(BaseModel):
      # fields: session_id: str, selector: str = '', text: str = '', timeout_ms: int = 10000, state: str = 'visible'
  class BrowserGetElementArgs(BaseModel):
      # fields: session_id: str, selector: str, attributes: list[str] = list()
  class BrowserScrollArgs(BaseModel):
      # fields: session_id: str, direction: str = 'down', amount_px: int = 500, selector: str = ''
  class BrowserCloseArgs(BaseModel):
      # fields: session_id: str


---
Filepath: tools/arg_models/math_args.py  [python]

  class CalculateArgs(BaseModel):
      # fields: expression: str


---
Filepath: tools/arg_models/memory_args.py  [python]

  class MemoryStoreArgs(BaseModel):
      # fields: key: str, content: str, memory_type: str = 'long', scope: str = 'user', importance: float = 0.5
  class MemoryRecallArgs(BaseModel):
      # fields: key: str = '', query: str = '', memory_type: str | None = None, scope: str = 'user', limit: int = 5
  class MemorySearchArgs(BaseModel):
      # fields: query: str, scope: str = 'user', memory_type: str | None = None, limit: int = 10
  class MemoryUpdateArgs(BaseModel):
      # fields: key: str, content: str, scope: str = 'user', importance: float | None = None
  class MemoryForgetArgs(BaseModel):
      # fields: key: str, scope: str = 'user'


---
Filepath: tools/arg_models/text_args.py  [python]

  class TextAnalyzeArgs(BaseModel):
      # fields: text: str, analysis_type: str = 'summary'
  class RegexExtractArgs(BaseModel):
      # fields: text: str, pattern: str, group: int = 0, find_all: bool = True


---
Filepath: tools/arg_models/web_args.py  [python]

  class WebSearchArgs(BaseModel):
      # fields: queries: list[str], freshness: str | None = None, max_results_per_query: int = 5
  class WebReadArgs(BaseModel):
      # fields: urls: list[str], instructions: str = '', summarize: bool = False, max_content_length: int = 50000
  class WebResearchArgs(BaseModel):
      # fields: queries: list[str], instructions: str, freshness: str | None = None, research_depth: Literal['shallow', 'medium', 'deep', 'very_deep'] = 'medium', country: str = 'us'


---
Filepath: tools/arg_models/db_args.py  [python]

  class DbQueryArgs(BaseModel):
      # fields: query: str, limit: int = 100
  class DbInsertArgs(BaseModel):
      # fields: table: str, data: dict[str, Any] | list[dict[str, Any]]
  class DbUpdateArgs(BaseModel):
      # fields: table: str, data: dict[str, Any], match: dict[str, Any]
  class DbSchemaArgs(BaseModel):
      # fields: table: str = ''


---
Filepath: tools/arg_models/fs_args.py  [python]

  class FsReadArgs(BaseModel):
      # fields: path: str, offset: int = 0, limit: int = 0
  class FsWriteArgs(BaseModel):
      # fields: path: str, content: str, create_dirs: bool = True, append: bool = False
  class FsListArgs(BaseModel):
      # fields: path: str = '.', recursive: bool = False, pattern: str = ''
  class FsSearchArgs(BaseModel):
      # fields: pattern: str, path: str = '.', content_search: bool = False, max_results: int = 50
  class FsMkdirArgs(BaseModel):
      # fields: path: str, parents: bool = True
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `tools/implementations/browser.py` | `BrowserClickArgs()` |
| `tools/implementations/browser.py` | `BrowserCloseArgs()` |
| `tools/implementations/browser.py` | `BrowserGetElementArgs()` |
| `tools/implementations/browser.py` | `BrowserNavigateArgs()` |
| `tools/implementations/browser.py` | `BrowserScreenshotArgs()` |
| `tools/implementations/browser.py` | `BrowserScrollArgs()` |
| `tools/implementations/browser.py` | `BrowserSelectOptionArgs()` |
| `tools/implementations/browser.py` | `BrowserTypeArgs()` |
| `tools/implementations/browser.py` | `BrowserWaitForArgs()` |
| `tools/implementations/math.py` | `CalculateArgs()` |
| `tools/implementations/database.py` | `DbInsertArgs()` |
| `tools/implementations/database.py` | `DbQueryArgs()` |
| `tools/implementations/database.py` | `DbSchemaArgs()` |
| `tools/implementations/database.py` | `DbUpdateArgs()` |
| `tools/implementations/filesystem.py` | `FsListArgs()` |
| `tools/implementations/filesystem.py` | `FsMkdirArgs()` |
| `tools/implementations/filesystem.py` | `FsReadArgs()` |
| `tools/implementations/filesystem.py` | `FsSearchArgs()` |
| `tools/implementations/filesystem.py` | `FsWriteArgs()` |
| `tools/implementations/memory.py` | `MemoryForgetArgs()` |
| `tools/implementations/memory.py` | `MemoryRecallArgs()` |
| `tools/implementations/memory.py` | `MemorySearchArgs()` |
| `tools/implementations/memory.py` | `MemoryStoreArgs()` |
| `tools/implementations/memory.py` | `MemoryUpdateArgs()` |
| `tools/implementations/text.py` | `RegexExtractArgs()` |
| `tools/implementations/shell.py` | `ShellExecuteArgs()` |
| `tools/implementations/shell.py` | `ShellPythonArgs()` |
| `tools/implementations/text.py` | `TextAnalyzeArgs()` |
| `tools/implementations/web.py` | `WebReadArgs()` |
| `tools/implementations/web.py` | `WebResearchArgs()` |
| `tools/implementations/web.py` | `WebSearchArgs()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** pydantic
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tools/arg_models",
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
