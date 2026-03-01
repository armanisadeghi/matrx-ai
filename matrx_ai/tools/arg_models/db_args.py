from typing import Any

from pydantic import BaseModel, Field


class DbQueryArgs(BaseModel):
    query: str = Field(description="Read-only SQL SELECT query to execute")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum rows to return")


class DbInsertArgs(BaseModel):
    table: str = Field(description="Table name to insert into")
    data: dict[str, Any] | list[dict[str, Any]] = Field(description="Row or rows to insert")


class DbUpdateArgs(BaseModel):
    table: str = Field(description="Table name to update")
    data: dict[str, Any] = Field(description="Columns and values to set")
    match: dict[str, Any] = Field(description="WHERE conditions as column=value pairs")


class DbSchemaArgs(BaseModel):
    table: str = Field(default="", description="Table name (empty = list all tables)")
