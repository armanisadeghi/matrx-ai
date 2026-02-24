# File: database/main/managers/cx_media.py
from db.managers.cx_media import CxMediaBase


class CxMediaManager(CxMediaBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxMediaManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_media_manager_instance = CxMediaManager()