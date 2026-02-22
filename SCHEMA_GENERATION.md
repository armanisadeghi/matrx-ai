# Schema Generation — Models & Managers

This document explains how to add new tables to the ORM and regenerate the Python
model and manager files.

---

## What gets generated

Running `makemigrations.py` produces three things inside `database/main/`:

| Output | Location | What it is |
|---|---|---|
| `models.py` | `database/main/models.py` | One Python `Model` class per table, plus DTOs and inline manager stubs |
| Individual managers | `database/main/managers/<table>.py` | Full `BaseManager` subclass per table, ready to extend |
| Auto-config | `database/main/helpers/auto_config.py` | Config dicts used by manager tooling |

---

## Step 1 — Add your table name to MANAGED_TABLES

Open `database_registry.py` and add the exact PostgreSQL table name (snake_case,
no schema prefix) to `MANAGED_TABLES`:

```python
MANAGED_TABLES = {
    "cx_conversation",
    "cx_messages",
    # ... existing tables ...
    "your_new_table",   # <-- add it here
}
```

`MANAGED_TABLES` lives in `database_registry.py` alongside the rest of the database
configuration.  Do **not** add it to `makemigrations.py` — that file only runs the
generator and should not contain config.

The name must match the table name in the `public` schema of the Supabase database
exactly. You can verify the name in the Supabase dashboard under
**Table Editor** or by running:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

### FK dependencies are included automatically

If your table has a foreign key to a table that is *not* in `MANAGED_TABLES`, the
generator will still include a minimal stub model for that dependency so the FK
field compiles correctly. You do not need to add every referenced table.

---

## Step 2 — Run the generator

```bash
uv run python makemigrations.py
```

That's it. The script connects to the database, introspects the schema, and writes
the updated files directly into `database/main/`.

---

## What to expect in the output

After the run you will see a batch-print summary in the terminal listing every file
that was written. The relevant Python paths are:

```
database/main/models.py
database/main/helpers/auto_config.py
database/main/managers/<table>.py   (one per table in MANAGED_TABLES)
```

Your new table will have:
- A `Model` subclass in `models.py` with one field per column and FK relationships
  wired up.
- A manager file at `database/main/managers/<table>.py` containing a `<Table>DTO`
  dataclass and a `<Table>Manager` class — extend these to add your business logic.

---

## Excluding tables

If you want to *stop* generating a table, remove it from `MANAGED_TABLES` in
`database_registry.py` and rerun. The existing files are overwritten on every run,
so the removed table will disappear from `models.py` and its manager file will no
longer be regenerated (though you may want to delete the old `managers/<table>.py`
manually).

---

## Troubleshooting

**Table not showing up in the output**
- Confirm the table name is spelled correctly (check for singular vs plural).
- Make sure the table exists in the `public` schema, not a custom schema.
- The `additional_schemas = ["auth"]` line in `makemigrations.py` covers the `auth`
  schema; tables there are available for FK resolution but are not generated unless
  added to `MANAGED_TABLES`.

**`TypeError: __init__() got an unexpected keyword argument 'include_tables'`**
- Your installed `matrx-orm` is older than `1.5.3`. Update it:
  ```bash
  uv add "matrx-orm>=1.5.3"
  ```

**Files written to the wrong directory**
- Check `.env` — `ADMIN_PYTHON_ROOT` must point to this project root:
  ```
  ADMIN_PYTHON_ROOT="/Volumes/Samsung2TB/code/matrx-ai"
  ```
