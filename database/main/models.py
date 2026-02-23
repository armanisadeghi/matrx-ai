# File: database/main/models.py
from matrx_orm import BigIntegerField, BooleanField, CharField, DateTimeField, DecimalField, FloatField, ForeignKey, IntegerField, JSONBField, Model, SmallIntegerField, TextField, UUIDField, model_registry, BaseDTO, BaseManager
from enum import Enum
from dataclasses import dataclass

class Users(Model):
    id = UUIDField(primary_key=True, null=False)
    email = CharField(null=False)

    _table_name = "users"
    _db_schema = "auth"
    _database = "supabase_automation_matrix"

class AiProvider(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField()
    company_description = TextField()
    documentation_link = CharField()
    models_link = CharField()
    _inverse_foreign_keys = {'ai_settingss': {'from_model': 'AiSettings', 'from_field': 'ai_provider', 'referenced_field': 'id', 'related_name': 'ai_settingss'}, 'ai_models': {'from_model': 'AiModel', 'from_field': 'model_provider', 'referenced_field': 'id', 'related_name': 'ai_models'}}
    _database = "supabase_automation_matrix"

class CxAgentMemory(Model):
    id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False, unique=True)
    memory_type = TextField(null=False)
    scope = TextField(null=False, default='user', unique=True)
    scope_id = TextField(unique=True)
    key = TextField(null=False, unique=True)
    content = TextField(null=False)
    importance = FloatField(default=0.5)
    access_count = IntegerField(default=0)
    last_accessed_at = DateTimeField()
    expires_at = DateTimeField()
    metadata = JSONBField(null=False, default={})
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys = {}
    _database = "supabase_automation_matrix"

class Prompts(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField()
    name = CharField()
    messages = JSONBField()
    variable_defaults = JSONBField()
    tools = JSONBField()
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', )
    settings = JSONBField()
    description = TextField()
    _inverse_foreign_keys = {'prompt_appss': {'from_model': 'PromptApps', 'from_field': 'prompt_id', 'referenced_field': 'id', 'related_name': 'prompt_appss'}, 'system_prompts_news': {'from_model': 'SystemPromptsNew', 'from_field': 'source_prompt_id', 'referenced_field': 'id', 'related_name': 'system_prompts_news'}, 'prompt_builtinss': {'from_model': 'PromptBuiltins', 'from_field': 'source_prompt_id', 'referenced_field': 'id', 'related_name': 'prompt_builtinss'}, 'prompt_actionss': {'from_model': 'PromptActions', 'from_field': 'prompt_id', 'referenced_field': 'id', 'related_name': 'prompt_actionss'}, 'system_promptss': {'from_model': 'SystemPrompts', 'from_field': 'source_prompt_id', 'referenced_field': 'id', 'related_name': 'system_promptss'}}
    _database = "supabase_automation_matrix"

class ShortcutCategories(Model):
    id = UUIDField(primary_key=True, null=False)
    placement_type = TextField(null=False)
    parent_category_id = ForeignKey(to_model='ShortcutCategories', to_column='id', )
    label = TextField(null=False)
    description = TextField()
    icon_name = TextField(null=False, default='SquareMenu')
    color = TextField(default='zinc')
    sort_order = IntegerField(default=999)
    is_active = BooleanField(default=True)
    metadata = JSONBField(default={})
    enabled_contexts = JSONBField(default=['general'])
    _inverse_foreign_keys = {'content_blockss': {'from_model': 'ContentBlocks', 'from_field': 'category_id', 'referenced_field': 'id', 'related_name': 'content_blockss'}, 'prompt_shortcutss': {'from_model': 'PromptShortcuts', 'from_field': 'category_id', 'referenced_field': 'id', 'related_name': 'prompt_shortcutss'}, 'system_prompts_news': {'from_model': 'SystemPromptsNew', 'from_field': 'category_id', 'referenced_field': 'id', 'related_name': 'system_prompts_news'}}
    _database = "supabase_automation_matrix"

class Tools(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False, unique=True)
    description = TextField(null=False)
    parameters = JSONBField(null=False)
    output_schema = JSONBField()
    annotations = JSONBField(default=[])
    function_path = TextField(null=False)
    category = TextField()
    tags = JSONBField()
    icon = CharField(max_length=255)
    is_active = BooleanField(default=True)
    version = TextField(default='1.0.0')
    created_at = DateTimeField()
    updated_at = DateTimeField()
    _inverse_foreign_keys = {'tool_test_sampless': {'from_model': 'ToolTestSamples', 'from_field': 'tool_id', 'referenced_field': 'id', 'related_name': 'tool_test_sampless'}, 'tool_ui_componentss': {'from_model': 'ToolUiComponents', 'from_field': 'tool_id', 'referenced_field': 'id', 'related_name': 'tool_ui_componentss'}}
    _database = "supabase_automation_matrix"

class UserTables(Model):
    id = UUIDField(primary_key=True, null=False)
    table_name = CharField(null=False, max_length=255, unique=True)  # pyright: ignore[reportIncompatibleMethodOverride, reportAssignmentType]
    description = TextField()
    version = IntegerField(null=False, default=1)
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False, unique=True)
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    row_ordering_config = JSONBField()
    _inverse_foreign_keys = {'table_datas': {'from_model': 'TableData', 'from_field': 'table_id', 'referenced_field': 'id', 'related_name': 'table_datas'}, 'table_fieldss': {'from_model': 'TableFields', 'from_field': 'table_id', 'referenced_field': 'id', 'related_name': 'table_fieldss'}}
    _database = "supabase_automation_matrix"

class AiModel(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=False)
    common_name = CharField()
    model_class = CharField(null=False)
    provider = CharField()
    endpoints = JSONBField()
    context_window = BigIntegerField()
    max_tokens = BigIntegerField()
    capabilities = JSONBField()
    controls = JSONBField()
    model_provider = ForeignKey(to_model=AiProvider, to_column='id', )
    is_deprecated = BooleanField(default=False)
    is_primary = BooleanField(default=False)
    is_premium = BooleanField(default=False)
    api_class = CharField()
    _inverse_foreign_keys = {'ai_model_endpoints': {'from_model': 'AiModelEndpoint', 'from_field': 'ai_model_id', 'referenced_field': 'id', 'related_name': 'ai_model_endpoints'}, 'recipe_models': {'from_model': 'RecipeModel', 'from_field': 'ai_model', 'referenced_field': 'id', 'related_name': 'recipe_models'}, 'ai_settingss': {'from_model': 'AiSettings', 'from_field': 'ai_model', 'referenced_field': 'id', 'related_name': 'ai_settingss'}, 'agent_conversationss': {'from_model': 'AgentConversations', 'from_field': 'model_id', 'referenced_field': 'id', 'related_name': 'agent_conversationss'}, 'agent_requestss': {'from_model': 'AgentRequests', 'from_field': 'model_id', 'referenced_field': 'id', 'related_name': 'agent_requestss'}, 'cx_conversations': {'from_model': 'CxConversation', 'from_field': 'ai_model_id', 'referenced_field': 'id', 'related_name': 'cx_conversations'}, 'cx_user_requests': {'from_model': 'CxUserRequest', 'from_field': 'ai_model_id', 'referenced_field': 'id', 'related_name': 'cx_user_requests'}, 'cx_requests': {'from_model': 'CxRequest', 'from_field': 'ai_model_id', 'referenced_field': 'id', 'related_name': 'cx_requests'}}
    _database = "supabase_automation_matrix"

class ContentBlocks(Model):
    id = UUIDField(primary_key=True, null=False)
    block_id = CharField(null=False, max_length=100, unique=True)
    label = CharField(null=False, max_length=255)
    description = TextField()
    icon_name = CharField(null=False, max_length=100)
    template = TextField(null=False)
    sort_order = IntegerField(default=0)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    category_id = ForeignKey(to_model=ShortcutCategories, to_column='id', )
    _inverse_foreign_keys = {}
    _database = "supabase_automation_matrix"

class PromptBuiltins(Model):
    id = UUIDField(primary_key=True, null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    name = CharField(null=False)
    description = TextField()
    messages = JSONBField(null=False)
    variable_defaults = JSONBField()
    tools = JSONBField()
    settings = JSONBField()
    created_by_user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', )
    is_active = BooleanField(null=False, default=True)
    source_prompt_id = ForeignKey(to_model=Prompts, to_column='id', )
    source_prompt_snapshot_at = DateTimeField()
    _inverse_foreign_keys = {'prompt_shortcutss': {'from_model': 'PromptShortcuts', 'from_field': 'prompt_builtin_id', 'referenced_field': 'id', 'related_name': 'prompt_shortcutss'}, 'prompt_actionss': {'from_model': 'PromptActions', 'from_field': 'prompt_builtin_id', 'referenced_field': 'id', 'related_name': 'prompt_actionss'}}
    _database = "supabase_automation_matrix"

class TableData(Model):
    id = UUIDField(primary_key=True, null=False, unique=True)
    table_id = ForeignKey(to_model=UserTables, to_column='id', null=False, unique=True)
    data = JSONBField(null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False)
    is_public = BooleanField(null=False, default=False)
    authenticated_read = BooleanField(null=False, default=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    _inverse_foreign_keys = {}
    _database = "supabase_automation_matrix"

class CxConversation(Model):
    id = UUIDField(primary_key=True, null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False)
    title = TextField()
    system_instruction = TextField()
    config = JSONBField(null=False, default={})
    status = TextField(null=False, default='active')
    message_count = SmallIntegerField(null=False, default=0)
    forked_from_id = ForeignKey(to_model='CxConversation', to_column='id', )
    forked_at_position = SmallIntegerField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    metadata = JSONBField(null=False, default={})
    ai_model_id = ForeignKey(to_model=AiModel, to_column='id', )
    parent_conversation_id = ForeignKey(to_model='CxConversation', to_column='id', )
    variables = JSONBField(null=False, default={})
    overrides = JSONBField(null=False, default={})
    _inverse_foreign_keys = {'cx_tool_calls': {'from_model': 'CxToolCall', 'from_field': 'conversation_id', 'referenced_field': 'id', 'related_name': 'cx_tool_calls'}, 'cx_messages': {'from_model': 'CxMessage', 'from_field': 'conversation_id', 'referenced_field': 'id', 'related_name': 'cx_messages'}, 'cx_medias': {'from_model': 'CxMedia', 'from_field': 'conversation_id', 'referenced_field': 'id', 'related_name': 'cx_medias'}, 'cx_user_requests': {'from_model': 'CxUserRequest', 'from_field': 'conversation_id', 'referenced_field': 'id', 'related_name': 'cx_user_requests'}, 'cx_requests': {'from_model': 'CxRequest', 'from_field': 'conversation_id', 'referenced_field': 'id', 'related_name': 'cx_requests'}}
    _database = "supabase_automation_matrix"

class CxMedia(Model):
    id = UUIDField(primary_key=True, null=False)
    conversation_id = ForeignKey(to_model=CxConversation, to_column='id', )
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False)
    kind = TextField(null=False)
    url = TextField(null=False)
    file_uri = TextField()
    mime_type = TextField()
    file_size_bytes = BigIntegerField()
    created_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    metadata = JSONBField(null=False, default={})
    _inverse_foreign_keys = {}
    _database = "supabase_automation_matrix"

class CxMessage(Model):
    id = UUIDField(primary_key=True, null=False)
    conversation_id = ForeignKey(to_model=CxConversation, to_column='id', null=False)
    role = TextField(null=False)
    position = SmallIntegerField(null=False)
    status = TextField(null=False, default='active')
    content = JSONBField(null=False, default=[])
    created_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    metadata = JSONBField(null=False, default={})
    _inverse_foreign_keys = {'cx_tool_calls': {'from_model': 'CxToolCall', 'from_field': 'message_id', 'referenced_field': 'id', 'related_name': 'cx_tool_calls'}}
    _database = "supabase_automation_matrix"

class CxUserRequest(Model):
    id = UUIDField(primary_key=True, null=False)
    conversation_id = ForeignKey(to_model=CxConversation, to_column='id', null=False)
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False)
    trigger_message_position = SmallIntegerField()
    api_class = TextField()
    total_input_tokens = IntegerField(null=False, default=0)
    total_output_tokens = IntegerField(null=False, default=0)
    total_cached_tokens = IntegerField(null=False, default=0)
    total_tokens = IntegerField(null=False, default=0)
    total_cost = DecimalField(default=0)
    total_duration_ms = IntegerField()
    api_duration_ms = IntegerField()
    tool_duration_ms = IntegerField()
    iterations = SmallIntegerField(null=False, default=1)
    total_tool_calls = SmallIntegerField(null=False, default=0)
    status = TextField(null=False, default='pending')
    finish_reason = TextField()
    error = TextField()
    result_start_position = SmallIntegerField()
    result_end_position = SmallIntegerField()
    created_at = DateTimeField(null=False)
    completed_at = DateTimeField()
    deleted_at = DateTimeField()
    metadata = JSONBField(null=False, default={})
    ai_model_id = ForeignKey(to_model=AiModel, to_column='id', )
    _inverse_foreign_keys = {'cx_tool_calls': {'from_model': 'CxToolCall', 'from_field': 'request_id', 'referenced_field': 'id', 'related_name': 'cx_tool_calls'}, 'cx_requests': {'from_model': 'CxRequest', 'from_field': 'user_request_id', 'referenced_field': 'id', 'related_name': 'cx_requests'}}
    _database = "supabase_automation_matrix"

class CxRequest(Model):
    id = UUIDField(primary_key=True, null=False)
    user_request_id = ForeignKey(to_model=CxUserRequest, to_column='id', null=False)
    conversation_id = ForeignKey(to_model=CxConversation, to_column='id', null=False)
    api_class = TextField()
    iteration = SmallIntegerField(null=False, default=1)
    input_tokens = IntegerField()
    output_tokens = IntegerField()
    cached_tokens = IntegerField()
    total_tokens = IntegerField()
    cost = DecimalField()
    api_duration_ms = IntegerField()
    tool_duration_ms = IntegerField()
    total_duration_ms = IntegerField()
    tool_calls_count = SmallIntegerField(default=0)
    tool_calls_details = JSONBField()
    finish_reason = TextField()
    response_id = TextField()
    created_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    metadata = JSONBField(null=False, default={})
    ai_model_id = ForeignKey(to_model=AiModel, to_column='id', null=False)
    _inverse_foreign_keys = {}
    _database = "supabase_automation_matrix"

class CxToolCall(Model):
    id = UUIDField(primary_key=True, null=False)
    conversation_id = ForeignKey(to_model=CxConversation, to_column='id', null=False)
    message_id = ForeignKey(to_model=CxMessage, to_column='id', )
    user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=False)
    request_id = ForeignKey(to_model=CxUserRequest, to_column='id', )
    tool_name = TextField(null=False)
    tool_type = TextField(null=False, default='local')
    call_id = TextField(null=False)
    status = TextField(null=False, default='pending')
    arguments = JSONBField(null=False, default={})
    success = BooleanField(null=False, default=True)
    output = TextField()
    output_type = TextField(default='text')
    is_error = BooleanField(default=False)
    error_type = TextField()
    error_message = TextField()
    duration_ms = IntegerField(null=False, default=0)
    started_at = DateTimeField(null=False)
    completed_at = DateTimeField(null=False)
    input_tokens = IntegerField(default=0)
    output_tokens = IntegerField(default=0)
    total_tokens = IntegerField(default=0)
    cost_usd = DecimalField(default=0)
    iteration = IntegerField(null=False, default=0)
    retry_count = IntegerField(default=0)
    parent_call_id = ForeignKey(to_model='CxToolCall', to_column='id', )
    execution_events = JSONBField(default=[])
    persist_key = TextField()
    file_path = TextField()
    metadata = JSONBField(null=False, default={})
    created_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys = {}
    _database = "supabase_automation_matrix"


model_registry.register_all(
[
        AiProvider,
        CxAgentMemory,
        Prompts,
        ShortcutCategories,
        Tools,
        UserTables,
        AiModel,
        ContentBlocks,
        PromptBuiltins,
        TableData,
        CxConversation,
        CxMedia,
        CxMessage,
        CxUserRequest,
        CxRequest,
        CxToolCall,
        Users
    ]
)



@dataclass
class AiProviderDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class AiProviderManager(BaseManager):
    def __init__(self):
        super().__init__(AiProvider, AiProviderDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_provider):
        pass
    


@dataclass
class CxAgentMemoryDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxAgentMemoryManager(BaseManager):
    def __init__(self):
        super().__init__(CxAgentMemory, CxAgentMemoryDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_agent_memory):
        pass
    


@dataclass
class PromptsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class PromptsManager(BaseManager):
    def __init__(self):
        super().__init__(Prompts, PromptsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, prompts):
        pass
    


@dataclass
class ShortcutCategoriesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class ShortcutCategoriesManager(BaseManager):
    def __init__(self):
        super().__init__(ShortcutCategories, ShortcutCategoriesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, shortcut_categories):
        pass
    


@dataclass
class ToolsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class ToolsManager(BaseManager):
    def __init__(self):
        super().__init__(Tools, ToolsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, tools):
        pass
    


@dataclass
class UserTablesDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class UserTablesManager(BaseManager):
    def __init__(self):
        super().__init__(UserTables, UserTablesDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, user_tables):
        pass
    


@dataclass
class AiModelDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class AiModelManager(BaseManager):
    def __init__(self):
        super().__init__(AiModel, AiModelDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_model):
        pass
    


@dataclass
class ContentBlocksDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class ContentBlocksManager(BaseManager):
    def __init__(self):
        super().__init__(ContentBlocks, ContentBlocksDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, content_blocks):
        pass
    


@dataclass
class PromptBuiltinsDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class PromptBuiltinsManager(BaseManager):
    def __init__(self):
        super().__init__(PromptBuiltins, PromptBuiltinsDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, prompt_builtins):
        pass
    


@dataclass
class TableDataDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class TableDataManager(BaseManager):
    def __init__(self):
        super().__init__(TableData, TableDataDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, table_data):
        pass
    


@dataclass
class CxConversationDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxConversationManager(BaseManager):
    def __init__(self):
        super().__init__(CxConversation, CxConversationDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_conversation):
        pass
    


@dataclass
class CxMediaDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxMediaManager(BaseManager):
    def __init__(self):
        super().__init__(CxMedia, CxMediaDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_media):
        pass
    


@dataclass
class CxMessageDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxMessageManager(BaseManager):
    def __init__(self):
        super().__init__(CxMessage, CxMessageDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_message):
        pass
    


@dataclass
class CxUserRequestDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxUserRequestManager(BaseManager):
    def __init__(self):
        super().__init__(CxUserRequest, CxUserRequestDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_user_request):
        pass
    


@dataclass
class CxRequestDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxRequestManager(BaseManager):
    def __init__(self):
        super().__init__(CxRequest, CxRequestDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_request):
        pass
    


@dataclass
class CxToolCallDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class CxToolCallManager(BaseManager):
    def __init__(self):
        super().__init__(CxToolCall, CxToolCallDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_tool_call):
        pass