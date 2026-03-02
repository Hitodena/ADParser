"""Session capture module for AutoDealer parser."""

from typing import Any

from loguru import logger
from playwright.async_api import Page

from .config import CATALOG_WORKS_URL, TIMEOUT


async def capture_session(page: Page) -> dict[str, Any]:
    """Navigate to CATALOG_WORKS_URL and capture cookies + headers.

    Args:
        page: Playwright page object

    Returns:
        Dictionary containing cookies and headers needed for API requests
    """
    captured_headers: dict[str, str] = {}

    def handle_request(request) -> None:
        if "/api/commonWorks/search" in request.url:
            captured_headers.update(dict(request.headers))

    page.on("request", handle_request)

    await page.goto(
        CATALOG_WORKS_URL, wait_until="load", timeout=TIMEOUT * 1000
    )

    await page.wait_for_timeout(5000)

    logger.info(f"Captured headers: {list(captured_headers.keys())}")

    cookies = await page.context.cookies()

    cookies_dict: dict[str, str] = {}
    for cookie in cookies:
        name = cookie.get("name")
        value = cookie.get("value")
        if name and value:
            cookies_dict[name] = value

    # Build headers from captured API request headers
    headers: dict[str, str] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": CATALOG_WORKS_URL,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    # Add captured Autodealer headers
    autodealer_keys = [
        "autodealer-product",
        "autodealer-var",
        "autodealer-version",
        "autodealer-wsid",
    ]
    for key in autodealer_keys:
        if key in captured_headers:
            header_name = "-".join(
                part.capitalize() for part in key.split("-")
            )
            headers[header_name] = captured_headers[key]

    return {
        "cookies": cookies_dict,
        "headers": headers,
    }
