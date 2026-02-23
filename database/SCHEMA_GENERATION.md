# Schema Generation — Models & Managers

This document explains how to add new tables to the ORM and regenerate the
Python model and manager files.

---

## What gets generated

Running `generate.py` produces three things inside `database/main/`:

| Output | Location | What it is |
|---|---|---|
| `models.py` | `database/main/models.py` | One Python `Model` class per table, plus DTOs and inline manager stubs |
| Individual managers | `database/main/managers/<table>.py` | Full `BaseManager` subclass per table, ready to extend |
| Auto-config | `database/main/helpers/auto_config.py` | Config dicts used by manager tooling |

---

## Step 1 — Add the table name to `matrx_orm.yaml`

Open `database/matrx_orm.yaml` and add the exact PostgreSQL table name
(snake_case, no schema prefix) to the `include_tables` list under the
relevant `generate` entry:

```yaml
generate:
  - database: supabase_automation_matrix
    schema: public
    include_tables:
      - cx_conversation
      - cx_messages
      - your_new_table   # <-- add it here
```

The name must match the table name in the `public` schema exactly. You can
verify it in the Supabase dashboard under **Table Editor** or by running:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

### FK dependencies are included automatically

If your table has a foreign key to a table that is *not* in `include_tables`,
the generator will still include a minimal stub model for that dependency so
the FK field compiles correctly. You do not need to add every referenced table.

---

## Step 2 — Run the generator

```bash
cd database
uv run python generate.py
```

Or from the project root:

```bash
uv run python database/generate.py
```

That's it. The script connects to the database, introspects the schema, and
writes the updated files directly into `database/main/`.

---

## What to expect in the output

After the run you will see a batch-print summary in the terminal listing every
file that was written. The relevant Python paths are:

```
database/main/models.py
database/main/helpers/auto_config.py
database/main/managers/<table>.py   (one per table in include_tables)
```

Your new table will have:
- A `Model` subclass in `models.py` with one field per column and FK
  relationships wired up.
- A manager file at `database/main/managers/<table>.py` containing a
  `<Table>DTO` dataclass and a `<Table>Manager` class — extend these to add
  your business logic.

---

## Excluding tables

Remove the table name from `include_tables` in `matrx_orm.yaml` and rerun.
The existing files are overwritten on every run, so the removed table will
disappear from `models.py`. You may want to manually delete the old
`managers/<table>.py` as well.

---

## Controlling which methods are generated

`matrx_orm.yaml` has a `manager_flags` section under each `generate` entry
that controls which methods every manager class gets by default:

```yaml
generate:
  - database: supabase_automation_matrix
    manager_flags:
      include_core_relations: true   # FK/IFK fetch methods — keep this true
      include_filter_fields: true    # filter_by_* methods — keep this true
      include_active_relations: false
      include_active_methods: false
      include_or_not_methods: false
      include_to_dict_methods: false
      include_to_dict_relations: false
```

You can also override flags for a specific table using `manager_config_overrides`
under the database entry — those take priority over `manager_flags`.

---

## Forward migrations (schema changes in code → database)

`run_migrations.py` handles forward migrations (creating/altering tables).

```bash
# Generate a migration from model/DB differences
uv run python database/run_migrations.py make

# Apply pending migrations
uv run python database/run_migrations.py apply

# Check which migrations have been applied
uv run python database/run_migrations.py status

# Roll back the last migration
uv run python database/run_migrations.py rollback
```

---

## Troubleshooting

**Table not showing up in the output**
- Confirm the table name is spelled correctly (check for singular vs plural).
- Make sure the table exists in the `public` schema, not a custom schema.

**Files written to the wrong directory**
- Check `.env` — set `MATRX_PYTHON_ROOT` to override where Python files land:
  ```
  MATRX_PYTHON_ROOT=/Volumes/Samsung2TB/code/matrx-ai
  ```
- `matrx-orm` looks for `.env` starting from `database/` and walking up to
  the project root automatically — you don't need to copy it.

**`save_direct` is `false` — files aren't overwriting my live code**
- That's the safe default. Set `save_direct: true` in `matrx_orm.yaml` (or
  `MATRX_SAVE_DIRECT=true` in `.env`) once you've committed any pending
  changes. The generator will refuse to run with `save_direct: true` if
  the output directory has uncommitted git changes.
