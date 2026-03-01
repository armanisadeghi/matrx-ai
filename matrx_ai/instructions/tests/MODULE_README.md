# `instructions.tests` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `instructions/tests` |
| Last generated | 2026-03-01 00:10 |
| Output file | `instructions/tests/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py instructions/tests --mode signatures
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
instructions/tests/
├── MODULE_README.md
├── __init__.py
├── direct_fetch_test.py
├── instruction_builder_test.py
├── integration_test.py
├── simple_variable_example.py
├── user_table_data_test.py
├── variable_recognition_test.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: instructions/tests/__init__.py  [python]



---
Filepath: instructions/tests/instruction_builder_test.py  [python]

  async def main()


---
Filepath: instructions/tests/simple_variable_example.py  [python]



---
Filepath: instructions/tests/direct_fetch_test.py  [python]

  def is_valid_uuid(value)
  def fetch_content_blocks_direct(value)
  def fetch_content_block(field_name: str, value: str)
  def fetch_content_blocks(field_name: str, value: str)
  def fetch_content_blocks_flexible(field_name: str, value: str, template_fn: callable = lambda cb: cb.template)
  def fetch_content_blocks_by_attribute(field_name: str, value: str, content_attr: str)
  def fetch_content_blocks_by_attributes(field_name: str, value: str, content_attrs: str | list[str])


---
Filepath: instructions/tests/integration_test.py  [python]

  def process_text_with_matrx(text: str, verbose: bool = True) -> str


---
Filepath: instructions/tests/variable_recognition_test.py  [python]

  def replacement_func(pattern: MatrxPattern) -> str


---
Filepath: instructions/tests/user_table_data_test.py  [python]

  def get_table_data(table_id: str) -> list[dict[str, Any]]
  def get_table_row_data(row_id: str) -> dict[str, Any]
  def get_table_cell_data(row_id: str, column_name: str) -> Any
  def filter_table_data_by_row_value(table_id: str, filter_key: str, filter_value: str) -> list[dict[str, Any]]
  def filter_table_data_by_column_name(table_id: str, filter_key: str) -> list[Any]
  def sample_exercises() -> list[dict[str, Any]]
  def sample_research() -> list[dict[str, Any]]
  def sample_research_findings_summary() -> list[Any]
  def get_data_with_bookmark(bookmark: dict[str, Any], item_type: Literal['table', 'column', 'row', 'cell']) -> Any
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_utils
**Internal modules:** db.models, instructions.core, instructions.matrx_fetcher, instructions.pattern_parser
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "instructions/tests",
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
