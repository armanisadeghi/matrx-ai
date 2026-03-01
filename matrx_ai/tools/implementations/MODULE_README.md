# `tools.implementations` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tools/implementations` |
| Last generated | 2026-03-01 00:10 |
| Output file | `tools/implementations/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tools/implementations --mode signatures
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

> Auto-generated. 19 files across 1 directories.

```
tools/implementations/
├── MODULE_README.md
├── __init__.py
├── _summarize_helper.py
├── browser.py
├── code.py
├── database.py
├── filesystem.py
├── math.py
├── memory.py
├── news.py
├── personal_tables.py
├── questionnaire.py
├── seo.py
├── shell.py
├── text.py
├── travel.py
├── user_lists.py
├── user_tables.py
├── web.py
# excluded: 2 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tools/implementations/shell.py  [python]

  WORKSPACE_BASE = os.environ.get('TOOL_WORKSPACE_BASE', '/tmp/workspaces')
  MAX_OUTPUT_SIZE = 10240
  BLOCKED_COMMANDS = {11 items}
  def _is_blocked(command: str) -> bool
  def _workspace_dir(ctx: ToolContext, working_dir: str = '.') -> str
  async def shell_execute(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def shell_python(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/user_lists.py  [python]

  async def userlist_create(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def userlist_create_simple(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  def _make_serializable(obj: Any) -> Any
  async def userlist_get_all(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def userlist_get_details(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def userlist_update_item(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def userlist_batch_update(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/travel.py  [python]

  async def travel_get_location(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def travel_get_weather(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def travel_get_restaurants(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def travel_get_activities(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def travel_get_events(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def travel_create_summary(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/__init__.py  [python]



---
Filepath: tools/implementations/_summarize_helper.py  [python]

  async def summarize_content(content: str, instructions: str, ctx: ToolContext, model_id: str = 'gemini-2.5-flash-preview-05-20') -> tuple[str, list[TokenUsage]]


---
Filepath: tools/implementations/personal_tables.py  [python]

  def _run_query(query_name: str, params: dict[str, Any]) -> list[dict]
  def _run_batch(query_name: str, batch_params: list[dict], batch_size: int = 50) -> list[dict]
  async def usertable_get_all(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_get_metadata(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_get_fields(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_get_data(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_search_data(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_add_rows(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_update_row(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_delete_row(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def usertable_create_advanced(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/web.py  [python]

  async def web_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def web_read(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def research_web(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def _search_with_query(query: str) -> tuple[str, dict[str, Any] | None]


---
Filepath: tools/implementations/memory.py  [python]

  EXPIRY_MAP = {'short': timedelta(hours=1), 'medium': timedelta(days=7), 'long': None}
  def _scope_id(ctx: ToolContext, scope: str) -> str | None
  async def memory_store(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def memory_recall(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def memory_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def memory_update(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def memory_forget(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/text.py  [python]

  async def text_analyze(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def text_regex_extract(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/code.py  [python]

  def _workspace_dir(ctx: ToolContext) -> Path
  async def code_execute_python(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def code_store_html(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  def _resolve_project_root(project_root: str) -> str | None
  async def code_fetch_code(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def code_fetch_tree(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/questionnaire.py  [python]

  VALID_COMPONENT_TYPES = {'dropdown', 'checkboxes', 'radio', 'toggle', 'slider', 'input', 'textarea'}
  async def interaction_ask(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/seo.py  [python]

  async def seo_check_meta_titles(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def seo_check_meta_descriptions(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def seo_check_meta_tags_batch(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def seo_get_keyword_data(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/filesystem.py  [python]

  MAX_READ_SIZE = 1048576
  WORKSPACE_BASE = os.environ.get('TOOL_WORKSPACE_BASE', '/tmp/workspaces')
  def _resolve_path(relative: str, ctx: ToolContext) -> Path
  async def fs_read(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def fs_write(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def fs_list(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def fs_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def fs_mkdir(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/user_tables.py  [python]

  async def usertable_create(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/math.py  [python]

  async def math_calculate(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/browser.py  [python]

  def _mgr()
  async def browser_navigate(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_click(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_type_text(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_screenshot(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_close(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_select_option(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_wait_for(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_get_element(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def browser_scroll(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/database.py  [python]

  BLOCKED_TABLES = {'auth', 'cx_conversation', 'cx_message', 'cx_user_request', 'cx_request'}
  READ_ONLY_TABLES = {'ai_models', 'tools', 'prompt_builtins'}
  DANGEROUS_KEYWORDS = {'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE'}
  MAX_QUERY_TIMEOUT = 10
  def _get_async_supabase()
  def _is_blocked_table(table: str) -> bool
  def _is_read_only(table: str) -> bool
  def _is_safe_select(query: str) -> bool
  async def db_query(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def db_insert(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def db_update(args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def db_schema(args: dict[str, Any], ctx: ToolContext) -> ToolResult


---
Filepath: tools/implementations/news.py  [python]

  async def news_get_headlines(args: dict[str, Any], ctx: ToolContext) -> ToolResult
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `tools/tests/mimic_model_tests.py` | `browser_click()` |
| `tools/tests/mimic_model_tests.py` | `browser_close()` |
| `tools/tests/mimic_model_tests.py` | `browser_get_element()` |
| `tools/tests/mimic_model_tests.py` | `browser_navigate()` |
| `tools/tests/mimic_model_tests.py` | `browser_screenshot()` |
| `tools/tests/mimic_model_tests.py` | `browser_scroll()` |
| `tools/tests/mimic_model_tests.py` | `browser_select_option()` |
| `tools/tests/mimic_model_tests.py` | `browser_type_text()` |
| `tools/tests/mimic_model_tests.py` | `browser_wait_for()` |
| `tools/tests/mimic_model_tests.py` | `code_execute_python()` |
| `tools/tests/mimic_model_tests.py` | `code_fetch_code()` |
| `tools/tests/mimic_model_tests.py` | `code_fetch_tree()` |
| `tools/tests/mimic_model_tests.py` | `code_store_html()` |
| `tools/tests/mimic_model_tests.py` | `db_insert()` |
| `tools/tests/mimic_model_tests.py` | `db_query()` |
| `tools/tests/mimic_model_tests.py` | `db_schema()` |
| `tools/tests/mimic_model_tests.py` | `db_update()` |
| `tools/tests/mimic_model_tests.py` | `fs_list()` |
| `tools/tests/mimic_model_tests.py` | `fs_mkdir()` |
| `tools/tests/mimic_model_tests.py` | `fs_read()` |
| `tools/tests/mimic_model_tests.py` | `fs_search()` |
| `tools/tests/mimic_model_tests.py` | `fs_write()` |
| `tools/tests/mimic_model_tests.py` | `interaction_ask()` |
| `tools/tests/mimic_model_tests.py` | `math_calculate()` |
| `tools/tests/mimic_model_tests.py` | `memory_forget()` |
| `tools/tests/mimic_model_tests.py` | `memory_recall()` |
| `tools/tests/mimic_model_tests.py` | `memory_search()` |
| `tools/tests/mimic_model_tests.py` | `memory_store()` |
| `tools/tests/mimic_model_tests.py` | `memory_update()` |
| `tools/tests/mimic_model_tests.py` | `news_get_headlines()` |
| `tools/tests/mimic_model_tests.py` | `research_web()` |
| `tools/tests/mimic_model_tests.py` | `seo_check_meta_descriptions()` |
| `tools/tests/mimic_model_tests.py` | `seo_check_meta_tags_batch()` |
| `tools/tests/mimic_model_tests.py` | `seo_check_meta_titles()` |
| `tools/tests/mimic_model_tests.py` | `seo_get_keyword_data()` |
| `tools/tests/mimic_model_tests.py` | `shell_execute()` |
| `tools/tests/mimic_model_tests.py` | `shell_python()` |
| `tools/tests/mimic_model_tests.py` | `text_analyze()` |
| `tools/tests/mimic_model_tests.py` | `text_regex_extract()` |
| `tools/tests/mimic_model_tests.py` | `travel_create_summary()` |
| `tools/tests/mimic_model_tests.py` | `travel_get_activities()` |
| `tools/tests/mimic_model_tests.py` | `travel_get_events()` |
| `tools/tests/mimic_model_tests.py` | `travel_get_location()` |
| `tools/tests/mimic_model_tests.py` | `travel_get_restaurants()` |
| `tools/tests/mimic_model_tests.py` | `travel_get_weather()` |
| `tools/tests/mimic_model_tests.py` | `userlist_batch_update()` |
| `tools/tests/mimic_model_tests.py` | `userlist_create()` |
| `tools/tests/mimic_model_tests.py` | `userlist_create_simple()` |
| `tools/tests/mimic_model_tests.py` | `userlist_get_all()` |
| `tools/tests/mimic_model_tests.py` | `userlist_get_details()` |
| `tools/tests/mimic_model_tests.py` | `userlist_update_item()` |
| `tools/tests/mimic_model_tests.py` | `usertable_add_rows()` |
| `tools/tests/mimic_model_tests.py` | `usertable_create()` |
| `tools/tests/mimic_model_tests.py` | `usertable_create_advanced()` |
| `tools/tests/mimic_model_tests.py` | `usertable_delete_row()` |
| `tools/tests/mimic_model_tests.py` | `usertable_get_all()` |
| `tools/tests/mimic_model_tests.py` | `usertable_get_data()` |
| `tools/tests/mimic_model_tests.py` | `usertable_get_fields()` |
| `tools/tests/mimic_model_tests.py` | `usertable_get_metadata()` |
| `tools/tests/mimic_model_tests.py` | `usertable_search_data()` |
| `tools/tests/mimic_model_tests.py` | `usertable_update_row()` |
| `tools/tests/mimic_model_tests.py` | `web_read()` |
| `tools/tests/mimic_model_tests.py` | `web_search()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** api_management, common, matrx_orm, matrx_utils, requests, scraper, seo, user_data
**Internal modules:** agents.definition, config, config.unified_config, context.app_context, db.custom, tools.arg_models, tools.browser_sessions, tools.models, tools.output_models, tools.streaming, utils.code_context
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tools/implementations",
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
