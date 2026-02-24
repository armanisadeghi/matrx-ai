# File: database/main/managers/cx_message.py
from db.managers.cx_message import CxMessageBase


class CxMessageManager(CxMessageBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxMessageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_message_manager_instance = CxMessageManager()