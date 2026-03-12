"""
sync_from_aidream.py — Bidirectional sync between aidream/ai and matrx_ai.

Copies shared AI engine files from aidream → matrx-ai (or matrx-ai → aidream),
then applies mechanical import path transformations so the files work in the
destination without manual edits.

DIRECTORY MAPPING (AI engine sync)
-----------------------------------
aidream/ai/<subdir>/        ↔   matrx-ai/matrx_ai/<subdir>/
aidream/aidream/api/        ↔   matrx-ai/matrx_ai/app/  (NOT synced — differs intentionally)

DIRECTORY MAPPING (API core sync, matrx-ai → aidream only)
------------------------------------------------------------
matrx-ai/matrx_ai/context/           →  aidream/aidream/api/context/
matrx-ai/matrx_ai/app/core/          →  aidream/aidream/api/core/
matrx-ai/matrx_ai/app/middleware/auth.py    →  aidream/aidream/api/middleware/auth.py
matrx-ai/matrx_ai/app/dependencies/auth.py →  aidream/aidream/api/dependencies/auth.py

IMPORT SUBSTITUTION RULES (aidream → matrx-ai)
-----------------------------------------------
  ai.<pkg>                     →  matrx_ai.<pkg>
  aidream.api.emitter_protocol  →  matrx_ai.context.emitter_protocol
  aidream.api.events            →  matrx_ai.context.events
  ai.db.*                       →  matrx_ai.db.custom.*
  db.models                     →  matrx_ai.db.models
  db.managers.*                 →  matrx_ai.db.managers.*
  db.custom.*                   →  matrx_ai.db.custom.*
  matrix.ai_models.*            →  matrx_ai.db.custom.ai_models.*
  common.utils...FileHandler    →  matrx_utils.FileHandler
  f"ai.{function_path}"         →  f"matrx_ai.{function_path}"  (tool registry)

Reverse substitutions are applied automatically when direction is matrx-ai → aidream.

USAGE
-----
  # Pull latest from aidream into matrx-ai (default):
  python scripts/sync_from_aidream.py

  # Dry run — show what would change without writing:
  python scripts/sync_from_aidream.py --dry-run

  # Push matrx-ai changes back to aidream:
  python scripts/sync_from_aidream.py --direction matrx-to-aidream

  # Push API core layer from matrx-ai → aidream:
  python scripts/sync_from_aidream.py --sync-core

  # Push everything (AI engine + core) from matrx-ai → aidream:
  python scripts/sync_from_aidream.py --direction matrx-to-aidream --sync-core

  # Sync only specific subdirectories:
  python scripts/sync_from_aidream.py --only orchestrator providers

  # Show a diff of what would change:
  python scripts/sync_from_aidream.py --dry-run --diff

  # Auto-modernize type hints after syncing (aidream-to-matrx only):
  python scripts/sync_from_aidream.py --modernize-types
"""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
AIDREAM_ROOT = REPO_ROOT.parent / "aidream"
MATRX_AI_ROOT = REPO_ROOT / "matrx_ai"
AIDREAM_API_ROOT = AIDREAM_ROOT / "aidream" / "api"

# Subdirectories of aidream/ai/ that are synced 1:1 with matrx_ai/
# Omit: app/ (differs intentionally), db/ (separate solution), context/ (lives in aidream/api/)
SHARED_SUBDIRS = [
    "agent_runners",
    "agents",
    "config",
    "instructions",
    "media",
    "orchestrator",
    "processing",
    "providers",
    "tools",
    "utils",
]

# Files that must NOT be overwritten by core sync.
# ai_task.py is excluded because it contains AI engine imports (matrx_ai.config,
# matrx_ai.orchestrator, matrx_ai.agents) that need the full AIDREAM_TO_MATRX
# substitution table — it is handled by the regular AI engine sync instead.
CORE_SKIP_FILES: frozenset[str] = frozenset({
    "request_log.py",
    "test_context.py",
    "app.py",
    "ai_task.py",
})

# ---------------------------------------------------------------------------
# Import substitution rules
# Each rule is (pattern_to_find, replacement) as plain strings applied via
# str.replace(). Order matters — more specific rules go first.
# ---------------------------------------------------------------------------

# aidream → matrx-ai
AIDREAM_TO_MATRX: list[tuple[str, str]] = [
    # Cross-package references: aidream.api → matrx_ai.context
    ("from aidream.api.emitter_protocol import", "from matrx_ai.context.emitter_protocol import"),
    ("from aidream.api.events import", "from matrx_ai.context.events import"),
    ("from aidream.api.middleware.context import", "from matrx_ai.context.app_context import"),
    # DB path deepening: ai.db. → matrx_ai.db.custom.
    ("from ai.db.cx_managers import", "from matrx_ai.db.custom.cx_managers import"),
    ("from ai.db.persistence import", "from matrx_ai.db.custom.persistence import"),
    ("from ai.db.conversation_gate import", "from matrx_ai.db.custom.conversation_gate import"),
    ("from ai.db.conversation_rebuild import", "from matrx_ai.db.custom.conversation_rebuild import"),
    ("from ai.db import", "from matrx_ai.db.custom import"),
    ("import ai.db.", "import matrx_ai.db.custom."),
    # Bare `matrix.` imports — aidream has matrix/ at repo root; matrx-ai has it under matrx_ai/db/custom/
    ("from matrix.ai_models.ai_model_manager import", "from matrx_ai.db.custom.ai_models.ai_model_manager import"),
    ("from matrix.ai_models.", "from matrx_ai.db.custom.ai_models."),
    ("from matrix.", "from matrx_ai.db.custom."),
    ("import matrix.", "import matrx_ai.db.custom."),
    # Bare `db.` imports — aidream has db/ at repo root; matrx-ai has it under matrx_ai/db/
    ("from db.managers.prompt_builtins import", "from matrx_ai.db.managers.prompt_builtins import"),
    ("from db.managers.prompts import", "from matrx_ai.db.managers.prompts import"),
    ("from db.managers.content_blocks import", "from matrx_ai.db.managers.content_blocks import"),
    ("from db.managers.tools import", "from matrx_ai.db.managers.tools import"),
    ("from db.managers.table_fields import", "from matrx_ai.db.managers.table_fields import"),
    ("from db.managers.table_data import", "from matrx_ai.db.managers.table_data import"),
    ("from db.managers.user_tables import", "from matrx_ai.db.managers.user_tables import"),
    ("from db.managers.ai_model import", "from matrx_ai.db.managers.ai_model import"),
    ("from db.managers.", "from matrx_ai.db.managers."),
    ("from db.models import", "from matrx_ai.db.models import"),
    ("from db.custom.", "from matrx_ai.db.custom."),
    ("import db.models", "import matrx_ai.db.models"),
    ("import db.managers", "import matrx_ai.db.managers"),
    # aidream common.utils → matrx_utils / matrx_ai.utils
    ("from common.utils.file_handlers.file_handler import FileHandler", "from matrx_utils import FileHandler"),
    ("from common.supabase.supabase_client import", "from matrx_ai.utils.supabase_client import"),
    # Root package rename: ai. → matrx_ai.
    ("from ai.", "from matrx_ai."),
    ("import ai.", "import matrx_ai."),
    # f-string package prefix in tool registry path resolution
    ('f"ai.{function_path}"', 'f"matrx_ai.{function_path}"'),
]

# matrx-ai → aidream (exact reversal)
MATRX_TO_AIDREAM: list[tuple[str, str]] = [
    ("from matrx_ai.context.emitter_protocol import", "from aidream.api.emitter_protocol import"),
    ("from matrx_ai.context.events import", "from aidream.api.events import"),
    ("from matrx_ai.context.app_context import", "from aidream.api.middleware.context import"),
    ("from matrx_ai.db.custom.cx_managers import", "from ai.db.cx_managers import"),
    ("from matrx_ai.db.custom.persistence import", "from ai.db.persistence import"),
    ("from matrx_ai.db.custom.conversation_gate import", "from ai.db.conversation_gate import"),
    ("from matrx_ai.db.custom.conversation_rebuild import", "from ai.db.conversation_rebuild import"),
    ("from matrx_ai.db.custom import", "from ai.db import"),
    ("import matrx_ai.db.custom.", "import ai.db."),
    # Reverse matrix.* rules
    ("from matrx_ai.db.custom.ai_models.ai_model_manager import", "from matrix.ai_models.ai_model_manager import"),
    ("from matrx_ai.db.custom.ai_models.", "from matrix.ai_models."),
    ("from matrx_ai.db.custom.", "from matrix."),
    # Reverse bare db.* rules
    ("from matrx_ai.db.managers.", "from db.managers."),
    ("from matrx_ai.db.models import", "from db.models import"),
    ("from matrx_ai.db.custom.", "from db.custom."),
    ("import matrx_ai.db.models", "import db.models"),
    ("import matrx_ai.db.managers", "import db.managers"),
    # matrx_utils → common.utils
    ("from matrx_utils import FileHandler", "from common.utils.file_handlers.file_handler import FileHandler"),
    ("from matrx_ai.utils.supabase_client import", "from common.supabase.supabase_client import"),
    ("from matrx_ai.", "from ai."),
    ("import matrx_ai.", "import ai."),
    # f-string package prefix in tool registry path resolution
    ('f"matrx_ai.{function_path}"', 'f"ai.{function_path}"'),
]

# matrx-ai → aidream/api/ (core layer sync — keeps aidream.api.* paths)
CORE_MATRX_TO_AIDREAM: list[tuple[str, str]] = [
    # context package: matrx_ai.context.* → aidream.api.context.*
    ("from matrx_ai.context._log import", "from aidream.api.context._log import"),
    ("from matrx_ai.context.app_context import", "from aidream.api.context.app_context import"),
    ("from matrx_ai.context.emitter_protocol import", "from aidream.api.context.emitter_protocol import"),
    ("from matrx_ai.context.events import", "from aidream.api.context.events import"),
    ("from matrx_ai.context.stream_emitter import", "from aidream.api.context.stream_emitter import"),
    ("from matrx_ai.context.console_emitter import", "from aidream.api.context.console_emitter import"),
    ("from matrx_ai.context import", "from aidream.api.context import"),
    # app.core: matrx_ai.app.core.* → aidream.api.core.*
    ("from matrx_ai.app.core.cancellation import", "from aidream.api.core.cancellation import"),
    ("from matrx_ai.app.core.exceptions import", "from aidream.api.core.exceptions import"),
    ("from matrx_ai.app.core.middleware import", "from aidream.api.core.middleware import"),
    ("from matrx_ai.app.core.response import", "from aidream.api.core.response import"),
    ("from matrx_ai.app.core.sentry import", "from aidream.api.core.sentry import"),
    ("from matrx_ai.app.core.streaming import", "from aidream.api.core.streaming import"),
    ("from matrx_ai.app.core import", "from aidream.api.core import"),
    # middleware.auth: matrx_ai.app.middleware.auth → aidream.api.middleware.auth
    ("from matrx_ai.app.middleware.auth import", "from aidream.api.middleware.auth import"),
    # dependencies.auth: matrx_ai.app.dependencies.auth → aidream.api.dependencies.auth
    ("from matrx_ai.app.dependencies.auth import", "from aidream.api.dependencies.auth import"),
    # config: matrx_ai.app.config → aidream.api.config
    ("from matrx_ai.app.config import", "from aidream.api.config import"),
    # orjson is not installed in aidream — replace with stdlib json.
    # ORJSONResponse → JSONResponse (FastAPI built-in, no extra dep).
    ("import orjson", "import json"),
    ("orjson.dumps(", "json.dumps("),
    ("from fastapi.responses import ORJSONResponse", "from fastapi.responses import JSONResponse"),
    ("-> ORJSONResponse:", "-> JSONResponse:"),
    ("return ORJSONResponse(", "return JSONResponse("),
    # ndjson_generator: orjson.dumps returns bytes; json.dumps returns str — must encode
    ("yield orjson.dumps(chunk) + b\"\\n\"", "yield (json.dumps(chunk) + \"\\n\").encode()"),
    ("yield json.dumps(chunk) + b\"\\n\"", "yield (json.dumps(chunk) + \"\\n\").encode()"),
]


# ---------------------------------------------------------------------------
# Core transformation
# ---------------------------------------------------------------------------

def transform_source(source: str, rules: list[tuple[str, str]]) -> tuple[str, int]:
    """Apply substitution rules to Python source. Returns (new_source, change_count)."""
    result = source
    changes = 0
    for find, replace in rules:
        count = result.count(find)
        if count:
            result = result.replace(find, replace)
            changes += count
    return result, changes


def transform_file(
    src: Path,
    dst: Path,
    rules: list[tuple[str, str]],
    dry_run: bool,
    show_diff: bool,
) -> tuple[bool, bool]:
    """
    Copy src → dst applying import transformations.
    Returns (file_was_written, file_was_changed).
    """
    source = src.read_text(encoding="utf-8")
    transformed, change_count = transform_source(source, rules)

    dst_exists = dst.exists()
    dst_content = dst.read_text(encoding="utf-8") if dst_exists else ""
    content_changed = transformed != dst_content

    if not content_changed:
        return False, False

    if show_diff:
        diff = difflib.unified_diff(
            dst_content.splitlines(keepends=True),
            transformed.splitlines(keepends=True),
            fromfile=f"current: {dst.relative_to(REPO_ROOT) if dst.is_relative_to(REPO_ROOT) else dst}",
            tofile=f"incoming: {src.relative_to(src.anchor)}",
            n=3,
        )
        sys.stdout.writelines(diff)

    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(transformed, encoding="utf-8")

    label = "(import rewrites)" if change_count else "(content differs, no import changes)"
    tag = "[DRY RUN] " if dry_run else ""
    print(f"  {tag}{'WRITE' if not dry_run else 'WOULD WRITE'}: {dst.name}  {label}")

    return True, True


def sync_directory(
    src_dir: Path,
    dst_dir: Path,
    rules: list[tuple[str, str]],
    dry_run: bool,
    show_diff: bool,
    skip_patterns: frozenset[str],
    skip_filenames: frozenset[str] = frozenset(),
) -> tuple[int, int]:
    """Sync all .py files from src_dir into dst_dir. Returns (written, skipped)."""
    written = 0
    skipped = 0

    src_py_files = sorted(src_dir.rglob("*.py"))
    for src_file in src_py_files:
        rel = src_file.relative_to(src_dir)
        if any(part in skip_patterns for part in rel.parts):
            skipped += 1
            continue
        if src_file.name in skip_filenames:
            skipped += 1
            continue

        dst_file = dst_dir / rel
        was_written, _ = transform_file(src_file, dst_file, rules, dry_run, show_diff)
        if was_written:
            written += 1

    return written, skipped


def remove_orphans(src_dir: Path, dst_dir: Path, dry_run: bool) -> int:
    """Remove .py files in dst_dir that no longer exist in src_dir."""
    removed = 0
    if not dst_dir.exists():
        return 0
    for dst_file in sorted(dst_dir.rglob("*.py")):
        rel = dst_file.relative_to(dst_dir)
        src_file = src_dir / rel
        if not src_file.exists():
            tag = "[DRY RUN] " if dry_run else ""
            print(f"  {tag}REMOVE orphan: {dst_file.name}")
            if not dry_run:
                dst_file.unlink()
            removed += 1
    return removed


# ---------------------------------------------------------------------------
# Core layer sync (matrx-ai → aidream only)
# ---------------------------------------------------------------------------

# Mapping: (src_relative_to_matrx_ai, dst_relative_to_aidream_api)
# Each entry is either a directory-to-directory mapping or a file-to-file mapping.
CORE_SYNC_MAPPINGS: list[tuple[str, str, bool]] = [
    # (src_path, dst_path, is_directory)
    ("context",              "context",              True),
    ("app/core",             "core",                 True),
    ("app/middleware/auth.py", "middleware/auth.py", False),
    ("app/dependencies/auth.py", "dependencies/auth.py", False),
]


def sync_core_layer(dry_run: bool, show_diff: bool) -> int:
    """Push the shared API core from matrx_ai → aidream/api/.

    Returns the total number of files written.
    """
    if not AIDREAM_API_ROOT.exists():
        print(f"ERROR: aidream api root not found at {AIDREAM_API_ROOT}", file=sys.stderr)
        return 0

    skip_patterns: frozenset[str] = frozenset({"__pycache__", ".mypy_cache"})
    total_written = 0

    for src_rel, dst_rel, is_dir in CORE_SYNC_MAPPINGS:
        src_path = MATRX_AI_ROOT / src_rel
        dst_path = AIDREAM_API_ROOT / dst_rel

        if not src_path.exists():
            print(f"  [SKIP] {src_rel} — not found in matrx_ai ({src_path})")
            continue

        if is_dir:
            print(f"[core: {src_rel}/ → aidream/api/{dst_rel}/]")
            written, _ = sync_directory(
                src_path, dst_path, CORE_MATRX_TO_AIDREAM, dry_run, show_diff,
                skip_patterns, skip_filenames=CORE_SKIP_FILES,
            )
            total_written += written
            if written == 0:
                print("  (no changes)")
        else:
            # Single file — check skip list
            if src_path.name in CORE_SKIP_FILES:
                print(f"  [SKIP] {src_rel} — in skip list")
                continue
            print(f"[core: {src_rel} → aidream/api/{dst_rel}]")
            was_written, _ = transform_file(
                src_path, dst_path, CORE_MATRX_TO_AIDREAM, dry_run, show_diff
            )
            if was_written:
                total_written += 1
            else:
                print("  (no changes)")

    return total_written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--direction",
        choices=["aidream-to-matrx", "matrx-to-aidream"],
        default="aidream-to-matrx",
        help="Sync direction for AI engine files (default: aidream-to-matrx)",
    )
    parser.add_argument(
        "--sync-core",
        action="store_true",
        help=(
            "Also push the API core layer (context/, app/core/, auth middleware/deps) "
            "from matrx-ai → aidream. Always runs matrx-to-aidream regardless of --direction."
        ),
    )
    parser.add_argument(
        "--core-only",
        action="store_true",
        help="Only sync the core layer (skip AI engine sync). Implies --sync-core.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show unified diff for each changed file (implies --dry-run view).",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="SUBDIR",
        help=f"Sync only these subdirectories. Available: {', '.join(SHARED_SUBDIRS)}",
    )
    parser.add_argument(
        "--skip-orphan-removal",
        action="store_true",
        help="Do not remove files in destination that no longer exist in source.",
    )
    parser.add_argument(
        "--modernize-types",
        action="store_true",
        help=(
            "After syncing, run 'ruff --select UP --fix --unsafe-fixes' on written files "
            "to upgrade legacy typing (Optional[X]→X|None, Dict→dict, etc.). "
            "Only applies to aidream-to-matrx direction."
        ),
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help=(
            "Simulate aidream→matrx substitutions on every synced file and report any "
            "imports that would survive untranslated (bare 'ai.', 'db.', 'matrix.', "
            "'common.', or f\"ai.\" string literals). Exits non-zero if any are found. "
            "Does not write files."
        ),
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # --verify: simulate substitutions and report any leaking imports
    # ------------------------------------------------------------------
    if args.verify:
        aidream_ai = AIDREAM_ROOT / "ai"
        broken: list[tuple[str, list[str]]] = []
        for subdir in SHARED_SUBDIRS:
            src_dir = aidream_ai / subdir
            if not src_dir.exists():
                continue
            for py_file in src_dir.rglob("*.py"):
                if "__pycache__" in py_file.parts or "tests" in py_file.parts:
                    continue
                src = py_file.read_text()
                transformed = src
                for old, new in AIDREAM_TO_MATRX:
                    transformed = transformed.replace(old, new)
                bad = [
                    line.strip()
                    for line in transformed.splitlines()
                    if (
                        "from ai." in line
                        or "from db." in line
                        or "from matrix." in line
                        or "from common." in line
                        or 'f"ai.' in line
                    )
                    and not line.strip().startswith("#")
                ]
                if bad:
                    rel = py_file.relative_to(aidream_ai)
                    broken.append((str(rel), bad))

        if broken:
            print("\n[VERIFY] FAIL — these imports would survive sync untranslated:\n")
            for rel, lines in broken:
                print(f"  {rel}")
                for ln in lines:
                    print(f"    !! {ln}")
            print(f"\n{len(broken)} file(s) need new substitution rules in AIDREAM_TO_MATRX.")
            sys.exit(1)
        else:
            print("[VERIFY] PASS — all aidream imports translate cleanly to matrx_ai.")
            sys.exit(0)

    # Validate paths
    if not AIDREAM_ROOT.exists():
        print(f"ERROR: aidream repo not found at {AIDREAM_ROOT}", file=sys.stderr)
        print("       Set AIDREAM_ROOT in this script if it lives elsewhere.", file=sys.stderr)
        sys.exit(1)

    aidream_ai = AIDREAM_ROOT / "ai"

    mode = "DRY RUN — " if args.dry_run else ""
    total_written = 0
    total_removed = 0
    written_dirs: list[Path] = []

    # ------------------------------------------------------------------
    # AI engine sync (unless --core-only)
    # ------------------------------------------------------------------
    if not args.core_only:
        if not aidream_ai.exists():
            print(f"ERROR: {aidream_ai} does not exist", file=sys.stderr)
            sys.exit(1)

        subdirs = args.only if args.only else SHARED_SUBDIRS
        unknown = [s for s in subdirs if s not in SHARED_SUBDIRS]
        if unknown:
            print(f"ERROR: unknown subdirectories: {', '.join(unknown)}", file=sys.stderr)
            print(f"       Available: {', '.join(SHARED_SUBDIRS)}", file=sys.stderr)
            sys.exit(1)

        if args.direction == "aidream-to-matrx":
            src_root = aidream_ai
            dst_root = MATRX_AI_ROOT
            rules = AIDREAM_TO_MATRX
            label = "aidream/ai → matrx_ai"
        else:
            src_root = MATRX_AI_ROOT
            dst_root = aidream_ai
            rules = MATRX_TO_AIDREAM
            label = "matrx_ai → aidream/ai"

        skip_patterns: frozenset[str] = frozenset({"__pycache__", ".mypy_cache", "tests"})

        print(f"\n{mode}Syncing AI engine: {label}")
        print(f"Subdirectories: {', '.join(subdirs)}\n")

        for subdir in subdirs:
            src_dir = src_root / subdir
            dst_dir = dst_root / subdir

            if not src_dir.exists():
                print(f"  [SKIP] {subdir}/ — not found in source ({src_dir})")
                continue

            print(f"[{subdir}/]")
            written, _ = sync_directory(src_dir, dst_dir, rules, args.dry_run, args.diff, skip_patterns)
            total_written += written
            if written:
                written_dirs.append(dst_dir)

            if not args.skip_orphan_removal:
                removed = remove_orphans(src_dir, dst_dir, args.dry_run)
                total_removed += removed

            if written == 0 and total_removed == 0:
                print("  (no changes)")

    # ------------------------------------------------------------------
    # API core sync (if --sync-core or --core-only)
    # ------------------------------------------------------------------
    if args.sync_core or args.core_only:
        print(f"\n{mode}Syncing API core: matrx_ai → aidream/api/\n")
        core_written = sync_core_layer(args.dry_run, args.diff)
        total_written += core_written

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Done.")
    print(f"  Files written/updated : {total_written}")
    if not args.core_only:
        print(f"  Orphan files removed  : {total_removed}")

    # ------------------------------------------------------------------
    # --modernize-types post-pass (aidream-to-matrx only)
    # ------------------------------------------------------------------
    if args.modernize_types and not args.dry_run and written_dirs:
        if args.direction != "aidream-to-matrx" or args.core_only:
            print("\n  [--modernize-types] skipped — only applies to aidream-to-matrx direction.")
        else:
            print("\n  [--modernize-types] Running ruff UP fix on written files...")
            targets = [str(d) for d in written_dirs]
            result = subprocess.run(
                ["uv", "run", "ruff", "check", "--select", "UP", "--fix", "--unsafe-fixes"] + targets,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    print(f"    {line}")
            if result.returncode not in (0, 1):
                print(f"  [--modernize-types] ruff exited {result.returncode}", file=sys.stderr)
                if result.stderr:
                    print(result.stderr.strip(), file=sys.stderr)
            else:
                print("  [--modernize-types] Done.")

    print()

    if args.dry_run:
        print("Re-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
