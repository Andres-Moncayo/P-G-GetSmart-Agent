"""
Phase 0 game search service.
Queries RAWG and returns GameCandidate dicts.
Falls back to an empty list on failure — never raises.
"""

import asyncio
import logging
from typing import Any

import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)

RAWG_GAMES_URL = "https://api.rawg.io/api/games"


def _rawg_release_year(released: str | None) -> int | None:
    if not released:
        return None
    try:
        return int(released[:4])
    except Exception:
        return None


async def _search_rawg(query: str, limit: int) -> list[dict]:
    if not settings.rawg_api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                RAWG_GAMES_URL,
                params={"search": query, "key": settings.rawg_api_key, "page_size": limit},
            )
            resp.raise_for_status()
            games = resp.json().get("results", [])
    except Exception as exc:
        logger.warning("RAWG search failed: %s", exc)
        return []

    candidates = []
    for g in games:
        rawg_id = str(g.get("id", ""))
        platforms = [
            p["platform"]["name"]
            for p in (g.get("platforms") or [])
            if p.get("platform")
        ]
        genres = [gn["name"] for gn in (g.get("genres") or [])]
        released = g.get("released")
        year = _rawg_release_year(released)
        cover = g.get("background_image")

        developers = g.get("developers") or []
        developer = developers[0]["name"] if developers else None
        publishers = g.get("publishers") or []
        publisher = publishers[0]["name"] if publishers else None

        candidates.append({
            "id": f"rawg-{rawg_id}",
            "name": g.get("name", ""),
            "slug": g.get("slug"),
            "release_year": year,
            "release_date": released,
            "developer": developer,
            "publisher": publisher,
            "platforms": platforms,
            "genres": genres,
            "cover_url": cover,
            "summary": None,
            "rawg_id": rawg_id,
            "steam_app_id": None,
            "sources": [{"provider": "rawg", "external_id": rawg_id, "confidence": 0.90}],
        })
    return candidates


def _sources_queried(rawg: list[dict]) -> list[str]:
    sources = []
    if rawg:
        sources.append("rawg")
    if not sources:
        sources.append("none")
    return sources

    candidates = []
    for g in games:
        rawg_id = str(g.get("id", ""))
        platforms = [
            p["platform"]["name"]
            for p in (g.get("platforms") or [])
            if p.get("platform")
        ]
        genres = [gn["name"] for gn in (g.get("genres") or [])]
        released = g.get("released")
        year = int(released[:4]) if released and len(released) >= 4 else None
        cover = g.get("background_image")

        developers = g.get("developers") or []
        developer = developers[0]["name"] if developers else None
        publishers = g.get("publishers") or []
        publisher = publishers[0]["name"] if publishers else None

        candidates.append({
            "id": f"rawg-{rawg_id}",
            "name": g.get("name", ""),
            "slug": g.get("slug"),
            "release_year": year,
            "release_date": released,
            "developer": developer,
            "publisher": publisher,
            "platforms": platforms,
            "genres": genres,
            "cover_url": cover,
            "summary": None,
            "rawg_id": rawg_id,
            "steam_app_id": None,
            "sources": [{"provider": "rawg", "external_id": rawg_id, "confidence": 0.90}],
        })
    return candidates


def _sources_queried(rawg: list[dict]) -> list[str]:
    sources = []
    if rawg:
        sources.append("rawg")
    if not sources:
        sources.append("none")
    return sources


async def search_games(query: str, limit: int) -> tuple[list[dict], list[str]]:
    """
    Search RAWG.
    Returns (candidates, sources_queried).
    Never raises — the source degrades to [] on failure.
    """
    rawg_results: Any = await _search_rawg(query, limit)
    rawg_list: list[dict] = rawg_results if isinstance(rawg_results, list) else []
    sources = _sources_queried(rawg_list)
    return rawg_list[:limit], sources