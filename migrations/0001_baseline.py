"""Baseline: establish tracked tables for the matrx-ai migration scope.

Tables already present in the database are created with IF NOT EXISTS so
this migration is safe to apply against the live Supabase database without
touching existing data.

"""

dependencies = []


async def up(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."ai_model" (
            "id" uuid PRIMARY KEY,
            "name" character varying NOT NULL,
            "common_name" character varying,
            "model_class" character varying NOT NULL,
            "provider" character varying,
            "endpoints" jsonb,
            "context_window" bigint,
            "max_tokens" bigint,
            "capabilities" jsonb,
            "controls" jsonb,
            "model_provider" uuid,
            "is_deprecated" boolean,
            "is_primary" boolean,
            "is_premium" boolean,
            "api_class" character varying
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_conversation" (
            "id" uuid PRIMARY KEY,
            "user_id" uuid NOT NULL,
            "title" text,
            "system_instruction" text,
            "config" jsonb NOT NULL,
            "status" text NOT NULL,
            "message_count" smallint NOT NULL,
            "forked_from_id" uuid,
            "forked_at_position" smallint,
            "created_at" timestamp with time zone NOT NULL,
            "updated_at" timestamp with time zone NOT NULL,
            "deleted_at" timestamp with time zone,
            "metadata" jsonb NOT NULL,
            "ai_model_id" uuid,
            "parent_conversation_id" uuid,
            "variables" jsonb NOT NULL,
            "overrides" jsonb NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_message" (
            "id" uuid PRIMARY KEY,
            "conversation_id" uuid NOT NULL,
            "user_id" uuid NOT NULL,
            "role" text NOT NULL,
            "content" text NOT NULL,
            "position" smallint NOT NULL,
            "created_at" timestamp with time zone NOT NULL,
            "deleted_at" timestamp with time zone,
            "metadata" jsonb NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_agent_memory" (
            "id" uuid PRIMARY KEY,
            "user_id" uuid NOT NULL,
            "memory_type" text NOT NULL,
            "scope" text NOT NULL,
            "scope_id" text,
            "key" text NOT NULL,
            "content" text NOT NULL,
            "importance" double precision,
            "access_count" integer,
            "last_accessed_at" timestamp with time zone,
            "expires_at" timestamp with time zone,
            "metadata" jsonb NOT NULL,
            "created_at" timestamp with time zone NOT NULL,
            "updated_at" timestamp with time zone NOT NULL,
            "deleted_at" timestamp with time zone
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_media" (
            "id" uuid PRIMARY KEY,
            "conversation_id" uuid,
            "user_id" uuid NOT NULL,
            "kind" text NOT NULL,
            "url" text NOT NULL,
            "file_uri" text,
            "mime_type" text,
            "file_size_bytes" bigint,
            "created_at" timestamp with time zone NOT NULL,
            "deleted_at" timestamp with time zone,
            "metadata" jsonb NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_user_request" (
            "id" uuid PRIMARY KEY,
            "conversation_id" uuid NOT NULL,
            "user_id" uuid NOT NULL,
            "trigger_message_position" smallint,
            "api_class" text,
            "total_input_tokens" integer NOT NULL,
            "total_output_tokens" integer NOT NULL,
            "total_cached_tokens" integer NOT NULL,
            "total_tokens" integer NOT NULL,
            "total_cost" numeric(12,6),
            "total_duration_ms" integer,
            "api_duration_ms" integer,
            "tool_duration_ms" integer,
            "iterations" smallint NOT NULL,
            "total_tool_calls" smallint NOT NULL,
            "status" text NOT NULL,
            "finish_reason" text,
            "error" text,
            "result_start_position" smallint,
            "result_end_position" smallint,
            "created_at" timestamp with time zone NOT NULL,
            "completed_at" timestamp with time zone,
            "deleted_at" timestamp with time zone,
            "metadata" jsonb NOT NULL,
            "ai_model_id" uuid
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_request" (
            "id" uuid PRIMARY KEY,
            "user_request_id" uuid NOT NULL,
            "conversation_id" uuid NOT NULL,
            "api_class" text,
            "iteration" smallint NOT NULL,
            "input_tokens" integer,
            "output_tokens" integer,
            "cached_tokens" integer,
            "total_tokens" integer,
            "cost" numeric(12,6),
            "api_duration_ms" integer,
            "tool_duration_ms" integer,
            "total_duration_ms" integer,
            "tool_calls_count" smallint,
            "tool_calls_details" jsonb,
            "finish_reason" text,
            "response_id" text,
            "created_at" timestamp with time zone NOT NULL,
            "deleted_at" timestamp with time zone,
            "metadata" jsonb NOT NULL,
            "ai_model_id" uuid NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS "public"."cx_tool_call" (
            "id" uuid PRIMARY KEY,
            "conversation_id" uuid NOT NULL,
            "message_id" uuid,
            "user_id" uuid NOT NULL,
            "request_id" uuid,
            "tool_name" text NOT NULL,
            "tool_type" text NOT NULL,
            "call_id" text NOT NULL,
            "status" text NOT NULL,
            "arguments" jsonb NOT NULL,
            "success" boolean NOT NULL,
            "output" text,
            "output_type" text,
            "is_error" boolean,
            "error_type" text,
            "error_message" text,
            "duration_ms" integer NOT NULL,
            "started_at" timestamp with time zone NOT NULL,
            "completed_at" timestamp with time zone NOT NULL,
            "input_tokens" integer,
            "output_tokens" integer,
            "total_tokens" integer,
            "cost_usd" numeric(10,6),
            "iteration" integer NOT NULL,
            "retry_count" integer,
            "parent_call_id" uuid,
            "execution_events" jsonb,
            "persist_key" text,
            "file_path" text,
            "metadata" jsonb NOT NULL,
            "created_at" timestamp with time zone NOT NULL,
            "deleted_at" timestamp with time zone
        )
    """)


async def down(db):
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_tool_call" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_request" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_user_request" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_media" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_agent_memory" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_message" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."cx_conversation" CASCADE""")
    await db.execute("""DROP TABLE IF EXISTS "public"."ai_model" CASCADE""")
