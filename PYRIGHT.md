# Pyright Type Checking — Cheatsheet

Config is split across two files:
- `pyrightconfig.json` — primary file read by the Cursor Pyright extension
- `pyproject.toml` → `[tool.pyright]` — used by CLI (`pyright`) and other tools

Keep both in sync. `pyrightconfig.json` takes precedence in the editor.

---

## Checking Modes (`typeCheckingMode`)

| Mode       | Behavior                                              |
|------------|-------------------------------------------------------|
| `"off"`    | No type checking at all                               |
| `"basic"`  | Only the most obvious errors (missing imports, etc.)  |
| `"standard"` | **Current** — moderate, catches most real issues    |
| `"strict"` | Everything, very loud — treats warnings as errors     |

Change the mode to quickly dial the overall volume up or down.

---

## Rule Severity Levels

Each individual rule can be set independently:

| Value       | Effect                              |
|-------------|-------------------------------------|
| `"none"`    | Silenced — never shown              |
| `"warning"` | Shown as a warning (yellow)         |
| `"error"`   | Shown as an error (red), blocks CI  |

---

## Currently Suppressed Rules

| Rule                        | What it catches                                         |
|-----------------------------|---------------------------------------------------------|
| `reportCallIssue`           | Wrong number of args, calling non-callables             |
| `reportArgumentType`        | Argument type mismatches                                |
| `reportOperatorIssue`       | Operator used on incompatible types (`+`, `==`, etc.)  |
| `reportAttributeAccessIssue`| Accessing attributes that don't exist on a type         |
| `reportIndexIssue`          | Indexing into types that don't support it               |
| `reportReturnType`          | Return type doesn't match declared return annotation    |
| `reportMissingTypeArgument` | Generic used without type args (e.g. `list` vs `list[str]`) |

These are suppressed because the ORM returns dynamic types that Pyright
can't statically verify — `hasattr` checks, `.to_dict()`, JSONB fields, etc.

---

## Doing an Explicit Audit

To temporarily surface all suppressed errors for a review pass, change
any rule from `"none"` to `"warning"` in `pyrightconfig.json`, then
restart the Pyright server:

  Ctrl+Shift+P → "Pyright: Restart Server"

Revert to `"none"` when done.

---

## Other Useful Rules (not currently configured)

| Rule                          | What it catches                                    |
|-------------------------------|----------------------------------------------------|
| `reportUnknownVariableType`   | Variables inferred as `Unknown`                    |
| `reportUnknownMemberType`     | Members with unknown types                         |
| `reportMissingImports`        | Imports that can't be resolved                     |
| `reportUndefinedVariable`     | Using variables before assignment                  |
| `reportUnusedImport`          | Imported but never used                            |
| `reportPrivateUsage`          | Accessing `_private` members from outside a class  |
| `reportAbstractUsage`         | Instantiating abstract classes directly            |

Full rule list: https://microsoft.github.io/pyright/#/configuration?id=type-check-diagnostics-settings
