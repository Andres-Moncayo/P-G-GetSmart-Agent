"""
GET  /api/v1/reports          — list reports (filters, pagination, facets)
GET  /api/v1/reports/{id}     — report detail (scalars + JSONB sections)
PATCH /api/v1/reports/{id}    — update tags / notes
DELETE /api/v1/reports/{id}   — delete report
GET  /api/v1/reports/{id}/content  — download format content
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.connection import get_db
from ..services import ReportService
from ..models import Report, ReportListResponse

reports_router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


def _get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    # Instantiate without a user_id filter for now (demo mode shows all reports)
    return ReportService(db=db, user_id=None)


@reports_router.get("", response_model=ReportListResponse)
async def list_reports(
    genre: Optional[List[str]] = Query(None),
    developer: Optional[List[str]] = Query(None),
    platform: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    sort_by: str = Query("created_at", pattern="^(created_at|game\\.name|game\\.release_year|updated_at|progress_percent)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=200),
    svc: ReportService = Depends(_get_report_service),
) -> ReportListResponse:
    """List reports for the dashboard with filters, sort, and pagination."""
    return await svc.list_reports(
        genre=genre,
        developer=developer,
        platform=platform,
        status=status,
        year_from=year_from,
        year_to=year_to,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@reports_router.get("/facets")
async def get_facets(svc: ReportService = Depends(_get_report_service)):
    """Return all facet counts for dashboard filter UI."""
    return await svc.get_facets()


@reports_router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: UUID,
    svc: ReportService = Depends(_get_report_service),
) -> Report:
    """Return a single report (scalars + JSONB sections) for the preview/detail modal."""
    report = await svc.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail={"error_code": "REPORT_001", "message": "Report not found"})
    return report


@reports_router.get("/{report_id}/content")
async def get_report_content(
    report_id: UUID,
    format: str = Query("markdown", pattern="^(markdown|json|json_rag|pdf)$"),
    svc: ReportService = Depends(_get_report_service),
):
    """Return content/download URL for a specific report format."""
    content = await svc.get_report_content(report_id, format)
    if not content:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "REPORT_002", "message": f"Format '{format}' not available for this report"},
        )
    return content


@reports_router.patch("/{report_id}", response_model=Report)
async def update_report(
    report_id: UUID,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    svc: ReportService = Depends(_get_report_service),
) -> Report:
    """Update user-editable fields (tags, notes)."""
    report = await svc.update_report(report_id, tags=tags, notes=notes)
    if not report:
        raise HTTPException(status_code=404, detail={"error_code": "REPORT_001", "message": "Report not found"})
    return report


@reports_router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: UUID,
    svc: ReportService = Depends(_get_report_service),
):
    """Permanently delete a report."""
    deleted = await svc.delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"error_code": "REPORT_001", "message": "Report not found"})
