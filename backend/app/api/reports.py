"""
Reports API endpoints for Phase 4 database integration.

Provides endpoints for retrieving and managing analysis reports stored in the database.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from ..services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportResponse(BaseModel):
    """Response model for full report data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    game_id: str
    game_title: str
    platform: str
    title: str
    status: str
    markdown_content: str
    json_content: dict
    summary: str
    confidence_score: float
    quality_rating: str
    word_count: int
    data_completeness: float
    created_at: str
    updated_at: str
    phases_completed: List[str]


class ReportSummaryResponse(BaseModel):
    """Response model for report summary/list views."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    game_id: str
    game_title: str
    platform: str
    title: str
    status: str
    confidence_score: float
    quality_rating: str
    word_count: int
    created_at: str
    summary: Optional[str] = None


def _summarize_report(report: object) -> ReportSummaryResponse:
    return ReportSummaryResponse(
        id=report.id,
        game_id=report.game_id,
        game_title=report.game_title,
        platform=report.platform,
        title=report.title,
        status=report.status,
        confidence_score=report.confidence_score,
        quality_rating=report.quality_rating,
        word_count=report.word_count,
        created_at=report.created_at.isoformat(),
        summary=report.summary[:200] + "..." if report.summary and len(report.summary) > 200 else report.summary
    )


@router.get("/", response_model=List[ReportSummaryResponse])
async def search_reports(
    q: str = Query(..., description="Search query for game titles or game IDs"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
) -> List[ReportSummaryResponse]:
    """
    Search reports by game title or game ID.

    Returns paginated results matching the search query.
    """
    async with ReportService() as report_service:
        reports = await report_service.search_reports(q, limit, offset)

    return [_summarize_report(report) for report in reports]


@router.get("/recent", response_model=List[ReportSummaryResponse])
async def get_recent_reports(
    limit: int = Query(default=50, le=100),
    days: int = Query(default=30, le=365, description="Number of days to look back")
) -> List[ReportSummaryResponse]:
    """
    Get recent reports from the last N days.

    Returns the most recently created reports.
    """
    async with ReportService() as report_service:
        reports = await report_service.get_recent_reports(limit, days)

    return [_summarize_report(report) for report in reports]


@router.get("/game/{game_id}", response_model=List[ReportSummaryResponse])
async def get_reports_by_game(
    game_id: str,
    limit: int = Query(default=10, le=50)
) -> List[ReportSummaryResponse]:
    """
    Get all reports for a specific game.

    Returns a list of report summaries for the given game ID.
    """
    async with ReportService() as report_service:
        reports = await report_service.get_all_reports_for_game(game_id, limit)

    return [_summarize_report(report) for report in reports]


@router.get("/game/{game_id}/latest", response_model=ReportResponse)
async def get_latest_report_by_game(game_id: str) -> ReportResponse:
    """
    Get the most recent report for a specific game.

    Returns the full content of the latest report for the given game ID.
    """
    async with ReportService() as report_service:
        report = await report_service.get_latest_report_for_game(game_id)

    if not report:
        raise HTTPException(status_code=404, detail="No reports found for this game")

    return ReportResponse(
        id=report.id,
        game_id=report.game_id,
        game_title=report.game_title,
        platform=report.platform,
        title=report.title,
        status=report.status,
        markdown_content=report.markdown_content,
        json_content=report.json_content,
        summary=report.summary,
        confidence_score=report.confidence_score,
        quality_rating=report.quality_rating,
        word_count=report.word_count,
        data_completeness=report.data_completeness,
        created_at=report.created_at.isoformat(),
        updated_at=report.updated_at.isoformat(),
        phases_completed=report.phases_completed or []
    )


@router.get("/game/{game_id}/history", response_model=List[ReportSummaryResponse])
async def get_game_analysis_history(game_id: str, limit: int = Query(default=20, le=50)) -> List[ReportSummaryResponse]:
    """
    Get analysis history for a specific game.

    Returns chronological list of all reports for the game with summaries.
    """
    async with ReportService() as report_service:
        history = await report_service.get_game_analysis_history(game_id)

    return [ReportSummaryResponse(**summary) for summary in history[:limit]]


@router.get("/{report_id}/status")
async def get_report_pipeline_status(report_id: str) -> dict:
    """
    Get detailed pipeline execution status for a report.

    Returns status information for each phase of the pipeline.
    """
    async with ReportService() as report_service:
        status_updates = await report_service.get_pipeline_status(report_id)

    if not status_updates:
        raise HTTPException(status_code=404, detail="Report or status not found")

    return {
        "report_id": report_id,
        "pipeline_status": [
            {
                "phase": status.phase_name,
                "status": status.status,
                "progress_percentage": status.progress_percentage,
                "started_at": status.started_at.isoformat() if status.started_at else None,
                "completed_at": status.completed_at.isoformat() if status.completed_at else None,
                "error_message": status.error_message,
                "retry_count": status.retry_count,
                "phase_data": status.phase_data
            }
            for status in status_updates
        ]
    }


@router.get("/{report_id}/summary", response_model=ReportSummaryResponse)
async def get_report_summary(report_id: str) -> ReportSummaryResponse:
    """
    Get a lightweight summary of a report.

    Returns summary metadata without full content for faster loading.
    """
    async with ReportService() as report_service:
        summary = await report_service.get_report_summary(report_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportSummaryResponse(**summary)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str) -> ReportResponse:
    """
    Get a complete analysis report by ID.

    Returns the full report content including markdown and JSON data.
    """
    async with ReportService() as report_service:
        report = await report_service.get_report_by_id(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse(
        id=report.id,
        game_id=report.game_id,
        game_title=report.game_title,
        platform=report.platform,
        title=report.title,
        status=report.status,
        markdown_content=report.markdown_content,
        json_content=report.json_content,
        summary=report.summary,
        confidence_score=report.confidence_score,
        quality_rating=report.quality_rating,
        word_count=report.word_count,
        data_completeness=report.data_completeness,
        created_at=report.created_at.isoformat(),
        updated_at=report.updated_at.isoformat(),
        phases_completed=report.phases_completed or []
    )
