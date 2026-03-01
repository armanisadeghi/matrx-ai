# `instructions` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `instructions` |
| Last generated | 2026-03-01 00:10 |
| Output file | `instructions/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`instructions/tests/MODULE_README.md`](instructions/tests/MODULE_README.md) | last generated 2026-03-01 00:10 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py instructions --mode signatures
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

> Auto-generated. 14 files across 2 directories.

```
instructions/
├── MODULE_README.md
├── __init__.py
├── content_blocks_manager.py
├── core.py
├── matrx_fetcher.py
├── pattern_parser.py
├── tests/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── direct_fetch_test.py
│   ├── instruction_builder_test.py
│   ├── integration_test.py
│   ├── simple_variable_example.py
│   ├── user_table_data_test.py
│   ├── variable_recognition_test.py
# excluded: 2 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: instructions/matrx_fetcher.py  [python]

  class MatrxFetcher:
      def fetch(cls, table: str, column: str, value: str, fields: str | None = None) -> str
      def fetch_content_blocks(cls, column: str, value: str, fields: str | None = None) -> str
      def _fetch_generic(cls, table: str, column: str, value: str, fields: str | None = None) -> str
      def _parse_fields(cls, fields: str | None, default: str) -> list[str]
      def process_text_with_patterns(cls, text: str, patterns: list[Any]) -> str
  def is_valid_uuid(value: str) -> bool



---
Filepath: instructions/__init__.py  [python]




---
Filepath: instructions/content_blocks_manager.py  [python]

  class ContentBlocksBase(BaseManager[ContentBlocks]):
      def __init__(self, view_class: type[Any] | None = None, fetch_on_init_limit: int = 200, fetch_on_init_with_warnings_off: str = 'YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100')
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None
      async def create_content_blocks(self, **data)
      async def delete_content_blocks(self, id)
      async def get_content_blocks_with_all_related(self, id)
      async def load_content_blocks_by_id(self, id)
      async def load_content_blocks(self, use_cache = True, **kwargs)
      async def update_content_blocks(self, id, **updates)
      async def load_content_block(self, **kwargs)
      async def filter_content_block(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_content_blocks_with_shortcut_categories(self, id)
      async def get_content_block_with_shortcut_categories(self)
      async def load_content_block_by_category_id(self, category_id)
      async def filter_content_block_by_category_id(self, category_id)
      async def load_content_block_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_content_blocks_ids(self)
  class ContentBlocksManager(ContentBlocksBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None
      async def get_template_text(self, id_or_block_id: str)
  def is_valid_uuid(value)
  def get_content_blocks_manager()



---
Filepath: instructions/core.py  [python]

  class SystemInstruction:
      async def load_content_blocks(self) -> 'SystemInstruction'
      def __str__(self) -> str
      def _tools_available(tools_list: list[str]) -> str
      def _code_guidelines() -> str
      def _safety_guidelines() -> str
      def to_string(self) -> str
      def from_value(cls, value: 'str | dict | SystemInstruction') -> 'SystemInstruction'
      async def from_dict(cls, data: dict) -> 'SystemInstruction'
      def for_code_review(cls, language: str = 'TypeScript') -> 'SystemInstruction'
      def for_ai_matrix(cls, additional_context: str = '') -> 'SystemInstruction'



---
Filepath: instructions/pattern_parser.py  [python]

  class MatrxPattern:
      def __repr__(self)
  class MatrxPatternParser:
      def parse(cls, text: str) -> list[MatrxPattern]
      def parse_simple_variables(cls, text: str, variable_config: dict[str, dict[str, Any]]) -> list[MatrxPattern]
      def find_first(cls, text: str) -> MatrxPattern | None
      def parse_all(cls, text: str, variable_config: dict[str, dict[str, Any]] | None = None) -> list[MatrxPattern]
      def replace_patterns(cls, text: str, replacement_func) -> str
  def resolve_matrx_patterns(text: str) -> str



---
Submodule: instructions/tests/  [7 files — full detail in instructions/tests/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, matrx_utils
**Internal modules:** db.managers, db.models
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "instructions",
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

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `config/unified_config.py` | `SystemInstruction()` |
| `config/unified_config.py` | `resolve_matrx_patterns()` |
<!-- /AUTO:callers -->
