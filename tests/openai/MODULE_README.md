# `tests.openai` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tests/openai` |
| Last generated | 2026-03-01 00:10 |
| Output file | `tests/openai/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tests/openai --mode signatures
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

> Auto-generated. 8 files across 1 directories.

```
tests/openai/
├── MODULE_README.md
├── __init__.py
├── background_stream_async.py
├── conversation_id_test.py
├── openai_function_test.py
├── openai_image_input.py
├── openai_small_tests.py
├── openai_translation_test.py
# excluded: 1 .json, 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tests/openai/__init__.py  [python]



---
Filepath: tests/openai/openai_small_tests.py  [python]



---
Filepath: tests/openai/conversation_id_test.py  [python]

  def test_conversation_id()
  def retreive_by_id(id: str)
  def test_with_hard_coded_id(id: str)


---
Filepath: tests/openai/openai_image_input.py  [python]



---
Filepath: tests/openai/background_stream_async.py  [python]

  class Step(BaseModel):
      # fields: explanation: str, output: str
  class MathResponse(BaseModel):
      # fields: steps: List[Step], final_answer: str
  async def main() -> None


---
Filepath: tests/openai/openai_translation_test.py  [python]



---
Filepath: tests/openai/openai_function_test.py  [python]

  def get_horoscope(sign)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** dotenv, matrx_utils, openai, pydantic, rich
**Internal modules:** config.unified_config
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tests/openai",
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
