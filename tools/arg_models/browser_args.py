from pydantic import BaseModel, Field


class BrowserNavigateArgs(BaseModel):
    url: str = Field(description="URL to navigate to")
    wait_for: str = Field(default="load", description="Wait condition: 'load', 'domcontentloaded', 'networkidle'")
    extract_text: bool = Field(default=True, description="Extract visible page text after navigation")
    session_id: str = Field(default="", description="Existing session ID to reuse (empty = create new session)")


class BrowserClickArgs(BaseModel):
    selector: str = Field(description="CSS selector of the element to click")
    session_id: str = Field(description="Session ID returned by browser_navigate")
    wait_after_ms: int = Field(default=1000, ge=0, le=10000, description="Milliseconds to wait after the click")


class BrowserTypeArgs(BaseModel):
    selector: str = Field(description="CSS selector of the input element to type into")
    text: str = Field(description="Text to type")
    session_id: str = Field(description="Session ID returned by browser_navigate")
    clear_first: bool = Field(default=True, description="Clear the field before typing")
    press_enter: bool = Field(default=False, description="Press Enter after typing (e.g. to submit a search)")


class BrowserScreenshotArgs(BaseModel):
    session_id: str = Field(description="Session ID returned by browser_navigate")
    selector: str = Field(default="", description="CSS selector to screenshot (empty = full page)")
    width: int = Field(default=1280, ge=320, le=3840, description="Viewport width in pixels")
    height: int = Field(default=720, ge=240, le=2160, description="Viewport height in pixels")


class BrowserSelectOptionArgs(BaseModel):
    session_id: str = Field(description="Session ID returned by browser_navigate")
    selector: str = Field(description="CSS selector of the <select> element")
    value: str = Field(default="", description="Option value attribute to select (use this OR label)")
    label: str = Field(default="", description="Visible option text to select (use this OR value)")


class BrowserWaitForArgs(BaseModel):
    session_id: str = Field(description="Session ID returned by browser_navigate")
    selector: str = Field(default="", description="CSS selector to wait for (empty if waiting for text or navigation)")
    text: str = Field(default="", description="Text that must appear on the page (empty if waiting for selector or navigation)")
    timeout_ms: int = Field(default=10000, ge=500, le=60000, description="Maximum milliseconds to wait")
    state: str = Field(default="visible", description="Selector state to wait for: 'visible', 'attached', 'detached', 'hidden'")


class BrowserGetElementArgs(BaseModel):
    session_id: str = Field(description="Session ID returned by browser_navigate")
    selector: str = Field(description="CSS selector of the element to inspect")
    attributes: list[str] = Field(default_factory=list, description="HTML attribute names to extract (e.g. ['href', 'src', 'value', 'placeholder'])")


class BrowserScrollArgs(BaseModel):
    session_id: str = Field(description="Session ID returned by browser_navigate")
    direction: str = Field(default="down", description="Scroll direction: 'down', 'up', 'top', 'bottom'")
    amount_px: int = Field(default=500, ge=0, le=10000, description="Pixels to scroll (ignored for 'top' and 'bottom')")
    selector: str = Field(default="", description="CSS selector of a scrollable container (empty = scroll the page)")


class BrowserCloseArgs(BaseModel):
    session_id: str = Field(description="Session ID to close")
