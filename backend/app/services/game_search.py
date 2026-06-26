"""
Phase 0 game search service.
Queries IGDB + RAWG in parallel, merges results, and returns GameCandidate dicts.
Falls back to an empty list per-source on timeout or auth failure — never raises.
"""

import time
import asyncio
import logging
from typing import Any
from datetime import datetime, timezone

import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)

# ── IGDB token cache (Twitch tokens last ~60 days, refresh on expiry) ─────────
_igdb_token: str | None = None
_igdb_token_expires_at: float = 0.0

IGDB_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_GAMES_URL = "https://api.igdb.com/v4/games"
RAWG_GAMES_URL = "https://api.rawg.io/api/games"


async def _get_igdb_token() -> str | None:
    """Return a valid IGDB bearer token, refreshing if expired."""
    global _igdb_token, _igdb_token_expires_at

    if not settings.igdb_client_id or not settings.igdb_client_secret:
        return None

    if _igdb_token and time.monotonic() < _igdb_token_expires_at:
        return _igdb_token

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                IGDB_TOKEN_URL,
                params={
                    "client_id": settings.igdb_client_id,
                    "client_secret": settings.igdb_client_secret,
                    "grant_type": "client_credentials",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            _igdb_token = data["access_token"]
            # Refresh 5 minutes before actual expiry
            _igdb_token_expires_at = time.monotonic() + data["expires_in"] - 300
            return _igdb_token
    except Exception as exc:
        logger.warning("IGDB token fetch failed: %s", exc)
        return None


def _igdb_cover_url(cover: dict | None) -> str | None:
    if not cover:
        return None
    url = cover.get("url", "")
    if url.startswith("//"):
        url = "https:" + url
    return url.replace("/t_thumb/", "/t_cover_big/")


def _igdb_release_year(timestamp: int | None) -> int | None:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).year
    except Exception:
        return None


def _igdb_release_date(timestamp: int | None) -> str | None:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return None


def _igdb_extract_developer(companies: list[dict]) -> str | None:
    for c in companies:
        if c.get("developer"):
            return c.get("company", {}).get("name")
    if companies:
        return companies[0].get("company", {}).get("name")
    return None


async def _search_igdb(query: str, limit: int) -> list[dict]:
    token = await _get_igdb_token()
    if not token:
        return []

    body = (
        f'fields id, name, slug, first_release_date, platforms.name, '
        f'involved_companies.company.name, involved_companies.developer, '
        f'genres.name, cover.url, summary; '
        f'search "{query}"; limit {limit};'
    )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                IGDB_GAMES_URL,
                content=body,
                headers={
                    "Client-ID": settings.igdb_client_id,
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "text/plain",
                },
            )
            resp.raise_for_status()
            games = resp.json()
    except Exception as exc:
        logger.warning("IGDB search failed: %s", exc)
        return []

    candidates = []
    for g in games:
        igdb_id = str(g.get("id", ""))
        companies = g.get("involved_companies") or []
        candidates.append({
            "id": igdb_id,
            "name": g.get("name", ""),
            "slug": g.get("slug"),
            "release_year": _igdb_release_year(g.get("first_release_date")),
            "release_date": _igdb_release_date(g.get("first_release_date")),
            "developer": _igdb_extract_developer(companies),
            "publisher": None,
            "platforms": [p["name"] for p in (g.get("platforms") or [])],
            "genres": [gn["name"] for gn in (g.get("genres") or [])],
            "cover_url": _igdb_cover_url(g.get("cover")),
            "summary": (g.get("summary") or "")[:500] or None,
            "igdb_id": igdb_id,
            "rawg_id": None,
            "steam_app_id": None,
            "sources": [{"provider": "igdb", "external_id": igdb_id, "confidence": 0.95}],
        })
    return candidates


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
            "igdb_id": None,
            "rawg_id": rawg_id,
            "steam_app_id": None,
            "sources": [{"provider": "rawg", "external_id": rawg_id, "confidence": 0.90}],
        })
    return candidates


def _normalize_name(name: str) -> str:
    return name.lower().strip()


def _merge_candidates(igdb: list[dict], rawg: list[dict]) -> list[dict]:
    """
    Merge IGDB and RAWG results. When the same title appears in both,
    keep the IGDB entry as canonical and attach the RAWG source + ids.
    IGDB entries that don't match anything in RAWG are kept as-is.
    RAWG-only entries are appended at the end.
    """
    merged: list[dict] = []
    rawg_by_name: dict[str, dict] = {_normalize_name(r["name"]): r for r in rawg}
    matched_rawg_keys: set[str] = set()

    for igdb_game in igdb:
        key = _normalize_name(igdb_game["name"])
        rawg_match = rawg_by_name.get(key)
        if rawg_match:
            matched_rawg_keys.add(key)
            igdb_game = {**igdb_game}
            igdb_game["rawg_id"] = rawg_match["rawg_id"]
            if not igdb_game["publisher"] and rawg_match["publisher"]:
                igdb_game["publisher"] = rawg_match["publisher"]
            if not igdb_game["developer"] and rawg_match["developer"]:
                igdb_game["developer"] = rawg_match["developer"]
            if not igdb_game["cover_url"] and rawg_match["cover_url"]:
                igdb_game["cover_url"] = rawg_match["cover_url"]
            igdb_game["sources"] = igdb_game["sources"] + [
                {"provider": "rawg", "external_id": rawg_match["rawg_id"], "confidence": 0.90}
            ]
        merged.append(igdb_game)

    for key, rawg_game in rawg_by_name.items():
        if key not in matched_rawg_keys:
            merged.append(rawg_game)

    return merged


def _sources_queried(igdb: list[dict], rawg: list[dict]) -> list[str]:
    sources = []
    if igdb:
        sources.append("igdb")
    if rawg:
        sources.append("rawg")
    if not sources:
        sources.append("none")
    return sources


async def search_games(query: str, limit: int) -> tuple[list[dict], list[str]]:
    """
    Search IGDB and RAWG in parallel.
    Returns (candidates, sources_queried).
    Never raises — each source degrades to [] on failure.
    """
    igdb_results: Any
    rawg_results: Any
    igdb_results, rawg_results = await asyncio.gather(
        _search_igdb(query, limit),
        _search_rawg(query, limit),
        return_exceptions=True,
    )

    igdb_list: list[dict] = igdb_results if isinstance(igdb_results, list) else []
    rawg_list: list[dict] = rawg_results if isinstance(rawg_results, list) else []

    candidates = _merge_candidates(igdb_list, rawg_list)
    sources = _sources_queried(igdb_list, rawg_list)

    return candidates[:limit], sources
