from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from uuid import UUID
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    ReportListResponse, Report, ReportContentResponse, 
    ReportUpdateRequest, Facets
)
from app.services import ReportService
from app.db.connection import get_db
from app.core import get_current_user

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

@router.get("/", response_model=ReportListResponse)
async def list_reports(
    genre: Optional[List[str]] = Query(None, alias="genre"),
    developer: Optional[List[str]] = Query(None, alias="developer"),
    platform: Optional[List[str]] = Query(None, alias="platform"),
    status: Optional[List[str]] = Query(None, alias="status"),
    year_from: Optional[int] = Query(None, ge=1980, le=2030, alias="year_from"),
    year_to: Optional[int] = Query(None, ge=1980, le=2030, alias="year_to"),
    search: Optional[str] = Query(None, max_length=100, alias="search"),
sort_by: Optional[str] = Query("created_at", pattern=r"^(created_at|game\.name|game\.release_year|updated_at|progress_percent)$", alias="sort_by"),
sort_dir: Optional[str] = Query("desc", pattern=r"^(asc|desc)$", alias="sort_dir"),
    page: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(12, ge=1, le=50, alias="page_size"),
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    List game analysis reports with filtering and pagination
    GET /api/v1/reports
    """
    service = ReportService(db, current_user)
    return await service.list_reports(
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
        page_size=page_size
    )

@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Get a single report by ID
    GET /api/v1/reports/{report_id}
    """
    service = ReportService(db, current_user)
    report = await service.get_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report

@router.get("/{report_id}/content", response_model=ReportContentResponse)
async def get_report_content(
    report_id: UUID,
format: str = Query(..., pattern=r"^(markdown|json|json_rag)$"),
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Get report content in specified format
    GET /api/v1/reports/{report_id}/content
    """
    service = ReportService(db, current_user)
    content_data = await service.get_report_content(report_id, format)
    
    if not content_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report or format not found"
        )
    
    return ReportContentResponse(
        format=format,
        content=content_data.get("content_url", ""),
        download_url=content_data.get("download_url")
    )

@router.get("/{report_id}/download")
async def download_report_pdf(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Download report as PDF
    GET /api/v1/reports/{report_id}/download
    """
    service = ReportService(db, current_user)
    pdf_url = await service.get_report_pdf_url(report_id)
    
    if not pdf_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or PDF not generated"
        )
    
    # Stream PDF from storage
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            
            return StreamingResponse(
                response.iter_bytes(),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download PDF"
        )

@router.patch("/{report_id}", response_model=Report)
async def update_report(
    report_id: UUID,
    update_data: ReportUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Update report metadata (tags, notes) - RESTRICTED by YAML
    PATCH /api/v1/reports/{report_id}
    """
    service = ReportService(db, current_user)
    
    # Verify ownership (RLS also enforces this)
    existing_report = await service.get_report(report_id)
    if not existing_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Update only allowed fields (tags, notes)
    updated_report = await service.update_report(
        report_id,
        tags=update_data.tags,
        notes=update_data.notes
    )
    
    if not updated_report:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify report not owned by user"
        )
    
    return updated_report

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Delete a report and all associated files
    DELETE /api/v1/reports/{report_id}
    """
    service = ReportService(db, current_user)
    
    # Verify ownership
    existing_report = await service.get_report(report_id)
    if not existing_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    deleted = await service.delete_report(report_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete report not owned by user"
        )

@router.get("/facets", response_model=Facets)
async def get_filter_facets(
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Get available filter options with counts
    GET /api/v1/reports/facets
    """
    service = ReportService(db, current_user)
    return await service.get_facets()

# Health check (keep existing)
@router.get("/health")
async def health():
    return {'status': 'ok'}