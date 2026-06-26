"""
Service layer for report operations and business logic.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from ..db.connection import AsyncSessionLocal
from ..repositories.report_repository import ReportRepository, PipelineStatusRepository, RawDataRepository
from ..models.report import AnalysisReport, PipelineStatus


class ReportService:
    """High-level service for report operations."""
    
    def __init__(self):
        self._report_repo = None
        self._status_repo = None
        self._raw_data_repo = None
        self._db = None

    async def _get_repositories(self):
        """Initialize repositories with async session."""
        if not self._db:
            self._db = AsyncSessionLocal()
            self._report_repo = ReportRepository(self._db)
            self._status_repo = PipelineStatusRepository(self._db)
            self._raw_data_repo = RawDataRepository(self._db)
        return self._report_repo, self._status_repo, self._raw_data_repo

    async def close(self):
        """Close the database session if open."""
        if self._db:
            await self._db.close()
            self._db = None
            self._report_repo = None
            self._status_repo = None
            self._raw_data_repo = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_new_report(self, game_id: str, game_title: str, platform: str) -> AnalysisReport:
        """Create a new report and initialize pipeline tracking."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        
        # Create the report with placeholder content so the initial record is valid.
        report_data = {
            "game_id": game_id,
            "game_title": game_title,
            "platform": platform,
            "title": f"Analysis Report: {game_title}",
            "status": "pending",
            "phases_completed": [],
            "total_phases": 4,
            "markdown_content": "",
            "json_content": {},
        }
        
        report = await report_repo.create_report(report_data)
        
        # Initialize pipeline status tracking
        phases = ["phase1", "phase2", "phase3", "phase4"]
        for phase in phases:
            await status_repo.update_phase_status(
                report.id, phase, "pending", 0.0
            )
        
        return report

    async def save_analysis_results(self, report_id: str, game_id: str, game_title: str, platform: str,
                                  master_json: Dict[str, Any], markdown_content: str) -> AnalysisReport:
        """Save complete analysis results to database."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        
        # Save the main report, updating the existing draft report record.
        report = await report_repo.save_synthesis_result(
            game_id, game_title, platform, master_json, markdown_content, report_id=report_id
        )
        
        # Update final phase status
        await status_repo.update_phase_status(
            report.id, "phase4", "completed", 100.0
        )
        
        # Store raw data for potential reprocessing
        await raw_repo.store_raw_data(
            game_id=game_id,
            phase="synthesis",
            source="ai_orchestrator",
            data_type="final_result",
            content={
                "master_json": master_json,
                "markdown_content": markdown_content
            },
            metadata={
                "report_id": str(report.id),
                "processing_time_ms": master_json.get("metadata", {}).get("processing_time_ms"),
                "confidence_score": master_json.get("metadata", {}).get("overall_confidence")
            }
        )
        
        return report

    async def get_report_by_id(self, report_id: str) -> Optional[AnalysisReport]:
        """Get a complete report with status tracking."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        return await report_repo.get_report_by_id(report_id)

    async def get_latest_report_for_game(self, game_id: str) -> Optional[AnalysisReport]:
        """Get the most recent report for a specific game."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        return await report_repo.get_latest_report_by_game_id(game_id)

    async def get_all_reports_for_game(self, game_id: str, limit: int = 10) -> List[AnalysisReport]:
        """Get all reports for a specific game."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        return await report_repo.get_reports_by_game_id(game_id, limit)

    async def update_pipeline_progress(self, report_id: str, phase: str, 
                                     status: str, progress: float = None,
                                     error_message: str = None, phase_data: Dict = None) -> bool:
        """Update pipeline progress for a specific phase."""
        try:
            report_repo, status_repo, raw_repo = await self._get_repositories()
            
            await status_repo.update_phase_status(
                report_id, phase, status, progress, error_message, phase_data
            )
            
            # Update overall report status if needed
            if status == "failed":
                await report_repo.update_report_status(report_id, "failed")
            elif phase == "phase4" and status == "completed":
                await report_repo.update_report_status(report_id, "completed")
            
            return True
        except Exception as e:
            print(f"Error updating pipeline progress: {e}")
            return False

    async def search_reports(self, query: str, limit: int = 20, offset: int = 0) -> List[AnalysisReport]:
        """Search reports by content."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        return await report_repo.search_reports(query, limit, offset)

    async def get_recent_reports(self, limit: int = 50, days: int = 30) -> List[AnalysisReport]:
        """Get reports from recent activity."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        return await report_repo.get_recent_reports(limit, days)

    async def get_pipeline_status(self, report_id: str) -> List[PipelineStatus]:
        """Get complete pipeline status for a report."""
        report_repo, status_repo, raw_repo = await self._get_repositories()
        return await status_repo.get_statuses_by_report_id(report_id)

    async def store_phase_data(self, game_id: str, phase: str, source: str,
                             data_type: str, content: Dict, metadata: Dict = None) -> bool:
        """Store raw phase data for debugging."""
        try:
            report_repo, status_repo, raw_repo = await self._get_repositories()
            await raw_repo.store_raw_data(
                game_id, phase, source, data_type, content, metadata
            )
            return True
        except Exception as e:
            print(f"Error storing phase data: {e}")
            return False

    async def get_report_summary(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a lightweight summary of a report."""
        report = await self.get_report_by_id(report_id)
        if not report:
            return None
        
        return {
            "id": report.id,
            "game_id": report.game_id,
            "game_title": report.game_title,
            "platform": report.platform,
            "title": report.title,
            "status": report.status,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
            "confidence_score": report.confidence_score,
            "quality_rating": report.quality_rating,
            "word_count": report.word_count,
            "phases_completed": report.phases_completed,
            "summary": report.summary[:200] + "..." if len(report.summary) > 200 else report.summary
        }

    async def get_game_analysis_history(self, game_id: str) -> List[Dict[str, Any]]:
        """Get analysis history for a game with summaries."""
        reports = await self.get_all_reports_for_game(game_id, limit=20)
        
        history = []
        for report in reports:
            summary = await self.get_report_summary(report.id)
            if summary:
                history.append(summary)
        
        return history