# `` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `` |
| Last generated | 2026-03-01 00:14 |
| Output file | `MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`agent_runners/MODULE_README.md`](agent_runners/MODULE_README.md) | last generated 2026-02-28 13:39 |
| [`agents/MODULE_README.md`](agents/MODULE_README.md) | last generated 2026-03-01 00:09 |
| [`app/MODULE_README.md`](app/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`config/MODULE_README.md`](config/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`context/MODULE_README.md`](context/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`db/MODULE_README.md`](db/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`instructions/MODULE_README.md`](instructions/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`media/MODULE_README.md`](media/MODULE_README.md) | last generated 2026-02-28 13:39 |
| [`orchestrator/MODULE_README.md`](orchestrator/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`processing/MODULE_README.md`](processing/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`providers/MODULE_README.md`](providers/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`scripts/MODULE_README.md`](scripts/MODULE_README.md) | last generated 2026-02-28 13:39 |
| [`tests/MODULE_README.md`](tests/MODULE_README.md) | last generated 2026-03-01 00:14 |
| [`tools/MODULE_README.md`](tools/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`utils/MODULE_README.md`](utils/MODULE_README.md) | last generated 2026-02-28 13:39 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py  --mode signatures
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

> Auto-generated. 229 files across 47 directories.

```
./
├── .dockerignore
├── .python-version
├── MODULE_README.md
├── agent_runners/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── research.py
├── agents/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── cache.py
│   ├── definition.py
│   ├── manager.py
│   ├── resolver.py
│   ├── tests/
│   │   ├── agent_example.py
│   │   ├── agent_test.py
│   │   ├── new_agent_test.py
│   │   ├── test_variable_application.py
│   ├── types.py
│   ├── variables.py
├── app/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ai_task.py
│   │   ├── cancellation.py
│   │   ├── exceptions.py
│   │   ├── middleware.py
│   │   ├── response.py
│   │   ├── sentry.py
│   │   ├── streaming.py
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py
│   ├── main.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── health.py
│   │   ├── tool.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── health.py
│   │   ├── tool.py
├── config/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── config_utils.py
│   ├── enums.py
│   ├── extra_config.py
│   ├── finish_reason.py
│   ├── media_config.py
│   ├── message_config.py
│   ├── thinking_config.py
│   ├── tools_config.py
│   ├── unified_config.py
│   ├── unified_content.py
│   ├── usage_config.py
├── context/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── app_context.py
│   ├── console_emitter.py
│   ├── emitter_protocol.py
│   ├── events.py
│   ├── stream_emitter.py
├── db/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── custom/
│   │   ├── __init__.py
│   │   ├── ai_model_manager.py
│   │   ├── ai_models/
│   │   │   ├── __init__.py
│   │   │   ├── ai_model_base.py
│   │   │   ├── ai_model_dto.py
│   │   │   ├── ai_model_manager.py
│   │   │   ├── ai_model_validator.py
│   │   ├── conversation_gate.py
│   │   ├── conversation_rebuild.py
│   │   ├── cx_managers.py
│   │   ├── persistence.py
│   │   ├── tests/
│   │   │   ├── ai_model_tests.py
│   │   │   ├── cx_manager_tests.py
│   ├── generate.py
│   ├── helpers/
│   │   ├── auto_config.py
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── ai_model.py
│   │   ├── ai_provider.py
│   │   ├── content_blocks.py
│   │   ├── cx_agent_memory.py
│   │   ├── cx_conversation.py
│   │   ├── cx_media.py
│   │   ├── cx_message.py
│   │   ├── cx_request.py
│   │   ├── cx_tool_call.py
│   │   ├── cx_user_request.py
│   │   ├── prompt_builtins.py
│   │   ├── prompts.py
│   │   ├── shortcut_categories.py
│   │   ├── table_data.py
│   │   ├── tools.py
│   │   ├── user_tables.py
│   ├── models.py
│   ├── run_migrations.py
├── entrypoint.sh
├── instructions/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── content_blocks_manager.py
│   ├── core.py
│   ├── matrx_fetcher.py
│   ├── pattern_parser.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── direct_fetch_test.py
│   │   ├── instruction_builder_test.py
│   │   ├── integration_test.py
│   │   ├── simple_variable_example.py
│   │   ├── user_table_data_test.py
│   │   ├── variable_recognition_test.py
├── matrx_ai.egg-info/
│   ├── PKG-INFO
├── media/
│   ├── MODULE_README.md
├── orchestrator/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── executor.py
│   ├── recovery_logic.py
│   ├── requests.py
│   ├── tracking.py
├── processing/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_preprocessing.py
│   │   ├── audio_support.py
│   │   ├── groq_transcription.py
│   │   ├── transcription_cache.py
├── providers/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── anthropic/
│   │   ├── __init__.py
│   │   ├── anthropic_api.py
│   │   ├── translator.py
│   ├── cerebras/
│   │   ├── __init__.py
│   │   ├── cerebras_api.py
│   │   ├── translator.py
│   ├── errors.py
│   ├── google/
│   │   ├── __init__.py
│   │   ├── google_api.py
│   │   ├── translator.py
│   ├── groq/
│   │   ├── __init__.py
│   │   ├── groq_api.py
│   │   ├── translator.py
│   ├── openai/
│   │   ├── __init__.py
│   │   ├── openai_api.py
│   │   ├── translator.py
│   ├── together/
│   │   ├── __init__.py
│   │   ├── together_api.py
│   │   ├── translator.py
│   ├── unified_client.py
│   ├── xai/
│   │   ├── __init__.py
│   │   ├── translator.py
│   │   ├── xai_api.py
├── scripts/
│   ├── MODULE_README.md
│   ├── _rewrite_imports.py
│   ├── _test_new_imports.py
├── tests/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── execution_test.py
│   │   ├── groq_transcription_test.py
│   │   ├── small_test.py
│   │   ├── test_context.py
│   │   ├── test_error_handling.py
│   │   ├── test_translations.py
│   ├── db-pull-push/
│   │   ├── message-rebuild.py
│   ├── openai/
│   │   ├── __init__.py
│   │   ├── background_stream_async.py
│   │   ├── conversation_id_test.py
│   │   ├── openai_function_test.py
│   │   ├── openai_image_input.py
│   │   ├── openai_small_tests.py
│   │   ├── openai_translation_test.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── agent_comparison.py
│   │   ├── prompt_to_config.py
│   │   ├── test_basic_prompts.py
│   ├── random/
│   │   ├── print_test.py
│   ├── util_tests/
│   │   ├── readme_updates.py
├── tools/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── agent_tool.py
│   ├── arg_models/
│   │   ├── __init__.py
│   │   ├── browser_args.py
│   │   ├── db_args.py
│   │   ├── fs_args.py
│   │   ├── math_args.py
│   │   ├── memory_args.py
│   │   ├── shell_args.py
│   │   ├── text_args.py
│   │   ├── web_args.py
│   ├── browser_sessions.py
│   ├── executor.py
│   ├── external_mcp.py
│   ├── guardrails.py
│   ├── handle_tool_calls.py
│   ├── implementations/
│   │   ├── __init__.py
│   │   ├── _summarize_helper.py
│   │   ├── browser.py
│   │   ├── code.py
│   │   ├── database.py
│   │   ├── filesystem.py
│   │   ├── math.py
│   │   ├── memory.py
│   │   ├── news.py
│   │   ├── personal_tables.py
│   │   ├── questionnaire.py
│   │   ├── seo.py
│   │   ├── shell.py
│   │   ├── text.py
│   │   ├── travel.py
│   │   ├── user_lists.py
│   │   ├── user_tables.py
│   │   ├── web.py
│   ├── lifecycle.py
│   ├── logger.py
│   ├── models.py
│   ├── output_models/
│   │   ├── __init__.py
│   │   ├── seo.py
│   ├── registry.py
│   ├── streaming.py
│   ├── tests/
│   │   ├── mimic_model_tests.py
│   ├── tools_db.py
├── utils/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── cache.py
# excluded: 35 .md, 7 .json, 4 (no ext), 4 .txt, 1 .example, 1 .toml, 1 .lock, 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: .dockerignore  [unknown ()]

  # signature extraction not supported for this language



---
Filepath: .python-version  [unknown ()]

  # signature extraction not supported for this language



---
Filepath: entrypoint.sh  [unknown (.sh)]

  # signature extraction not supported for this language



---
Filepath: matrx_ai.egg-info/PKG-INFO  [unknown ()]

  # signature extraction not supported for this language



---
Submodule: tests/  [22 files — full detail in tests/MODULE_README.md]

---
Submodule: scripts/  [2 files — full detail in scripts/MODULE_README.md]

---
Submodule: instructions/  [12 files — full detail in instructions/MODULE_README.md]

---
Submodule: agents/  [11 files — full detail in agents/MODULE_README.md]

---
Submodule: context/  [6 files — full detail in context/MODULE_README.md]

---
Submodule: providers/  [24 files — full detail in providers/MODULE_README.md]

---
Submodule: utils/  [2 files — full detail in utils/MODULE_README.md]

---
Submodule: config/  [12 files — full detail in config/MODULE_README.md]

---
Submodule: orchestrator/  [5 files — full detail in orchestrator/MODULE_README.md]

---
Submodule: agent_runners/  [2 files — full detail in agent_runners/MODULE_README.md]

---
Submodule: db/  [35 files — full detail in db/MODULE_README.md]

---
Submodule: tools/  [43 files — full detail in tools/MODULE_README.md]

---
Submodule: processing/  [6 files — full detail in processing/MODULE_README.md]

---
Submodule: app/  [27 files — full detail in app/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Covered submodules shown as stubs — see child READMEs for full detail: `agent_runners`, `agents`, `app`, `config`, `context`, `db`, `instructions`, `media`, `orchestrator`, `processing`, `providers`, `scripts`, `tests`, `tools`, `utils`
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: scripts._rewrite_imports

> Full detail in [`scripts/MODULE_README.md`](scripts/MODULE_README.md)

```
`Global Scope → scripts._rewrite_imports.Path(__file__) (line 13)` → ... → `scripts._rewrite_imports.main() (line 241)`
```

### Call graph: scripts._test_new_imports

> Full detail in [`scripts/MODULE_README.md`](scripts/MODULE_README.md)

```
`Global Scope → scripts._test_new_imports.Path(__file__) (line 8)` → ... → `scripts._test_new_imports.main() (line 77)`
```

### Call graph: instructions.matrx_fetcher

> Full detail in [`instructions/MODULE_README.md`](instructions/MODULE_README.md)

```
`instructions.matrx_fetcher.is_valid_uuid → uuid.UUID(str(value)) (line 17)` → ... → `MatrxFetcher.process_text_with_patterns(test_text, patterns) (line 234)`
```

### Call graph: instructions.content_blocks_manager

> Full detail in [`instructions/MODULE_README.md`](instructions/MODULE_README.md)

```
`instructions.content_blocks_manager.is_valid_uuid → uuid.UUID(str(value)) (line 11)` → ... → `instructions.content_blocks_manager.get_content_blocks_manager() (line 144)`
```

### Call graph: instructions.core

> Full detail in [`instructions/MODULE_README.md`](instructions/MODULE_README.md)

```
`Global Scope → instructions.core.field() (line 16)` → ... → `instructions.core.cls() (line 200)`
```

### Call graph: instructions.pattern_parser

> Full detail in [`instructions/MODULE_README.md`](instructions/MODULE_README.md)

```
`Global Scope → re.compile('<<MATRX>><<([^>]+)>><<([^>]+)>>((?:(?!<<FIELDS>>|<</MATRX>>).)*?)(?:<<FIELDS>>([^<]+))?<</MATRX>>', re.DOTALL | re.MULTILINE) (line 49)` → ... → `MatrxFetcher.process_text_with_patterns(text, patterns) (line 253)`
```

### Call graph: agents.cache

> Full detail in [`agents/MODULE_README.md`](agents/MODULE_README.md)

```
`Global Scope → agents.cache.TTLCache() (line 15)` → ... → `_warm_cache.clear() (line 55)`
```

### Call graph: agents.resolver

> Full detail in [`agents/MODULE_README.md`](agents/MODULE_README.md)

```
`async agents.resolver.from_conversation_id → AgentCache.get(conversation_id) (line 70)` → ... → `Agent.from_id(agent_id) (line 195)`
```

### Call graph: agents.manager

> Full detail in [`agents/MODULE_README.md`](agents/MODULE_README.md)

```
`async agents.manager.to_config → self.load_prompts_by_id(prompt_id) (line 34)` → ... → `agents.manager.PromptManagers() (line 280)`
```

### Call graph: agents.variables

> Full detail in [`agents/MODULE_README.md`](agents/MODULE_README.md)

```
`Global Scope → agents.variables.ConfigDict() (line 19)` → ... → `AgentVariable.from_dict(var_def) (line 64)`
```

### Call graph: agents.definition

> Full detail in [`agents/MODULE_README.md`](agents/MODULE_README.md)

```
`Global Scope → agents.definition.field() (line 34)` → ... → `agents.definition.AgentExecuteResult() (line 421)`
```

### Call graph: context.events

> Full detail in [`context/MODULE_README.md`](context/MODULE_README.md)

```
`Global Scope → context.events.frozenset((e.value for e in EventType)) (line 22)` → ... → `context.events.StreamEvent() (line 165)`
```

### Call graph: context.stream_emitter

> Full detail in [`context/MODULE_README.md`](context/MODULE_README.md)

```
`context.stream_emitter.__init__ → asyncio.Queue() (line 36)` → ... → `self.send_end() (line 240)`
```

### Call graph: context.console_emitter

> Full detail in [`context/MODULE_README.md`](context/MODULE_README.md)

```
`Global Scope → resolve() (line 17)` → ... → `json.dump(output, f) (line 165)`
```

### Call graph: context.app_context

> Full detail in [`context/MODULE_README.md`](context/MODULE_README.md)

```
`Global Scope → context.app_context.field() (line 34)` → ... → `context.app_context.HTTPException() (line 96)`
```

### Call graph: providers.errors

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.errors._classify_by_status → providers.errors.RetryableError() (line 48)` → ... → `providers.errors._fallback_classify(str(exception), provider) (line 165)`
```

### Call graph: providers.unified_client

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.unified_client.__init__ → providers.unified_client.GoogleChat() (line 58)` → ... → `providers.unified_client.CerebrasTranslator() (line 236)`
```

### Call graph: providers.together.together_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.together.together_api.__init__ → providers.together.together_api.AsyncTogether() (line 34)` → ... → `providers.together.together_api.UnifiedResponse() (line 301)`
```

### Call graph: providers.together.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.together.translator.to_together → messages.append({'role': 'system', 'content': config.system_instruction}) (line 37)` → ... → `providers.together.translator.UnifiedResponse() (line 197)`
```

### Call graph: providers.openai.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.openai.translator.to_openai → messages.append({'role': 'developer', 'content': [{'type': 'input_text', 'text': config.system_instruction}]}) (line 39)` → ... → `providers.openai.translator.UnifiedResponse() (line 174)`
```

### Call graph: providers.openai.openai_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.openai.openai_api.__init__ → providers.openai.openai_api.AsyncOpenAI() (line 30)` → ... → `emitter.send_error() (line 235)`
```

### Call graph: providers.google.google_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.google.google_api.__init__ → genai.Client() (line 35)` → ... → `asyncio.sleep(0) (line 151)`
```

### Call graph: providers.google.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.google.translator.to_google → msg.to_google_content() (line 76)` → ... → `providers.google.translator.UnifiedResponse() (line 315)`
```

### Call graph: providers.anthropic.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.anthropic.translator.to_anthropic → msg.to_anthropic_blocks() (line 43)` → ... → `providers.anthropic.translator.UnifiedResponse() (line 150)`
```

### Call graph: providers.anthropic.anthropic_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.anthropic.anthropic_api.__init__ → providers.anthropic.anthropic_api.AsyncAnthropic() (line 28)` → ... → `emitter.send_chunk(f'\n<reasoning>\n{text}\n</reasoning>\n') (line 285)`
```

### Call graph: providers.groq.groq_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.groq.groq_api.__init__ → providers.groq.groq_api.AsyncGroq() (line 34)` → ... → `providers.groq.groq_api.UnifiedResponse() (line 249)`
```

### Call graph: providers.groq.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.groq.translator.to_groq → messages.append({'role': 'system', 'content': config.system_instruction}) (line 37)` → ... → `providers.groq.translator.UnifiedResponse() (line 191)`
```

### Call graph: providers.cerebras.cerebras_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.cerebras.cerebras_api.__init__ → providers.cerebras.cerebras_api.AsyncCerebras() (line 32)` → ... → `self.to_unified_response(mock_response, model) (line 287)`
```

### Call graph: providers.cerebras.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.cerebras.translator.to_cerebras → messages.append({'role': 'system', 'content': config.system_instruction}) (line 41)` → ... → `providers.cerebras.translator.UnifiedResponse() (line 235)`
```

### Call graph: providers.xai.xai_api

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.xai.xai_api.__init__ → providers.xai.xai_api.AsyncOpenAI() (line 34)` → ... → `providers.xai.xai_api.UnifiedResponse() (line 251)`
```

### Call graph: providers.xai.translator

> Full detail in [`providers/MODULE_README.md`](providers/MODULE_README.md)

```
`providers.xai.translator.to_xai → messages.append({'role': 'system', 'content': config.system_instruction}) (line 37)` → ... → `providers.xai.translator.UnifiedResponse() (line 191)`
```

### Call graph: utils.cache

> Full detail in [`utils/MODULE_README.md`](utils/MODULE_README.md)

```
`utils.cache.__init__ → utils.cache.OrderedDict() (line 17)` → ... → `...items() (line 77)`
```

### Call graph: config.unified_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.unified_config.field() (line 43)` → ... → `value.to_dict() (line 443)`
```

### Call graph: config.usage_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.usage_config.ModelPricing() (line 105)` → ... → `config.usage_config.UsageTotals() (line 866)`
```

### Call graph: config.finish_reason

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`config.finish_reason.from_google → upper() (line 89)` → ... → `mapping.get(reason_str, cls.OTHER) (line 111)`
```

### Call graph: config.extra_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.extra_config.field() (line 13)` → ... → `config.extra_config.cls() (line 123)`
```

### Call graph: config.thinking_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`config.thinking_config.to_openai_reasoning → effort_mapping.get(self.reasoning_effort) (line 52)` → ... → `config.thinking_config.cls() (line 417)`
```

### Call graph: config.media_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.media_config.field() (line 23)` → ... → `block.get('mime_type') (line 886)`
```

### Call graph: config.message_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.message_config.field() (line 39)` → ... → `message.replace_variables(variables) (line 656)`
```

### Call graph: config.config_utils

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`config.config_utils.truncate_base64_in_dict → d.items() (line 32)` → ... → `config.config_utils.truncate_base64_in_dict(item, min_length) (line 48)`
```

### Call graph: config.tools_config

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.tools_config.field() (line 14)` → ... → `config.tools_config.cls() (line 272)`
```

### Call graph: config.unified_content

> Full detail in [`config/MODULE_README.md`](config/MODULE_README.md)

```
`Global Scope → config.unified_content.field() (line 40)` → ... → `config.unified_content.TextContent() (line 488)`
```

### Call graph: orchestrator.recovery_logic

> Full detail in [`orchestrator/MODULE_README.md`](orchestrator/MODULE_README.md)

```
`orchestrator.recovery_logic.handle_finish_reason → orchestrator.recovery_logic.FinishReason(finish_reason) (line 39)` → ... → `finish_reason.is_error() (line 92)`
```

### Call graph: orchestrator.executor

> Full detail in [`orchestrator/MODULE_README.md`](orchestrator/MODULE_README.md)

```
`async orchestrator.executor.execute_ai_request → orchestrator.executor.get_app_context() (line 67)` → ... → `orchestrator.executor.UnifiedResponse() (line 637)`
```

### Call graph: orchestrator.requests

> Full detail in [`orchestrator/MODULE_README.md`](orchestrator/MODULE_README.md)

```
`Global Scope → orchestrator.requests.field() (line 38)` → ... → `...items() (line 408)`
```

### Call graph: orchestrator.tracking

> Full detail in [`orchestrator/MODULE_README.md`](orchestrator/MODULE_README.md)

```
`orchestrator.tracking.aggregate → detail.get('name', 'unknown') (line 42)` → ... → `detail.get('success', True) (line 53)`
```

### Call graph: agent_runners.research

> Full detail in [`agent_runners/MODULE_README.md`](agent_runners/MODULE_README.md)

```
`async agent_runners.research.scrape_research_condenser_agent_1 → fork_for_child_agent(str(uuid4())) (line 40)` → ... → `agent_runners.research.clear_execution_context(token) (line 98)`
```

### Call graph: db.__init__

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`Global Scope → db.__init__.load_dotenv() (line 3)` → ... → `db.__init__.register_database_from_env() (line 7)`
```

### Call graph: db.run_migrations

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`Global Scope → db.run_migrations.load_dotenv() (line 34)` → ... → `db.run_migrations._usage() (line 114)`
```

### Call graph: db.generate

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`Global Scope → db.generate.run_schema_generation('matrx_orm.yaml') (line 3)`
```

### Call graph: db.models

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`Global Scope → db.models.UUIDField() (line 26)` → ... → `db.models.cls() (line 916)`
```

### Call graph: db.managers.content_blocks

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.content_blocks.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.content_blocks.ContentBlocksManager() (line 184)`
```

### Call graph: db.managers.cx_message

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_message.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_message.CxMessageManager() (line 190)`
```

### Call graph: db.managers.table_data

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.table_data.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.table_data.TableDataManager() (line 190)`
```

### Call graph: db.managers.tools

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.tools.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.tools.ToolsManager() (line 190)`
```

### Call graph: db.managers.cx_user_request

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_user_request.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_user_request.CxUserRequestManager() (line 214)`
```

### Call graph: db.managers.ai_model

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.ai_model.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.ai_model.AiModelManager() (line 226)`
```

### Call graph: db.managers.cx_media

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_media.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_media.CxMediaManager() (line 190)`
```

### Call graph: db.managers.shortcut_categories

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.shortcut_categories.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.shortcut_categories.ShortcutCategoriesManager() (line 202)`
```

### Call graph: db.managers.cx_request

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_request.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_request.CxRequestManager() (line 208)`
```

### Call graph: db.managers.cx_tool_call

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_tool_call.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_tool_call.CxToolCallManager() (line 226)`
```

### Call graph: db.managers.cx_agent_memory

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_agent_memory.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_agent_memory.CxAgentMemoryManager() (line 178)`
```

### Call graph: db.managers.user_tables

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.user_tables.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.user_tables.UserTablesManager() (line 190)`
```

### Call graph: db.managers.cx_conversation

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.cx_conversation.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.cx_conversation.CxConversationManager() (line 238)`
```

### Call graph: db.managers.ai_provider

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.ai_provider.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.ai_provider.AiProviderManager() (line 184)`
```

### Call graph: db.managers.prompt_builtins

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.prompt_builtins.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.prompt_builtins.PromptBuiltinsManager() (line 202)`
```

### Call graph: db.managers.prompts

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.managers.prompts.get_validated_dict → self.to_dict() (line 88)` → ... → `db.managers.prompts.PromptsManager() (line 208)`
```

### Call graph: db.custom.cx_managers

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`Global Scope → db.custom.cx_managers.CxConversationManager() (line 133)` → ... → `db.custom.cx_managers.CxManagers() (line 252)`
```

### Call graph: db.custom.conversation_gate

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`db.custom.conversation_gate._is_valid_uuid → db.custom.conversation_gate.UUID(value) (line 51)` → ... → `gate_task.add_done_callback(_on_gate_done) (line 407)`
```

### Call graph: db.custom.ai_model_manager

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.custom.ai_model_manager.load_all_models → self.load_items() (line 30)` → ... → `db.custom.ai_model_manager.AiModelManager() (line 102)`
```

### Call graph: db.custom.persistence

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`db.custom.persistence._is_valid_uuid → db.custom.persistence.UUID(value) (line 35)` → ... → `traceback.print_exc() (line 374)`
```

### Call graph: db.custom.conversation_rebuild

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`db.custom.conversation_rebuild._rebuild_tool_result_content → content_blocks.append({'type': 'tool_result', 'tool_use_id': tc.call_id, 'call_id': tc.call_id, 'name': tc.tool_name, 'content': tc.output, 'is_error': tc.is_error}) (line 32)` → ... → `result.append(unified_message) (line 88)`
```

### Call graph: db.custom.ai_models.ai_model_validator

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.custom.ai_models.ai_model_validator.validate_data_integrity → self.load_all_models() (line 18)` → ... → `db.custom.ai_models.ai_model_validator.validate_and_fix_endpoints() (line 281)`
```

### Call graph: db.custom.ai_models.ai_model_base

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.custom.ai_models.ai_model_base.create_ai_model → self.create_item() (line 42)` → ... → `db.custom.ai_models.ai_model_base.main() (line 152)`
```

### Call graph: db.custom.ai_models.ai_model_dto

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.custom.ai_models.ai_model_dto._initialize_dto → ...startswith('claude-sonnet-4-6') (line 35)` → ... → `self.to_dict() (line 101)`
```

### Call graph: db.custom.ai_models.ai_model_manager

> Full detail in [`db/MODULE_README.md`](db/MODULE_README.md)

```
`async db.custom.ai_models.ai_model_manager.load_all_models → self.load_items() (line 37)` → ... → `db.custom.ai_models.ai_model_manager.AiModelManager() (line 83)`
```

### Call graph: tools.agent_tool

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 16)` → ... → `tools.agent_tool.ToolDefinition() (line 133)`
```

### Call graph: tools.logger

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.logger.log_started → datetime.now(timezone.utc) (line 39)` → ... → `child.calculate_cost() (line 245)`
```

### Call graph: tools.executor

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 19)` → ... → `time.time() (line 409)`
```

### Call graph: tools.guardrails

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 12)` → ... → `normalized.encode() (line 232)`
```

### Call graph: tools.tools_db

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → tools.tools_db.ToolsManager() (line 14)`
```

### Call graph: tools.registry

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`tools.registry.get_instance → tools.registry.cls() (line 34)` → ... → `registered.append(namespaced) (line 409)`
```

### Call graph: tools.external_mcp

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 12)` → ... → `prop.get('description', '') (line 199)`
```

### Call graph: tools.streaming

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.streaming.emit → ...append(event) (line 69)` → ... → `e.model_dump() (line 182)`
```

### Call graph: tools.handle_tool_calls

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 30)` → ... → `guardrails.clear_conversation(conversation_id) (line 156)`
```

### Call graph: tools.browser_sessions

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → tools.browser_sessions.field() (line 35)` → ... → `atexit.register(_shutdown_browser_sessions) (line 163)`
```

### Call graph: tools.models

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`tools.models.to_agent_message → parts.append(f'Suggested action: {self.suggested_action}') (line 33)` → ... → `datetime.now(timezone.utc) (line 473)`
```

### Call graph: tools.lifecycle

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`tools.lifecycle.get_instance → tools.lifecycle.cls() (line 35)` → ... → `...values() (line 124)`
```

### Call graph: tools.implementations.shell

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 13)` → ... → `time.time() (line 209)`
```

### Call graph: tools.implementations.user_lists

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.user_lists.userlist_create → args.get('list_name', '') (line 13)` → ... → `tools.implementations.user_lists.ToolResult() (line 335)`
```

### Call graph: tools.implementations.travel

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.travel.travel_get_location → tools.implementations.travel.ToolResult() (line 17)` → ... → `tools.implementations.travel.ToolResult() (line 120)`
```

### Call graph: tools.implementations._summarize_helper

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations._summarize_helper.summarize_content → fork_for_child_agent(str(uuid4())) (line 35)` → ... → `traceback.format_exc() (line 69)`
```

### Call graph: tools.implementations.personal_tables

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`tools.implementations.personal_tables._run_query → tools.implementations.personal_tables.execute_query(query_name, params) (line 27)` → ... → `traceback.format_exc() (line 503)`
```

### Call graph: tools.implementations.web

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.web.web_search → time.time() (line 21)` → ... → `time.time() (line 433)`
```

### Call graph: tools.implementations.memory

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 18)` → ... → `time.time() (line 225)`
```

### Call graph: tools.implementations.text

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.text.text_analyze → time.time() (line 13)` → ... → `time.time() (line 144)`
```

### Call graph: tools.implementations.code

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → ...get('TOOL_WORKSPACE_BASE', '/tmp/workspaces') (line 14)` → ... → `traceback.format_exc() (line 281)`
```

### Call graph: tools.implementations.questionnaire

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.questionnaire.interaction_ask → args.get('introduction', '') (line 19)` → ... → `tools.implementations.questionnaire.ToolResult() (line 142)`
```

### Call graph: tools.implementations.seo

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.seo.seo_check_meta_titles → args.get('titles', []) (line 17)` → ... → `traceback.format_exc() (line 263)`
```

### Call graph: tools.implementations.filesystem

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 19)` → ... → `time.time() (line 311)`
```

### Call graph: tools.implementations.user_tables

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.user_tables.usertable_create → args.get('table_name', '') (line 12)` → ... → `traceback.format_exc() (line 50)`
```

### Call graph: tools.implementations.math

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → k.startswith('_') (line 11)` → ... → `time.time() (line 49)`
```

### Call graph: tools.implementations.browser

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 20)` → ... → `time.time() (line 597)`
```

### Call graph: tools.implementations.database

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 16)` → ... → `time.time() (line 307)`
```

### Call graph: tools.implementations.news

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`async tools.implementations.news.news_get_headlines → args.get('country') (line 13)` → ... → `traceback.format_exc() (line 92)`
```

### Call graph: tools.output_models.seo

> Full detail in [`tools/MODULE_README.md`](tools/MODULE_README.md)

```
`tools.output_models.seo.normalize_keyword_item → raw.get('monthly_searches') (line 46)` → ... → `raw.get('competition_index') (line 61)`
```

### Call graph: processing.audio.transcription_cache

> Full detail in [`processing/MODULE_README.md`](processing/MODULE_README.md)

```
`processing.audio.transcription_cache._generate_key → hexdigest() (line 50)` → ... → `_global_cache.clear() (line 117)`
```

### Call graph: processing.audio.audio_preprocessing

> Full detail in [`processing/MODULE_README.md`](processing/MODULE_README.md)

```
`processing.audio.audio_preprocessing.preprocess_audio_in_messages → processing.audio.audio_preprocessing.api_class_supports_audio(api_class) (line 46)` → ... → `messages.to_list() (line 228)`
```

### Call graph: processing.audio.audio_support

> Full detail in [`processing/MODULE_README.md`](processing/MODULE_README.md)

```
`processing.audio.audio_support.api_supports_audio → api.lower() (line 34)` → ... → `processing.audio.audio_support.api_class_supports_audio(api_class) (line 77)`
```

### Call graph: processing.audio.groq_transcription

> Full detail in [`processing/MODULE_README.md`](processing/MODULE_README.md)

```
`Global Scope → processing.audio.groq_transcription.field() (line 46)` → ... → `segment.get('end') (line 471)`
```

### Call graph: app.config

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.config.SettingsConfigDict() (line 7)` → ... → `app.config.Settings() (line 59)`
```

### Call graph: app.main

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → ...reconfigure() (line 24)` → ... → `uvicorn.run('app.main:app') (line 237)`
```

### Call graph: app.dependencies.auth

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`async app.dependencies.auth.require_guest_or_above → app.dependencies.auth.HTTPException() (line 9)` → ... → `app.dependencies.auth.HTTPException() (line 41)`
```

### Call graph: app.middleware.auth

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`async app.middleware.auth.__call__ → self.app(scope, receive, send) (line 25)` → ... → `decoded.get('email') (line 137)`
```

### Call graph: app.routers.health

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.routers.health.APIRouter() (line 9)` → ... → `app.routers.health._event_loop_check() (line 62)`
```

### Call graph: app.routers.tool

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.routers.tool.APIRouter() (line 19)` → ... → `app.routers.tool.eval(expr, {'__builtins__': {}}, {}) (line 98)`
```

### Call graph: app.routers.chat

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.routers.chat.APIRouter() (line 24)` → ... → `router.post('/chat') (line 59)`
```

### Call graph: app.routers.conversation

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.routers.conversation.APIRouter() (line 22)` → ... → `public_router.post('/{conversation_id}/warm') (line 57)`
```

### Call graph: app.routers.agent

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.routers.agent.APIRouter() (line 25)` → ... → `cancel_router.post('/cancel/{request_id}') (line 92)`
```

### Call graph: app.models.chat

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → app.models.chat.ConfigDict() (line 8)` → ... → `app.models.chat.field_validator('response_format') (line 66)`
```

### Call graph: app.core.exceptions

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`async app.core.exceptions.matrx_exception_handler → app.core.exceptions.ORJSONResponse() (line 64)` → ... → `app.core.exceptions.ORJSONResponse() (line 89)`
```

### Call graph: app.core.cancellation

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`app.core.cancellation.__init__ → asyncio.Lock() (line 22)` → ... → `...items() (line 46)`
```

### Call graph: app.core.response

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`async app.core.response._stream → json.dumps({'event': 'status_update', 'data': {'status': 'connected', 'system_message': 'Stream established', 'user_message': initial_message}}) (line 43)` → ... → `app.core.response._stream() (line 98)`
```

### Call graph: app.core.sentry

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 24)` → ... → `app.core.sentry.get_settings() (line 90)`
```

### Call graph: app.core.streaming

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 21)` → ... → `json.dumps({'error': str(exc)}) (line 133)`
```

### Call graph: app.core.middleware

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`Global Scope → logging.getLogger(__name__) (line 8)` → ... → `logger.info('%s %s %s %.2fms id=%s', method, path, status_code, elapsed_ms, request_id) (line 51)`
```

### Call graph: app.core.ai_task

> Full detail in [`app/MODULE_README.md`](app/MODULE_README.md)

```
`async app.core.ai_task.run_ai_task → emitter.send_status_update() (line 47)` → ... → `completion.model_dump() (line 117)`
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** AppKit, BeautifulSoup, ConfigParser, Cython, Foundation, HTMLParser, IPython, MySQLdb, OpenSSL, PIL, PyInstaller, PyQt4, PyQt5, PyQt6, PySide6, Queue, StringIO, UnleashClient, UserDict, __builtin__, __main__, __pypy__, _abcoll, _cffi_backend, _dummy_thread, _manylinux, _pytest, _registry, _ruamel_yaml, _testbuffer, _typeshed, _winreg, a2wsgi, acres, adbc_driver_manager, adbc_driver_postgresql, adbc_driver_sqlite, adlfs, aidream, aiocontextvars, aiodns, aiohappyeyeballs, aiohttp, aioquic, aiosignal, android, annotated_doc, annotated_types, annotationlib, anthropic, anyio, apache_beam, api_management, argcomplete, ariadne, arq, array_api_compat, array_api_strict, array_interface_testing, asttokens, async_timeout, asyncpg, attr, awscrt, azure, backports, bcrypt, berkeleydb, bids, billiard, blinker, blobfile, bodo, boto, boto3, botocore, bottle, brotli, brotlicffi, bs4, bson, cStringIO, ca_certs_locater, cachetools, celery, cerebras, certifi, cffi, cfflib, cgi, chalice, channels, chardet, charset_normalizer, checks, ci, ci_info, click, clickhouse_driver, client, cmp, code_generators, cohere, colorama, commandline, common, compiler, compression, configobj, copy_reg, cron_converter, cryptography, cssselect, ctags, cupy, cupyx, curio, cviewer, cycler, cython, daft, dask, datalad, dateutil, dcmstack, defusedxml, deprecation, dipy, distributed, distro, distutils, django, dns, docstring_parser, docutils, dotenv, dramatiq, duckdb, duecredit, dummy_thread, dummy_threading, email_validator, etelemetry, eval_type_backport, eventlet, exceptiongroup, executing, falcon, fastapi, fastapi_cli, fastapi_cloud_cli, fastapi_new, fastar, fastmcp, fastparquet, fb303, filelock, fitz, flask, flask_login, frontend, frozenlist, fsspec, fuse, gcsfs, gevent, git, gitdb, gitdb_speedups, google, gql, graph_tool, graphene, graphql, graphutils, greenlet, groq, grpc, grpc_health, grpc_reflection, grpc_tools, gunicorn, h11, h2, h5py, hive_metastore, hpack, html5lib, html5rdf, htmlentitydefs, httpcore, httplib, httplib2, httptools, httpx, httpx_aiohttp, huey, huggingface_hub, hyperframe, hypothesis, idna, imp, importlib_metadata, importlib_resources, indexed_gzip, inflect, iniconfig, initialize_systems, ipyparallel, ipywidgets, isal, isodate, itsdangerous, java, jax, jinja, jinja2, jiter, jmespath, jnius, js, jwt, keras, kerchunk, keyring, kombu, langchain, langchain_aws, langchain_classic, langchain_cohere, langchain_core, langchain_google_vertexai, langchain_huggingface, langchain_mistralai, langchain_ollama, langchain_openai, langgraph, ldclient, libarchive, limited_api1, limited_api2, limited_api_latest, linkify_it, litellm, litestar, loguru, looseversion, lxml, lxml_html_clean, lz4, lzmaffi, markdown_it, markupsafe, matplotlib, matrix, matrx_orm, matrx_utils, mcp, mdurl, mem_policy, memory_profiler, mmh3, more_itertools, mpl_toolkits, mpmath, multidict, multipart, mypy, mypy_boto3_dynamodb, mypy_boto3_glue, mypy_boto3_s3, mypy_boto3_secretsmanager, ndonnx, networkx, nibabel, niflow, nilearn, nipy, nipype, nitime, nodejs_wheel, ntlm, numba, numexpr, numpy, numpy_distutils, oauth2client, odf, olefile, openai, openfeature, openpyxl, opentelemetry, ordereddict, orjson, outcome, packaging, pandas, panel, paramiko, pendulum, pexpect, phonenumbers, pip, pipes, pkg_resources, platformdirs, playwright, pluggy, polars, pooch, postgrest, pptx, prompts, propcache, prov, psutil, psycopg, psycopg_binary, psycopg_c, psycopg_pool, pure_eval, puremagic, py, py4j, pyarrow, pyasn1, pyasn1_modules, pycountry, pycparser, pydantic, pydantic_ai, pydantic_core, pydantic_settings, pydicom, pydoctor, pydot, pygit2, pygments, pygraphviz, pyiceberg, pyiceberg_core, pylab, pymongo, pyodide, pyparsing, pyramid, pyroaring, pyspark, pytesseract, pytest, pytest_fail_slow, pytest_run_parallel, pytest_timeout, python_calamine, python_multipart, python_socks, pythoncom, pytz, pyu2f, pyxlsb, pyxnat, pyzstd, qtpy, quart, quart_auth, railroad, ray, rb, rdflib, realtime, redbeat, redis, rediscluster, regex, requests, requests_kerberos, rest_framework, rich, rich_toolkit, rignore, roistats, rq, rsa, ruamel, s3fs, s3transfer, sanic, scikits, scipy, scipy_doctest, scraper, seaborn, semver, sentencepiece, sentry_sdk, seo, sessionmirror, setup_project, setuptools, sha, shapely, shellingham, simplejson, six, sklearn, sksparse, slack_sdk, smbclient, smbprotocol, smmap, snappy, sniffio, socks, socksio, soma, sounddevice, sparse, sphinx, sqlalchemy, src, sse_starlette, starlette, starlite, statsig, storage3, strawberry, strenum, strictyaml, supabase, supabase_auth, supabase_functions, sympy, tables, tabula, tabulate, tenacity, tensorflow, test, thread, threadpoolctl, thrift, tiktoken, tiktoken_ext, together, toml, tomli, torch, tornado, tqdm, traitlets, traits, traitsui, trio, trytond, tvtk, twisted, typeguard, typer, typeshed, typing_extensions, typing_inspection, uarray, ujson, ulid, urllib2, urllib3, urllib3_secure_extra, urlparse, user_data, uvicorn, uvloop, uwsgi, vtk, watchfiles, wcwidth, webob, websockets, werkzeug, win32com, win32pdh, winloop, wmi, wsproto, xai_sdk, xdist, xlrd, xlsxwriter, xmlrpclib, xvfbwrapper, yaml, yarl, zipp, zope, zstandard
**Internal modules:** agent_runners.research, agents, agents._utils, agents.cache, agents.definition, agents.exceptions, agents.manager, agents.resolver, agents.run, agents.run_internal, agents.tool, agents.types, agents.util, agents.variables, agents.version, app.config, app.core, app.dependencies, app.middleware, app.models, app.routers, config, config.extra_config, config.finish_reason, config.media_config, config.message_config, config.unified_config, config.usage_config, context.app_context, context.console_emitter, context.emitter_protocol, context.events, context.stream_emitter, db.custom, db.managers, db.models, instructions.core, instructions.matrx_fetcher, instructions.pattern_parser, instructions.tests, media, media.audio, orchestrator, orchestrator.executor, orchestrator.requests, orchestrator.tracking, processing.audio, providers, providers.anthropic, providers.cerebras, providers.errors, providers.google, providers.groq, providers.openai, providers.together, providers.unified_client, providers.xai, tests.ai, tools, tools.arg_models, tools.browser_sessions, tools.external_mcp, tools.handle_tool_calls, tools.implementations, tools.models, tools.output_models, tools.registry, tools.streaming, tools.tools_db, utils.cache, utils.code_context
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": true,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
