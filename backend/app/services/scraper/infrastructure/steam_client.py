from __future__ import annotations

import logging
from typing import Any

import httpx

from ....core.config import settings

logger = logging.getLogger(__name__)


class SteamClient:
    """Async client for Steam APIs used by scraper contracts with graceful fallback."""

    STOREFRONT_URL = "https://store.steampowered.com/api/appdetails"
    WEB_API_PLAYERS_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    WEB_API_SCHEMA_URL = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 30.0) -> None:
        self.api_key = api_key or settings.steam_api_key
        self.timeout_seconds = timeout_seconds
        
        # Flag to check if API key is available
        self.has_api_key = bool(self.api_key)

    async def get_storefront_details(self, steam_app_id: int) -> dict[str, Any]:
        """Fetches public Steam storefront details (no API key required)."""
        try:
            params = {"appids": steam_app_id}
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(self.STOREFRONT_URL, params=params)
                response.raise_for_status()
                payload = response.json()

            app_payload = payload.get(str(steam_app_id), {})
            if not app_payload.get("success"):
                return {}

            return app_payload.get("data", {})
        except Exception as e:
            logger.warning("Steam storefront API call failed: %s", e)
            return {}

    async def get_current_player_count(self, steam_app_id: int) -> dict[str, Any]:
        """Fetches current player count (API key required).
        
        Returns empty dict if Steam API key is not configured.
        """
        if not self.has_api_key:
            logger.warning("Steam API key not configured, skipping player count API call")
            return {}

        try:
            params = {"appid": steam_app_id, "key": self.api_key}
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(self.WEB_API_PLAYERS_URL, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("Steam player count API call failed: %s", e)
            return {}

    async def get_achievements_schema(self, steam_app_id: int) -> dict[str, Any]:
        """Fetches achievements schema (API key required).
        
        Returns empty dict if Steam API key is not configured.
        """
        if not self.has_api_key:
            logger.warning("Steam API key not configured, skipping achievements API call")
            return {}

        try:
            params = {"appid": steam_app_id, "key": self.api_key}
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(self.WEB_API_SCHEMA_URL, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("Steam achievements API call failed: %s", e)
            return {}

    async def get_reviews(self, steam_app_id: int, num_per_page: int = 20) -> dict[str, Any]:
        """Fetches Steam reviews (public, no API key required)."""
        try:
            reviews_url = f"https://store.steampowered.com/appreviews/{steam_app_id}"
            params = {
                "json": 1,
                "num_per_page": num_per_page,
                "language": "all",
                "filter": "recent",
            }
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(reviews_url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("Steam reviews API call failed: %s", e)
            return {}

    # Additional convenience methods used by scrapers
    async def get_app_details(self, steam_app_id: int) -> dict[str, Any]:
        """Alias for get_storefront_details for consistency."""
        return await self.get_storefront_details(steam_app_id)

    async def get_game_reviews(self, steam_app_id: int, limit: int = 20) -> list[dict[str, Any]]:
        """Get game reviews as a list, simplified format."""
        try:
            data = await self.get_reviews(steam_app_id, num_per_page=limit)
            return data.get("reviews", [])
        except Exception:
            return []