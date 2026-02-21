All files compile clean. Here's a complete summary of everything that was built:

---

## What was built

There was **no** existing table filtering capability. The full system is now implemented across 4 files.

### New file: `src/matrx_orm/migrations/table_filter.py`

The `TableFilter` class — pick exactly one mode:
- **`include`** — allowlist: only diff these tables, ignore everything else
- **`exclude`** — denylist: diff everything except these tables

It also emits `UserWarning` whenever an included table has a FK column that points to a table outside the migration scope.

---

### How to use it

**CLI — include-only:**
```bash
matrx-orm makemigrations --database mydb --include-tables user post comment
```

**CLI — exclude:**
```bash
matrx-orm makemigrations --database mydb --exclude-tables legacy_audit scratch_pad
```

`--include-tables` and `--exclude-tables` are mutually exclusive — argparse enforces this automatically.

**Programmatic — include-only:**
```python
from matrx_orm import makemigrations

await makemigrations(
    "mydb",
    include_tables={"user", "post", "comment"},
)
```

**Programmatic — exclude:**
```python
await makemigrations(
    "mydb",
    exclude_tables={"legacy_audit", "scratch_pad"},
)
```

**Programmatic — build the filter manually and hand it to `SchemaDiff` directly:**
```python
from matrx_orm import SchemaDiff, TableFilter
from matrx_orm.migrations import MigrationDB

db = MigrationDB("mydb")
f = TableFilter(include={"user", "post"})
diff = SchemaDiff(db, schema="public", table_filter=f)
path = await diff.generate_migration_file("migrations/")
```

---

### Cross-reference warnings

If `post.author_id` is an FK to `user`, and `user` is not in the migration scope, you'll see:

```
UserWarning: [matrx-orm] Cross-scope FK detected: 'post.author_id' references 'user',
which is outside the current migration scope. The FK constraint will be included
in the generated SQL, but 'user' will not be created or managed by this migration set.
Ensure it already exists in the target database.
```

To suppress warnings in scripts where you know what you're doing:
```python
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matrx_orm")
```

---

### Note on `migrate` / `migrate_rebuild`

Table filtering only applies to `makemigrations` (the diff/generation step). `migrate` and `migrate_rebuild` apply already-generated files in full — there's nothing to filter there.