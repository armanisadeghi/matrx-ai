from pydantic import BaseModel, Field


class TextAnalyzeArgs(BaseModel):
    text: str = Field(description="Text to analyze")
    analysis_type: str = Field(
        default="summary",
        description="Type of analysis: 'summary', 'sentiment', 'keywords', 'entities', 'language'",
    )


class RegexExtractArgs(BaseModel):
    text: str = Field(description="Text to search")
    pattern: str = Field(description="Regular expression pattern")
    group: int = Field(default=0, ge=0, description="Capture group index to return")
    find_all: bool = Field(default=True, description="Return all matches (True) or just the first (False)")
