"""API client for AutoDealer parser."""

import httpx
from loguru import logger

from .config import (
    CURRENT_WORK_URL,
    SEARCH_API_URL,
    create_search_payload,
)
from .models import WorkDetail, WorkListItem


class APIClient:
    """HTTP client for AutoDealer API."""

    def __init__(self, cookies: dict, headers: dict):
        """Initialize API client.

        Args:
            cookies: Cookies dict from browser session
            headers: Headers dict from browser session
        """
        self.cookies = cookies
        self.headers = headers
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            # Add Content-Type for POST requests
            headers = {
                **self.headers,
                "Content-Type": "application/json",
                "Origin": "https://online.autodealer.ru",
            }
            self._client = httpx.AsyncClient(
                cookies=self.cookies,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_works_list(
        self, folder_id: int, filter_barcode: bool = True
    ) -> list[WorkListItem]:
        """Get list of all services/works for a specific folder.

        Args:
            folder_id: Folder ID to search in
            filter_barcode: If True, only return services with barcodes

        Returns:
            List of WorkListItem

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        client = await self._get_client()

        payload = create_search_payload(folder_id)

        response = await client.post(
            SEARCH_API_URL,
            json=payload,
        )

        logger.info(f"Search response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Search response text: {response.text}")

        response.raise_for_status()

        data = response.json()

        # API returns dict with entityList
        if isinstance(data, dict) and "entityList" in data:
            entity_list = data["entityList"]
            works = [WorkListItem.model_validate(item) for item in entity_list]
            # Filter out services without barcodes if requested
            if filter_barcode:
                return [w for w in works if w.barcodes]
            return works

        # Fallback: if it's a list
        if isinstance(data, list):
            works = [WorkListItem.model_validate(item) for item in data]
            if filter_barcode:
                return [w for w in works if w.barcodes]
            return works

        return []

    async def get_work_detail(self, work_id: int) -> WorkDetail:
        """Get detailed work information with items and works.

        Args:
            work_id: Work/service ID

        Returns:
            WorkDetail with formItems and works

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        client = await self._get_client()

        response = await client.get(
            CURRENT_WORK_URL.format(id=work_id),
            params={"forEdit": "true"},
        )

        response.raise_for_status()

        data = response.json()

        parsed = WorkDetail.model_validate(data)

        return parsed
