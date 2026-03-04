# File: db/managers/__init__.py
# from .ai_model import AiModelBase, AiModelDTO, AiModelView
from .ai_provider import AiProviderBase, AiProviderDTO, AiProviderView
from .content_blocks import ContentBlocksBase, ContentBlocksDTO, ContentBlocksView
from .cx_agent_memory import CxAgentMemoryBase, CxAgentMemoryDTO, CxAgentMemoryView
from .cx_conversation import CxConversationBase, CxConversationDTO, CxConversationView
from .cx_media import CxMediaBase, CxMediaDTO, CxMediaView
from .cx_message import CxMessageBase, CxMessageDTO, CxMessageView
from .cx_request import CxRequestBase, CxRequestDTO, CxRequestView
from .cx_tool_call import CxToolCallBase, CxToolCallDTO, CxToolCallView
from .cx_user_request import CxUserRequestBase, CxUserRequestDTO, CxUserRequestView
from .prompt_builtins import PromptBuiltinsBase, PromptBuiltinsDTO, PromptBuiltinsView
from .prompts import PromptsBase, PromptsDTO, PromptsView
from .shortcut_categories import (
    ShortcutCategoriesBase,
    ShortcutCategoriesDTO,
    ShortcutCategoriesView,
)
from .table_data import TableDataBase, TableDataDTO, TableDataView
from .tools import ToolsBase, ToolsDTO, ToolsView
from .user_tables import UserTablesBase, UserTablesDTO, UserTablesView
