# `tests` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tests` |
| Last generated | 2026-03-01 00:14 |
| Output file | `tests/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`tests/ai/MODULE_README.md`](tests/ai/MODULE_README.md) | last generated 2026-03-01 00:14 |
| [`tests/openai/MODULE_README.md`](tests/openai/MODULE_README.md) | last generated 2026-03-01 00:10 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tests --mode signatures
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

> Auto-generated. 25 files across 7 directories.

```
tests/
├── MODULE_README.md
├── __init__.py
├── ai/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── execution_test.py
│   ├── groq_transcription_test.py
│   ├── small_test.py
│   ├── test_context.py
│   ├── test_error_handling.py
│   ├── test_translations.py
├── db-pull-push/
│   ├── message-rebuild.py
├── openai/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── background_stream_async.py
│   ├── conversation_id_test.py
│   ├── openai_function_test.py
│   ├── openai_image_input.py
│   ├── openai_small_tests.py
│   ├── openai_translation_test.py
├── prompts/
│   ├── __init__.py
│   ├── agent_comparison.py
│   ├── prompt_to_config.py
│   ├── test_basic_prompts.py
├── random/
│   ├── print_test.py
├── util_tests/
│   ├── readme_updates.py
# excluded: 6 .json, 3 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: tests/__init__.py  [python]




---
Submodule: tests/openai/  [7 files — full detail in tests/openai/MODULE_README.md]

---
Filepath: tests/random/print_test.py  [python]




---
Filepath: tests/util_tests/readme_updates.py  [python]




---
Filepath: tests/db-pull-push/message-rebuild.py  [python]




---
Filepath: tests/prompts/__init__.py  [python]




---
Filepath: tests/prompts/agent_comparison.py  [python]

  async def test_autonomous_execution(settings_to_use)
  async def create_conversation_with_agent(prompt_id: str, variables: dict, debug: bool = False)
  async def create_conversation_simple(prompt_id: str, variables: dict, debug: bool = False)
  async def main()



---
Filepath: tests/prompts/test_basic_prompts.py  [python]

  async def load_prompt_by_id(prompt_id: str)
  async def load_prompt_by_name(prompt_name: str)
  async def load_prompt_by_user_id(user_id: str)



---
Filepath: tests/prompts/prompt_to_config.py  [python]

  async def test_autonomous_execution(settings_to_use)
  def replace_variables(prompt: Prompts, variables: dict)
  async def load_and_convert_prompt(prompt_id: str, variables: Optional[dict] = None)
  async def create_conversation_from_prompt(prompt_id: str, variables: Optional[dict] = None, debug: bool = False)



---
Submodule: tests/ai/  [7 files — full detail in tests/ai/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** client, dotenv, initialize_systems, matrx_utils, openai, prompts, pydantic, rich
**Internal modules:** config.unified_config, context.app_context, context.console_emitter, context.emitter_protocol, db.models, media.audio, orchestrator.executor, tools.models, tools.registry
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tests",
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
