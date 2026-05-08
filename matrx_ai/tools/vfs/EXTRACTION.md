# Extracting the VFS into another codebase

A focused, copy-pasteable guide. For the broader architecture doc, see
[README.md](./README.md). For a runnable end-to-end example, see
[../../../examples/embed_vfs.py](../../../examples/embed_vfs.py).

## What you're copying

Just the `matrx_ai/tools/vfs/` directory. It is a fully self-contained Python
package; an AST-level test (`tests/vfs/test_package_isolation.py`) gates this
guarantee in CI.

**Do NOT copy** these — they're matrx-ai-specific adapter glue, not part of
the package:

- `matrx_ai/tools/implementations/vfs_filesystem.py`
- `matrx_ai/tools/implementations/vfs_shell.py`
- `matrx_ai/tools/vfs_routing.py`
- `matrx_ai/tools/arg_models/fs_args.py` and `shell_args.py`

You'll write thin equivalents tailored to your project's tool surface (see
[Adapter pattern](#adapter-pattern) below).

## Required dependencies

Add these four to your `pyproject.toml`. No others.

```toml
dependencies = [
    "fsspec >= 2026.4.0",   # async filesystem framework
    "wcmatch >= 10.0",      # bash-grade globbing (** / extglob / brace)
    "pathspec >= 1.0.0",    # gitignore-style path filtering
    "pydantic >= 2.10",     # Inode model + arg models
]
```

Python `>= 3.13` recommended (uses `from __future__ import annotations`,
PEP 695 type syntax in some files, structural Protocols).

## Five-command extraction

```bash
# Substitute YOUR_PKG with your package name (e.g. "my_app").

# 1. Copy the package
cp -r /path/to/matrx-ai/matrx_ai/tools/vfs YOUR_PKG/vfs

# 2. Rewrite the import root
find YOUR_PKG/vfs -name '*.py' -exec \
    sed -i 's|matrx_ai\.tools\.vfs|YOUR_PKG.vfs|g' {} \;

# 3. (Optional) rename the env-var prefix
find YOUR_PKG/vfs -name '*.py' -exec \
    sed -i 's|MATRX_VFS_|YOUR_VFS_|g' {} \;

# 4. Copy the tests
cp -r /path/to/matrx-ai/tests/vfs YOUR_PKG/tests/vfs
find YOUR_PKG/tests/vfs -name '*.py' -exec \
    sed -i 's|matrx_ai\.tools\.vfs|YOUR_PKG.vfs|g' {} \;

# 5. (Optional) copy the Postgres schema if you want the durable backend
cp /path/to/matrx-ai/migrations/0050_vfs_inode_blob.sql YOUR_PKG/migrations/
```

## Verify

```bash
pytest YOUR_PKG/tests/vfs -q          # ~1000 unit tests + fidelity harness
python YOUR_PKG/examples/embed_vfs.py # if you copied it (see below)
```

You should see ~1000 passes and a few expected `xfail` entries from the real-
vs-virtual fidelity harness (timestamp-dependent comparisons).

## Minimal usage

```python
from YOUR_PKG.vfs import (
    make_vfs, VfsCommandRunner, ShellEnv,
    parse, execute, load_all,
)

load_all()                                  # registers ~50 virtual commands

fs = await make_vfs("workspace-id")         # MemoryBackend by default
await fs._pipe_file("/hello.txt", b"hi\n")

runner = VfsCommandRunner(fs)
env = ShellEnv()
result = await execute(
    parse("cat /hello.txt | tr a-z A-Z"),
    env, runner, capture=True,
)
print(result.stdout)                        # b"HI\n"
```

For the full demo (file creation, ls -la, grep -rn, find, error-path
behaviour), see [`examples/embed_vfs.py`](../../../examples/embed_vfs.py).

## Adapter pattern

Anything with `.user_id` and `.conversation_id` attributes satisfies the
package's only context contract (`WorkspaceContext` Protocol). Your project's
tool-context type satisfies it structurally; no inheritance or registration
required.

Minimal adapter that ports the matrx-ai `fs_read` tool to a hypothetical
`my_app.tools` surface:

```python
from YOUR_PKG.vfs import get_workspace_fs

async def fs_read(args: dict, ctx: MyToolContext) -> MyToolResult:
    vfs = await get_workspace_fs(ctx)       # ctx satisfies WorkspaceContext
    path = args["path"] if args["path"].startswith("/") else "/" + args["path"]
    try:
        data = await vfs._cat_file(path)
    except FileNotFoundError:
        return MyToolResult.error("not_found", f"File not found: {path}")
    return MyToolResult.ok({"content": data.decode("utf-8", errors="replace")})
```

If your project doesn't have a `user_id`/`conversation_id` notion, derive a
workspace_id any way you like and use `get_workspace_fs_by_id(workspace_id)`
instead — it skips the Protocol entirely.

## Backends

- **Memory** — default. Single-process, in-memory, ephemeral.
- **Postgres** — stub in this repo; schema in `migrations/0050_vfs_inode_blob.sql`.
  Wire `backends/postgres.py` to your DB layer of choice.
- **Custom** — satisfy the `AbstractBackend` Protocol in `core.py`.

Selection is via `MATRX_VFS_BACKEND=memory|postgres` (or your renamed
equivalent). Caching is automatic via `CachingBackend` in `get_backend()`.

## What's in the box

| Capability | Module |
|---|---|
| ~50 virtual GNU commands (ls/cat/grep/find/sed/awk/tar/...) | `commands/<name>.py` |
| Bash parser (pipes, redirects, &&/||, heredocs, globs, $vars) | `shell/{lexer,parser,expansion,executor}.py` |
| Byte-exact GNU coreutils output formatters | `mimicry/{ls,stat,grep,coreutils_errors,...}.py` |
| Anthropic / Claude Code error wording | `mimicry/claude_tool.py` |
| Python traceback emitter (CPython 3.13 byte-exact) | `mimicry/traceback.py` |
| In-memory inode store | `backends/memory.py` |
| LRU + in-flight-dedupe cache | `cache.py` |
| fsspec-compatible async FS class | `core.py` |
| Workspace bootstrap + Protocol | `workspace.py` |
| Public API surface | `__init__.py` |

## CI tripwires that protect the extraction story

These tests live in `tests/vfs/test_package_isolation.py`. If a future
contributor introduces coupling, CI fails:

- `test_no_external_matrx_imports_in_vfs_source` — grep for `from matrx_ai`
  outside vfs itself; must find none.
- `test_ast_level_cleanliness` — full AST scan with relative-import handling.
- `test_external_dependency_set_is_minimal` — third-party deps must be a
  subset of `{fsspec, wcmatch, pathspec, pydantic}`.
- `test_minimal_embedded_usage` — the package functions standalone.
- `test_workspace_protocol_satisfaction` — a bare dataclass satisfies the
  context contract.

Copy these tests too (Step 4 above) — they're equally valuable in your fork.
