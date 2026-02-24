from typing import Literal

from pydantic import BaseModel, Field


class WebSearchArgs(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=5, description="Search queries to execute")
    freshness: str | None = Field(default=None, description="Time filter: 'day', 'week', 'month'")
    max_results_per_query: int = Field(default=5, ge=1, le=20, description="Max results per query")


class WebReadArgs(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=10, description="URLs to scrape and read")
    instructions: str = Field(default="", description="Instructions for how to process the content")
    summarize: bool = Field(default=False, description="Whether to summarize content with an AI model")
    max_content_length: int = Field(default=50000, ge=100, le=200000, description="Max chars of content to return per URL")


RESEARCH_DEPTH_CONFIG: dict[str, dict[str, int]] = {
    "shallow": {"urls_per_query": 3, "good_scrape_threshold": 1000, "target_good_per_query": 2},
    "medium": {"urls_per_query": 5, "good_scrape_threshold": 1000, "target_good_per_query": 3},
    "deep": {"urls_per_query": 8, "good_scrape_threshold": 1000, "target_good_per_query": 5},
    "very_deep": {"urls_per_query": 12, "good_scrape_threshold": 1000, "target_good_per_query": 7},
}


class WebResearchArgs(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=5, description="Search queries to execute concurrently")
    instructions: str = Field(description="Specific instructions directing what the research should focus on")
    freshness: str | None = Field(default=None, description="Filter results by recency: pd (past day), pw (past week), pm (past month), py (past year)")
    research_depth: Literal["shallow", "medium", "deep", "very_deep"] = Field(
        default="medium",
        description="Controls how many URLs are scraped and analyzed per query",
    )
    country: str = Field(default="us", description="Two-letter country code for search results")
