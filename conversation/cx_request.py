# File: database/main/managers/cx_request.py
from db.managers.cx_request import CxRequestBase

class CxRequestManager(CxRequestBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxRequestManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_request_manager_instance = CxRequestManager()