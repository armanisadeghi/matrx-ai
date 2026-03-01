# Tool System Overhaul — Complete Architecture Plan

**Date**: February 15, 2026
**Status**: Proposal — Pending Team Review
**Scope**: Replace the entire `mcp_server/` tool system, tool registry, tool execution pipeline, and tool tracking with a unified, Pydantic-based architecture that supports internal functions, external MCPs, agent-as-tool, and full observability.

---

## Table of Contents

1. [Problem Statement — Why This Overhaul](#1-problem-statement)
2. [Current Architecture Audit](#2-current-architecture-audit)
3. [Target Architecture Overview](#3-target-architecture-overview)
4. [Core Pydantic Models](#4-core-pydantic-models)
5. [Tool Context — The Orchestration Engine](#5-tool-context)
6. [Tool Registry v2 — Single Source of Truth](#6-tool-registry-v2)
7. [Tool Executor — Unified Execution Pipeline](#7-tool-executor)
8. [External MCP Client](#8-external-mcp-client)
9. [Agent-as-Tool System](#9-agent-as-tool-system)
10. [Streaming & Client Updates](#10-streaming-and-client-updates)
11. [Guardrails & Safety](#11-guardrails-and-safety)
12. [Observability — Logging, Costs, and Metrics](#12-observability)
13. [Memory System — Short, Medium, Long-Term](#13-memory-system)
14. [Database Tools](#14-database-tools)
15. [Computer Use Tools — Filesystem, Browser, Shell](#15-computer-use-tools)
16. [Lifecycle & Cleanup](#16-lifecycle-and-cleanup)
17. [Data Persistence for Valuable Outputs](#17-data-persistence)
18. [Migration Strategy](#18-migration-strategy)
19. [New File Structure](#19-new-file-structure)
20. [Implementation Phases](#20-implementation-phases)

---

## 1. Problem Statement

### The Wrapper Problem

The current tool system has accumulated 6 layers of indirection for a single tool call:

```
ToolCallContent (unified dataclass)
  → tool_registry.execute_tool_call()      [converts dataclass → dict]
    → tool_registry.execute_tool()          [inspect.signature() for DI, duplicate detection]
      → web_search_summarized()             [thin wrapper: extracts args, calls helper]
        → search_web_mcp_summarized()       [actual business logic]
          → summarize_scrape_pages_agent_DEPRECATED()                    [LEGACY GoogleChatEndpoint — bypasses entire unified system]
```

Each layer adds complexity, transforms data formats, and obscures the actual execution. The result:

- **No usage tracking** for internal AI calls (tools that spawn sub-agents like `summarize_scrape_pages_agent_DEPRECATED()` use the legacy `GoogleChatEndpoint` directly, bypassing `UnifiedAIClient`, `AIMatrixRequest`, and all cost tracking)
- **Fragile dependency injection** via `inspect.signature()` — adding a parameter to a tool function requires the registry to know about it
- **Tool definitions duplicated in 3 places**: hardcoded in Python `register_*()` functions, in the `tools` database table, and in frontend `tools_constants.tsx`
- **No context propagation** — tools don't automatically receive user ID, conversation ID, API keys, or project context unless manually wired
- **No external MCP support** — the system is called "MCP" but only handles local Python functions
- **No guardrails** — the only loop protection is checking if the last call had identical arguments (one comparison, trivially bypassed by models)
- **No lifecycle management** — tool state (tracker history, scraping sessions, temp files) accumulates without cleanup
- **Unstructured error handling** — tools return `{"status": "error", "result": "..."}` strings with no structured error types or tracebacks

### Why Patching Won't Work

The previous migration plan (web scraping → agent system) proposed adding `internal_usage` to `ToolResultContent` and threading session context through 4 intermediate layers. This is the right idea but it would be the 7th layer in an already fragile stack. Every new capability (external MCPs, agent-as-tool, computer use, memory) would require similar threading through all layers.

The system needs to be rebuilt from the execution core outward, using Pydantic models as the single source of truth for tool definitions, execution context, results, and tracking.

---

## 2. Current Architecture Audit

### What Works Well (Keep)

| Component | Location | Why It's Good |
|-----------|----------|---------------|
| `ToolCallContent` / `ToolResultContent` | `ai/config/tools_config.py` | Provider-agnostic content types with proper serialization for OpenAI, Anthropic, Google. Keep these as the message-layer representation. |
| `UnifiedConfig` / `UnifiedResponse` | `ai/config/unified_config.py` | Solid provider abstraction. Tool calls flow through this correctly. |
| `execute_until_complete()` loop | `ai/ai_requests.py` | Good iterative execution with retry logic, timing, and usage aggregation. Needs minor updates, not a rewrite. |
| `AIMatrixRequest` tracking | `ai/unified_client.py` | Usage history, timing history, tool call history — well-designed accumulation pattern. |
| `ToolDefinition` format converters | `mcp_server/core/definitions.py` | The `to_openai_format()`, `to_google_format()`, etc. are necessary and correct. Move into Pydantic model. |
| Database `tools` table | Supabase | Good schema — `function_path`, `parameters` JSONB, `category`, `tags`, `is_active`. Use as source of truth. |

### What Must Be Replaced

| Component | Location | Problem |
|-----------|----------|---------|
| `ToolRegistry` singleton | `mcp_server/core/registry.py` | Dict-based, no typing, uses `inspect.signature()` for DI, mixes execution with format conversion |
| `register_*_tool()` functions | `mcp_server/tools/core/web.py` etc. | Hardcoded definitions that duplicate database. Every tool is a 200+ line registration block |
| `ToolDefinition` dataclass | `mcp_server/core/definitions.py` | No Pydantic validation, stores callable directly, parameter schema processing is brittle |
| `ToolUsageTracker` | `mcp_server/core/tracker.py` | In-memory singleton, only checks last call, no rate limiting, no cost awareness |
| Thin wrapper functions | `mcp_server/tools/core/web.py` | `web_search_summarized()` is just `try: args["queries"]... except...` around the real function |
| `summarize_scrape_pages_agent_DEPRECATED()` legacy call | `scraper/.../mcp_tool_helpers.py` | Uses `GoogleChatEndpoint` + `AiConfig` (legacy), completely bypasses unified system |
| Frontend `tools_constants.tsx` | `mcp_server/local_utils/` | Manual copy of tool metadata — should be auto-generated or fetched from DB |

### The Core Insight

A tool call is fundamentally simple:

1. **Context**: Who is calling, from where, with what permissions
2. **Definition**: What the tool does, its parameters, its constraints
3. **Execution**: Run the function with validated arguments + context
4. **Result**: Structured output with usage/cost data
5. **Tracking**: Log everything for observability

Every one of these should be a Pydantic model. The execution should be a single async function, not a 6-layer chain.

---

## 3. Target Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent / AI Request                       │
│              (execute_until_complete loop)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ ToolCallContent from LLM response
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ToolExecutor                               │
│  1. Resolve tool (registry lookup by name)                   │
│  2. Build ToolContext (user, conversation, keys, limits)      │
│  3. Validate args against Pydantic schema                    │
│  4. Check guardrails (rate limits, cost caps, loop detect)   │
│  5. Stream "executing" event to client                       │
│  6. Execute:                                                 │
│     ├── LocalTool → call Python function(args, context)      │
│     ├── ExternalMCP → MCP protocol call to remote server     │
│     └── AgentTool → spawn child agent with parent tracking   │
│  7. Build ToolResult with usage, cost, timing                │
│  8. Stream "completed" event to client                       │
│  9. Log to tool_execution_logs table                         │
│  10. Return ToolResultContent for message history            │
└─────────────────────────────────────────────────────────────┘
```

**Key principle**: Every tool, regardless of type, goes through the same executor. The executor is the single point for context injection, validation, guardrails, streaming, tracking, and cleanup.

---

## 4. Core Pydantic Models

### 4.1 ToolDefinition (replaces dataclass + DB schema)

```python
from pydantic import BaseModel, Field
from typing import Any, Callable, Awaitable, Optional
from enum import StrEnum

class ToolType(StrEnum):
    LOCAL = "local"           # Python function in this codebase
    EXTERNAL_MCP = "external" # Remote MCP server
    AGENT = "agent"           # Agent prompt executed as a tool

class ToolDefinition(BaseModel):
    """Single source of truth for a tool's identity and capabilities.
    
    Synced with the database `tools` table. The DB is authoritative for
    metadata (description, parameters, category, tags, icon, is_active).
    The codebase is authoritative for the function_path → actual callable mapping.
    """
    name: str = Field(description="Unique tool identifier, e.g. 'web_search_v1'")
    description: str
    parameters: dict[str, Any] = Field(description="JSON Schema for tool arguments")
    output_schema: dict[str, Any] | None = None
    annotations: list[dict[str, Any]] = Field(default_factory=list)

    tool_type: ToolType = ToolType.LOCAL
    function_path: str = Field(description="Dotted import path, e.g. 'tools.web.search.web_search_summarized'")
    
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    icon: str | None = None
    is_active: bool = True
    version: str = "1.0.0"

    # Runtime-only (not stored in DB)
    _callable: Callable[..., Awaitable[Any]] | None = None

    # Agent-as-tool specific
    prompt_id: str | None = Field(default=None, description="For ToolType.AGENT — the prompt/builtin ID to execute")

    # External MCP specific
    mcp_server_url: str | None = Field(default=None, description="For ToolType.EXTERNAL_MCP — the MCP server endpoint")
    mcp_server_auth: dict[str, Any] | None = None

    # Guardrail config
    max_calls_per_conversation: int | None = Field(default=None, description="Max times this tool can be called in one conversation")
    max_calls_per_minute: int | None = Field(default=None, description="Rate limit per minute")
    cost_cap_per_call: float | None = Field(default=None, description="Max cost allowed per single invocation (USD)")
    timeout_seconds: float = Field(default=120.0, description="Execution timeout")

    # UI messaging
    on_call_message_template: str | None = Field(default=None, description="Template with {{param}} placeholders for user-facing messages")

    model_config = {"arbitrary_types_allowed": True}

    def to_openai_format(self) -> dict[str, Any]:
        """OpenAI Chat Completions function format."""
        ...

    def to_openai_responses_format(self) -> dict[str, Any]:
        """OpenAI Responses API format."""
        ...

    def to_google_format(self) -> dict[str, Any]:
        """Google Gemini function declaration format."""
        ...

    def to_anthropic_format(self) -> dict[str, Any]:
        """Anthropic tool_use format."""
        ...

    def to_mcp_format(self) -> dict[str, Any]:
        """Standard MCP tool format."""
        ...

    def get_provider_format(self, provider: str) -> dict[str, Any]:
        """Single dispatcher for all providers."""
        formatters = {
            "openai": self.to_openai_responses_format,
            "anthropic": self.to_anthropic_format,
            "google": self.to_google_format,
            "cerebras": self.to_openai_format,
            "xai": self.to_openai_format,
            "together": self.to_openai_format,
            "groq": self.to_openai_format,
            "mcp": self.to_mcp_format,
        }
        formatter = formatters.get(provider, self.to_openai_format)
        return formatter()
```

### 4.2 ToolContext (the orchestration engine)

```python
class ToolContext(BaseModel):
    """Everything a tool might need to know about its execution environment.
    
    Built once per tool call by the ToolExecutor. Passed to every tool function.
    Tools declare what they need via type hints — no inspect.signature() magic.
    
    This replaces the fragile pattern of:
      - Checking if 'user_id' is in function parameters
      - Checking if 'stream_handler' is in function parameters
      - Manually threading conversation_id through 4 layers
    """
    # Identity
    user_id: str
    conversation_id: str
    request_id: str
    call_id: str                     # The specific tool call ID from the LLM
    
    # Execution context
    tool_name: str
    iteration: int                   # Which iteration of the execution loop
    parent_agent_name: str | None = None  # If called by an agent
    
    # Auth & permissions
    api_keys: dict[str, str] = Field(default_factory=dict, description="Provider API keys available")
    user_role: str = "user"          # For permission checks
    
    # Streaming
    stream_handler: Any = None       # StreamHandler instance for real-time updates
    
    # Limits (from ToolDefinition guardrails + user/org settings)
    cost_budget_remaining: float | None = None
    calls_remaining_this_conversation: int | None = None
    
    # Database access
    supabase_client: Any = None      # Typed Supabase client for tools that need DB access
    
    # Project context
    project_id: str | None = None
    organization_id: str | None = None
    
    model_config = {"arbitrary_types_allowed": True}
```

### 4.3 ToolResult (structured output)

```python
class ToolResult(BaseModel):
    """Structured result from any tool execution.
    
    This is the internal result that gets converted to ToolResultContent
    for the message history. It carries much richer data than ToolResultContent
    because it includes usage, timing, and metadata that gets logged separately.
    """
    success: bool
    output: Any                      # The actual tool output (string, dict, list)
    error: ToolError | None = None   # Structured error if failed
    
    # Usage tracking
    usage: TokenUsage | None = None  # If this tool made AI calls
    child_usages: list[TokenUsage] = Field(default_factory=list)  # If it spawned sub-agents
    
    # Timing
    started_at: float
    completed_at: float
    duration_ms: int = 0
    
    # Metadata for logging
    tool_name: str
    call_id: str
    retry_count: int = 0
    
    # For persistence
    should_persist_output: bool = False   # Flag for tools that generate valuable data
    persist_key: str | None = None        # Key for retrieval if persisted
    
    def to_tool_result_content(self) -> "ToolResultContent":
        """Convert to message-layer ToolResultContent for conversation history."""
        content = self.output if self.success else (self.error.to_agent_message() if self.error else "Unknown error")
        return ToolResultContent(
            tool_use_id=self.call_id,
            call_id=self.call_id,
            name=self.tool_name,
            content=content,
            is_error=not self.success,
        )


class ToolError(BaseModel):
    """Structured error with full context for the calling agent."""
    error_type: str                  # e.g. "timeout", "rate_limit", "validation", "execution", "permission"
    message: str                     # Human-readable error message
    traceback: str | None = None     # Full Python traceback
    is_retryable: bool = False
    suggested_action: str | None = None  # Guidance for the model: "Try with different parameters", "Wait and retry", etc.
    
    def to_agent_message(self) -> str:
        """Format error for the LLM to understand and act on."""
        parts = [f"TOOL ERROR [{self.error_type}]: {self.message}"]
        if self.suggested_action:
            parts.append(f"Suggested action: {self.suggested_action}")
        if self.traceback:
            parts.append(f"Technical details:\n{self.traceback}")
        return "\n".join(parts)
```

### 4.4 ToolExecutionLog (for the `tool_execution_logs` table)

```python
class ToolExecutionLog(BaseModel):
    """Row in the tool_execution_logs table for full observability."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    
    # Identity
    tool_name: str
    tool_type: ToolType
    call_id: str
    request_id: str
    conversation_id: str
    user_id: str
    
    # Execution
    arguments: dict[str, Any]
    success: bool
    output_preview: str | None = None  # First 500 chars of output
    error_type: str | None = None
    error_message: str | None = None
    
    # Performance
    duration_ms: int
    started_at: datetime
    completed_at: datetime
    
    # Cost
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    
    # Context
    iteration: int
    retry_count: int = 0
    parent_tool_call_id: str | None = None  # For nested tool calls (agent-as-tool)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## 5. Tool Context — The Orchestration Engine

### How Context Flows

Currently, context is threaded through parameters at each layer. The new system builds a `ToolContext` once and passes it as a single object.

**Current (fragile):**
```python
# registry.py — inspects function signature to decide what to inject
if "stream_handler" in function_signature.parameters:
    kwargs["stream_handler"] = stream_handler
if "session_manager" in function_signature.parameters:
    kwargs["session_manager"] = session_manager
if "call_id" in function_signature.parameters:
    kwargs["call_id"] = tool_call.get("id")
# Plus manual user_id injection by checking parameter schema
```

**New (explicit):**
```python
# Every tool function has the same signature
async def web_search_v1(args: WebSearchArgs, ctx: ToolContext) -> ToolResult:
    # ctx.user_id, ctx.stream_handler, ctx.conversation_id are always available
    # No inspection, no magic, no fragility
    ...
```

### Context Builder

```python
class ToolContextBuilder:
    """Builds ToolContext from the current request state."""
    
    @staticmethod
    def from_request(
        request: AIMatrixRequest,
        tool_call: ToolCallContent,
        iteration: int,
        tool_def: ToolDefinition,
    ) -> ToolContext:
        return ToolContext(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            request_id=request.request_id,
            call_id=tool_call.call_id or tool_call.id,
            tool_name=tool_call.name,
            iteration=iteration,
            stream_handler=request.stream_handler,
            # Budget/limits computed from tool_def + user settings
            cost_budget_remaining=_compute_remaining_budget(request, tool_def),
            calls_remaining_this_conversation=_compute_remaining_calls(request, tool_def),
        )
```

---

## 6. Tool Registry v2 — Single Source of Truth

### Design Principles

1. **Database is the metadata authority** — tool names, descriptions, parameters, categories, tags, icons all come from the `tools` table
2. **Code is the execution authority** — the actual Python callable is resolved from `function_path` at startup
3. **No hardcoded registrations** — no more 200-line `register_web_tool()` blocks
4. **Hot-reloadable** — changing a tool's description or parameters in the DB takes effect without redeployment (for metadata changes)

### Implementation

```python
class ToolRegistryV2:
    """Singleton registry that loads tool definitions from the database
    and resolves function_path to actual callables at startup."""
    
    _tools: dict[str, ToolDefinition] = {}
    _loaded: bool = False
    
    async def load_from_database(self) -> None:
        """Load all active tools from the tools table."""
        rows = await supabase.table("tools").select("*").eq("is_active", True).execute()
        for row in rows.data:
            tool_def = ToolDefinition(**row)
            tool_def._callable = self._resolve_callable(tool_def.function_path)
            self._tools[tool_def.name] = tool_def
        self._loaded = True
    
    def _resolve_callable(self, function_path: str) -> Callable:
        """Import and return the callable from a dotted path.
        e.g. 'tools.web.search.web_search_v1' → the actual async function
        """
        module_path, func_name = function_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)
    
    def register_local(self, name: str, func: Callable, **overrides) -> None:
        """Register a tool programmatically (for tools not yet in DB, or testing).
        
        Auto-generates parameter schema from Pydantic model type hints
        on the function's first argument.
        """
        ...
    
    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)
    
    def get_provider_tools(self, tool_names: list[str], provider: str) -> list[dict]:
        """Get tool definitions formatted for a specific provider."""
        return [
            self._tools[name].get_provider_format(provider)
            for name in tool_names
            if name in self._tools
        ]
    
    def list_tools(self, category: str | None = None, tags: list[str] | None = None) -> list[ToolDefinition]:
        """List tools with optional filtering."""
        ...
```

### Auto-Generated Parameter Schemas

For local tools, if the function uses a Pydantic model for its `args` parameter, the parameter schema can be auto-generated:

```python
class WebSearchArgs(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=2, description="Search queries")
    instructions: str = Field(description="Instructions for the summarizer")
    freshness: str | None = Field(default=None, description="Time filter: 'day', 'week', 'month'")

async def web_search_v1(args: WebSearchArgs, ctx: ToolContext) -> ToolResult:
    # args is already validated by Pydantic
    ...

# The registry can extract the JSON schema:
schema = WebSearchArgs.model_json_schema()
# This gives us the exact same format we currently hardcode in register_web_tool()
```

This means **parameter definitions are never out of sync** — they're derived directly from the code.

---

## 7. Tool Executor — Unified Execution Pipeline

### The Single Execution Path

```python
class ToolExecutor:
    """The single entry point for all tool executions.
    
    Replaces:
    - tool_registry.execute_tool_call()
    - tool_registry.execute_tool()
    - All thin wrapper functions in mcp_server/tools/
    """
    
    def __init__(self, registry: ToolRegistryV2):
        self.registry = registry
        self.guardrails = GuardrailEngine()
        self.logger = ToolExecutionLogger()
    
    async def execute(
        self,
        tool_call: ToolCallContent,
        request: AIMatrixRequest,
        iteration: int,
    ) -> ToolResultContent:
        """Execute a single tool call through the full pipeline."""
        
        started_at = time.time()
        tool_def = self.registry.get(tool_call.name)
        
        if not tool_def:
            return self._unknown_tool_error(tool_call)
        
        # 1. Build context
        ctx = ToolContextBuilder.from_request(request, tool_call, iteration, tool_def)
        
        # 2. Validate arguments
        validated_args = self._validate_args(tool_call.arguments, tool_def)
        
        # 3. Check guardrails
        guardrail_result = await self.guardrails.check(tool_call, ctx, tool_def)
        if guardrail_result.blocked:
            return guardrail_result.to_tool_result_content()
        
        # 4. Stream "executing" to client
        if ctx.stream_handler:
            await ctx.stream_handler.send_function_call(
                call_id=ctx.call_id,
                tool_name=tool_def.name,
                user_visible_message=self._format_user_message(tool_def, tool_call.arguments),
                mcp_input={"name": tool_def.name, "arguments": tool_call.arguments},
            )
        
        # 5. Execute based on tool type
        try:
            result = await asyncio.wait_for(
                self._dispatch(tool_def, validated_args, ctx),
                timeout=tool_def.timeout_seconds,
            )
        except asyncio.TimeoutError:
            result = ToolResult(
                success=False,
                output=None,
                error=ToolError(
                    error_type="timeout",
                    message=f"Tool '{tool_def.name}' timed out after {tool_def.timeout_seconds}s",
                    is_retryable=True,
                    suggested_action="Try with simpler parameters or break the task into smaller parts.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )
        except Exception as e:
            result = ToolResult(
                success=False,
                output=None,
                error=ToolError(
                    error_type="execution",
                    message=str(e),
                    traceback=traceback.format_exc(),
                    is_retryable=False,
                    suggested_action="Check the error details and try with different parameters.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )
        
        result.duration_ms = int((result.completed_at - result.started_at) * 1000)
        
        # 6. Stream "completed" to client
        if ctx.stream_handler:
            await ctx.stream_handler.send_function_call(
                call_id=ctx.call_id,
                tool_name=tool_def.name,
                user_visible_message="Completed" if result.success else "Failed",
                mcp_output=result.output if result.success else result.error.to_agent_message(),
            )
        
        # 7. Log execution (fire-and-forget, never blocks)
        asyncio.create_task(self.logger.log(result, ctx, tool_def))
        
        # 8. Persist output if flagged
        if result.should_persist_output:
            asyncio.create_task(self._persist_output(result, ctx))
        
        # 9. Return ToolResultContent for message history
        return result.to_tool_result_content(), result
    
    async def _dispatch(
        self, tool_def: ToolDefinition, args: dict, ctx: ToolContext
    ) -> ToolResult:
        """Route to the correct execution strategy."""
        match tool_def.tool_type:
            case ToolType.LOCAL:
                return await self._execute_local(tool_def, args, ctx)
            case ToolType.EXTERNAL_MCP:
                return await self._execute_external_mcp(tool_def, args, ctx)
            case ToolType.AGENT:
                return await self._execute_agent(tool_def, args, ctx)
    
    async def _execute_local(
        self, tool_def: ToolDefinition, args: dict, ctx: ToolContext
    ) -> ToolResult:
        """Execute a local Python function."""
        func = tool_def._callable
        started_at = time.time()
        
        raw_result = await func(args, ctx)
        
        # Normalize: tools can return ToolResult directly or a simple dict
        if isinstance(raw_result, ToolResult):
            return raw_result
        
        # Legacy compatibility: dict with "status" and "result"
        if isinstance(raw_result, dict):
            is_error = raw_result.get("status") == "error"
            return ToolResult(
                success=not is_error,
                output=raw_result.get("result") if not is_error else raw_result.get("error", raw_result.get("result")),
                started_at=started_at,
                completed_at=time.time(),
                tool_name=tool_def.name,
                call_id=ctx.call_id,
            )
        
        return ToolResult(
            success=True,
            output=raw_result,
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_def.name,
            call_id=ctx.call_id,
        )
```

### Batch Execution (Parallel Tool Calls)

```python
async def execute_batch(
    self,
    tool_calls: list[ToolCallContent],
    request: AIMatrixRequest,
    iteration: int,
) -> tuple[list[ToolResultContent], list[ToolResult]]:
    """Execute multiple tool calls concurrently.
    
    Replaces the current asyncio.gather in handle_tool_calls.
    """
    tasks = [
        self.execute(tc, request, iteration)
        for tc in tool_calls
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    content_results = []
    full_results = []
    for r in results:
        if isinstance(r, Exception):
            # Convert unhandled exceptions to error results
            err_result = ToolResult(
                success=False,
                error=ToolError(error_type="unhandled", message=str(r), traceback=traceback.format_exc()),
                ...
            )
            content_results.append(err_result.to_tool_result_content())
            full_results.append(err_result)
        else:
            content_result, full_result = r
            content_results.append(content_result)
            full_results.append(full_result)
    
    return content_results, full_results
```

---

## 8. External MCP Client

### Architecture

External MCPs follow the Model Context Protocol spec. We need a client that:
1. Discovers available tools from a remote MCP server
2. Calls tools on that server with proper argument marshaling
3. Returns results in our `ToolResult` format

```python
class ExternalMCPClient:
    """Client for calling tools on external MCP servers.
    
    Supports both stdio (local process) and SSE/HTTP (remote) transports.
    """
    
    async def discover_tools(self, server_url: str) -> list[ToolDefinition]:
        """Call tools/list on a remote MCP server and return ToolDefinitions."""
        ...
    
    async def call_tool(
        self,
        tool_def: ToolDefinition,
        args: dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        """Call a tool on the remote MCP server."""
        # 1. Build MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_def.name,
                "arguments": args,
            },
        }
        
        # 2. Send request via configured transport
        raw_response = await self._send(tool_def.mcp_server_url, mcp_request)
        
        # 3. Parse response into ToolResult
        return self._parse_response(raw_response, tool_def, ctx)
```

### Registration Flow

```python
# In ToolRegistryV2:
async def register_mcp_server(self, server_url: str, server_name: str) -> list[str]:
    """Connect to an MCP server, discover its tools, and register them."""
    client = ExternalMCPClient()
    remote_tools = await client.discover_tools(server_url)
    
    registered = []
    for tool in remote_tools:
        tool.tool_type = ToolType.EXTERNAL_MCP
        tool.mcp_server_url = server_url
        tool.name = f"{server_name}_{tool.name}"  # Namespace to avoid collisions
        self._tools[tool.name] = tool
        registered.append(tool.name)
    
    return registered
```

---

## 9. Agent-as-Tool System

### Core Concept

An agent is a prompt + model + configuration that can be executed as a tool. The key differences from a regular tool:

1. **Cost amplification** — an agent tool makes its own LLM calls, potentially many
2. **Tracking** — needs its own conversation, linked to the parent
3. **Context inheritance** — needs the parent's user ID, stream handler, and budget limits
4. **Streaming** — should relay progress to the parent's stream

### Implementation

```python
async def _execute_agent(
    self, tool_def: ToolDefinition, args: dict, ctx: ToolContext
) -> ToolResult:
    """Execute an agent prompt as a tool call."""
    from ai.prompts.agent import Agent
    
    started_at = time.time()
    
    # 1. Create child session linked to parent
    child_session = SimpleSession(
        user_id=ctx.user_id,
        conversation_id=str(uuid4()),  # New conversation for the child
        project_id=ctx.project_id,
        stream_handler=ctx.stream_handler,  # Share parent's stream for UI updates
    )
    # Attach parent tracking metadata
    child_session.parent_conversation_id = ctx.conversation_id
    child_session.parent_request_id = ctx.request_id
    child_session.is_internal_agent = True
    
    # 2. Create agent from prompt
    agent = await Agent.from_prompt(
        tool_def.prompt_id,
        variables=args.get("variables"),
    )
    agent.set_session(child_session)
    
    # 3. Execute with budget awareness
    user_input = args.get("input") or args.get("user_input") or args.get("query")
    result = await agent.execute(user_input=user_input)
    
    # 4. Collect all usage from the child agent
    child_usages = []
    if agent.last_completed_request:
        for usage in agent.last_completed_request.request.usage_history:
            child_usages.append(usage)
    
    return ToolResult(
        success=True,
        output=result.get("output"),
        child_usages=child_usages,
        started_at=started_at,
        completed_at=time.time(),
        tool_name=tool_def.name,
        call_id=ctx.call_id,
    )
```

### Converting a Prompt to a Tool

```python
async def register_agent_as_tool(
    prompt_id: str,
    tool_name: str,
    description: str,
    input_schema: dict | None = None,
) -> ToolDefinition:
    """Register an existing prompt/agent as a callable tool.
    
    If input_schema is None, uses a default schema with a single 'input' string parameter.
    """
    default_schema = {
        "input": {
            "type": "string",
            "description": "The input/query to send to the agent",
            "required": True,
        }
    }
    
    tool_def = ToolDefinition(
        name=tool_name,
        description=description,
        parameters=input_schema or default_schema,
        tool_type=ToolType.AGENT,
        function_path=f"agent:{prompt_id}",
        prompt_id=prompt_id,
        # Agent tools should have stricter guardrails by default
        max_calls_per_conversation=5,
        cost_cap_per_call=1.0,  # $1 max per invocation
        timeout_seconds=300.0,  # 5 minute timeout
    )
    
    # Save to database
    await supabase.table("tools").insert(tool_def.model_dump(exclude={"_callable"})).execute()
    
    # Register in runtime registry
    tool_registry.register(tool_def)
    
    return tool_def
```

---

## 10. Streaming & Client Updates

### Centralized Event Protocol

Every tool call streams structured events to the client. This replaces the scattered `stream_handler.send_function_call()` calls throughout the codebase.

```python
class ToolStreamEvent(BaseModel):
    """Standard event format streamed to the client during tool execution."""
    event: Literal[
        "tool_started",       # Tool execution began
        "tool_progress",      # Intermediate update (e.g., "Searching for...")
        "tool_step",          # Named step within the tool (e.g., "scraping", "summarizing")
        "tool_result_preview",# Partial result available
        "tool_completed",     # Tool finished successfully
        "tool_error",         # Tool failed
    ]
    call_id: str
    tool_name: str
    timestamp: float
    
    # UI guidance
    user_visible_message: str | None = None
    show_spinner: bool = True
    
    # Data payload (varies by event type)
    data: dict[str, Any] = Field(default_factory=dict)


class ToolStreamManager:
    """Manages streaming updates for tool executions.
    
    Dual-writes:
    1. To the client via StreamHandler (real-time)
    2. To the tool_execution_events table (for replay/history)
    """
    
    def __init__(self, stream_handler: StreamHandler | None, call_id: str, tool_name: str):
        self.stream_handler = stream_handler
        self.call_id = call_id
        self.tool_name = tool_name
        self._events: list[ToolStreamEvent] = []
    
    async def emit(self, event: ToolStreamEvent) -> None:
        """Emit an event to both the client stream and the event log."""
        self._events.append(event)
        
        if self.stream_handler:
            await self.stream_handler.send_function_call(
                call_id=event.call_id,
                tool_name=event.tool_name,
                user_visible_message=event.user_visible_message,
                step_data=event.data,
            )
    
    async def started(self, message: str = "Starting...") -> None:
        await self.emit(ToolStreamEvent(
            event="tool_started",
            call_id=self.call_id,
            tool_name=self.tool_name,
            timestamp=time.time(),
            user_visible_message=message,
        ))
    
    async def progress(self, message: str, data: dict | None = None) -> None:
        await self.emit(ToolStreamEvent(
            event="tool_progress",
            call_id=self.call_id,
            tool_name=self.tool_name,
            timestamp=time.time(),
            user_visible_message=message,
            data=data or {},
        ))
    
    async def completed(self, message: str = "Done", preview: str | None = None) -> None:
        await self.emit(ToolStreamEvent(
            event="tool_completed",
            call_id=self.call_id,
            tool_name=self.tool_name,
            timestamp=time.time(),
            user_visible_message=message,
            show_spinner=False,
            data={"preview": preview} if preview else {},
        ))
    
    async def error(self, message: str, error_type: str = "execution") -> None:
        await self.emit(ToolStreamEvent(
            event="tool_error",
            call_id=self.call_id,
            tool_name=self.tool_name,
            timestamp=time.time(),
            user_visible_message=message,
            show_spinner=False,
            data={"error_type": error_type},
        ))
    
    def get_events_for_persistence(self) -> list[dict]:
        """Get all events as dicts for database storage."""
        return [e.model_dump() for e in self._events]
```

### Usage in Tools

```python
async def web_search_v1(args: WebSearchArgs, ctx: ToolContext) -> ToolResult:
    stream = ToolStreamManager(ctx.stream_handler, ctx.call_id, "web_search_v1")
    
    await stream.started("Searching the web...")
    
    # Step 1: Search
    for query in args.queries:
        await stream.progress(f"Searching: {query}")
        results = await brave_search(query, args.freshness)
    
    # Step 2: Scrape
    await stream.progress(f"Reading {len(urls)} pages...")
    scraped = await scrape_urls(urls)
    
    # Step 3: Summarize (sub-agent)
    await stream.progress("Analyzing and summarizing results...")
    summary, usage = await summarize_agent(scraped, args.instructions, ctx)
    
    await stream.completed("Search complete", preview=summary[:200])
    
    return ToolResult(
        success=True,
        output=summary,
        child_usages=[usage],
        ...
    )
```

### Database Persistence for Replay

```sql
CREATE TABLE tool_execution_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    call_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    request_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    user_visible_message TEXT,
    data JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_tool_events_call_id ON tool_execution_events(call_id);
CREATE INDEX idx_tool_events_conversation ON tool_execution_events(conversation_id);
```

This allows the frontend to reconstruct tool execution history for any conversation — show what the agent did, step by step, even after the session ends.

---

## 11. Guardrails & Safety

### Guardrail Engine

```python
class GuardrailEngine:
    """Prevents runaway tool usage, especially for agent-as-tool calls."""
    
    async def check(
        self,
        tool_call: ToolCallContent,
        ctx: ToolContext,
        tool_def: ToolDefinition,
    ) -> GuardrailResult:
        """Run all guardrail checks. Returns blocked=True if the call should be denied."""
        
        checks = [
            self._check_duplicate(tool_call, ctx),
            self._check_rate_limit(tool_call, ctx, tool_def),
            self._check_conversation_limit(tool_call, ctx, tool_def),
            self._check_cost_budget(ctx, tool_def),
            self._check_loop_detection(tool_call, ctx),
            self._check_recursion_depth(ctx, tool_def),
        ]
        
        for check in checks:
            result = await check
            if result.blocked:
                return result
        
        return GuardrailResult(blocked=False)
    
    async def _check_loop_detection(
        self, tool_call: ToolCallContent, ctx: ToolContext
    ) -> GuardrailResult:
        """Detect when a model is calling the same tool repeatedly with similar args.
        
        Heuristic: If the same tool has been called 3+ times in the last 5 iterations
        with >80% argument similarity, block it.
        
        This catches the common failure mode where small models get stuck
        in a loop calling web_search with slightly different queries.
        """
        ...
    
    async def _check_recursion_depth(
        self, ctx: ToolContext, tool_def: ToolDefinition
    ) -> GuardrailResult:
        """Prevent agent-as-tool from spawning infinite child agents.
        
        Max depth: 3 levels (agent → agent-tool → agent-tool → hard stop)
        """
        ...
    
    async def _check_cost_budget(
        self, ctx: ToolContext, tool_def: ToolDefinition
    ) -> GuardrailResult:
        """Block execution if estimated cost would exceed budget.
        
        For agent-as-tool, estimate based on average cost of that agent's
        previous executions. Block if remaining budget < estimated cost.
        """
        ...
```

### Per-Tool Guardrail Config (in `tools` table)

```jsonc
// Example: web_search_v1 guardrails
{
    "max_calls_per_conversation": 10,
    "max_calls_per_minute": 5,
    "cost_cap_per_call": null,  // No cost cap for non-agent tools
    "timeout_seconds": 120
}

// Example: research_agent tool guardrails
{
    "max_calls_per_conversation": 3,
    "max_calls_per_minute": 1,
    "cost_cap_per_call": 2.0,     // $2 max per invocation
    "timeout_seconds": 300,
    "max_recursion_depth": 2      // Can call tools but those tools can't call agents
}
```

---

## 12. Observability — Logging, Costs, and Metrics

### Database Schema: `tool_execution_logs`

```sql
CREATE TABLE tool_execution_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identity
    tool_name TEXT NOT NULL,
    tool_type TEXT NOT NULL,           -- 'local', 'external', 'agent'
    call_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    
    -- Execution
    arguments JSONB NOT NULL,
    success BOOLEAN NOT NULL,
    output_preview TEXT,               -- First 500 chars
    error_type TEXT,
    error_message TEXT,
    
    -- Performance
    duration_ms INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    
    -- Cost (for tools that make AI calls)
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd NUMERIC(10,6) DEFAULT 0,
    
    -- Context
    iteration INTEGER NOT NULL,
    retry_count INTEGER DEFAULT 0,
    parent_tool_call_id TEXT,         -- For nested calls
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX idx_tel_tool_name ON tool_execution_logs(tool_name);
CREATE INDEX idx_tel_conversation ON tool_execution_logs(conversation_id);
CREATE INDEX idx_tel_user ON tool_execution_logs(user_id);
CREATE INDEX idx_tel_created ON tool_execution_logs(created_at);
CREATE INDEX idx_tel_errors ON tool_execution_logs(tool_name, success) WHERE success = false;
```

### Analytics Queries

```sql
-- Tools with highest error rates
SELECT 
    tool_name,
    COUNT(*) as total_calls,
    COUNT(*) FILTER (WHERE NOT success) as errors,
    ROUND(COUNT(*) FILTER (WHERE NOT success)::numeric / COUNT(*) * 100, 1) as error_rate,
    AVG(duration_ms) as avg_duration_ms,
    SUM(cost_usd) as total_cost
FROM tool_execution_logs
WHERE created_at > now() - interval '7 days'
GROUP BY tool_name
ORDER BY error_rate DESC;

-- Most expensive tool calls (for spotting runaway agents)
SELECT tool_name, call_id, conversation_id, cost_usd, duration_ms, total_tokens
FROM tool_execution_logs
WHERE cost_usd > 0.10
ORDER BY cost_usd DESC
LIMIT 50;

-- Tool call patterns per conversation (detect loops)
SELECT conversation_id, tool_name, COUNT(*) as calls, 
       ARRAY_AGG(success ORDER BY started_at) as success_pattern
FROM tool_execution_logs
GROUP BY conversation_id, tool_name
HAVING COUNT(*) > 5
ORDER BY calls DESC;
```

### Cost Tracking Integration

The `ToolResult.child_usages` field flows all the way back to `handle_tool_calls`:

```python
# Updated handle_tool_calls in ai/ai_requests.py
async def handle_tool_calls(
    response: UnifiedResponse, request: AIMatrixRequest, iteration: int
) -> tuple[list[ToolResultContent] | None, ToolCallUsage | None]:
    ...
    content_results, full_results = await executor.execute_batch(tool_calls, request, iteration)
    
    # Aggregate child agent usage into parent request
    for result in full_results:
        if result.usage:
            request.add_usage(result.usage)
        for child_usage in result.child_usages:
            request.add_usage(child_usage)
    
    return content_results, tool_call_usage
```

---

## 13. Memory System — Short, Medium, Long-Term

### Concept

Tools that enable an agent to manage its own persistent knowledge across conversations.

```python
class MemoryType(StrEnum):
    SHORT = "short"    # Current conversation context, auto-expires
    MEDIUM = "medium"  # Cross-conversation within a session/project, expires after days
    LONG = "long"      # Permanent knowledge, skills, preferences

# Database table
CREATE TABLE agent_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    
    memory_type TEXT NOT NULL,        -- 'short', 'medium', 'long'
    scope TEXT NOT NULL DEFAULT 'user',  -- 'user', 'project', 'organization'
    scope_id TEXT,                     -- project_id or org_id
    
    key TEXT NOT NULL,                 -- Semantic key for retrieval
    content TEXT NOT NULL,             -- The actual memory content
    embedding VECTOR(1536),            -- For semantic search (pgvector)
    
    importance FLOAT DEFAULT 0.5,      -- 0.0 to 1.0
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    
    expires_at TIMESTAMPTZ,            -- Null for long-term
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    UNIQUE(user_id, scope, scope_id, key)
);
```

### Memory Tools

```python
# Tools registered in the system:
# memory_store   — Store a memory with key, content, type, importance
# memory_recall  — Retrieve memories by key or semantic similarity
# memory_update  — Update existing memory content
# memory_forget  — Delete a specific memory
# memory_search  — Search memories with natural language query (uses embeddings)
# memory_list    — List all memories for current scope

async def memory_store(args: MemoryStoreArgs, ctx: ToolContext) -> ToolResult:
    """Store a new memory."""
    # Automatically scoped to the current user
    # Can also be scoped to project or organization
    ...

async def memory_recall(args: MemoryRecallArgs, ctx: ToolContext) -> ToolResult:
    """Recall memories relevant to the current context.
    
    Uses a combination of:
    1. Exact key match
    2. Embedding similarity search
    3. Importance ranking
    4. Recency weighting
    """
    ...
```

### Auto-Expiry

- **Short-term**: Expires when the conversation ends (or after 1 hour of inactivity)
- **Medium-term**: Expires after 7 days (configurable per project)
- **Long-term**: Never expires, but importance decays over time if not accessed

A background job runs periodically to clean expired memories and decay importance scores.

---

## 14. Database Tools

### Direct Database Manipulation

Tools for agents to interact with the database safely.

```python
# Core database tools:
# db_query       — Execute a read-only SQL query
# db_insert      — Insert rows into a table (with validation)
# db_update      — Update rows with WHERE clause
# db_upsert      — Insert or update based on key
# db_schema      — Get table schema information
# db_list_tables — List available tables

async def db_query(args: DbQueryArgs, ctx: ToolContext) -> ToolResult:
    """Execute a read-only SQL query.
    
    Safety:
    - Query is analyzed to ensure it's SELECT-only (no mutations)
    - Row limit enforced (default 100, max 1000)
    - Timeout: 10 seconds
    - RLS policies enforced via user's Supabase context
    """
    ...

async def db_insert(args: DbInsertArgs, ctx: ToolContext) -> ToolResult:
    """Insert data into a table.
    
    Safety:
    - Validates against table schema
    - Enforces RLS policies
    - Auto-sets user_id, created_at, updated_at
    - Blocked for system tables (cx_*, auth.*)
    """
    ...
```

### Allowlist/Blocklist

```python
DB_TOOL_CONFIG = {
    "blocked_tables": ["auth.*", "cx_conversation", "cx_message", "cx_user_request", "cx_request"],
    "read_only_tables": ["ai_models", "tools", "prompt_builtins"],
    "max_rows_per_query": 1000,
    "query_timeout_seconds": 10,
}
```

---

## 15. Computer Use Tools — Filesystem, Browser, Shell

### Filesystem Tools

```python
# fs_read_file     — Read a file's contents
# fs_write_file    — Write/overwrite a file
# fs_list_dir      — List directory contents
# fs_search        — Search files by name or content (ripgrep)
# fs_mkdir          — Create directories
# fs_move           — Move/rename files
# fs_delete         — Delete files (with confirmation for non-empty dirs)

async def fs_read_file(args: FsReadArgs, ctx: ToolContext) -> ToolResult:
    """Read a file from the sandboxed workspace.
    
    Safety:
    - Path sandboxed to user's workspace directory
    - Max file size: 1MB (returns truncated with warning for larger)
    - Binary files return base64 with type detection
    """
    ...
```

### Shell Tools

```python
# shell_execute    — Run a shell command in a sandboxed environment
# shell_python     — Execute Python code in an isolated subprocess

async def shell_execute(args: ShellArgs, ctx: ToolContext) -> ToolResult:
    """Execute a shell command.
    
    Safety:
    - Runs in a sandboxed Docker container or restricted subprocess
    - Timeout: 30 seconds (configurable)
    - Network access configurable per tool instance
    - Output captured (stdout + stderr, max 10KB)
    - Blocked commands: rm -rf /, format, dd, etc.
    """
    ...
```

### Browser Tools

```python
# browser_navigate  — Navigate to a URL and return page content
# browser_click     — Click an element by selector
# browser_type      — Type text into an input field
# browser_screenshot — Capture a screenshot (returns base64 image)
# browser_extract   — Extract structured data using CSS selectors

# These wrap a headless browser (Playwright/Puppeteer)
# Managed as a pool of browser contexts with automatic cleanup
```

### Workspace Isolation

Each user/conversation gets an isolated workspace:
```
/workspaces/{user_id}/{project_id}/
├── files/           # User files
├── temp/            # Tool temp files (auto-cleaned)
└── output/          # Tool output files (persisted)
```

---

## 16. Lifecycle & Cleanup

### Tool Execution Lifecycle

```python
class ToolLifecycleManager:
    """Manages cleanup of resources created during tool execution."""
    
    _cleanup_tasks: dict[str, list[Callable]] = {}  # conversation_id → cleanup functions
    
    def register_cleanup(self, conversation_id: str, cleanup_fn: Callable) -> None:
        """Register a cleanup function to run when the conversation ends."""
        ...
    
    async def cleanup_conversation(self, conversation_id: str) -> None:
        """Run all cleanup functions for a conversation.
        
        Called when:
        - Conversation explicitly ended by user
        - Conversation idle timeout (configurable, default 30 min)
        - Server shutdown (graceful)
        """
        ...
    
    async def cleanup_expired(self) -> None:
        """Background task: clean up stale resources.
        
        Runs every 5 minutes:
        - Delete temp files older than 1 hour
        - Clear tracker history for ended conversations
        - Close idle browser contexts
        - Expire short-term memories
        """
        ...
```

### What Gets Cleaned Up

| Resource | Trigger | Retention |
|----------|---------|-----------|
| Temp files in `/workspaces/.../temp/` | Conversation end or 1 hour idle | None |
| Browser contexts | Conversation end or 5 min idle | None |
| Tool tracker history (in-memory) | Conversation end | None |
| Short-term memories | Conversation end or 1 hour | None |
| Medium-term memories | 7 days after last access | Configurable |
| Tool execution logs | Never auto-deleted | 90 days (configurable) |
| Tool execution events | Never auto-deleted | 30 days (configurable) |
| Persisted tool outputs | Never auto-deleted | Permanent |

---

## 17. Data Persistence for Valuable Outputs

### When to Persist

Tools flag their output for persistence when the result is valuable:

```python
async def research_agent(args: ResearchArgs, ctx: ToolContext) -> ToolResult:
    ...
    return ToolResult(
        success=True,
        output=research_report,
        should_persist_output=True,
        persist_key=f"research:{args.topic}",
        ...
    )
```

### Where to Persist

```sql
CREATE TABLE tool_outputs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    call_id TEXT NOT NULL,
    
    persist_key TEXT,                  -- Semantic key for retrieval
    output_type TEXT DEFAULT 'text',   -- 'text', 'json', 'file', 'image'
    content TEXT,                      -- For text/json outputs
    file_path TEXT,                    -- For file/image outputs (Supabase Storage)
    
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    
    UNIQUE(conversation_id, persist_key)
);
```

### Retrieval

Agents can retrieve persisted outputs via the `memory_recall` tool or a dedicated `tool_output_retrieve` tool.

---

## 18. Migration Strategy

### Phase 0: Foundation (No Breaking Changes)

1. Create the Pydantic models (`ToolDefinition`, `ToolContext`, `ToolResult`, `ToolError`)
2. Create `ToolExecutor` class with the new pipeline
3. Create `ToolRegistryV2` that loads from DB + resolves callables
4. Wire `ToolRegistryV2.load_from_database()` into app startup

**The old system continues to work.** No tools are migrated yet.

### Phase 1: Parallel Execution Path

1. Add a feature flag: `USE_NEW_TOOL_EXECUTOR = True/False`
2. In `handle_tool_calls()`, dispatch to either old `tool_registry.execute_tool_call()` or new `ToolExecutor.execute()`
3. Migrate one simple tool (e.g., `core_math_calculate`) to the new system as a proof of concept
4. Validate that results are identical

### Phase 2: Migrate Core Tools

1. Migrate all tools to the new `async def tool(args, ctx) -> ToolResult` signature
2. For backward compatibility, tools can still return `dict` — the executor normalizes it
3. Remove thin wrapper functions (e.g., the `web_search_summarized()` in `web.py` that just calls `search_web_mcp_summarized()`)
4. Replace `summarize_scrape_pages_agent_DEPRECATED()` legacy call with proper agent-as-tool invocation

### Phase 3: New Capabilities

1. External MCP client
2. Agent-as-tool registration
3. Memory tools
4. Database tools
5. Computer use tools (filesystem, shell, browser)

### Phase 4: Cleanup

1. Remove old `mcp_server/core/registry.py`, `mcp_server/core/tracker.py`
2. Remove all `register_*_tool()` functions
3. Remove `mcp_server/local_utils/tools_constants.tsx` (frontend reads from DB)
4. Archive old `mcp_server/tools/` wrappers
5. Update `handle_tool_calls()` to only use `ToolExecutor`

---

## 19. New File Structure

```
ai/
├── config/
│   ├── unified_config.py          # Existing — keep as-is
│   ├── tools_config.py            # Existing — keep ToolCallContent, ToolResultContent
│   └── TOOL_OVERHAUL_PLAN.md      # This file
│
├── tools/                          # NEW — replaces mcp_server/
│   ├── __init__.py                # Exports ToolExecutor, ToolRegistryV2
│   ├── models.py                  # ToolDefinition, ToolContext, ToolResult, ToolError, ToolExecutionLog
│   ├── registry.py                # ToolRegistryV2 — loads from DB, resolves callables
│   ├── executor.py                # ToolExecutor — the single execution pipeline
│   ├── guardrails.py              # GuardrailEngine — rate limits, loop detection, cost caps
│   ├── streaming.py               # ToolStreamManager, ToolStreamEvent
│   ├── logger.py                  # ToolExecutionLogger — writes to tool_execution_logs
│   ├── lifecycle.py               # ToolLifecycleManager — cleanup and resource management
│   ├── external_mcp.py            # ExternalMCPClient — calls remote MCP servers
│   ├── agent_tool.py              # Agent-as-tool execution logic
│   │
│   ├── implementations/           # Actual tool functions (replaces mcp_server/tools/)
│   │   ├── __init__.py
│   │   ├── web.py                 # web_search_v1, web_read_v1, etc.
│   │   ├── database.py            # db_query, db_insert, db_schema, etc.
│   │   ├── filesystem.py          # fs_read, fs_write, fs_search, etc.
│   │   ├── shell.py               # shell_execute, shell_python
│   │   ├── browser.py             # browser_navigate, browser_click, etc.
│   │   ├── memory.py              # memory_store, memory_recall, etc.
│   │   ├── math.py                # calculate
│   │   ├── text.py                # analyze, regex_extract
│   │   ├── code.py                # python_execute, html_store
│   │   ├── data.py                # user_lists, seo_tools
│   │   └── news.py                # fetch_headlines
│   │
│   └── arg_models/                # Pydantic models for tool arguments
│       ├── __init__.py
│       ├── web_args.py            # WebSearchArgs, WebReadArgs
│       ├── db_args.py             # DbQueryArgs, DbInsertArgs
│       ├── fs_args.py             # FsReadArgs, FsWriteArgs
│       ├── memory_args.py         # MemoryStoreArgs, MemoryRecallArgs
│       └── shell_args.py          # ShellArgs, PythonArgs
```

---

## 20. Implementation Phases

### Phase 0 — Foundation (Week 1)

| Task | Effort | Priority |
|------|--------|----------|
| Create `ai/tools/models.py` with all Pydantic models | 1 day | P0 |
| Create `ai/tools/registry.py` (ToolRegistryV2) | 1 day | P0 |
| Create `ai/tools/executor.py` (ToolExecutor) | 2 days | P0 |
| Create `ai/tools/streaming.py` (ToolStreamManager) | 0.5 day | P0 |
| Create `tool_execution_logs` DB table | 0.5 day | P0 |
| Create `ai/tools/logger.py` | 0.5 day | P0 |

### Phase 1 — Parallel Path + First Migration (Week 2)

| Task | Effort | Priority |
|------|--------|----------|
| Feature flag in `handle_tool_calls()` | 0.5 day | P0 |
| Migrate `core_math_calculate` as proof of concept | 0.5 day | P0 |
| Migrate `text_analyze`, `text_regex_extract` | 0.5 day | P1 |
| Validate identical results for migrated tools | 0.5 day | P0 |
| Create `ai/tools/guardrails.py` with basic checks | 1 day | P1 |

### Phase 2 — Core Tool Migration (Week 3-4)

| Task | Effort | Priority |
|------|--------|----------|
| Migrate all web tools (`web_search_*`, `web_read_*`) | 2 days | P0 |
| Replace `summarize_scrape_pages_agent_DEPRECATED()` with agent-as-tool pattern | 1 day | P0 |
| Migrate data tools (SQL, user_lists, SEO) | 1 day | P1 |
| Migrate code tools (python_execute, html_store) | 1 day | P1 |
| Create `tool_execution_events` DB table | 0.5 day | P1 |
| Create `ai/tools/lifecycle.py` | 1 day | P2 |

### Phase 3 — New Capabilities (Week 5-6)

| Task | Effort | Priority |
|------|--------|----------|
| Agent-as-tool system | 2 days | P0 |
| External MCP client | 2 days | P1 |
| Memory tools + `agent_memory` table | 2 days | P1 |
| Database manipulation tools | 1 day | P1 |
| Filesystem tools | 1 day | P2 |
| Shell tools (sandboxed) | 1 day | P2 |
| Browser tools (Playwright pool) | 2 days | P2 |

### Phase 4 — Cleanup (Week 7)

| Task | Effort | Priority |
|------|--------|----------|
| Remove old `mcp_server/core/registry.py` | 0.5 day | P0 |
| Remove all `register_*_tool()` blocks | 0.5 day | P0 |
| Remove thin wrapper functions | 0.5 day | P0 |
| Remove `tools_constants.tsx` + add DB-driven frontend | 1 day | P1 |
| Remove old `mcp_server/core/tracker.py` | 0.5 day | P0 |
| Final integration tests | 1 day | P0 |
| Documentation and handoff | 0.5 day | P1 |

---

## Summary of Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Pydantic models for everything** | Validation, serialization, JSON Schema generation, IDE support — all free |
| **Database as metadata authority** | Single source of truth for tool definitions. No more 3-way sync |
| **`ToolContext` replaces `inspect.signature()`** | Explicit > magic. Every tool gets the same context object |
| **Single `ToolExecutor` pipeline** | All tools (local, external MCP, agent) go through the same path |
| **`ToolResult` with structured errors** | Models get actionable error messages, not opaque strings |
| **Guardrails at the executor level** | Not scattered across tools. Centralized, configurable, auditable |
| **Streaming via `ToolStreamManager`** | Consistent UI updates, dual-write to client + DB for replay |
| **`tool_execution_logs` table** | Full observability — costs, timing, error rates, patterns |
| **Agent-as-tool via `ToolType.AGENT`** | Same execution path, with automatic child usage aggregation |
| **Backward compatibility during migration** | Feature flags, dual paths, tools can return old `dict` format |

---

## Appendix: Current Call Chain vs. New Call Chain

### Current (6 layers)

```
1. handle_tool_calls()           → extracts ToolCallContent from response
2. tool_registry.execute_tool_call()  → converts ToolCallContent to dict
3. tool_registry.execute_tool()       → inspect.signature(), inject params
4. web_search_summarized()            → thin wrapper, extracts args
5. search_web_mcp_summarized()        → actual business logic
6. summarize_scrape_pages_agent_DEPRECATED()                       → LEGACY GoogleChatEndpoint (untracked)
```

### New (2 layers)

```
1. handle_tool_calls() → extracts ToolCallContent from response
2. ToolExecutor.execute() → validates, builds context, dispatches:
   └── web_search_v1(args, ctx) → direct business logic with context
       └── (if AI needed) child agent via agent_tool.execute_agent() → tracked, streamed
```

The intermediate layers (dict conversion, inspect.signature, thin wrappers) are eliminated entirely. The business logic functions receive validated Pydantic arguments and a rich context object directly.
