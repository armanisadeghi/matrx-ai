-- VFS Phase A1: virtual filesystem tables.
--
-- vfs_inode  : a single row per directory/file/symlink in a workspace.
-- vfs_blob   : content-addressed bytes; many inodes can share one blob.
--
-- Each workspace has a synthetic root inode where parent_id IS NULL and name='/'.
-- The (workspace_id, parent_id, name) tuple is unique; NULLs are made distinct via
-- COALESCE in the partial unique index so the root row remains unique per workspace.

CREATE TABLE IF NOT EXISTS "public"."vfs_blob" (
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "bytes" bytea NOT NULL,
    "sha256" text NOT NULL,
    "size" bigint NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX IF NOT EXISTS "vfs_blob_sha256_uniq"
    ON "public"."vfs_blob" ("sha256");

CREATE TABLE IF NOT EXISTS "public"."vfs_inode" (
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "workspace_id" uuid NOT NULL,
    "parent_id" uuid REFERENCES "public"."vfs_inode" ("id") ON DELETE CASCADE,
    "name" text NOT NULL,
    "type" text NOT NULL CHECK ("type" IN ('file', 'dir', 'symlink')),
    "mode" integer NOT NULL DEFAULT 420,
    "uid" integer NOT NULL DEFAULT 0,
    "gid" integer NOT NULL DEFAULT 0,
    "size" bigint NOT NULL DEFAULT 0,
    "symlink_target" text,
    "content_id" uuid REFERENCES "public"."vfs_blob" ("id") ON DELETE SET NULL,
    "ctime" timestamptz NOT NULL DEFAULT now(),
    "mtime" timestamptz NOT NULL DEFAULT now(),
    "atime" timestamptz NOT NULL DEFAULT now()
);

-- Uniqueness of (workspace_id, parent_id, name). The COALESCE makes NULL parent_id
-- comparable so the per-workspace root inode (parent_id IS NULL) is unique.
CREATE UNIQUE INDEX IF NOT EXISTS "vfs_inode_ws_parent_name_uniq"
    ON "public"."vfs_inode" (
        "workspace_id",
        COALESCE("parent_id", '00000000-0000-0000-0000-000000000000'::uuid),
        "name"
    );

CREATE INDEX IF NOT EXISTS "vfs_inode_workspace_idx"
    ON "public"."vfs_inode" ("workspace_id");

CREATE INDEX IF NOT EXISTS "vfs_inode_parent_idx"
    ON "public"."vfs_inode" ("parent_id");

CREATE INDEX IF NOT EXISTS "vfs_inode_content_idx"
    ON "public"."vfs_inode" ("content_id");

-- Sanity: file/symlink rows should never act as a parent.
CREATE OR REPLACE FUNCTION "public"."vfs_inode_parent_must_be_dir"()
RETURNS trigger AS $$
DECLARE
    parent_type text;
BEGIN
    IF NEW."parent_id" IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT "type" INTO parent_type FROM "public"."vfs_inode" WHERE "id" = NEW."parent_id";
    IF parent_type IS DISTINCT FROM 'dir' THEN
        RAISE EXCEPTION 'vfs_inode parent must be a directory (got %)', parent_type;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS "vfs_inode_parent_check" ON "public"."vfs_inode";
CREATE TRIGGER "vfs_inode_parent_check"
    BEFORE INSERT OR UPDATE OF "parent_id" ON "public"."vfs_inode"
    FOR EACH ROW EXECUTE FUNCTION "public"."vfs_inode_parent_must_be_dir"();
