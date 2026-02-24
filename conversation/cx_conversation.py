# File: database/main/managers/cx_conversation.py
from db.managers.cx_conversation import CxConversationBase

class CxConversationManager(CxConversationBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxConversationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_conversation_manager_instance = CxConversationManager()