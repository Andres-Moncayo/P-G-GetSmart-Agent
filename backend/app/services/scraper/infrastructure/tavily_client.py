from __future__ import annotations

import logging
from typing import Any

import httpx

from ....core.config import settings

logger = logging.getLogger(__name__)


class TavilyClient:
    """Async Tavily client with safe defaults for LLM context protection and graceful fallback."""

    SEARCH_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 30.0) -> None:
        self.api_key = api_key or settings.tavily_api_key
        self.timeout_seconds = timeout_seconds
        
        # Flag to check if API key is available
        self.has_api_key = bool(self.api_key)
        
        # Mock mode for development/testing when API key is missing
        self.mock_mode = not self.has_api_key

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_images: bool = False,
        include_answer: bool = False,
        include_raw_content: bool = False,
    ) -> dict[str, Any]:
        """
        Executes Tavily search.

        CRITICAL: include_raw_content is always forced to False to protect
        downstream LLM context size and reduce unnecessary payload.
        """
        if self.mock_mode:
            logger.warning("Tavily API key not configured, returning mock search results")
            return self._mock_response(query=query, max_results=max_results)

        if not self.api_key:
            logger.warning("Tavily API key not configured, skipping Tavily API call")
            return self._empty_response(query=query)

        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_images": include_images,
                "include_answer": include_answer,
                "include_raw_content": False,
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.SEARCH_URL, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("Tavily API call failed: %s", e)
            return self._empty_response(query=query)

    def _mock_response(self, query: str, max_results: int) -> dict[str, Any]:
        fake_results = []
        for index in range(max_results):
            fake_results.append(
                {
                    "title": f"Mock result {index + 1} for query",
                    "url": f"https://mock.local/result/{index + 1}",
                    "content": f"Mock content for '{query}'",
                    "score": 0.75,
                    "raw_content": None,
                }
            )

        return {
            "query": query,
            "answer": None,
            "images": [],
            "results": fake_results,
            "response_time": 0.01,
            "mocked": True,
            "include_raw_content": False,
        }

    def _empty_response(self, query: str) -> dict[str, Any]:
        """Return empty response when API is not available."""
        return {
            "query": query,
            "answer": None,
            "images": [],
            "results": [],
            "response_time": 0.01,
            "mocked": False,
            "include_raw_content": False,
            "error": "API key not configured or API call failed",
        }
