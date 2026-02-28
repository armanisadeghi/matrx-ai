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
| Last generated | 2026-02-28 13:39 |
| Output file | `instructions/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py instructions --mode signatures \
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

> Auto-generated. 13 files across 2 directories.

```
instructions/
├── MODULE_README.md
├── __init__.py
├── content_blocks_manager.py
├── core.py
├── matrx_fetcher.py
├── pattern_parser.py
├── tests/
│   ├── __init__.py
│   ├── direct_fetch_test.py
│   ├── instruction_builder_test.py
│   ├── integration_test.py
│   ├── simple_variable_example.py
│   ├── user_table_data_test.py
│   ├── variable_recognition_test.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

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
