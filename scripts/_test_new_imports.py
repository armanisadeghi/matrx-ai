#!/usr/bin/env python3
"""Test imports for all new package modules."""

import importlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

NEW_PACKAGES = [
    "providers",
    "tools",
    "prompts",
    "config",
    "conversation",
    "client",
    "media",
    "context",
    "models",
    "shared",
]

SKIP_PATTERNS = [
    "__pycache__",
    ".venv",
    "tests/",
    "/tests/",
    "/docs/",
]

def should_skip(path: str) -> bool:
    for pattern in SKIP_PATTERNS:
        if pattern in path:
            return True
    return False


def main():
    successes = []
    failures = []

    for pkg in NEW_PACKAGES:
        pkg_dir = PROJECT_ROOT / pkg
        if not pkg_dir.exists():
            continue

        for py_file in sorted(pkg_dir.rglob("*.py")):
            rel = py_file.relative_to(PROJECT_ROOT)
            if should_skip(str(rel)):
                continue
            if py_file.name == "__init__.py":
                module_name = str(rel.parent).replace("/", ".")
            else:
                module_name = str(rel.with_suffix("")).replace("/", ".")

            if module_name.endswith("."):
                module_name = module_name[:-1]

            try:
                importlib.import_module(module_name)
                successes.append(module_name)
                print(f"  ✓ {module_name}")
            except Exception as e:
                failures.append((module_name, str(e)))
                print(f"  ✗ {module_name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {len(successes)} passed, {len(failures)} failed")
    if failures:
        print(f"\nFailures:")
        for mod, err in failures:
            print(f"  {mod}: {err}")


if __name__ == "__main__":
    main()
