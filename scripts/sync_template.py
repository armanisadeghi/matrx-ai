"""
sync_template.py — Push the API core layer from matrx-ai to matrx-service-core template.

Copies the canonical context/, app/core/, app/middleware/auth.py, and
app/dependencies/auth.py files from matrx_ai/ into the template at
templates/matrx-service-core/matrx_service/, applying package name
substitutions so the template remains self-contained.

DIRECTORY MAPPING
-----------------
matrx_ai/context/              → matrx_service/context/
matrx_ai/app/core/             → matrx_service/app/core/
matrx_ai/app/middleware/auth.py → matrx_service/app/middleware/auth.py
matrx_ai/app/dependencies/auth.py → matrx_service/app/dependencies/auth.py

SUBSTITUTIONS APPLIED
---------------------
  matrx_ai.context.   → matrx_service.context.
  matrx_ai.app.core.  → matrx_service.app.core.
  matrx_ai.app.middleware.auth → matrx_service.app.middleware.auth
  matrx_ai.app.dependencies.auth → matrx_service.app.dependencies.auth
  matrx_ai.app.config → matrx_service.app.config
  supabase_matrix_jwt_secret → supabase_jwt_secret  (field name normalisation)

Files that live in the template but NOT in matrx_ai are left untouched:
  - matrx_service/client/service_client.py  (template-only)
  - matrx_service/__init__.py               (template-only)
  - matrx_service/app/main.py               (template-only)
  - matrx_service/app/config.py             (template-only — has different field set)

USAGE
-----
  python scripts/sync_template.py
  python scripts/sync_template.py --dry-run
  python scripts/sync_template.py --diff
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
MATRX_AI_ROOT = REPO_ROOT / "matrx_ai"
TEMPLATE_ROOT = REPO_ROOT / "templates" / "matrx-service-core" / "matrx_service"

# ---------------------------------------------------------------------------
# Import substitution rules (matrx_ai → matrx_service)
# ---------------------------------------------------------------------------

MATRX_TO_TEMPLATE: list[tuple[str, str]] = [
    # Logging shim
    ("from matrx_ai.context._log import", "from matrx_service.context._log import"),
    # Context package
    ("from matrx_ai.context.app_context import", "from matrx_service.context.app_context import"),
    ("from matrx_ai.context.emitter_protocol import", "from matrx_service.context.emitter_protocol import"),
    ("from matrx_ai.context.events import", "from matrx_service.context.events import"),
    ("from matrx_ai.context.stream_emitter import", "from matrx_service.context.stream_emitter import"),
    ("from matrx_ai.context.console_emitter import", "from matrx_service.context.console_emitter import"),
    ("from matrx_ai.context import", "from matrx_service.context import"),
    # App core
    ("from matrx_ai.app.core.cancellation import", "from matrx_service.app.core.cancellation import"),
    ("from matrx_ai.app.core.exceptions import", "from matrx_service.app.core.exceptions import"),
    ("from matrx_ai.app.core.middleware import", "from matrx_service.app.core.middleware import"),
    ("from matrx_ai.app.core.response import", "from matrx_service.app.core.response import"),
    ("from matrx_ai.app.core.sentry import", "from matrx_service.app.core.sentry import"),
    ("from matrx_ai.app.core.streaming import", "from matrx_service.app.core.streaming import"),
    ("from matrx_ai.app.core import", "from matrx_service.app.core import"),
    # Auth middleware and dependencies
    ("from matrx_ai.app.middleware.auth import", "from matrx_service.app.middleware.auth import"),
    ("from matrx_ai.app.dependencies.auth import", "from matrx_service.app.dependencies.auth import"),
    # Config
    ("from matrx_ai.app.config import", "from matrx_service.app.config import"),
    # Logger name
    ('logging.getLogger("matrx_ai.context")', 'logging.getLogger("matrx_service.emitter")'),
    # JWT secret field name normalisation (matrx_ai uses supabase_jwt_secret already)
    # This is a no-op after Step 1 but kept as a safety net.
    ("supabase_matrix_jwt_secret", "supabase_jwt_secret"),
]

# ---------------------------------------------------------------------------
# Files/dirs to skip when syncing (template-only or intentionally diverged)
# ---------------------------------------------------------------------------

# These files exist in the template but must never be overwritten by the sync
TEMPLATE_ONLY_FILES: frozenset[str] = frozenset({
    "app/main.py",
    "app/config.py",
    "client/service_client.py",
    "__init__.py",
})

# Mapping: (src_relative_to_matrx_ai, dst_relative_to_template, is_directory)
TEMPLATE_SYNC_MAPPINGS: list[tuple[str, str, bool]] = [
    ("context",                  "context",                  True),
    ("app/core",                 "app/core",                 True),
    ("app/middleware/auth.py",   "app/middleware/auth.py",   False),
    ("app/dependencies/auth.py", "app/dependencies/auth.py", False),
]


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def transform_source(source: str, rules: list[tuple[str, str]]) -> tuple[str, int]:
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
) -> bool:
    """Copy src → dst with substitutions. Returns True if file was written."""
    source = src.read_text(encoding="utf-8")
    transformed, change_count = transform_source(source, rules)

    dst_exists = dst.exists()
    dst_content = dst.read_text(encoding="utf-8") if dst_exists else ""

    if transformed == dst_content:
        return False

    if show_diff:
        diff = difflib.unified_diff(
            dst_content.splitlines(keepends=True),
            transformed.splitlines(keepends=True),
            fromfile=f"current:  {dst.relative_to(REPO_ROOT) if dst.is_relative_to(REPO_ROOT) else dst}",
            tofile=f"incoming: {src.relative_to(REPO_ROOT) if src.is_relative_to(REPO_ROOT) else src}",
            n=3,
        )
        sys.stdout.writelines(diff)

    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(transformed, encoding="utf-8")

    label = "(import rewrites)" if change_count else "(content differs)"
    tag = "[DRY RUN] " if dry_run else ""
    print(f"  {tag}{'WRITE' if not dry_run else 'WOULD WRITE'}: {dst.name}  {label}")
    return True


def sync_directory(
    src_dir: Path,
    dst_dir: Path,
    rules: list[tuple[str, str]],
    dry_run: bool,
    show_diff: bool,
) -> int:
    """Sync all .py files from src_dir → dst_dir. Returns count of files written."""
    skip = frozenset({"__pycache__", ".mypy_cache"})
    written = 0
    for src_file in sorted(src_dir.rglob("*.py")):
        rel = src_file.relative_to(src_dir)
        if any(p in skip for p in rel.parts):
            continue
        dst_file = dst_dir / rel
        if transform_file(src_file, dst_file, rules, dry_run, show_diff):
            written += 1
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing.")
    parser.add_argument("--diff", action="store_true", help="Show unified diff per changed file.")
    args = parser.parse_args()

    if not TEMPLATE_ROOT.exists():
        print(f"ERROR: template not found at {TEMPLATE_ROOT}", file=sys.stderr)
        sys.exit(1)

    mode = "DRY RUN — " if args.dry_run else ""
    print(f"\n{mode}Syncing API core: matrx_ai → matrx-service-core template\n")

    total_written = 0

    for src_rel, dst_rel, is_dir in TEMPLATE_SYNC_MAPPINGS:
        src_path = MATRX_AI_ROOT / src_rel
        dst_path = TEMPLATE_ROOT / dst_rel

        if not src_path.exists():
            print(f"  [SKIP] {src_rel} — not found in matrx_ai ({src_path})")
            continue

        if is_dir:
            print(f"[{src_rel}/ → template/{dst_rel}/]")
            written = sync_directory(src_path, dst_path, MATRX_TO_TEMPLATE, args.dry_run, args.diff)
            total_written += written
            if written == 0:
                print("  (no changes)")
        else:
            print(f"[{src_rel} → template/{dst_rel}]")
            if transform_file(src_path, dst_path, MATRX_TO_TEMPLATE, args.dry_run, args.diff):
                total_written += 1
            else:
                print("  (no changes)")

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Done.")
    print(f"  Files written/updated: {total_written}")
    if args.dry_run:
        print("\nRe-run without --dry-run to apply changes.")
    print()


if __name__ == "__main__":
    main()
