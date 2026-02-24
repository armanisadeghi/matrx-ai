# File: database/main/managers/cx_user_request.py
from db.managers.cx_user_request import CxUserRequestBase

class CxUserRequestManager(CxUserRequestBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxUserRequestManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_user_request_manager_instance = CxUserRequestManager()