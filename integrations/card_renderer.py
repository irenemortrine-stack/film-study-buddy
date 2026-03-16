import asyncio
import base64
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright


async def html_to_png_bytes(html: str, width: int = 512, height: int = 512) -> bytes:
    """Render HTML to PNG bytes using Playwright headless browser."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html)
        await page.wait_for_timeout(200)
        screenshot = await page.screenshot(clip={"x": 0, "y": 0, "width": width, "height": height})
        await browser.close()
    return screenshot


async def html_to_png_base64(html: str) -> str:
    data = await html_to_png_bytes(html)
    return base64.b64encode(data).decode()
