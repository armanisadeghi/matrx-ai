from pydantic import BaseModel, Field


class CalculateArgs(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate (e.g. '2 + 2', 'sqrt(16)')")
