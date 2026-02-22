from pydantic import BaseModel, Field


class BrowserNavigateArgs(BaseModel):
    url: str = Field(description="URL to navigate to")
    wait_for: str = Field(default="load", description="Wait condition: 'load', 'domcontentloaded', 'networkidle'")
    extract_text: bool = Field(default=True, description="Extract page text content")


class BrowserClickArgs(BaseModel):
    selector: str = Field(description="CSS selector of element to click")
    wait_after_ms: int = Field(default=1000, ge=0, le=10000, description="Milliseconds to wait after click")


class BrowserTypeArgs(BaseModel):
    selector: str = Field(description="CSS selector of input element")
    text: str = Field(description="Text to type")
    clear_first: bool = Field(default=True, description="Clear the field before typing")


class BrowserScreenshotArgs(BaseModel):
    url: str = Field(default="", description="URL to navigate to first (empty = current page)")
    selector: str = Field(default="", description="CSS selector to screenshot (empty = full page)")
    width: int = Field(default=1280, ge=320, le=3840, description="Viewport width")
    height: int = Field(default=720, ge=240, le=2160, description="Viewport height")
