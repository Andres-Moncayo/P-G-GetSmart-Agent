from __future__ import annotations

import logging
from typing import Any

import httpx

from ....core.config import settings

logger = logging.getLogger(__name__)


class RAWGClient:
    """Async client for RAWG API with graceful fallback when API key is missing."""

    BASE_URL = "https://api.rawg.io/api"

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 30.0) -> None:
        self.api_key = api_key or settings.rawg_api_key
        self.timeout_seconds = timeout_seconds
        
        # Flag to check if API key is available
        self.has_api_key = bool(self.api_key)

    async def get_game_by_id(self, rawg_id: int) -> dict[str, Any]:
        """Fetches game data by RAWG id.
        
        Returns empty dict if RAWG API key is not configured.
        """
        if not self.has_api_key:
            logger.warning("RAWG API key not configured, skipping RAWG API call")
            return {}

        try:
            url = f"{self.BASE_URL}/games/{rawg_id}"
            params = {"key": self.api_key}

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("RAWG API call failed: %s", e)
            return {}

    async def get_game_details(self, rawg_id: int) -> dict[str, Any]:
        """Alias for get_game_by_id for consistency with other clients."""
        return await self.get_game_by_id(rawg_id)
