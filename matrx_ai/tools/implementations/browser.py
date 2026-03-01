from __future__ import annotations

import logging
import time
from typing import Any

from matrx_ai.tools.arg_models.browser_args import (
    BrowserClickArgs,
    BrowserCloseArgs,
    BrowserGetElementArgs,
    BrowserNavigateArgs,
    BrowserScreenshotArgs,
    BrowserScrollArgs,
    BrowserSelectOptionArgs,
    BrowserTypeArgs,
    BrowserWaitForArgs,
)
from matrx_ai.tools.models import ToolContext, ToolError, ToolResult

logger = logging.getLogger(__name__)


def _mgr():
    from matrx_ai.tools.browser_sessions import get_browser_session_manager

    return get_browser_session_manager()


async def browser_navigate(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Navigate to a URL. Returns a session_id for follow-up browser tool calls."""
    started_at = time.time()
    parsed = BrowserNavigateArgs(**args)

    try:
        manager = _mgr()

        if parsed.session_id:
            session = await manager.get(parsed.session_id)
            if session is None:
                return ToolResult(
                    success=False,
                    error=ToolError(
                        error_type="not_found",
                        message=f"Browser session '{parsed.session_id}' not found or expired.",
                        suggested_action="Call browser_navigate without a session_id to start a new session.",
                    ),
                    started_at=started_at,
                    completed_at=time.time(),
                    tool_name="browser_navigate",
                    call_id=ctx.call_id,
                )
        else:
            session = await manager.create()

        wait_until = (
            parsed.wait_for
            if parsed.wait_for in ("load", "domcontentloaded", "networkidle")
            else "load"
        )
        await session.page.goto(parsed.url, wait_until=wait_until, timeout=30000)

        result_data: dict[str, Any] = {
            "session_id": session.session_id,
            "url": session.page.url,
            "title": await session.page.title(),
        }

        if parsed.extract_text:
            text = await session.page.inner_text("body")
            result_data["text"] = text[:50000]

        return ToolResult(
            success=True,
            output=result_data,
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_navigate",
            call_id=ctx.call_id,
        )
    except ImportError as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="import",
                message=str(exc),
                suggested_action="Run: pip install playwright && playwright install chromium",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_navigate",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="browser",
                message=f"Navigation failed: {exc}",
                is_retryable=True,
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_navigate",
            call_id=ctx.call_id,
        )


async def browser_click(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Click an element on the current page. Requires a session_id from browser_navigate."""
    started_at = time.time()
    parsed = BrowserClickArgs(**args)

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_click",
            call_id=ctx.call_id,
        )

    try:
        await session.page.click(parsed.selector, timeout=10000)

        if parsed.wait_after_ms > 0:
            await session.page.wait_for_timeout(parsed.wait_after_ms)

        text = await session.page.inner_text("body")

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "clicked": parsed.selector,
                "url": session.page.url,
                "title": await session.page.title(),
                "page_text": text[:20000],
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_click",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Click failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_click",
            call_id=ctx.call_id,
        )


async def browser_type_text(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Type text into an input on the current page. Requires a session_id from browser_navigate."""
    started_at = time.time()
    parsed = BrowserTypeArgs(**args)

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_type_text",
            call_id=ctx.call_id,
        )

    try:
        if parsed.clear_first:
            await session.page.fill(parsed.selector, parsed.text, timeout=10000)
        else:
            await session.page.type(parsed.selector, parsed.text, timeout=10000)

        if parsed.press_enter:
            await session.page.keyboard.press("Enter")
            await session.page.wait_for_load_state("load", timeout=15000)

        text = await session.page.inner_text("body")

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "typed": parsed.text[:200],
                "selector": parsed.selector,
                "url": session.page.url,
                "page_text": text[:20000],
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_type_text",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Type failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_type_text",
            call_id=ctx.call_id,
        )


async def browser_screenshot(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Take a screenshot of the current page. Requires a session_id from browser_navigate."""
    import base64

    started_at = time.time()
    parsed = BrowserScreenshotArgs(**args)

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_screenshot",
            call_id=ctx.call_id,
        )

    try:
        await session.page.set_viewport_size(
            {"width": parsed.width, "height": parsed.height}
        )

        if parsed.selector:
            element = await session.page.query_selector(parsed.selector)
            screenshot_bytes = (
                await element.screenshot(type="png")
                if element
                else await session.page.screenshot(type="png", full_page=True)
            )
        else:
            screenshot_bytes = await session.page.screenshot(type="png", full_page=True)

        b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "url": session.page.url,
                "screenshot_base64": b64,
                "screenshot_size_bytes": len(screenshot_bytes),
                "format": "png",
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_screenshot",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Screenshot failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_screenshot",
            call_id=ctx.call_id,
        )


async def browser_close(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Close a browser session to free resources. Always call this when done browsing."""
    started_at = time.time()
    parsed = BrowserCloseArgs(**args)

    await _mgr().close(parsed.session_id)

    return ToolResult(
        success=True,
        output={"closed": parsed.session_id},
        started_at=started_at,
        completed_at=time.time(),
        tool_name="browser_close",
        call_id=ctx.call_id,
    )


async def browser_select_option(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Select an option in a <select> dropdown by value or visible label."""
    started_at = time.time()
    parsed = BrowserSelectOptionArgs(**args)

    if not parsed.value and not parsed.label:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation",
                message="Provide either 'value' or 'label' to identify which option to select.",
                suggested_action="Use 'value' to match the option's value attribute, or 'label' to match its visible text.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_select_option",
            call_id=ctx.call_id,
        )

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_select_option",
            call_id=ctx.call_id,
        )

    try:
        if parsed.value:
            selected = await session.page.select_option(
                parsed.selector, value=parsed.value, timeout=10000
            )
        else:
            selected = await session.page.select_option(
                parsed.selector, label=parsed.label, timeout=10000
            )

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "selector": parsed.selector,
                "selected_values": selected,
                "url": session.page.url,
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_select_option",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Select failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_select_option",
            call_id=ctx.call_id,
        )


async def browser_wait_for(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Wait for a CSS selector or text to appear on the page. Essential for SPAs and dynamic content."""
    started_at = time.time()
    parsed = BrowserWaitForArgs(**args)

    if not parsed.selector and not parsed.text:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="validation",
                message="Provide either 'selector' or 'text' to wait for.",
                suggested_action="Use 'selector' to wait for a DOM element, or 'text' to wait for visible text.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_wait_for",
            call_id=ctx.call_id,
        )

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_wait_for",
            call_id=ctx.call_id,
        )

    try:
        if parsed.selector:
            valid_states = {"visible", "attached", "detached", "hidden"}
            state = parsed.state if parsed.state in valid_states else "visible"
            await session.page.wait_for_selector(
                parsed.selector, state=state, timeout=parsed.timeout_ms
            )
            waited_for = f"selector '{parsed.selector}' ({state})"
        else:
            await session.page.wait_for_function(
                f"document.body.innerText.includes({repr(parsed.text)})",
                timeout=parsed.timeout_ms,
            )
            waited_for = f"text '{parsed.text[:80]}'"

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "waited_for": waited_for,
                "url": session.page.url,
                "title": await session.page.title(),
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_wait_for",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="browser",
                message=f"Wait timed out or failed: {exc}",
                is_retryable=True,
                suggested_action="Increase timeout_ms or verify the selector/text is correct.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_wait_for",
            call_id=ctx.call_id,
        )


async def browser_get_element(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Inspect a specific DOM element: get its text, inner HTML, and any requested attributes."""
    started_at = time.time()
    parsed = BrowserGetElementArgs(**args)

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_get_element",
            call_id=ctx.call_id,
        )

    try:
        element = await session.page.query_selector(parsed.selector)
        if element is None:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="not_found",
                    message=f"No element found for selector '{parsed.selector}'.",
                    suggested_action="Check the selector. Use browser_navigate with extract_text=true to see page content.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="browser_get_element",
                call_id=ctx.call_id,
            )

        inner_text = await element.inner_text()
        inner_html = await element.inner_html()
        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

        attrs: dict[str, str | None] = {}
        for attr in parsed.attributes:
            attrs[attr] = await element.get_attribute(attr)

        bounding_box = await element.bounding_box()

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "selector": parsed.selector,
                "tag": tag_name,
                "text": inner_text[:5000],
                "inner_html": inner_html[:5000],
                "attributes": attrs,
                "bounding_box": bounding_box,
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_get_element",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Get element failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_get_element",
            call_id=ctx.call_id,
        )


async def browser_scroll(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Scroll the page or a specific container. Useful for revealing lazy-loaded content."""
    started_at = time.time()
    parsed = BrowserScrollArgs(**args)

    session = await _mgr().get(parsed.session_id)
    if session is None:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="not_found",
                message=f"Browser session '{parsed.session_id}' not found or expired.",
                suggested_action="Call browser_navigate first to get a session_id.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_scroll",
            call_id=ctx.call_id,
        )

    try:
        if parsed.selector:
            element = await session.page.query_selector(parsed.selector)
            if element is None:
                return ToolResult(
                    success=False,
                    error=ToolError(
                        error_type="not_found",
                        message=f"No element found for selector '{parsed.selector}'.",
                    ),
                    started_at=started_at,
                    completed_at=time.time(),
                    tool_name="browser_scroll",
                    call_id=ctx.call_id,
                )
            if parsed.direction == "top":
                await element.evaluate("el => el.scrollTop = 0")
            elif parsed.direction == "bottom":
                await element.evaluate("el => el.scrollTop = el.scrollHeight")
            elif parsed.direction == "up":
                await element.evaluate(f"el => el.scrollTop -= {parsed.amount_px}")
            else:
                await element.evaluate(f"el => el.scrollTop += {parsed.amount_px}")
        else:
            if parsed.direction == "top":
                await session.page.evaluate("window.scrollTo(0, 0)")
            elif parsed.direction == "bottom":
                await session.page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )
            elif parsed.direction == "up":
                await session.page.evaluate(f"window.scrollBy(0, -{parsed.amount_px})")
            else:
                await session.page.evaluate(f"window.scrollBy(0, {parsed.amount_px})")

        await session.page.wait_for_timeout(300)

        scroll_y = await session.page.evaluate("window.scrollY")
        page_height = await session.page.evaluate("document.body.scrollHeight")

        return ToolResult(
            success=True,
            output={
                "session_id": session.session_id,
                "direction": parsed.direction,
                "scroll_y": scroll_y,
                "page_height": page_height,
                "url": session.page.url,
            },
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_scroll",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Scroll failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_scroll",
            call_id=ctx.call_id,
        )
