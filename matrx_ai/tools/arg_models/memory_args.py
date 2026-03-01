from pydantic import BaseModel, Field


class MemoryStoreArgs(BaseModel):
    key: str = Field(description="Semantic key for later retrieval")
    content: str = Field(description="The memory content to store")
    memory_type: str = Field(default="long", description="Memory type: 'short', 'medium', 'long'")
    scope: str = Field(default="user", description="Scope: 'user', 'project', 'organization'")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")


class MemoryRecallArgs(BaseModel):
    key: str = Field(default="", description="Exact key to recall (empty = semantic search)")
    query: str = Field(default="", description="Natural language query for semantic search")
    memory_type: str | None = Field(default=None, description="Filter by type: 'short', 'medium', 'long'")
    scope: str = Field(default="user", description="Scope to search in")
    limit: int = Field(default=5, ge=1, le=20, description="Max memories to return")


class MemorySearchArgs(BaseModel):
    query: str = Field(description="Natural language search query")
    scope: str = Field(default="user", description="Scope to search in")
    memory_type: str | None = Field(default=None, description="Filter by type")
    limit: int = Field(default=10, ge=1, le=50, description="Max results")


class MemoryUpdateArgs(BaseModel):
    key: str = Field(description="Key of the memory to update")
    content: str = Field(description="New content")
    scope: str = Field(default="user", description="Scope")
    importance: float | None = Field(default=None, ge=0.0, le=1.0, description="Updated importance")


class MemoryForgetArgs(BaseModel):
    key: str = Field(description="Key of the memory to delete")
    scope: str = Field(default="user", description="Scope")
