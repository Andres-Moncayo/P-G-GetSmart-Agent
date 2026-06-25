"""
GET  /api/v1/games/search  — search candidates via IGDB + RAWG
POST /api/v1/games/confirm — confirm selection and issue pipeline token
"""

import re
import time
import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..services.game_search import search_games as _search_games
from ..core.config import settings

games_router = APIRouter(prefix="/api/v1/games", tags=["games"])

# Short-lived in-process cache: populated on each search, consumed on confirm.
# Keyed by game_id; holds the full GameCandidate dict so confirm never re-fetches.
# Good enough for the search → select → confirm flow (happens in seconds).
_candidate_cache: dict[str, dict] = {}

_QUERY_BLOCKLIST = re.compile(r"[<>{}\"]|script|javascript", re.IGNORECASE)


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ──────────────────────────────────────────────────────────────────────────────

class ConfirmRequest(BaseModel):
    game_id: str
    source: str = "igdb"


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@games_router.get("/search")
async def search_games(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(10, ge=1, le=20),
):
    if _QUERY_BLOCKLIST.search(q):
        raise HTTPException(
            status_code=400,
            detail={"error_code": "SEARCH_001", "message": "Invalid characters in query"},
        )

    if not settings.igdb_client_id and not settings.rawg_api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "SEARCH_002",
                "message": "No game data API keys configured. Set IGDB_CLIENT_ID + IGDB_CLIENT_SECRET or RAWG_API_KEY in .env",
            },
        )

    start = time.monotonic()
    candidates, sources_queried = await _search_games(q, limit)
    latency_ms = int((time.monotonic() - start) * 1000)

    # Populate confirm cache
    for c in candidates:
        _candidate_cache[c["id"]] = c

    return {
        "query": q,
        "total": len(candidates),
        "candidates": candidates,
        "sources_queried": sources_queried,
        "latency_ms": latency_ms,
    }


@games_router.post("/confirm")
async def confirm_game(body: ConfirmRequest):
    game = _candidate_cache.get(body.game_id)
    if not game:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "GAME_001", "message": "Game not found. Run a search first or the session may have expired."},
        )

    pipeline_token = str(uuid.uuid4())

    return {
        "confirmed_game": game,
        "can_run_pipeline": True,
        "pipeline_token": pipeline_token,
    }