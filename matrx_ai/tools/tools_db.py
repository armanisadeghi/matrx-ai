from db.managers.tools import ToolsBase

class ToolsManager(ToolsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ToolsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

tools_manager_instance = ToolsManager()

