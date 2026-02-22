from pydantic import BaseModel, Field


class FsReadArgs(BaseModel):
    path: str = Field(description="Path to the file to read (relative to workspace)")
    offset: int = Field(default=0, ge=0, description="Byte offset to start reading from")
    limit: int = Field(default=0, ge=0, description="Max bytes to read (0 = entire file, max 1MB)")


class FsWriteArgs(BaseModel):
    path: str = Field(description="Path to the file to write (relative to workspace)")
    content: str = Field(description="Content to write")
    create_dirs: bool = Field(default=True, description="Create parent directories if missing")
    append: bool = Field(default=False, description="Append to existing file instead of overwriting")


class FsListArgs(BaseModel):
    path: str = Field(default=".", description="Directory path to list")
    recursive: bool = Field(default=False, description="List recursively")
    pattern: str = Field(default="", description="Glob pattern to filter (e.g. '*.py')")


class FsSearchArgs(BaseModel):
    pattern: str = Field(description="Search pattern (file name glob or content regex)")
    path: str = Field(default=".", description="Directory to search in")
    content_search: bool = Field(default=False, description="Search file contents instead of names")
    max_results: int = Field(default=50, ge=1, le=500, description="Max results")


class FsMkdirArgs(BaseModel):
    path: str = Field(description="Directory path to create")
    parents: bool = Field(default=True, description="Create parent directories")
