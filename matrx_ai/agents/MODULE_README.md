# `agents` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `agents` |
| Last generated | 2026-03-01 00:09 |
| Output file | `agents/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py agents --mode signatures
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

> Auto-generated. 12 files across 2 directories.

```
agents/
├── MODULE_README.md
├── __init__.py
├── cache.py
├── definition.py
├── manager.py
├── resolver.py
├── tests/
│   ├── agent_example.py
│   ├── agent_test.py
│   ├── new_agent_test.py
│   ├── test_variable_application.py
├── types.py
├── variables.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: agents/__init__.py  [python]

  def __getattr__(name: str)


---
Filepath: agents/cache.py  [python]

  class AgentCache:
      def get(cls, conversation_id: str) -> Agent | None
      def set(cls, conversation_id: str, agent: Agent) -> None
      def set_warm(cls, conversation_id: str, agent: Agent) -> None
      def remove(cls, conversation_id: str) -> None
      def exists(cls, conversation_id: str) -> bool
      def clear(cls) -> None


---
Filepath: agents/resolver.py  [python]

  class ConversationResolver:
      async def from_conversation_id(conversation_id: str, user_input: str | list[dict[str, Any]] | None = None, config_overrides: dict[str, Any] | None = None) -> UnifiedConfig
      async def warm(conversation_id: str) -> bool
  class AgentConfigResolver:
      async def from_id(agent_id: str, variables: dict[str, Any] | None = None, overrides: dict[str, Any] | None = None) -> UnifiedConfig
      async def warm(agent_id: str) -> bool


---
Filepath: agents/manager.py  [python]

  class PromptType(StrEnum):
  class PromptsManager(PromptsBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def to_config(self, prompt_id: str) -> AgentConfig
  class PromptBuiltinsManager(PromptBuiltinsBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def to_config(self, builtin_id: str) -> AgentConfig
  class PromptManagers:
      def __new__(cls) -> PromptManagers
      def __init__(self) -> None
      def _cache(self, item_id: str, ptype: PromptType) -> None
      def get_type(self, prompt_id: str) -> PromptType | None
      def cache_size(self) -> int
      async def hydrate_builtins(self) -> int
      def hydrate_builtins_sync(self) -> int
      async def get_config(self, prompt_id: str) -> AgentConfig
      async def get_prompt_config(self, prompt_id: str) -> AgentConfig
      async def get_builtin_config(self, builtin_id: str) -> AgentConfig
      async def _prompt_config(self, prompt_id: str) -> AgentConfig
      async def _builtin_config(self, builtin_id: str) -> AgentConfig
      async def load_prompt(self, prompt_id: str) -> Prompts
      async def load_prompt_or_none(self, prompt_id: str) -> Prompts | None
      async def find_prompts(self, **kwargs: Any) -> list[Prompts]
      async def create_prompt(self, **data: Any) -> Prompts
      async def load_builtin(self, builtin_id: str) -> PromptBuiltins
      async def load_builtin_or_none(self, builtin_id: str) -> PromptBuiltins | None
      async def find_builtins(self, **kwargs: Any) -> list[PromptBuiltins]
      async def create_builtin(self, **data: Any) -> PromptBuiltins
      async def load_by_id(self, item_id: str) -> Prompts | PromptBuiltins
      async def load_by_id_or_none(self, item_id: str) -> Prompts | PromptBuiltins | None


---
Filepath: agents/variables.py  [python]

  class AgentVariable(BaseModel):
      # fields: name: str, value: str | None = None, default_value: str | None = None, required: bool = False, help_text: str | None = None
      def get_value(self) -> str
      def from_dict(cls, var_def: dict[str, Any]) -> 'AgentVariable'
      def from_list(var_defs: list | None) -> dict[str, 'AgentVariable']
      def to_dict(self) -> dict[str, Any]


---
Filepath: agents/types.py  [python]

  class AgentConfig:


---
Filepath: agents/definition.py  [python]

  class AgentExecuteResult:
  class Agent:
      def __init__(self, config: UnifiedConfig, variable_defaults: dict[str, AgentVariable] | None = None, name: str | None = None)
      def clone(self) -> Agent
      def clone_with_variables(self, **variables) -> Agent
      def clone_with_overrides(self, **overrides) -> Agent
      def clone_with(self, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None) -> Agent
      def set_variable(self, name: str, value: Any) -> Agent
      def set_variables(self, **variables) -> Agent
      def apply_variables(self, force: bool = False) -> Agent
      def with_variables(self, **variables) -> Agent
      def apply_config_overrides(self, **overrides) -> Agent
      def from_dict(cls, config_dict: dict[str, Any], variable_defaults: dict[str, AgentVariable] | None = None, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None) -> Agent
      def _build_from_config(cls, agent_config: AgentConfig, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None) -> Agent
      async def from_id(cls, prompt_id: str, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None) -> Agent
      async def from_prompt(cls, prompt_id: str, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None) -> Agent
      async def from_builtin(cls, builtin_id: str, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None) -> Agent
      def set_user_input(self, user_input: str | list[dict[str, Any]]) -> Agent
      async def execute(self, user_input: str | list[dict[str, Any]] | None = None) -> AgentExecuteResult
      def _clean_up_response(self, response: CompletedRequest) -> AgentExecuteResult
      def to_dict(self) -> dict[str, Any]


---
Filepath: agents/tests/agent_test.py  [python]

  async def test_1_basic_execution()
  async def test_2_oneshot_execution()
  async def test_3_partial_variables()
  async def test_4_user_input_handling()
  async def test_5_callable_syntax()
  async def test_6_chaining()
  async def test_7_multi_turn_conversation()
  async def test_8_workflow_pattern()
  async def test_9_emitter()
  async def test_10_not_ready_error()
  async def main()


---
Filepath: agents/tests/test_variable_application.py  [python]

  async def test_variable_application()


---
Filepath: agents/tests/agent_example.py  [python]

  async def example_1_basic_usage()
  async def example_2_chainable_api()
  async def example_3_multiple_variables()
  async def example_4_initialization_with_values()
  async def example_5_clone_and_modify()
  async def main()


---
Filepath: agents/tests/new_agent_test.py  [python]

  async def direct_news_agent_test()
  async def test_1_basic_execution()
  async def test_1B_basic_execution_with_parent_conversation()
  async def test_2_with_second_message()
  async def test_3_with_config_overrides()
  async def test_4_clone_with_different_models()
  async def scrape_research_condenser_agent_1(instructions, scraped_content, queries, search_results, emitter = None)
  async def test_scrape_research_condenser_agent_1()
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** aidream, fastapi, initialize_systems, matrx_utils, pydantic, scraper
**Internal modules:** config, config.unified_config, config.usage_config, context.app_context, db.custom, db.managers, db.models, orchestrator.executor, orchestrator.requests, utils.cache
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "agents",
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
| `agent_runners/research.py` | `Agent()` |
| `app/core/ai_task.py` | `Agent()` |
| `tools/agent_tool.py` | `Agent()` |
| `tools/implementations/_summarize_helper.py` | `Agent()` |
| `app/core/ai_task.py` | `AgentCache()` |
| `app/routers/agent.py` | `AgentConfigResolver()` |
| `app/routers/conversation.py` | `ConversationResolver()` |
<!-- /AUTO:callers -->
