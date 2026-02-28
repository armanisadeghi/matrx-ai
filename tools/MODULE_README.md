# `tools` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tools` |
| Last generated | 2026-02-28 13:39 |
| Output file | `tools/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tools --mode signatures \
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

> Auto-generated. 44 files across 5 directories.

```
tools/
├── MODULE_README.md
├── __init__.py
├── agent_tool.py
├── arg_models/
│   ├── __init__.py
│   ├── browser_args.py
│   ├── db_args.py
│   ├── fs_args.py
│   ├── math_args.py
│   ├── memory_args.py
│   ├── shell_args.py
│   ├── text_args.py
│   ├── web_args.py
├── browser_sessions.py
├── executor.py
├── external_mcp.py
├── guardrails.py
├── handle_tool_calls.py
├── implementations/
│   ├── __init__.py
│   ├── _summarize_helper.py
│   ├── browser.py
│   ├── code.py
│   ├── database.py
│   ├── filesystem.py
│   ├── math.py
│   ├── memory.py
│   ├── news.py
│   ├── personal_tables.py
│   ├── questionnaire.py
│   ├── seo.py
│   ├── shell.py
│   ├── text.py
│   ├── travel.py
│   ├── user_lists.py
│   ├── user_tables.py
│   ├── web.py
├── lifecycle.py
├── logger.py
├── models.py
├── output_models/
│   ├── __init__.py
│   ├── seo.py
├── registry.py
├── streaming.py
├── tests/
│   ├── mimic_model_tests.py
├── tools_db.py
# excluded: 4 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tools/__init__.py  [python]



---
Filepath: tools/agent_tool.py  [python]

  async def execute_agent_tool(tool_def: ToolDefinition, args: dict[str, Any], ctx: ToolContext) -> ToolResult
  async def register_agent_as_tool(prompt_id: str, tool_name: str, description: str, input_schema: dict[str, Any] | None = None, max_calls_per_conversation: int = 5, cost_cap_per_call: float = 1.0, timeout_seconds: float = 300.0) -> ToolDefinition


---
Filepath: tools/logger.py  [python]

  class ToolExecutionLogger:
      async def log_started(self, ctx: ToolContext, tool_def: ToolDefinition, arguments: dict[str, Any]) -> str
      async def log_completed(self, row_id: str, result: ToolResult, execution_events: list[dict[str, Any]] | None = None) -> None
      async def log_error(self, row_id: str, result: ToolResult, execution_events: list[dict[str, Any]] | None = None) -> None
      async def link_message(self, row_id: str, message_id: str) -> None
      async def backfill_message_id(self, call_id: str, conversation_id: str, message_id: str) -> None
      async def _update_row(self, row_id: str, data: dict[str, Any]) -> None
      def _truncate_arguments(arguments: dict[str, Any]) -> dict[str, Any]
      def _serialize_output(output: Any) -> tuple[str | None, str]
      def _aggregate_usage(result: ToolResult) -> tuple[int, int, float]


---
Filepath: tools/executor.py  [python]

  class ToolExecutor:
      def __init__(self, registry: ToolRegistryV2, guardrails: GuardrailEngine | None = None, execution_logger: ToolExecutionLogger | None = None, lifecycle: ToolLifecycleManager | None = None)
      def build_context(*, call_id: str, tool_name: str, iteration: int = 0, recursion_depth: int = 0, cost_budget_remaining: float | None = None, calls_remaining: int | None = None) -> ToolContext
      async def execute(self, tool_name: str, arguments: dict[str, Any], ctx: ToolContext) -> tuple[dict[str, Any], ToolResult]
      async def execute_batch(self, tool_calls: list[dict[str, Any]], ctx_base: ToolContext) -> tuple[list[dict[str, Any]], list[ToolResult]]
      async def _dispatch(self, tool_def: ToolDefinition, args: dict[str, Any], ctx: ToolContext, stream: ToolStreamManager) -> ToolResult
      async def _execute_local(self, tool_def: ToolDefinition, args: dict[str, Any], ctx: ToolContext, stream: ToolStreamManager) -> ToolResult
      async def _execute_external_mcp(self, tool_def: ToolDefinition, args: dict[str, Any], ctx: ToolContext) -> ToolResult
      async def _execute_agent(self, tool_def: ToolDefinition, args: dict[str, Any], ctx: ToolContext) -> ToolResult
      def _unknown_tool_result(tool_name: str, call_id: str, started_at: float) -> ToolResult


---
Filepath: tools/guardrails.py  [python]

  ToolCallLike = dict
  class _CallRecord:
  class GuardrailEngine:
      def __init__(self) -> None
      async def check(self, tool_name: str, arguments: dict, ctx: ToolContext, tool_def: ToolDefinition) -> GuardrailResult
      def record_call(self, tool_name: str, arguments: dict, ctx: ToolContext) -> None
      def clear_conversation(self, conversation_id: str) -> None
      def _check_duplicate(self, tool_name: str, arguments: dict, ctx: ToolContext) -> GuardrailResult
      def _check_rate_limit(self, tool_name: str, ctx: ToolContext, tool_def: ToolDefinition) -> GuardrailResult
      def _check_conversation_limit(self, tool_name: str, ctx: ToolContext, tool_def: ToolDefinition) -> GuardrailResult
      def _check_cost_budget(self, ctx: ToolContext, tool_def: ToolDefinition) -> GuardrailResult
      def _check_loop_detection(self, tool_name: str, arguments: dict, ctx: ToolContext) -> GuardrailResult
      def _check_recursion_depth(self, ctx: ToolContext, tool_def: ToolDefinition) -> GuardrailResult
      def _hash_args(arguments: dict) -> str
      def _similarity(hash_a: str, hash_b: str) -> float


---
Filepath: tools/tools_db.py  [python]

  class ToolsManager(ToolsBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)


---
Filepath: tools/registry.py  [python]

  class ToolRegistryV2:
      def __init__(self) -> None
      def get_instance(cls) -> ToolRegistryV2
      async def load_from_database(self) -> int
      def load_from_database_sync(self) -> int
      def _load_rows(self, rows: list[dict[str, Any]]) -> int
      def load_from_definitions(self, definitions: list[ToolDefinition]) -> int
      def register_local(self, name: str, func: Callable[..., Awaitable[Any]], description: str = '', category: str | None = None, tags: list[str] | None = None, **overrides: Any) -> ToolDefinition
      def register(self, tool_def: ToolDefinition) -> None
      def unregister(self, name: str) -> bool
      def get(self, name: str) -> ToolDefinition | None
      def get_provider_tools(self, tool_names: list[str], provider: str) -> list[dict[str, Any]]
      def list_tools(self, category: str | None = None, tags: list[str] | None = None, tool_type: ToolType | None = None, active_only: bool = True) -> list[ToolDefinition]
      def list_tool_names(self) -> list[str]
      def loaded(self) -> bool
      def count(self) -> int
      async def _fetch_tools_async() -> list[dict[str, Any]]
      def _fetch_tools_via_orm_sync() -> list[dict[str, Any]]
      def _row_to_definition(row: dict[str, Any]) -> ToolDefinition
      def _resolve_callable(function_path: str) -> Callable[..., Awaitable[Any]]
      def _pydantic_to_param_dict(model_cls: type[BaseModel]) -> dict[str, Any]
      async def register_mcp_server(self, server_url: str, server_name: str, mcp_client: Any | None = None) -> list[str]


---
Filepath: tools/external_mcp.py  [python]

  class ExternalMCPClient:
      def __init__(self, timeout: float = 120.0)
      async def discover_tools(self, server_url: str, auth: dict[str, Any] | None = None) -> list[ToolDefinition]
      async def call_tool(self, tool_def: ToolDefinition, args: dict[str, Any], ctx: ToolContext) -> ToolResult
      async def _send(self, server_url: str, payload: dict[str, Any], auth: dict[str, Any] | None = None) -> dict[str, Any]
      def _build_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]
      def _strip_namespace(name: str) -> str
      def _schema_to_params(input_schema: dict[str, Any]) -> dict[str, Any]


---
Filepath: tools/streaming.py  [python]

  class ToolStreamEvent(BaseModel):
      # fields: event: Literal['tool_started', 'tool_progress', 'tool_step', 'tool_result_preview', 'tool_completed', 'tool_error'], call_id: str, tool_name: str, timestamp: float = time(), message: str | None = None, show_spinner: bool = True, data: dict[str, Any] = dict()
  class ToolStreamManager:
      def __init__(self, emitter: Emitter | None, call_id: str, tool_name: str)
      async def emit(self, event: ToolStreamEvent) -> None
      async def started(self, message: str = 'Starting...', arguments: dict[str, Any] | None = None) -> None
      async def completed(self, message: str = 'Done', result: ToolResult | None = None) -> None
      async def error(self, message: str, error_type: str = 'execution') -> None
      async def progress(self, message: str, data: dict[str, Any] | None = None) -> None
      async def step(self, step_name: str, message: str, data: dict[str, Any] | None = None) -> None
      async def result_preview(self, preview: str) -> None
      def get_events_for_persistence(self) -> list[dict[str, Any]]


---
Filepath: tools/handle_tool_calls.py  [python]

  def get_executor() -> ToolExecutor
  async def initialize_tool_system() -> int
  def initialize_tool_system_sync() -> int
  async def handle_tool_calls_v2(tool_calls_raw: list[dict[str, Any]], *, iteration: int, recursion_depth: int = 0, cost_budget_remaining: float | None = None) -> tuple[list[dict[str, Any]], list['TokenUsage']]
  async def cleanup_conversation(conversation_id: str) -> None


---
Filepath: tools/browser_sessions.py  [python]

  SESSION_TTL_SECONDS = 300
  EVICTION_INTERVAL_SECONDS = 60
  class BrowserSession:
      async def close(self) -> None
  class BrowserSessionManager:
      def __init__(self) -> None
      def _ensure_eviction_task(self) -> None
      async def _eviction_loop(self) -> None
      async def create(self) -> BrowserSession
      async def get(self, session_id: str) -> BrowserSession | None
      async def close(self, session_id: str) -> None
      async def close_all(self) -> None
      async def evict_stale(self) -> None
      def active_count(self) -> int
      def session_ids(self) -> list[str]
  def get_browser_session_manager() -> BrowserSessionManager
  def _shutdown_browser_sessions() -> None


---
Filepath: tools/models.py  [python]

  CxToolCallStatus = Literal['pending', 'running', 'completed', 'error']
  class ToolType(StrEnum):
  class ToolError(BaseModel):
      # fields: error_type: str, message: str, traceback: str | None = None, is_retryable: bool = False, suggested_action: str | None = None
      def to_agent_message(self) -> str
  class ToolResult(BaseModel):
      # fields: success: bool, output: Any = None, error: ToolError | None = None, usage: dict[str, Any] | None = None, child_usages: list[TokenUsage] = list(), started_at: float = 0.0, completed_at: float = 0.0, duration_ms: int = 0, tool_name: str = '', call_id: str = '', retry_count: int = 0, should_persist_output: bool = False, persist_key: str | None = None
      def compute_duration(self) -> None
      def to_tool_result_content(self) -> dict[str, Any]
  class GuardrailResult(BaseModel):
      # fields: blocked: bool = False, reason: str | None = None, error_type: str = 'guardrail', suggested_action: str | None = None
      def to_tool_result_content(self, call_id: str = '', tool_name: str = '') -> dict[str, Any]
  class ToolContext(BaseModel):
      # fields: call_id: str, tool_name: str = '', iteration: int = 0, parent_agent_name: str | None = None, user_role: str = 'user', recursion_depth: int = 0, cost_budget_remaining: float | None = None, calls_remaining_this_conversation: int | None = None
      def user_id(self) -> str
      def conversation_id(self) -> str
      def request_id(self) -> str
      def emitter(self) -> Emitter | None
      def api_keys(self) -> dict[str, str]
      def project_id(self) -> str | None
      def organization_id(self) -> str | None
  class ToolDefinition(BaseModel):
      # fields: name: str, description: str = '', parameters: dict[str, Any] = dict(), output_schema: dict[str, Any] | None = None, annotations: list[dict[str, Any]] = list(), tool_type: ToolType = ToolType.LOCAL, function_path: str = '', category: str | None = None, tags: list[str] = list(), icon: str | None = None, is_active: bool = True, version: str = '1.0.0', prompt_id: str | None = None, mcp_server_url: str | None = None, mcp_server_auth: dict[str, Any] | None = None, max_calls_per_conversation: int | None = None, max_calls_per_minute: int | None = None, cost_cap_per_call: float | None = None, timeout_seconds: float = 120.0, max_recursion_depth: int = 3, on_call_message_template: str | None = None
      def _build_json_schema(self, *, strip_openai_unsupported: bool = False) -> dict[str, Any]
      def _process_nested(schema: dict[str, Any] | str, strip_unsupported: bool) -> dict[str, Any]
      def to_mcp_format(self) -> dict[str, Any]
      def to_openai_format(self) -> dict[str, Any]
      def to_openai_responses_format(self) -> dict[str, Any]
      def to_google_format(self) -> dict[str, Any]
      def to_anthropic_format(self) -> dict[str, Any]
      def get_provider_format(self, provider: str) -> dict[str, Any]
      def format_user_message(self, arguments: dict[str, Any]) -> str
  class CxToolCallRecord(BaseModel):
      # fields: id: str = lambda(), conversation_id: str, message_id: str | None = None, user_id: str, request_id: str | None = None, tool_name: str, tool_type: ToolType = ToolType.LOCAL, call_id: str, status: CxToolCallStatus = 'pending', arguments: dict[str, Any] = dict(), success: bool = True, output: str | None = None, output_type: str = 'text', is_error: bool = False, error_type: str | None = None, error_message: str | None = None, duration_ms: int = 0, started_at: datetime = lambda(), completed_at: datetime = lambda(), input_tokens: int = 0, output_tokens: int = 0, total_tokens: int = 0, cost_usd: float = 0.0, iteration: int = 0, retry_count: int = 0, parent_call_id: str | None = None, execution_events: list[dict[str, Any]] = list(), persist_key: str | None = None, file_path: str | None = None, metadata: dict[str, Any] = dict(), created_at: datetime = lambda(), deleted_at: datetime | None = None
  def _build(param_dict: dict[str, Any] | str) -> dict[str, Any]


---
Filepath: tools/lifecycle.py  [python]

  CleanupFn = Callable[[], Coroutine[Any, Any, None]]
  class ToolLifecycleManager:
      def __init__(self) -> None
      def get_instance(cls) -> ToolLifecycleManager
      def register_cleanup(self, conversation_id: str, cleanup_fn: CleanupFn) -> None
      def touch(self, conversation_id: str) -> None
      async def cleanup_conversation(self, conversation_id: str) -> int
      async def cleanup_idle(self) -> list[str]
      async def cleanup_all(self) -> int
      def sweep_running(self) -> bool
      def start_background_sweep(self) -> None
      def stop_background_sweep(self) -> None
      async def _sweep_loop(self) -> None
      def active_conversations(self) -> int
      def pending_cleanups(self) -> int


---
Filepath: tools/tests/mimic_model_tests.py  [python]

  COST_COMPARISON_MODELS = [3 items]
  CHARS_PER_TOKEN = 4
  def _estimate_cost_table(content: str) -> None
  def _build_ctx(tool_name: str, stream: bool = True) -> ToolContext
  def _get_tool_map() -> dict[str, Any]
  def _yline(char: str = '═', width: int = 80) -> str
  def _cline(char: str = '═', width: int = 80) -> str
  def _rline(char: str = '═', width: int = 80) -> str
  def _gline(char: str = '═', width: int = 80) -> str
  async def run_tool(tool_name: str, args: dict[str, Any], *, stream: bool = True, print_result: bool = True, use_db: bool | None = None) -> dict[str, Any]
  async def test_math_calculate()
  async def test_text_analyze()
  async def test_text_regex_extract()
  async def test_web_search()
  async def test_web_read()
  async def test_research_web()
  async def test_db_query()
  async def test_db_schema()
  async def test_memory_store()
  async def test_memory_recall()
  async def test_memory_search()
  async def test_fs_write_then_read()
  async def test_fs_list()
  async def test_fs_search()
  async def test_shell_execute()
  async def test_shell_python()
  async def test_browser_navigate()
  async def test_browser_screenshot()
  async def test_userlist_create_simple()
  async def test_userlist_get_all()
  async def test_seo_check_meta_titles()
  async def test_seo_check_meta_descriptions()
  async def test_code_store_html()
  async def test_code_fetch_code()
  async def test_code_fetch_tree()
  async def test_news_get_headlines()
  async def test_usertable_create()
  async def test_usertable_create_advanced()
  async def test_usertable_get_all()
  async def test_usertable_get_metadata()
  async def test_usertable_get_fields()
  async def test_usertable_get_data()
  async def test_usertable_search_data()
  async def test_usertable_add_rows()
  async def test_usertable_update_row()
  async def test_usertable_delete_row()
  async def test_interaction_ask()
  async def test_travel_get_location()
  async def test_travel_get_weather()
  async def test_travel_get_restaurants()
  async def test_travel_get_activities()
  async def test_travel_get_events()
  async def test_travel_create_summary()
  async def test_db_insert()
  async def test_db_update()
  async def test_memory_update()
  async def test_memory_forget()
  async def test_fs_mkdir()
  async def test_browser_click()
  async def test_browser_type_text()
  async def test_browser_full_session()
  async def test_seo_check_meta_tags_batch()
  async def test_seo_get_keyword_data()
  async def test_code_execute_python()
  async def test_code_execute_python_with_markers()
  async def test_userlist_create()
  async def test_userlist_get_details()
  async def test_userlist_update_item()
  async def test_userlist_batch_update()
  async def _run_interactive() -> None
  def _verify_tool_map_alignment() -> None
  def _parse(result: dict) -> dict
  def _session(result: dict) -> str
  def _ok(result: dict) -> bool


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


---
Filepath: tools/output_models/__init__.py  [python]



---
Filepath: tools/output_models/seo.py  [python]

  class MonthlySearchItem(BaseModel):
      # fields: year: int = 0, month: int = 0, search_volume: int = 0
  class SeoKeywordDataItem(BaseModel):
      # fields: keyword: str = '', cpc: float = 0.0, competition: str = '', search_volume: int = 0, competition_index: int = 0, monthly_searches: list[MonthlySearchItem] = list()
  class SeoKeywordDataOutput(BaseModel):
      # fields: keywords_data: list[SeoKeywordDataItem] = list(), total_keywords: int = 0, date_range: dict[str, str] = dict(), search_parameters: dict[str, Any] = dict()
  def normalize_keyword_item(raw: dict[str, Any]) -> SeoKeywordDataItem
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. Scoped to: `handle_tool_calls, executor, registry, guardrails`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: tools.executor

```
Global Scope → logging.getLogger(__name__) (line 19)
  tools.executor.__init__ → tools.executor.GuardrailEngine() (line 51)
  tools.executor.__init__ → tools.executor.ToolExecutionLogger() (line 52)
  tools.executor.__init__ → ToolLifecycleManager.get_instance() (line 53)
  tools.executor.build_context → tools.executor.ToolContext() (line 69)
  async tools.executor.execute → time.time() (line 96)
  async tools.executor.execute → ...get(tool_name) (line 99)
  async tools.executor.execute → ...list_tool_names() (line 107)
  async tools.executor.execute → result.to_tool_result_content() (line 113)
  async tools.executor.execute → ...log_started(ctx, tool_def, arguments) (line 116)
  async tools.executor.execute → tools.executor.ToolStreamManager(ctx.emitter, ctx.call_id, tool_name) (line 118)
  async tools.executor.execute → ...check(tool_name, arguments, ctx, tool_def) (line 121)
  async tools.executor.execute → tools.executor.ToolResult() (line 125)
  async tools.executor.execute → tools.executor.ToolError() (line 127)
  async tools.executor.execute → time.time() (line 133)
  async tools.executor.execute → error_result.compute_duration() (line 137)
  async tools.executor.execute → stream.error(guardrail_result.reason or 'Blocked', guardrail_result.error_type) (line 138)
  async tools.executor.execute → stream.get_events_for_persistence() (line 141)
  async tools.executor.execute → asyncio.create_task(self.execution_logger.log_error(row_id, error_result, events)) (line 142)
  async tools.executor.execute → ...log_error(row_id, error_result, events) (line 143)
  async tools.executor.execute → error_result.to_tool_result_content() (line 145)
  async tools.executor.execute → ...record_call(tool_name, arguments, ctx) (line 147)
  async tools.executor.execute → tool_def.format_user_message(arguments) (line 150)
  async tools.executor.execute → stream.started(user_message) (line 151)
  async tools.executor.execute → ...touch(ctx.conversation_id) (line 154)
  async tools.executor.execute → asyncio.wait_for(self._dispatch(tool_def, arguments, ctx, stream)) (line 158)
  async tools.executor.execute → tools.executor.ToolResult() (line 163)
  async tools.executor.execute → tools.executor.ToolError() (line 165)
  async tools.executor.execute → time.time() (line 172)
  async tools.executor.execute → tools.executor.ToolResult() (line 177)
  async tools.executor.execute → tools.executor.ToolError() (line 179)
  async tools.executor.execute → tb.format_exc() (line 182)
  async tools.executor.execute → time.time() (line 187)
  async tools.executor.execute → result.compute_duration() (line 192)
  async tools.executor.execute → stream.completed('Done') (line 196)
  async tools.executor.execute → stream.error(msg, result.error.error_type if result.error else 'execution') (line 199)
  async tools.executor.execute → stream.get_events_for_persistence() (line 204)
  async tools.executor.execute → asyncio.create_task(self.execution_logger.log_completed(row_id, result, events)) (line 206)
  async tools.executor.execute → ...log_completed(row_id, result, events) (line 207)
  async tools.executor.execute → asyncio.create_task(self.execution_logger.log_error(row_id, result, events)) (line 210)
  async tools.executor.execute → ...log_error(row_id, result, events) (line 210)
  async tools.executor.execute → result.to_tool_result_content() (line 212)
  async tools.executor.execute_batch → tc.get('name', '') (line 232)
  async tools.executor.execute_batch → tc.get('arguments', {}) (line 233)
  async tools.executor.execute_batch → tc.get('call_id') (line 234)
  async tools.executor.execute_batch → tc.get('id') (line 234)
  async tools.executor.execute_batch → ctx_base.model_copy() (line 236)
  async tools.executor.execute_batch → tasks.append(self.execute(name, arguments, child_ctx)) (line 242)
  async tools.executor.execute_batch → self.execute(name, arguments, child_ctx) (line 242)
  async tools.executor.execute_batch → asyncio.gather(*tasks) (line 244)
  async tools.executor.execute_batch → tc.get('call_id') (line 252)
  async tools.executor.execute_batch → tc.get('id') (line 252)
  async tools.executor.execute_batch → tools.executor.ToolResult() (line 253)
  async tools.executor.execute_batch → tools.executor.ToolError() (line 255)
  async tools.executor.execute_batch → tb.format_exc() (line 258)
  async tools.executor.execute_batch → time.time() (line 260)
  async tools.executor.execute_batch → time.time() (line 261)
  async tools.executor.execute_batch → tc.get('name', '') (line 262)
  async tools.executor.execute_batch → content_results.append(err_result.to_tool_result_content()) (line 265)
  async tools.executor.execute_batch → err_result.to_tool_result_content() (line 265)
  async tools.executor.execute_batch → full_results.append(err_result) (line 266)
  async tools.executor.execute_batch → content_results.append(content_dict) (line 269)
  async tools.executor.execute_batch → full_results.append(full_result) (line 270)
  async tools.executor._dispatch → tools.executor.ToolResult() (line 293)
  async tools.executor._dispatch → tools.executor.ToolError() (line 295)
  async tools.executor._dispatch → time.time() (line 299)
  async tools.executor._dispatch → time.time() (line 300)
  async tools.executor._execute_local → tools.executor.ToolResult() (line 314)
  async tools.executor._execute_local → tools.executor.ToolError() (line 316)
  async tools.executor._execute_local → time.time() (line 320)
  async tools.executor._execute_local → time.time() (line 321)
  async tools.executor._execute_local → time.time() (line 326)
  async tools.executor._execute_local → tools.executor.func(args, ctx) (line 327)
  async tools.executor._execute_local → time.time() (line 331)
  async tools.executor._execute_local → raw_result.get('status') (line 338)
  async tools.executor._execute_local → tools.executor.ToolResult() (line 339)
  async tools.executor._execute_local → raw_result.get('result') (line 342)
  async tools.executor._execute_local → raw_result.get('error', raw_result.get('result')) (line 344)
  async tools.executor._execute_local → raw_result.get('result') (line 344)
  async tools.executor._execute_local → tools.executor.ToolError() (line 346)
  async tools.executor._execute_local → raw_result.get('error', raw_result.get('result', '')) (line 348)
  async tools.executor._execute_local → raw_result.get('result', '') (line 348)
  async tools.executor._execute_local → time.time() (line 353)
  async tools.executor._execute_local → tools.executor.ToolResult() (line 358)
  async tools.executor._execute_local → time.time() (line 362)
  async tools.executor._execute_external_mcp → tools.executor.ExternalMCPClient() (line 375)
  async tools.executor._execute_external_mcp → client.call_tool(tool_def, args, ctx) (line 376)
  async tools.executor._execute_agent → ctx.model_copy() (line 386)
  async tools.executor._execute_agent → tools.executor.execute_agent_tool(tool_def, args, child_ctx) (line 391)
  tools.executor._unknown_tool_result → tools.executor.ToolResult() (line 401)
  tools.executor._unknown_tool_result → tools.executor.ToolError() (line 403)
  tools.executor._unknown_tool_result → time.time() (line 409)
```

### Call graph: tools.guardrails

```
Global Scope → logging.getLogger(__name__) (line 12)
  async tools.guardrails.check → tools.guardrails.GuardrailResult() (line 60)
  tools.guardrails.record_call → append(_CallRecord(tool_name=tool_name, args_hash=self._hash_args(arguments), timestamp=time.time(), iteration=ctx.iteration)) (line 63)
  tools.guardrails.record_call → tools.guardrails._CallRecord() (line 64)
  tools.guardrails.record_call → time.time() (line 67)
  tools.guardrails.clear_conversation → ...pop(conversation_id, None) (line 73)
  tools.guardrails._check_duplicate → ...get(ctx.conversation_id, []) (line 85)
  tools.guardrails._check_duplicate → tools.guardrails.GuardrailResult() (line 90)
  tools.guardrails._check_duplicate → tools.guardrails.GuardrailResult() (line 96)
  tools.guardrails._check_rate_limit → tools.guardrails.GuardrailResult() (line 105)
  tools.guardrails._check_rate_limit → time.time() (line 107)
  tools.guardrails._check_rate_limit → ...get(ctx.conversation_id, []) (line 108)
  tools.guardrails._check_rate_limit → tools.guardrails.GuardrailResult() (line 116)
  tools.guardrails._check_rate_limit → tools.guardrails.GuardrailResult() (line 122)
  tools.guardrails._check_conversation_limit → tools.guardrails.GuardrailResult() (line 131)
  tools.guardrails._check_conversation_limit → ...get(ctx.conversation_id, []) (line 133)
  tools.guardrails._check_conversation_limit → tools.guardrails.GuardrailResult() (line 137)
  tools.guardrails._check_conversation_limit → tools.guardrails.GuardrailResult() (line 143)
  tools.guardrails._check_cost_budget → tools.guardrails.GuardrailResult() (line 151)
  tools.guardrails._check_cost_budget → tools.guardrails.GuardrailResult() (line 163)
  tools.guardrails._check_cost_budget → tools.guardrails.GuardrailResult() (line 172)
  tools.guardrails._check_loop_detection → ...get(ctx.conversation_id, []) (line 180)
  tools.guardrails._check_loop_detection → tools.guardrails.GuardrailResult() (line 184)
  tools.guardrails._check_loop_detection → tools.guardrails.GuardrailResult() (line 192)
  tools.guardrails._check_loop_detection → tools.guardrails.GuardrailResult() (line 204)
  tools.guardrails._check_recursion_depth → tools.guardrails.GuardrailResult() (line 214)
  tools.guardrails._check_recursion_depth → tools.guardrails.GuardrailResult() (line 223)
  tools.guardrails._hash_args → json.dumps(arguments) (line 231)
  tools.guardrails._hash_args → hexdigest() (line 232)
  tools.guardrails._hash_args → hashlib.md5(normalized.encode()) (line 232)
  tools.guardrails._hash_args → normalized.encode() (line 232)
```

### Call graph: tools.registry

```
tools.registry.get_instance → tools.registry.cls() (line 34)
  tools.registry._load_rows → row.get('name', '?') (line 69)
  tools.registry._load_rows → failed.append(tool_name) (line 77)
  tools.registry._load_rows → row.get('function_path', '') (line 81)
  tools.registry._load_rows → traceback.format_exc() (line 83)
  tools.registry.load_from_definitions → traceback.format_exc() (line 108)
  tools.registry.register_local → inspect.signature(func) (line 138)
  tools.registry.register_local → ...values() (line 139)
  tools.registry.register_local → overrides.pop('parameters', {}) (line 141)
  tools.registry.register_local → tools.registry.issubclass(annotation, BaseModel) (line 147)
  tools.registry.register_local → tools.registry.ToolDefinition() (line 154)
  tools.registry.unregister → ...pop(name, None) (line 173)
  tools.registry.get → ...get(name) (line 180)
  tools.registry.get_provider_tools → ...keys() (line 204)
  tools.registry.get_provider_tools → get_provider_format(provider) (line 212)
  tools.registry.list_tools → ...values() (line 225)
  tools.registry.list_tools → issubset(set(t.tags)) (line 230)
  tools.registry.list_tools → result.append(t) (line 234)
  tools.registry.list_tool_names → ...keys() (line 238)
  async tools.registry._fetch_tools_async → tools_manager.filter_tool() (line 255)
  async tools.registry._fetch_tools_async → item.to_dict() (line 256)
  async tools.registry._fetch_tools_async → traceback.format_exc() (line 261)
  tools.registry._fetch_tools_via_orm_sync → tools_manager.filter_items_sync() (line 271)
  tools.registry._fetch_tools_via_orm_sync → item.to_dict() (line 273)
  tools.registry._fetch_tools_via_orm_sync → traceback.format_exc() (line 279)
  tools.registry._row_to_definition → row.get('function_path', '') (line 289)
  tools.registry._row_to_definition → function_path.startswith('agent:') (line 292)
  tools.registry._row_to_definition → function_path.split(':', 1) (line 294)
  tools.registry._row_to_definition → function_path.startswith('mcp:') (line 295)
  tools.registry._row_to_definition → row.get('annotations') (line 298)
  tools.registry._row_to_definition → guardrail_config.update(ann) (line 303)
  tools.registry._row_to_definition → row.get('parameters') (line 305)
  tools.registry._row_to_definition → raw_params.get('type') (line 308)
  tools.registry._row_to_definition → raw_params.get('required', []) (line 312)
  tools.registry._row_to_definition → params.items() (line 313)
  tools.registry._row_to_definition → tools.registry.ToolDefinition() (line 319)
  tools.registry._row_to_definition → row.get('description', '') (line 321)
  tools.registry._row_to_definition → row.get('output_schema') (line 323)
  tools.registry._row_to_definition → row.get('annotations') (line 324)
  tools.registry._row_to_definition → row.get('category') (line 327)
  tools.registry._row_to_definition → row.get('tags') (line 328)
  tools.registry._row_to_definition → row.get('icon') (line 329)
  tools.registry._row_to_definition → row.get('is_active', True) (line 330)
  tools.registry._row_to_definition → row.get('version', '1.0.0') (line 331)
  tools.registry._row_to_definition → guardrail_config.get('max_calls_per_conversation') (line 333)
  tools.registry._row_to_definition → guardrail_config.get('max_calls_per_minute') (line 336)
  tools.registry._row_to_definition → guardrail_config.get('cost_cap_per_call') (line 337)
  tools.registry._row_to_definition → guardrail_config.get('timeout_seconds', 120.0) (line 338)
  tools.registry._resolve_callable → function_path.startswith('agent:') (line 345)
  tools.registry._resolve_callable → function_path.startswith('mcp:') (line 346)
  tools.registry._resolve_callable → function_path.startswith('ai.') (line 349)
  tools.registry._resolve_callable → function_path.rsplit('.', 1) (line 351)
  tools.registry._resolve_callable → importlib.import_module(module_path) (line 352)
  tools.registry._pydantic_to_param_dict → model_cls.model_json_schema() (line 359)
  tools.registry._pydantic_to_param_dict → schema.get('required', []) (line 361)
  tools.registry._pydantic_to_param_dict → schema.get('properties', {}) (line 362)
  tools.registry._pydantic_to_param_dict → properties.items() (line 364)
  tools.registry._pydantic_to_param_dict → field_schema.get('type', 'string') (line 366)
  tools.registry._pydantic_to_param_dict → field_schema.get('description', '') (line 367)
  async tools.registry.register_mcp_server → tools.registry.ExternalMCPClient() (line 399)
  async tools.registry.register_mcp_server → mcp_client.discover_tools(server_url) (line 401)
  async tools.registry.register_mcp_server → registered.append(namespaced) (line 409)
```

### Call graph: tools.handle_tool_calls

```
Global Scope → logging.getLogger(__name__) (line 30)
  tools.handle_tool_calls.get_executor → ToolRegistryV2.get_instance() (line 39)
  tools.handle_tool_calls.get_executor → tools.handle_tool_calls.ToolExecutor() (line 51)
  tools.handle_tool_calls.get_executor → tools.handle_tool_calls.GuardrailEngine() (line 53)
  tools.handle_tool_calls.get_executor → tools.handle_tool_calls.ToolExecutionLogger() (line 54)
  tools.handle_tool_calls.get_executor → ToolLifecycleManager.get_instance() (line 55)
  async tools.handle_tool_calls.initialize_tool_system → ToolRegistryV2.get_instance() (line 65)
  async tools.handle_tool_calls.initialize_tool_system → registry.load_from_database() (line 66)
  async tools.handle_tool_calls.initialize_tool_system → tools.handle_tool_calls.get_executor() (line 77)
  async tools.handle_tool_calls.initialize_tool_system → ToolLifecycleManager.get_instance() (line 79)
  async tools.handle_tool_calls.initialize_tool_system → lifecycle.start_background_sweep() (line 80)
  tools.handle_tool_calls.initialize_tool_system_sync → ToolRegistryV2.get_instance() (line 91)
  tools.handle_tool_calls.initialize_tool_system_sync → registry.load_from_database_sync() (line 92)
  tools.handle_tool_calls.initialize_tool_system_sync → tools.handle_tool_calls.get_executor() (line 105)
  async tools.handle_tool_calls.handle_tool_calls_v2 → tools.handle_tool_calls.get_executor() (line 127)
  async tools.handle_tool_calls.handle_tool_calls_v2 → ToolLifecycleManager.get_instance() (line 129)
  async tools.handle_tool_calls.handle_tool_calls_v2 → lifecycle.start_background_sweep() (line 131)
  async tools.handle_tool_calls.handle_tool_calls_v2 → tools.handle_tool_calls.ToolContext() (line 133)
  async tools.handle_tool_calls.handle_tool_calls_v2 → executor.execute_batch(tool_calls_raw, ctx) (line 141)
  async tools.handle_tool_calls.handle_tool_calls_v2 → all_child_usages.extend(result.child_usages) (line 145)
  async tools.handle_tool_calls.cleanup_conversation → ToolLifecycleManager.get_instance() (line 152)
  async tools.handle_tool_calls.cleanup_conversation → lifecycle.cleanup_conversation(conversation_id) (line 153)
  async tools.handle_tool_calls.cleanup_conversation → tools.handle_tool_calls.get_executor() (line 155)
  async tools.handle_tool_calls.cleanup_conversation → guardrails.clear_conversation(conversation_id) (line 156)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-generated. Shows which files import and call the listed entry points.
> Update `ENTRY_POINTS` in `generate_readme.py` to control which functions are tracked.

| Caller | Calls |
|--------|-------|
| `orchestrator/executor.py` | `handle_tool_calls_v2()` |
| `app/main.py` | `initialize_tool_system()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** aidream, api_management, common, httpx, initialize_systems, matrx_orm, matrx_utils, playwright, pydantic, requests, rich, scraper, seo, user_data
**Internal modules:** agents.definition, config, config.unified_config, config.usage_config, context.app_context, context.emitter_protocol, db.custom, db.managers, utils.code_context
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tools",
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
