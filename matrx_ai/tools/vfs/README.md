# Virtual Filesystem (VFS)

A drop-in replacement for the real disk + bash that an AI coding model would
otherwise interact with. Backed by an in-memory inode store (or, optionally,
Postgres) and wired so the model sees byte-identical GNU coreutils output and
exact Anthropic / Claude Code error wording. Models pattern-match on strings
like `No such file or directory`, `Is a directory`, `String to replace not
found in file.` to decide retry vs. pivot, so fidelity is the design goal.

This package is **fully self-contained.** It depends only on `fsspec`,
`wcmatch`, `pathspec`, and `pydantic`. It does NOT import anything from
elsewhere in `matrx_ai`. The matrx-ai-specific glue lives outside this
directory (see "Adapter layer" below).

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Adapter layer            (LIVES OUTSIDE THIS PACKAGE)           │
│  matrx_ai/tools/implementations/vfs_filesystem.py                │
│  matrx_ai/tools/implementations/vfs_shell.py                     │
│  matrx_ai/tools/vfs_routing.py                                   │
│  Translates ToolContext → WorkspaceContext, ToolResult shape,    │
│  plus the registry switch-flip wiring.                           │
└──────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  vfs/ — public API                                               │
│  __init__.py exports MatrxAsyncFS, MemoryBackend, parse, execute │
│                                                                  │
│  Mimicry layer    mimicry/{ls,stat,grep,cat,traceback,           │
│                            coreutils_errors,claude_tool,...}.py  │
│   • Pure functions; emit byte-exact GNU / Claude tool strings    │
│                                                                  │
│  Shell parser     shell/{lexer,parser,expansion,executor,env,    │
│                          heredoc,ast,runner}.py                  │
│   • Tokenize → AST → expand → execute. Handles pipes, redirects, │
│     globs, heredocs, brace/var/cmd substitution, &&/||           │
│                                                                  │
│  Commands         commands/<name>.py × ~50                       │
│   • One file per virtual GNU command. Self-register via          │
│     @register("name") into a module-level dispatch table.        │
│                                                                  │
│  Core fsspec FS   core.py + paths.py + errors.py                 │
│   • MatrxAsyncFS subclass. Raises real OSError subclasses with   │
│     proper errno (ENOENT=2, EISDIR=21, etc.).                    │
│                                                                  │
│  Cache            cache.py (LRU, in-flight-dedupe, byte-bounded  │
│                            blob cache)                           │
│                                                                  │
│  Backends         backends/memory.py — in-process (default)      │
│                   backends/postgres.py — durable store (stub)    │
└──────────────────────────────────────────────────────────────────┘
```

## Quick start

```python
from matrx_ai.tools.vfs import (
    MemoryBackend, MatrxAsyncFS, VfsCommandRunner,
    ShellEnv, parse, execute, load_all, make_vfs,
)

load_all()  # registers all ~50 virtual commands

fs = await make_vfs("alice:session-1")
await fs._pipe_file("/hello.txt", b"world\n")

runner = VfsCommandRunner(fs)
env = ShellEnv()
node = parse("cat /hello.txt | tr a-z A-Z")
result = await execute(node, env, runner, capture=True)
print(result.stdout)  # b"WORLD\n"
```

## Workspaces

Every `MatrxAsyncFS` instance is scoped to a `workspace_id` string. Inodes
are isolated per workspace; two workspaces with the same path stay distinct.
The convenience helper `get_workspace_fs(ctx)` derives a workspace_id from
any object satisfying the `WorkspaceContext` Protocol:

```python
class WorkspaceContext(Protocol):
    user_id: str | None
    conversation_id: str | None
```

The default mapping is `f"{user_id or 'anonymous'}:{conversation_id or 'default'}"`.
Pass a different scoping if your application has different boundaries.

## Backends

- **MemoryBackend** (default) — single-process, in-memory. Good for tests,
  ephemeral conversations, and stateless deployments.
- **PostgresBackend** (stub in this repo) — durable inode + blob storage.
  See `migrations/0050_vfs_inode_blob.sql` for the schema.
- **CachingBackend** — LRU wrapper around any `AbstractBackend` with
  `asyncio.Future`-based in-flight read dedupe. Used in front of both
  backends by default in `get_backend()`.

To plug in your own backend, satisfy the `AbstractBackend` Protocol in
`core.py`.

## Dependencies

```toml
fsspec  >= 2026.4.0   # async filesystem framework
wcmatch >= 10.0       # bash-grade globbing (** / extglob / brace)
pathspec >= 1.0.0     # gitignore-style path filtering
pydantic >= 2.10      # Inode model + arg models
```

Standard library: `asyncio`, `dataclasses`, `re`, `shlex`, `pathlib`, `gzip`,
`tarfile`, `zipfile`, `difflib`, `tempfile`. No OS-specific calls.

## Extraction recipe

To lift this package into another project (`your_pkg/vfs/`):

```bash
# 1. Copy the package
cp -r matrx_ai/tools/vfs your_pkg/

# 2. Rename the import root
find your_pkg/vfs -type f -name '*.py' \
    -exec sed -i 's|matrx_ai\.tools\.vfs|your_pkg.vfs|g' {} \;

# 3. Rename the env-var prefix if you want (optional)
find your_pkg/vfs -type f -name '*.py' \
    -exec sed -i 's|MATRX_VFS_|YOUR_VFS_|g' {} \;

# 4. Add the four runtime deps to your pyproject.toml
#    (fsspec, wcmatch, pathspec, pydantic)

# 5. Copy the migration if you want Postgres
cp migrations/0050_vfs_inode_blob.sql your_pkg/migrations/

# 6. Run the test suite to confirm
cp -r tests/vfs your_pkg/tests/
pytest your_pkg/tests/vfs -v
```

The Postgres backend is a stub — wire it to your DB layer of choice.

If you want your own model-tool adapter (the equivalent of `vfs_filesystem.py`
and `vfs_shell.py`), see `examples/embed_vfs.py` for a 30-line minimum.

## What lives where

| Concern | Module |
|---|---|
| Public API surface | `__init__.py` |
| FSS-level VFS class | `core.py` |
| Path normalization, Inode dataclass | `paths.py` |
| OSError raisers (ENOENT/EISDIR/etc.) | `errors.py` |
| Caching layer | `cache.py` |
| Per-workspace FS bootstrap | `workspace.py` |
| In-memory inode store | `backends/memory.py` |
| Postgres inode store (stub) | `backends/postgres.py` |
| Bash lexer / parser / executor | `shell/{lexer,parser,executor,...}.py` |
| Shell environment ($PWD, $?, etc.) | `shell/env.py` |
| Bash → command dispatch protocol | `shell/runner.py` |
| Per-command implementations | `commands/<name>.py` |
| Command registry + dispatcher | `commands/registry.py`, `commands/runner.py` |
| GNU coreutils output formatters | `mimicry/ls.py`, `mimicry/stat.py`, ... |
| Anthropic / Claude Code wording | `mimicry/claude_tool.py` |
| GNU error string emitters | `mimicry/coreutils_errors.py` |
| Python traceback formatter | `mimicry/traceback.py` |

## Testing

Three suites:

```bash
# Unit tests for individual layers (~990 tests)
pytest tests/vfs

# Real-vs-virtual fidelity harness — compares output of every command against
# the host Linux's GNU coreutils via subprocess (~70 tests)
pytest tests/vfs/fidelity

# Adapter-level integration with the matrx-ai tool surface (~25 tests)
pytest tests/tools/test_vfs_adapters.py
```

The fidelity suite is the most valuable safety net for fidelity drift — it
catches any deviation from real coreutils output / exit codes / error wording.

## Switch-flip (matrx-ai integration)

Set `MATRX_VFS_ENABLED=1` to route `fs_read`/`fs_write`/`fs_list`/`fs_search`/
`fs_mkdir`/`shell_execute` through the VFS-backed adapters and surface a new
`fs_edit` tool. Per-tool override via `tools.source_app == 'matrx_vfs'` in the
DB. With the env var unset, behavior is identical to before. See
`matrx_ai/tools/vfs_routing.py`.
