"""
Repository layer for database operations on reports.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from ..models.report import AnalysisReport, PipelineStatus, RawAnalysisData


class ReportRepository:
    """Async repository for AnalysisReport operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(self, report_data: Dict[str, Any]) -> AnalysisReport:
        """Create a new analysis report."""
        report = AnalysisReport(**report_data)
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report_by_id(self, report_id: str) -> Optional[AnalysisReport]:
        """Get a report by its UUID."""
        result = await self.db.execute(
            select(AnalysisReport)
            .where(
                and_(
                    AnalysisReport.id == report_id,
                    AnalysisReport.is_deleted == False
                )
            )
            .options(selectinload(AnalysisReport.status_updates))
        )
        return result.scalar_one_or_none()

    async def get_reports_by_game_id(self, game_id: str, limit: int = 10) -> List[AnalysisReport]:
        """Get reports for a specific game."""
        result = await self.db.execute(
            select(AnalysisReport)
            .where(
                and_(
                    AnalysisReport.game_id == game_id,
                    AnalysisReport.is_deleted == False
                )
            )
            .order_by(desc(AnalysisReport.created_at))
            .limit(limit)
            .options(selectinload(AnalysisReport.status_updates))
        )
        return result.scalars().all()

    async def get_latest_report_by_game_id(self, game_id: str) -> Optional[AnalysisReport]:
        """Get the most recent report for a game."""
        result = await self.db.execute(
            select(AnalysisReport)
            .where(
                and_(
                    AnalysisReport.game_id == game_id,
                    AnalysisReport.is_deleted == False
                )
            )
            .order_by(desc(AnalysisReport.created_at))
            .limit(1)
            .options(selectinload(AnalysisReport.status_updates))
        )
        return result.scalar_one_or_none()

    async def update_report(self, report_id: str, update_data: Dict[str, Any]) -> Optional[AnalysisReport]:
        """Update an existing report."""
        result = await self.db.execute(
            select(AnalysisReport).where(AnalysisReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if report:
            for key, value in update_data.items():
                setattr(report, key, value)
            report.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(report)
        return report

    async def update_report_status(self, report_id: str, status: str) -> Optional[AnalysisReport]:
        """Update report status."""
        return await self.update_report(report_id, {"status": status})

    async def save_synthesis_result(self, game_id: str, game_title: str, platform: str, 
                                 master_json: Dict[str, Any], markdown_content: str,
                                 report_id: str = None) -> AnalysisReport:
        """Save the final synthesis result to database."""
        report_data = {
            "game_id": game_id,
            "game_title": game_title,
            "platform": platform,
            "title": f"Analysis Report: {game_title}",
            "markdown_content": markdown_content,
            "json_content": master_json,
            "summary": master_json.get("executive_summary", ""),
            "status": "completed",
            "phases_completed": master_json.get("metadata", {}).get("completed_phases", []),
            "confidence_score": master_json.get("metadata", {}).get("overall_confidence", 0.0),
            "quality_rating": master_json.get("metadata", {}).get("quality_rating", "unknown"),
            "word_count": len(markdown_content.split()),
            "data_completeness": master_json.get("metadata", {}).get("data_completeness", 0.0)
        }

        if report_id:
            updated_report = await self.update_report(report_id, report_data)
            if updated_report:
                return updated_report

        return await self.create_report(report_data)

    async def search_reports(self, query: str, limit: int = 20, offset: int = 0) -> List[AnalysisReport]:
        """Search reports by title or game title."""
        result = await self.db.execute(
            select(AnalysisReport)
            .where(
                and_(
                    or_(
                        AnalysisReport.title.ilike(f"%{query}%"),
                        AnalysisReport.game_title.ilike(f"%{query}%"),
                        AnalysisReport.game_id.ilike(f"%{query}%")
                    ),
                    AnalysisReport.is_deleted == False
                )
            )
            .order_by(desc(AnalysisReport.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_recent_reports(self, limit: int = 50, days: int = 30) -> List[AnalysisReport]:
        """Get recent reports from the last N days."""
        cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        result = await self.db.execute(
            select(AnalysisReport)
            .where(
                and_(
                    AnalysisReport.created_at >= cutoff_date,
                    AnalysisReport.is_deleted == False
                )
            )
            .order_by(desc(AnalysisReport.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_report(self, report_id: str) -> bool:
        """Soft delete a report."""
        report = await self.get_report_by_id(report_id)
        if report:
            report.is_deleted = True
            report.status = "deleted"
            await self.db.commit()
            return True
        return False


class PipelineStatusRepository:
    """Async repository for PipelineStatus operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_status_update(self, status_data: Dict[str, Any]) -> PipelineStatus:
        """Create a new pipeline status update."""
        status = PipelineStatus(**status_data)
        self.db.add(status)
        await self.db.commit()
        await self.db.refresh(status)
        return status

    async def update_status(self, status_id: str, update_data: Dict[str, Any]) -> Optional[PipelineStatus]:
        """Update an existing status."""
        result = await self.db.execute(
            select(PipelineStatus).where(PipelineStatus.id == status_id)
        )
        status = result.scalar_one_or_none()
        if status:
            for key, value in update_data.items():
                setattr(status, key, value)
            await self.db.commit()
            await self.db.refresh(status)
        return status

    async def get_statuses_by_report_id(self, report_id: str) -> List[PipelineStatus]:
        """Get all status updates for a report."""
        result = await self.db.execute(
            select(PipelineStatus)
            .where(PipelineStatus.report_id == report_id)
            .order_by(asc(PipelineStatus.created_at))
        )
        return result.scalars().all()

    async def get_latest_status_by_phase(self, report_id: str, phase_name: str) -> Optional[PipelineStatus]:
        """Get the latest status for a specific phase."""
        result = await self.db.execute(
            select(PipelineStatus)
            .where(
                and_(
                    PipelineStatus.report_id == report_id,
                    PipelineStatus.phase_name == phase_name
                )
            )
            .order_by(desc(PipelineStatus.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_phase_status(self, report_id: str, phase_name: str, 
                                status: str, progress: float = None, 
                                error_message: str = None, phase_data: Dict = None) -> PipelineStatus:
        """Update status for a specific phase."""
        # Get existing status or create new one
        existing = await self.get_latest_status_by_phase(report_id, phase_name)
        
        update_data = {
            "status": status,
            "progress_percentage": progress if progress is not None else 100.0 if status == "completed" else 0.0
        }
        
        if error_message:
            update_data["error_message"] = error_message
        if phase_data:
            update_data["phase_data"] = phase_data
        
        if status == "running":
            update_data["started_at"] = datetime.now(timezone.utc)
        elif status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.now(timezone.utc)
        
        if existing:
            return await self.update_status(existing.id, update_data)
        else:
            status_data = {
                "report_id": report_id,
                "phase_name": phase_name,
                **update_data
            }
            return await self.create_status_update(status_data)


class RawDataRepository:
    """Async repository for RawAnalysisData operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_raw_data(self, game_id: str, phase: str, source: str, 
                           data_type: str, content: Dict, metadata: Dict = None) -> RawAnalysisData:
        """Store raw analysis data for debugging/reprocessing."""
        data = RawAnalysisData(
            game_id=game_id,
            phase=phase,
            source=source,
            data_type=data_type,
            content=content,
            metadata=metadata or {}
        )
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data

    async def get_raw_data(self, game_id: str, phase: str = None, 
                         data_type: str = None, limit: int = 50) -> List[RawAnalysisData]:
        """Get raw analysis data with optional filters."""
        filters = [
            RawAnalysisData.game_id == game_id,
            RawAnalysisData.is_valid == True
        ]
        
        if phase:
            filters.append(RawAnalysisData.phase == phase)
        if data_type:
            filters.append(RawAnalysisData.data_type == data_type)
        
        result = await self.db.execute(
            select(RawAnalysisData)
            .where(and_(*filters))
            .order_by(desc(RawAnalysisData.created_at))
            .limit(limit)
        )
        return result.scalars().all()