"""Warehouse parser module for AutoDealer."""

import asyncio
import csv
import re
from typing import Any

from loguru import logger
from playwright.async_api import Page

from .auth import login
from .browser import BrowserManager
from .config import TIMEOUT, WAREHOUSES_URL


def parse_price(price_text: str) -> float:
    if not price_text:
        return 0.0
    price_text = price_text.split("(")[0]
    cleaned = re.sub(r"[\s\u00a0\u202f\ufeff₽]", "", price_text)
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


async def get_row_id(row) -> str:
    """Get unique row identifier from checkbox input id attribute."""
    checkbox = row.locator("input[type='checkbox']")
    if await checkbox.count() > 0:
        return await checkbox.get_attribute("id") or ""
    return ""


async def get_row_details(page: Page) -> dict[str, Any]:
    """Extract data from the right-side detail panel after dblclick."""
    details: dict[str, Any] = {}

    try:
        await page.wait_for_selector(
            "app-catalogs-warehouse-view .title-name",
            timeout=6000,
        )

        panel = page.locator("app-catalogs-warehouse-view .item-detail")

        async def label_content(label_text: str) -> str:
            elem = panel.locator(f'label:has-text("{label_text}") + .content')
            if await elem.count() > 0:
                return (await elem.inner_text()).strip()
            return ""

        async def label_first_span(label_text: str) -> str:
            span = panel.locator(
                f'label:has-text("{label_text}") + .content span:first-child'
            )
            if await span.count() > 0:
                return (await span.first.inner_text()).strip()
            return await label_content(label_text)

        details["name"] = await label_content("Наименование в чеке")
        details["manufacturer"] = await label_content("Производитель")
        details["unit_of_measure"] = await label_content("Единица измерения")

        mfr_num = panel.locator(".number--manufacturer").first
        details["manufacturer_number"] = (
            (await mfr_num.inner_text()).strip()
            if await mfr_num.count() > 0
            else ""
        )

        details["selling_price"] = parse_price(
            await label_first_span("Цена продажи")
        )
        details["purchase_price"] = parse_price(
            await label_first_span("Цена прихода")
        )
        details["max_discount"] = await label_content("Максимальная скидка")

    except Exception as exc:
        logger.warning(f"Failed to get row details: {exc}")

    return details


async def process_page(page: Page) -> list[dict[str, Any]]:
    """Process all rows on current pagination page.

    Uses reactive scrolling: after processing all currently visible rows,
    scrolls only if needed to load more items. Tracks processed rows by
    checkbox ID to avoid duplicates.
    """
    items = []
    processed_ids: set[str] = set()
    viewport = page.locator("cdk-virtual-scroll-viewport")

    pagination_range = page.locator(".pagination--range .gray")
    range_text = (
        await pagination_range.inner_text()
        if await pagination_range.count() > 0
        else "1-50"
    )
    items_per_page = int(range_text.split("-")[-1].strip())

    await viewport.evaluate("el => el.scrollTop = 0")
    await asyncio.sleep(1)

    first_row = page.locator("app-warehouse-row").first
    await first_row.locator("app-nomenclature-column").dblclick()
    await asyncio.sleep(2)

    # Get viewport dimensions
    client_height = await viewport.evaluate("el => el.clientHeight")
    scroll_step = int(
        client_height * 0.5
    )  # Smaller step for more controlled scrolling
    logger.debug(
        f"Viewport height: {client_height}px, scroll_step={scroll_step}px, "
        f"items_per_page={items_per_page}"
    )

    while True:
        rows = page.locator("app-warehouse-row")
        count = await rows.count()

        new_items_in_batch = 0

        # Process all currently visible rows
        for i in range(count):
            row = rows.nth(i)
            row_id = await get_row_id(row)
            if not row_id or row_id in processed_ids:
                continue

            processed_ids.add(row_id)
            new_items_in_batch += 1

            try:
                qty_elem = row.locator(".QUANTITY_AVAILABLE")
                qty_text = (
                    (await qty_elem.inner_text()).strip()
                    if await qty_elem.count() > 0
                    else ""
                )
                qty_match = re.search(r"(\d[\d\s\u00a0]*)", qty_text)
                quantity = (
                    int(re.sub(r"[\s\u00a0]", "", qty_match.group(1)))
                    if qty_match
                    else 0
                )

                await row.locator("app-nomenclature-column").dblclick()
                await asyncio.sleep(2)

                details = await get_row_details(page)
                details["quantity"] = quantity
                items.append(details)

                logger.debug(
                    f"Collected #{len(items)}: {details.get('name', '')[:40]}"
                )

            except Exception as exc:
                logger.warning(f"Row failed ({row_id}): {exc}")

        # After processing all visible rows, decide whether to scroll
        if new_items_in_batch == 0:
            # No new items found - check if we can scroll more
            scroll_info = await viewport.evaluate(
                "el => ({ scrollTop: el.scrollTop, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight })"
            )

            can_scroll = (
                scroll_info["scrollTop"] + scroll_info["clientHeight"]
                < scroll_info["scrollHeight"] - 10
            )

            if can_scroll:
                await viewport.evaluate(f"el => el.scrollTop += {scroll_step}")
                await asyncio.sleep(1.5)
                continue
            else:
                # Can't scroll anymore - we're done
                break
        else:
            # We collected some items, scroll to load more
            await viewport.evaluate(f"el => el.scrollTop += {scroll_step}")
            await asyncio.sleep(1.5)

    logger.info(f"Page done: {len(items)} items collected")
    return items


async def load_next(page: Page) -> bool:
    """Close detail panel, then click pagination next. Returns True if clicked."""

    next_button = page.locator(".input-page-more")
    if await next_button.count() > 0:
        try:
            await next_button.click()
            await asyncio.sleep(3)
            return True
        except Exception as exc:
            logger.warning(f"Failed to click next page: {exc}")
            return False
    return False


async def parse_warehouse(
    username: str,
    password: str,
    headless: bool,
) -> list[dict[str, Any]]:
    """Parse warehouse catalog — all pages."""
    logger.info("Starting warehouse parser...")

    browser_manager = BrowserManager(headless=headless)
    await browser_manager.start()

    try:
        async with browser_manager.context() as page:
            logger.info("Logging in...")
            await login(page, username, password)
            logger.success("Login successful")

            await page.goto(
                WAREHOUSES_URL, wait_until="load", timeout=TIMEOUT * 1000
            )

            all_items: list[dict[str, Any]] = []
            page_num = 1

            while True:
                logger.info(f"Processing page {page_num}...")
                page_items = await process_page(page)
                all_items.extend(page_items)
                logger.success(
                    f"Page {page_num}: {len(page_items)} items "
                    f"(total: {len(all_items)})"
                )

                if not await load_next(page):
                    break
                page_num += 1

            logger.success(f"Total items collected: {len(all_items)}")
            return all_items

    finally:
        await browser_manager.close()

    return []


async def run_warehouse_parser(
    username: str,
    password: str,
    output_path: str,
    headless: bool,
) -> None:
    """Run the warehouse parser and save to CSV."""

    items = await parse_warehouse(username, password, headless)

    if not items:
        logger.warning("No items collected")
        return

    columns = [
        "name",
        "manufacturer",
        "unit_of_measure",
        "manufacturer_number",
        "quantity",
        "selling_price",
        "purchase_price",
        "max_discount",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)

    logger.success(f"Saved {len(items)} items to {output_path}")
