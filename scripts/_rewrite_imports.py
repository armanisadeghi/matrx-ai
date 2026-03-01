"""
Rewrite flat cross-package absolute imports to use the matrx_ai. namespace.

Transforms:
    from config import ...          -> from matrx_ai.config import ...
    from orchestrator.x import ...  -> from matrx_ai.orchestrator.x import ...
    import providers                -> import matrx_ai.providers
    import db.custom                -> import matrx_ai.db.custom

Relative imports (from .models import ...) are never touched.
Run from the repo root:
    python scripts/_rewrite_imports.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOP_LEVEL_PACKAGES = [
    "agent_runners",
    "agents",
    "app",
    "config",
    "context",
    "db",
    "instructions",
    "media",
    "orchestrator",
    "processing",
    "providers",
    "tools",
    "utils",
]

# Build alternation once; longer names first to avoid prefix collisions.
_PKG_ALT = "|".join(sorted(TOP_LEVEL_PACKAGES, key=len, reverse=True))

# Matches:   from <pkg>              (absolute, not relative — no leading dot)
# Matches:   from <pkg>.something
# Does NOT match: from .pkg  or  from ..pkg
_FROM_RE = re.compile(
    rf"^(\s*from\s+)({_PKG_ALT})(\s|\.)(.*)$",
    re.MULTILINE,
)

# Matches:   import <pkg>
# Matches:   import <pkg>.something
_IMPORT_RE = re.compile(
    rf"^(\s*import\s+)({_PKG_ALT})([\s,\.].*)$",
    re.MULTILINE,
)


def rewrite_source(source: str) -> tuple[str, int]:
    """Return (rewritten_source, change_count)."""
    changes = 0

    def _replace_from(m: re.Match) -> str:
        nonlocal changes
        changes += 1
        prefix, pkg, sep, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        return f"{prefix}matrx_ai.{pkg}{sep}{rest}"

    def _replace_import(m: re.Match) -> str:
        nonlocal changes
        changes += 1
        prefix, pkg, rest = m.group(1), m.group(2), m.group(3)
        return f"{prefix}matrx_ai.{pkg}{rest}"

    source = _FROM_RE.sub(_replace_from, source)
    source = _IMPORT_RE.sub(_replace_import, source)
    return source, changes


def process_file(path: Path, dry_run: bool) -> int:
    original = path.read_text(encoding="utf-8")
    rewritten, count = rewrite_source(original)
    if count and not dry_run:
        path.write_text(rewritten, encoding="utf-8")
    if count:
        tag = "[DRY RUN] " if dry_run else ""
        print(f"{tag}{path}: {count} change(s)")
    return count


def collect_py_files(*roots: Path) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        else:
            files.extend(root.rglob("*.py"))
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print changes without writing files.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["matrx_ai", "tests"],
        help="Directories or files to process (default: matrx_ai tests).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    targets = [repo_root / p for p in args.paths]
    missing = [str(t) for t in targets if not t.exists()]
    if missing:
        print(f"Error: paths not found: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    files = collect_py_files(*targets)
    total_files = 0
    total_changes = 0
    for f in sorted(files):
        n = process_file(f, dry_run=args.dry_run)
        if n:
            total_files += 1
            total_changes += n

    mode = "DRY RUN — " if args.dry_run else ""
    print(f"\n{mode}{total_changes} change(s) across {total_files} file(s).")


if __name__ == "__main__":
    main()
