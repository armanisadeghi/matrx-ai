import database_registry  # noqa: F401
from matrx_utils import clear_terminal, vcprint
from matrx_orm.schema_builder import SchemaManager

clear_terminal()

schema = "public"
database_project = "supabase_automation_matrix"
additional_schemas = ["auth"]
save_direct = True

# Only generate models and managers for these tables.
# All other tables in the database are ignored.
MANAGED_TABLES = {
    "cx_conversation",
    "cx_messages",
    "cx_agent_memory",
    "cx_media",
    "cx_request",
    "cx_tool_call",
    "cx_user_request",
    "ai_model",
}

schema_manager = SchemaManager(
    schema=schema,
    database_project=database_project,
    additional_schemas=additional_schemas,
    save_direct=save_direct,
    include_tables=MANAGED_TABLES,
)
schema_manager.initialize()

# Claude with some familiarity with the structure, especially the json: https://claude.ai/chat/05e6e654-2574-4cdf-9f26-61f6a26ad631
# Potential Additions: https://claude.ai/chat/e26ff11e-0cd5-46a5-b281-cfa359ed1fcd

# example_usage(schema_manager)

# # Access tables, views, or columns as needed
# vcprint(schema_manager.schema.tables, title="Tables", pretty=True, verbose=verbose, color="blue")
# vcprint(schema_manager.schema.views, title="Views", pretty=True, verbose=verbose, color="green")
#
# # Example: Get a specific table and its columns
# table = schema_manager.get_table('flashcard_history').to_dict()
# vcprint(table, title="Flashcard History Table", pretty=True, verbose=verbose, color="cyan")

matrx_schema_entry = schema_manager.schema.generate_schema_files()

matrx_models = schema_manager.schema.generate_models()

# # Example: Get a specific column from a table
# column = schema_manager.get_column('flashcard_history', 'id').to_dict()
# vcprint(column, title="Flashcard ID Column", pretty=True, verbose=verbose, color="magenta")
#
# # Example: Get a specific view...
# view = schema_manager.get_view('view_registered_function_all_rels').to_dict()
# vcprint(view, title="Full Registered Function View", pretty=True, verbose=verbose, color="yellow")
#
analysis = schema_manager.analyze_schema()
vcprint(
    data=analysis,
    title="Schema Analysis",
    pretty=True,
    verbose=False,
    color="yellow",
)
#
# relationship_analysis = schema_manager.analyze_relationships()
# vcprint(data=relationship_analysis, title="Relationship Analysis", pretty=True, verbose=True, color="green")
#
# related_tables = schema_manager.schema.get_related_tables("flashcard_data")
# vcprint(f"Tables related to 'flashcard_data': {related_tables}", verbose=verbose, color="cyan")
#
schema_manager.schema.code_handler.print_all_batched()

# Not sure exactly what this is returning so we'll need to make updates for it to return the full data we need for react.
# full_schema_object = get_full_schema_object(schema, database_project)
# vcprint(full_schema_object, title="Full Schema Object", pretty=True, verbose=True, color="cyan")
