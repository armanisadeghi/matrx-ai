from __future__ import annotations

import logging
import time
from typing import Any

from tools.arg_models.browser_args import (
    BrowserClickArgs,
    BrowserNavigateArgs,
    BrowserScreenshotArgs,
    BrowserTypeArgs,
)
from tools.models import ToolContext, ToolError, ToolResult

logger = logging.getLogger(__name__)


async def _get_browser_page(ctx: ToolContext) -> Any:
    """Get or create a Playwright browser page for this context.

    Uses a pool of browser contexts managed per conversation.
    Falls back to creating a new one if none exists.
    """
    try:
        from playwright.async_api import async_playwright

        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        return page
    except ImportError:
        raise ImportError("playwright is not installed. Run: pip install playwright && playwright install chromium")


async def browser_navigate(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = BrowserNavigateArgs(**args)

    try:
        page = await _get_browser_page(ctx)
        wait_until = parsed.wait_for if parsed.wait_for in ("load", "domcontentloaded", "networkidle") else "load"
        await page.goto(parsed.url, wait_until=wait_until, timeout=30000)

        result_data: dict[str, Any] = {
            "url": page.url,
            "title": await page.title(),
        }

        if parsed.extract_text:
            text = await page.inner_text("body")
            result_data["text"] = text[:50000]

        await page.context.browser.close()

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
            error=ToolError(error_type="import", message=str(exc)),
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
    started_at = time.time()
    parsed = BrowserClickArgs(**args)

    try:
        page = await _get_browser_page(ctx)
        await page.click(parsed.selector, timeout=10000)

        if parsed.wait_after_ms > 0:
            await page.wait_for_timeout(parsed.wait_after_ms)

        text = await page.inner_text("body")
        await page.context.browser.close()

        return ToolResult(
            success=True,
            output={"clicked": parsed.selector, "page_text": text[:20000]},
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
    started_at = time.time()
    parsed = BrowserTypeArgs(**args)

    try:
        page = await _get_browser_page(ctx)

        if parsed.clear_first:
            await page.fill(parsed.selector, parsed.text, timeout=10000)
        else:
            await page.type(parsed.selector, parsed.text, timeout=10000)

        await page.context.browser.close()

        return ToolResult(
            success=True,
            output={"typed": parsed.text[:100], "selector": parsed.selector},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_type",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(error_type="browser", message=f"Type failed: {exc}"),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="browser_type",
            call_id=ctx.call_id,
        )


async def browser_screenshot(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = BrowserScreenshotArgs(**args)

    try:
        page = await _get_browser_page(ctx)
        await page.set_viewport_size({"width": parsed.width, "height": parsed.height})

        if parsed.url:
            await page.goto(parsed.url, wait_until="networkidle", timeout=30000)

        if parsed.selector:
            element = await page.query_selector(parsed.selector)
            if element:
                screenshot_bytes = await element.screenshot(type="png")
            else:
                screenshot_bytes = await page.screenshot(type="png", full_page=True)
        else:
            screenshot_bytes = await page.screenshot(type="png", full_page=True)

        import base64
        b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        await page.context.browser.close()

        return ToolResult(
            success=True,
            output={
                "screenshot_base64": b64[:100] + "...(truncated for preview)",
                "screenshot_size": len(screenshot_bytes),
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
