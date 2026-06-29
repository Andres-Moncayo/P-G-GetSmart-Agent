"""
GET  /api/v1/games/search  — search candidates via RAWG
POST /api/v1/games/confirm — confirm selection and issue pipeline token
POST /api/v1/games/pipeline/start — start analysis pipeline for confirmed game
"""
import asyncio
import re
import time
import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional

from ..services.game_search import search_games as _search_games
from ..services.scraper.application.orchestrator import run_scrape_task
from ..services.pipeline_tracker import pipeline_tracker
from ..models.pipelines import DetailedPipelineResponse, Phase
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
    source: str = "rawg"


class PipelineStartRequest(BaseModel):
    game_id: str
    source: str = "rawg"
    pipeline_token: Optional[str] = None


class PipelineResponse(BaseModel):
    report_id: str
    phase: str
    status: str
    is_complete: bool = False
    message: str
    result: Optional[Dict[Any, Any]] = None
    seconds_elapsed: Optional[float] = None
    seconds_remaining: Optional[float] = None
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    tasks_total: int = 0


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

    if not settings.rawg_api_key and not (settings.igdb_client_id and settings.igdb_client_secret):
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "SEARCH_002",
                "message": "No game data API keys configured. Set RAWG_API_KEY or IGDB_CLIENT_ID + IGDB_CLIENT_SECRET in .env",
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


class ScrapeNowRequest(BaseModel):
    game_id: str


@games_router.post("/scrape")
async def scrape_game_now(body: ScrapeNowRequest):
    """Run Phase 1 scraper logic immediately for a selected candidate."""
    game = _candidate_cache.get(body.game_id)
    if not game:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "GAME_001", "message": "Game not found. Run a search first or the session may have expired."},
        )

    payload = {
        "game_id": game.get("id"),
        "name": game.get("name"),
        "release_year": int(game.get("release_year", 0) or 0),
        "rawg_id": int(game.get("rawg_id")) if game.get("rawg_id") and str(game.get("rawg_id")).isdigit() else None,
        "steam_app_id": int(game.get("steam_app_id")) if game.get("steam_app_id") and str(game.get("steam_app_id")).isdigit() else None,
        "aliases": game.get("aliases", []),
    }

    result = await run_scrape_task(payload)
    return {
        "status": "completed",
        "message": "Phase 1 scraper executed using actual scraper services.",
        "result": result,
    }


# Temporary endpoint for frontend format
@games_router.post("/scraper/analyze")
async def analyze_game_scraper(body: dict):
    """Temp endpoint for frontend scraper compatibility using Phase 1 real scraping."""
    try:
        # Convert frontend payload to the scraper task format
        scraper_request = {
            "game_id": body.get("game_id") or str(uuid.uuid4()),
            "name": body.get("name") or body.get("steam_name"),
            "release_year": int(body.get("release_year", 0) or 0),
            "rawg_id": int(body.get("rawg_id", 0)) if body.get("rawg_id") else None,
            "steam_app_id": int(body.get("steam_app_id", 0)) if body.get("steam_app_id") else None,
            "aliases": body.get("aliases", []),
        }

        result = await run_scrape_task(scraper_request)

        return {
            "report_id": str(scraper_request["game_id"]),
            "phase": "scraping",
            "status": "completed" if not result.get("workers_failed") else "partial",
            "is_complete": True,
            "message": "Phase 1 scraping completed with real API calls",
            "result": result,
            "seconds_elapsed": result.get("metadata", {}).get("run_duration_seconds"),
            "seconds_remaining": None,
            "tasks_succeeded": len(result.get("workers_completed", [])),
            "tasks_failed": len(result.get("workers_failed", [])),
            "tasks_total": len(result.get("workers_total", [])),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "PIPELINE_001", "message": f"Failed to execute Phase 1 scraping: {str(e)}"}
        )


@games_router.post("/pipeline/start", response_model=PipelineResponse)
async def start_pipeline(body: PipelineStartRequest):
    """Start the analysis pipeline for a confirmed game."""
    # Get the game from cache (could also validate pipeline_token if desired)
    game = _candidate_cache.get(body.game_id)
    if not game:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "GAME_001", "message": "Game not found. Run a search first or the session may have expired."},
        )
    
    try:
        # Import here to avoid circular imports
        from ..services.pipeline_tracker_enabled import run_pipeline_with_tracking
        
        # Start the pipeline in background
        report_id = str(uuid.uuid4())
        
        # Convert cached candidate into the backend scraper payload expected by the real orchestrator
        genres = game.get("genres") or []
        platforms = game.get("platforms") or []
        scraper_request = {
            "game_id": game.get("id"),
            "name": game.get("name"),
            "release_year": int(game.get("release_year", 0) or 0),
            "platform": game.get("platform", "unknown") or "unknown",
            "rawg_id": int(game.get("rawg_id")) if game.get("rawg_id") and str(game.get("rawg_id")).isdigit() else None,
            "steam_app_id": int(game.get("steam_app_id")) if game.get("steam_app_id") and str(game.get("steam_app_id")).isdigit() else None,
            "aliases": game.get("aliases", []),
            # Extra metadata forwarded to Phase 4 DB row
            "developer_name": game.get("developer"),
            "primary_genre": genres[0] if genres else None,
            "primary_platform": platforms[0] if platforms else None,
            "all_genres": genres,
            "all_platforms": platforms,
            "cover_url": game.get("cover_url") or game.get("background_image"),
        }
        
        # Create pipeline tracker entry immediately so status/logs are available right away
        pipeline_tracker.create_pipeline(report_id, game.get("name") or "Unknown Game")
        
        # Schedule the pipeline task in the running uvicorn event loop
        asyncio.create_task(run_pipeline_with_tracking(scraper_request, report_id))
        await asyncio.sleep(0)

        return PipelineResponse(
            report_id=report_id,
            phase="scraping",
            status="started",
            is_complete=False,
            message="Analysis pipeline started successfully",
            result=None,
            seconds_elapsed=0.0,
            seconds_remaining=None,
            tasks_succeeded=0,
            tasks_failed=0,
            tasks_total=4  # scraping, analysis, synthesis, storage
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "PIPELINE_001", "message": f"Failed to start pipeline: {str(e)}"}
        )


@games_router.get("/pipeline/{report_id}/status", response_model=DetailedPipelineResponse)
async def get_pipeline_status_detailed(report_id: str):
    """Get detailed pipeline status with API call tracking and progress information."""
    try:
        # Import tracker
        from ..services.pipeline_tracker import pipeline_tracker
        
        # Get detailed status
        status = pipeline_tracker.get_pipeline_status(report_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "PIPELINE_002", "message": "Pipeline not found or has been archived"}
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "PIPELINE_003", "message": f"Failed to get pipeline status: {str(e)}"}
        )


# Temporary endpoint for frontend compatibility
@games_router.get("/scraper/api/v1/reports/{report_id}/status")
async def get_report_status_scraper(report_id: str):
    """Temp get status using frontend path."""
    try:
        from ..services.pipeline_tracker import pipeline_tracker
        
        # Get detailed status
        status = pipeline_tracker.get_pipeline_status(report_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "PIPELINE_002", "message": "Pipeline not found or has been archived"}
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "PIPELINE_003", "message": f"Failed to get pipeline status: {str(e)}"}
        )


@games_router.post("/pipeline/{report_id}/reset")
async def reset_pipeline(report_id: str):
    """Reset a stuck pipeline."""
    try:
        from ..services.pipeline_tracker import pipeline_tracker
        
        # Archive the stuck pipeline
        pipeline_tracker.archive_pipeline(report_id)
        
        # Create a new pipeline entry
        new_report_id = str(uuid.uuid4())
        
        return {
            "message": "Pipeline reset successfully",
            "old_report_id": report_id,
            "new_report_id": new_report_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "PIPELINE_004", "message": f"Failed to reset pipeline: {str(e)}"}
        )


@games_router.get("/pipeline/{report_id}/logs")
async def get_pipeline_logs(report_id: str, level: Optional[str] = None):
    """Get pipeline execution logs."""
    try:
        from ..services.pipeline_tracker import pipeline_tracker
        
        logs = pipeline_tracker.get_pipeline_logs(report_id, level)
        
        if not logs and report_id not in pipeline_tracker.active_pipelines:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "PIPELINE_002", "message": "Pipeline not found or has been archived"}
            )
        
        return {
            "report_id": report_id,
            "logs": logs,
            "total_logs": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "PIPELINE_003", "message": f"Failed to get pipeline logs: {str(e)}"}
        )