from pydantic import BaseModel, Field


class ShellExecuteArgs(BaseModel):
    command: str = Field(description="Shell command to execute")
    working_dir: str = Field(default=".", description="Working directory (relative to workspace)")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Execution timeout in seconds")
    allow_network: bool = Field(default=True, description="Allow network access")


class ShellPythonArgs(BaseModel):
    code: str = Field(description="Python code to execute")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Execution timeout")
