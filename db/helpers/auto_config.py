# File: db/helpers/auto_config.py
ai_provider_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'AiProvider', 'model_name': 'ai_provider', 'model_name_plural': 'ai_providers', 'model_name_snake': 'ai_provider', 'relations': ['ai_settings', 'ai_model'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_agent_memory_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxAgentMemory', 'model_name': 'cx_agent_memory', 'model_name_plural': 'cx_agent_memories', 'model_name_snake': 'cx_agent_memory', 'relations': [], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


prompts_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'Prompts', 'model_name': 'prompts', 'model_name_plural': 'prompt', 'model_name_snake': 'prompts', 'relations': ['prompt_apps', 'system_prompts_new', 'prompt_builtins', 'prompt_actions', 'system_prompts'], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


shortcut_categories_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'ShortcutCategories', 'model_name': 'shortcut_categories', 'model_name_plural': 'shortcut_category', 'model_name_snake': 'shortcut_categories', 'relations': ['self_reference', 'content_blocks', 'prompt_shortcuts', 'system_prompts_new'], 'filter_fields': ['parent_category_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


tools_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'Tools', 'model_name': 'tools', 'model_name_plural': 'tool', 'model_name_snake': 'tools', 'relations': ['tool_test_samples', 'tool_ui_components'], 'filter_fields': ['tags'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


user_tables_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'UserTables', 'model_name': 'user_tables', 'model_name_plural': 'user_table', 'model_name_snake': 'user_tables', 'relations': ['table_data', 'table_fields'], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


ai_model_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'AiModel', 'model_name': 'ai_model', 'model_name_plural': 'ai_models', 'model_name_snake': 'ai_model', 'relations': ['ai_provider', 'ai_model_endpoint', 'ai_settings', 'recipe_model'], 'filter_fields': ['name', 'common_name', 'provider', 'model_class', 'model_provider'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


content_blocks_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'ContentBlocks', 'model_name': 'content_blocks', 'model_name_plural': 'content_block', 'model_name_snake': 'content_blocks', 'relations': ['shortcut_categories'], 'filter_fields': ['category_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


prompt_builtins_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'PromptBuiltins', 'model_name': 'prompt_builtins', 'model_name_plural': 'prompt_builtin', 'model_name_snake': 'prompt_builtins', 'relations': ['prompts', 'prompt_shortcuts', 'prompt_actions'], 'filter_fields': ['created_by_user_id', 'source_prompt_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


table_data_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'TableData', 'model_name': 'table_data', 'model_name_plural': 'table_datas', 'model_name_snake': 'table_data', 'relations': ['user_tables'], 'filter_fields': ['table_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_conversation_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxConversation', 'model_name': 'cx_conversation', 'model_name_plural': 'cx_conversations', 'model_name_snake': 'cx_conversation', 'relations': ['ai_model', 'self_reference', 'cx_tool_call', 'cx_message', 'cx_media', 'cx_user_request', 'cx_request'], 'filter_fields': ['user_id', 'forked_from_id', 'ai_model_id', 'parent_conversation_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_media_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxMedia', 'model_name': 'cx_media', 'model_name_plural': 'cx_medias', 'model_name_snake': 'cx_media', 'relations': ['cx_conversation'], 'filter_fields': ['conversation_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_message_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxMessage', 'model_name': 'cx_message', 'model_name_plural': 'cx_messages', 'model_name_snake': 'cx_message', 'relations': ['cx_conversation', 'cx_tool_call'], 'filter_fields': ['conversation_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_user_request_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxUserRequest', 'model_name': 'cx_user_request', 'model_name_plural': 'cx_user_requests', 'model_name_snake': 'cx_user_request', 'relations': ['ai_model', 'cx_conversation', 'cx_tool_call', 'cx_request'], 'filter_fields': ['conversation_id', 'user_id', 'ai_model_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_request_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxRequest', 'model_name': 'cx_request', 'model_name_plural': 'cx_requests', 'model_name_snake': 'cx_request', 'relations': ['ai_model', 'cx_conversation', 'cx_user_request'], 'filter_fields': ['user_request_id', 'conversation_id', 'ai_model_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}


cx_tool_call_auto_config = {'models_module_path': 'db.models', 'model_pascal': 'CxToolCall', 'model_name': 'cx_tool_call', 'model_name_plural': 'cx_tool_calls', 'model_name_snake': 'cx_tool_call', 'relations': ['cx_conversation', 'cx_message', 'cx_user_request', 'self_reference'], 'filter_fields': ['conversation_id', 'message_id', 'user_id', 'request_id', 'parent_call_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False, 'm2m_relations': None}