# Prompts System — Typing TODOs

## 1. Pydantic models for JSONB fields (HIGH PRIORITY)

The ORM's `JSONBField` returns `dict[str, Any] | list[Any] | None` — a broad union
that requires isinstance narrowing at every call site. The fix is to define Pydantic
models for all known shapes so the types are precise and validated on load.

This will also force alignment with the TypeScript team on the exact shapes of these
objects — **this is a good thing**.

---

### `settings` (on `Prompts` and `PromptBuiltins`)

The settings JSONB column carries model/config overrides for a prompt. Almost entirely
known shape. Define one model covering both tables (or two if they diverge):

```python
# prompts/settings_schema.py
from pydantic import BaseModel
from typing import Optional, Literal

class PromptSettings(BaseModel):
    model_id: str = ""
    ai_model: str = ""           # legacy alias used in builtins
    temperature: float | None = None
    max_output_tokens: int | None = None
    top_p: float | None = None
    top_k: int | None = None
    tool_choice: Literal["none", "auto", "required"] | None = None
    reasoning_effort: str | None = None
    reasoning_summary: str | None = None
    thinking_budget: int | None = None
    stream: bool = False
    # add any other known keys
```

Usage in manager.py:
```python
settings = PromptSettings.model_validate(prompt.settings or {})
config_dict = {
    "messages": prompt.messages,
    "model": settings.model_id,
    **settings.model_dump(exclude_none=True, exclude={"ai_model"}),
}
```

---

### `variable_defaults` (on `Prompts` and `PromptBuiltins`)

Currently passed as `list | dict | None` to `AgentVariable.from_list()`. Should always
be a list of variable definition dicts. Define:

```python
class VariableDefaultEntry(BaseModel):
    name: str
    default_value: str = ""
    required: bool = False
    description: str = ""
    # any other variable fields
```

Usage: `PromptSettings.variable_defaults: list[VariableDefaultEntry] = []`

---

### `messages` (on `Prompts`, `PromptBuiltins`, `CxMessage`, etc.)

JSONB list of message dicts. Already handled by `UnifiedMessage.from_dict()` at the
config layer, but having a Pydantic model for the raw DB shape would make the
deserialization explicit and type-safe:

```python
class StoredMessage(BaseModel):
    role: str
    content: list[dict[str, Any]]
    id: str | None = None
    name: str | None = None
    status: str = "active"
    metadata: dict[str, Any] = {}
```

---

### `tools` (on `Prompts`, `PromptBuiltins`, `AiModel`)

Tool definitions stored in JSONB. Should match the tool definition schema already in
`config/tools_config.py`. Define a `StoredToolDefinition` Pydantic model and use it
here.

---

### `parameters` (on `Tools` table)

The `parameters` field holds the JSON schema for tool inputs. Define:

```python
class ToolParameterSchema(BaseModel):
    type: str
    properties: dict[str, Any]
    required: list[str] = []
    description: str = ""
```

---

### `cx_message.content` (on `CxMessage`)

Already has `reconstruct_content()` in `config/unified_config.py` but the raw DB type
is `JSONBField` (list). A `StoredContentBlock` model with a `type` discriminator would
give full static typing through the persistence layer.

---

## 2. ORM-level generics (depends on matrx-orm updates)

Once `matrx-orm` supports `JSONBField[T]`, model declarations can carry the type
directly:

```python
# db/models.py
settings: JSONBField[PromptSettings] = JSONBField()
variable_defaults: JSONBField[list[VariableDefaultEntry]] = JSONBField()
messages: JSONBField[list[StoredMessage]] = JSONBField()
```

This eliminates all isinstance narrowing at call sites. See
`matrx-orm/src/matrx_orm/core/TASKS.md` item #1.

---

## 3. `AgentConfig.name` optionality

`Prompts.name` and `PromptBuiltins.name` are `CharField` (nullable). `AgentConfig.name`
is currently `str`. Either:
- Make `AgentConfig.name: str = ""` (with default), or
- Accept `str | None` and propagate through `Agent.name`

Currently patched with `or ""` at the manager call sites.
