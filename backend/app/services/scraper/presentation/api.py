from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from ..application.orchestrator import run_scrape_task
from ..application.pipeline_status import pipeline_status_store

router = APIRouter(tags=["scraper"])


class ScrapeRequest(BaseModel):
    """Input payload aligned with scraper_contract.yaml -> input.fields."""

    model_config = ConfigDict(extra="forbid")

    game_id: UUID
    name: str = Field(min_length=1)
    release_year: int
    rawg_id: int
    steam_app_id: int | None = None
    aliases: list[str] = Field(default_factory=list)


async def _run_complete_pipeline_background_task(payload: dict[str, Any]) -> None:
    """Run Phase 1 + Phase 2 + Phase 3 + Phase 4 complete pipeline (Scraping + AI Analysis + Synthesis + DB Storage)."""
    from ..application.orchestrator import run_complete_pipeline_with_db
    
    report_id = str(payload["game_id"])
    game_name = payload.get("name", "Unknown")
    
    try:
        # Run complete pipeline (Phase 1 + 2 + 3 + 4)
        pipeline_status_store.set_status(
            report_id=report_id,
            status="processing",
            message="Starting complete pipeline with DB storage (Scraping + AI Analysis + Synthesis + Database)",
        )

        pipeline_result = await run_complete_pipeline_with_db(payload)
        
        # Extract key metrics
        status = pipeline_result.get("status", "failed")
        synthesis_performed = pipeline_result.get("metadata", {}).get("synthesis_performed", False)
        final_report = pipeline_result.get("final_report")
        word_count = pipeline_result.get("metadata", {}).get("word_count", 0)
        
        # Determine appropriate status message
        if status == "complete_success":
            if synthesis_performed:
                message = f"Complete pipeline successful for {game_name} - Final report ready ({word_count} words)"
            else:
                message = f"Pipeline analysis completed for {game_name} - Ready for manual synthesis"
        elif status == "partial_success":
            if synthesis_performed:
                message = f"Pipeline completed with issues for {game_name} - Partial report available ({word_count} words)"
            else:
                message = f"Pipeline analysis partially completed for {game_name} - Limited data available"
        else:
            message = f"Pipeline failed for {game_name}"
        
        # Update final status
        pipeline_status_store.set_status(
            report_id=report_id,
            status="completed" if status in ["complete_success", "partial_success"] else "failed",
            message=message,
            details=pipeline_result,
        )
        
    except Exception as exception:
        pipeline_status_store.set_status(
            report_id=report_id,
            status="failed",
            message=f"Pipeline failed for {game_name}: {str(exception)}",
            details={
                "error": str(exception),
                "game_name": game_name,
                "failed_phase": "pipeline_execution",
            },
        )


async def _run_scrape_background_task(payload: dict[str, Any]) -> None:
    """Legacy Phase 1 only scraper task - kept for backwards compatibility."""
    report_id = str(payload["game_id"])
    try:
        pipeline_status_store.set_status(
            report_id=report_id,
            status="processing",
            message="Phase 1: Scraping in progress (legacy mode)",
        )

        result = await run_scrape_task(payload)
        has_failures = len(result.get("workers_failed", [])) > 0

        pipeline_status_store.set_status(
            report_id=report_id,
            status="failed" if has_failures else "completed",
            message="Phase 1 scraping finished" if not has_failures else "Scraping finished with failures",
            details=result,
        )
    except Exception as exception:
        pipeline_status_store.set_status(
            report_id=report_id,
            status="failed",
            message="Legacy scraper pipeline error",
            details={"error": str(exception)},
        )


def _run_complete_pipeline_background_task_sync(payload: dict[str, Any]) -> None:
    """Sync adapter required by BackgroundTasks to execute async workflow."""
    asyncio.run(_run_complete_pipeline_background_task(payload))


def _run_synthesis_only_background_task_sync(payload: dict[str, Any]) -> None:
    """Sync adapter for synthesis-only tasks."""
    asyncio.run(_run_synthesis_only_background_task(payload))


def _run_scrape_background_task_sync(payload: dict[str, Any]) -> None:
    """Sync adapter required by BackgroundTasks to execute async workflow."""
    asyncio.run(_run_scrape_background_task(payload))


@router.post("/scrape")
async def scrape_game(request: ScrapeRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    """
    Legacy Phase 1 only endpoint - for backwards compatibility.
    
    Use /analyze for complete Phase 1 + 2 pipeline.
    """
    payload = request.model_dump(mode="json")
    report_id = str(request.game_id)

    pipeline_status_store.set_status(
        report_id=report_id,
        status="queued",
        message="Phase 1 scraping task queued (legacy mode)",
    )

    background_tasks.add_task(_run_scrape_background_task_sync, payload)

    return {
        "status": "queued",
        "report_id": report_id,
        "message": "Phase 1 scraping task started in background (legacy mode)",
        "note": "Use /analyze for direct Phase 1 scraping with immediate real scraper output",
    }


@router.post("/analyze")
async def analyze_game_complete(request: ScrapeRequest) -> dict[str, Any]:
    """
    Phase 1-only scraper endpoint for immediate real scraping results.

    This endpoint bypasses the full DB-backed pipeline and returns
    the actual Phase 1 scraper output directly.
    """
    payload = request.model_dump(mode="json")
    report_id = str(request.game_id)

    pipeline_status_store.set_status(
        report_id=report_id,
        status="processing",
        message="Phase 1 scraping in progress (immediate mode)",
    )

    result = await run_scrape_task(payload)
    has_failures = len(result.get("workers_failed", [])) > 0

    pipeline_status_store.set_status(
        report_id=report_id,
        status="failed" if has_failures else "completed",
        message="Phase 1 scraping finished" if not has_failures else "Scraping finished with failures",
        details=result,
    )

    return {
        "status": "completed" if not has_failures else "partial",
        "report_id": report_id,
        "message": "Phase 1 scraping finished",
        "result": result,
    }


@router.get("/api/v1/reports/{report_id}/status")
async def get_report_status(report_id: str) -> dict[str, Any]:
    status_record = pipeline_status_store.get_status(report_id)
    if status_record is None:
        raise HTTPException(status_code=404, detail="Report status not found")

    return status_record.to_dict()
