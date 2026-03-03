"""Authentication module for AutoDealer parser."""

import asyncio

from loguru import logger
from playwright.async_api import Page

from .config import LOGIN_URL, TIMEOUT


async def login(page: Page, username: str, password: str) -> bool:
    """Login to autodealer.ru.

    Args:
        page (Page): Playwright page object
        username (str): User email/username
        password (str): User password

    Returns:
        True if login successful, raises error otherwise

    Raises:
        RuntimeError: If login failed or redirected back to auth page
    """
    login_url = f"{LOGIN_URL}"

    await page.goto(login_url, wait_until="load", timeout=TIMEOUT * 1000)

    frame = page.frame_locator("#carrot-frame-bumperCookies")
    accept_cookie_btn = frame.get_by_role("button", name="Я согласен")
    try:
        logger.debug("Clicking accept cookie button")
        await accept_cookie_btn.click(timeout=5000)
        logger.debug("Cookie accepted")
    except Exception:
        logger.debug("Cookie button not found")

    username_locator = page.get_by_role("textbox", name="Email")
    password_locator = page.get_by_role("textbox", name="Пароль")

    await username_locator.fill(username)
    await asyncio.sleep(5)
    await password_locator.fill(password)

    auth_button = page.get_by_text("Войти", exact=True).nth(3)
    await auth_button.click()

    logger.info("Waiting for redirect...")
    await page.wait_for_load_state("load", timeout=TIMEOUT * 1000)
    await asyncio.sleep(10)

    current_url = page.url
    if "/auth" in current_url:
        raise RuntimeError(
            f"Login failed: redirected back to auth page, current url: {current_url}"
        )

    return True
