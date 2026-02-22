import importlib
import pathlib

ai_root = pathlib.Path("ai")
failures = []
successes = []

for py in sorted(ai_root.rglob("*.py")):
    if py.name.startswith("_") and py.name != "__init__.py":
        continue
    parts = list(py.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    mod = ".".join(parts)
    try:
        importlib.import_module(mod)
        successes.append(mod)
    except Exception as e:
        failures.append((mod, type(e).__name__, str(e)[:200]))

print(f"Successes: {len(successes)} | Failures: {len(failures)}")
if failures:
    print()
    for mod, etype, msg in failures:
        print(f"  FAIL  {mod}")
        print(f"        {etype}: {msg}")
        print()
