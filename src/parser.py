"""Main parser module for AutoDealer."""

import asyncio

from loguru import logger

from .auth import login
from .browser import BrowserManager
from .client import APIClient
from .config import FOLDERS
from .csv_writer import write_to_csv
from .session import capture_session


async def run_parser(
    username: str,
    password: str,
    output_path: str,
    headless: bool,
) -> None:
    """Run the AutoDealer parser.

    Args:
        username: Login username/email
        password: Login password
        output_path: Path to output CSV file
        headless: Run browser in headless mode
    """
    logger.info("Starting AutoDealer parser...")

    browser_manager = BrowserManager(headless=headless)
    await browser_manager.start()

    try:
        async with browser_manager.context() as page:
            logger.info("Logging in...")
            await login(page, username, password)
            logger.success("Login successful")

            logger.info("Capturing session...")
            session_data = await capture_session(page)
            logger.success(
                f"Session captured: {len(session_data['cookies'])} cookies"
            )

            logger.info("Creating API client...")
            client = APIClient(
                cookies=session_data["cookies"],
                headers=session_data["headers"],
            )

            try:
                # Collect all works from all folders
                all_works_list = []
                all_work_details = []

                for folder in FOLDERS:
                    logger.info(
                        f"Fetching works from folder {folder.folder_id} "
                        f"(filter_barcode={folder.filter_barcode}, "
                        f"needed_details={folder.needed_details})..."
                    )

                    works_list = await client.get_works_list(
                        folder_id=folder.folder_id,
                        filter_barcode=folder.filter_barcode,
                    )
                    logger.success(
                        f"Found {len(works_list)} services in folder "
                        f"{folder.folder_id}"
                    )

                    # Fetch details only if needed
                    folder_details = []
                    if folder.needed_details:
                        total = len(works_list)
                        for idx, work in enumerate(works_list, 1):
                            logger.info(
                                f"Fetching detail {idx}/{total}: {work.name}"
                            )
                            try:
                                detail = await client.get_work_detail(work.id)
                                folder_details.append(detail)
                            except Exception as exc:
                                logger.warning(
                                    f"Failed to get detail for {work.id}: {exc}"
                                )
                            finally:
                                await asyncio.sleep(5)
                    else:
                        logger.info(
                            f"Skipping details for folder {folder.folder_id}"
                        )

                    logger.success(
                        f"Fetched details for {len(folder_details)} works "
                        f"from folder {folder.folder_id}"
                    )

                    # Add to overall collections
                    all_works_list.extend(works_list)
                    all_work_details.extend(folder_details)

                logger.success(f"Total: {len(all_works_list)} services")

                logger.info(f"Writing to CSV: {output_path}")
                write_to_csv(all_works_list, all_work_details, output_path)
                logger.success(f"CSV saved to {output_path}")

            finally:
                await client.close()

    finally:
        await browser_manager.close()

    logger.success("Parser completed!")
