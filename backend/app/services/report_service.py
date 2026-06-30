"""
Pipeline-facing service for report persistence.

Writes to `reports` and `analysis` tables defined in backend/UnityGsmart.sql.
The in-memory pipeline_tracker handles live progress; this service handles
durable DB state only.
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..db.connection import AsyncSessionLocal
from ..repositories.report_repository import ReportRepository, AnalysisRepository
from ..models.report import Report

logger = logging.getLogger(__name__)

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


class ReportService:
    """Lifecycle management for reports and per-skill analysis rows."""

    def __init__(self):
        self._db = None
        self._report_repo: Optional[ReportRepository] = None
        self._analysis_repo: Optional[AnalysisRepository] = None

    async def _init(self):
        if not self._db:
            self._db = AsyncSessionLocal()
            self._report_repo = ReportRepository(self._db)
            self._analysis_repo = AnalysisRepository(self._db)

    async def close(self):
        if self._db:
            await self._db.close()
            self._db = None
            self._report_repo = None
            self._analysis_repo = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _is_uuid(value: str) -> bool:
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, AttributeError):
            return False

    # ── public API ───────────────────────────────────────────────────────────

    async def create_new_report(
        self,
        game_id: str,
        game_name: str,
        platform: str = "unknown",
        user_id: str = DEMO_USER_ID,
        developer_name: Optional[str] = None,
        release_year: Optional[int] = None,
        primary_genre: Optional[str] = None,
        primary_platform: Optional[str] = None,
        all_genres: Optional[List[str]] = None,
        all_platforms: Optional[List[str]] = None,
        cover_url: Optional[str] = None,
    ) -> Report:
        """Insert a 'processing' row in `reports` and return the ORM object."""
        await self._init()
        report_uuid = uuid.uuid4()
        # Use game_id as-is if it's a UUID, otherwise generate a fresh one
        db_game_id = game_id if self._is_uuid(game_id) else str(uuid.uuid4())

        data = {
            "id": report_uuid,
            "user_id": user_id,
            "game_id": db_game_id,
            "report_status": "processing",
            "report_type": "comprehensive",
            "game_name": game_name,
            "game_slug": game_name.lower().replace(" ", "-"),
            "developer_name": developer_name,
            "release_year": release_year,
            "primary_genre": primary_genre,
            "primary_platform": primary_platform or platform,
            "all_genres": all_genres or [],
            "all_platforms": all_platforms or [],
            "cover_url": cover_url,
            "current_phase": "scraping",
            "pipeline_progress": 0,
            "game_data_jsonb": {},
            "pipeline_data_jsonb": {},
            "report_metadata_jsonb": {},
            "executive_summary_jsonb": {},
            "thematic_analysis_jsonb": {},
            "cross_cutting_insights_jsonb": {},
            "strategic_recommendations_jsonb": {},
            "risk_assessment_jsonb": {},
            "appendices_jsonb": {},
            "confidence_analysis_jsonb": {},
            "performance_metrics_jsonb": {},
            "user_metadata_jsonb": {},
        }
        report = await self._report_repo.create_report(data)
        logger.info("Created report row %s for game '%s'", report.id, game_name)
        return report

    async def save_analysis_results(
        self,
        report_id: str,
        game_id: str,
        game_name: str,
        platform: str,
        master_json: Dict[str, Any],
        markdown_content: str,
        user_id: str = DEMO_USER_ID,
        ai_results: Optional[Dict[str, Any]] = None,
        started_at: Optional[datetime] = None,
    ) -> Report:
        """Persist synthesis output and create per-skill Analysis rows."""
        await self._init()

        skill_map = {
            "design_art": "design_art",
            "user_experience": "user_experience",
            "technology_systems": "technology_systems",
            "strategy_market": "strategy_market",
        }
        
        analysis_ids = {}

        if ai_results:
            for skill_key, analysis_type in skill_map.items():
                skill_data = ai_results.get(skill_key) or {}
                if skill_data:
                    try:
                        analysis_row = await self._analysis_repo.create_skill_analysis(
                            report_id=report_id,
                            user_id=user_id,
                            game_id=game_id,
                            analysis_type=analysis_type,
                            raw_output=skill_data,
                        )
                        analysis_ids[f"analysis_{skill_key}"] = analysis_row.id
                    except Exception as exc:
                        logger.warning("Could not save analysis row for %s: %s", analysis_type, exc)

        # Synthesis analysis row
        try:
            synth_data = master_json.get("synthesis", master_json)
            confidence = master_json.get("metadata", {}).get("overall_confidence")
            await self._analysis_repo.create_skill_analysis(
                report_id=report_id,
                user_id=user_id,
                game_id=game_id,
                analysis_type="synthesis",
                raw_output=synth_data,
                confidence_score=confidence,
            )
        except Exception as exc:
            logger.warning("Could not save synthesis analysis row: %s", exc)

        # Update the report row with the final result
        report = await self._report_repo.save_synthesis_result(
            report_id, master_json, markdown_content, started_at=started_at, analysis_ids=analysis_ids
        )
        return report

    async def update_pipeline_progress(
        self,
        report_id: str,
        phase: str,
        status: str,
        progress: float = None,
        error_message: str = None,
        phase_data: Dict = None,
    ) -> bool:
        """Persist pipeline phase/progress to the reports row."""
        try:
            await self._init()
            update_data: Dict[str, Any] = {}
            if phase:
                update_data["current_phase"] = phase
            if progress is not None:
                update_data["pipeline_progress"] = min(max(int(progress), 0), 100)
            if status == "failed":
                update_data["report_status"] = "failed"
            elif status == "completed" and phase in ("phase4", "synthesis", "storage"):
                update_data["report_status"] = "completed"
                update_data["pipeline_progress"] = 100
            if update_data:
                await self._report_repo.update_report(report_id, update_data)
            return True
        except Exception as exc:
            logger.error("update_pipeline_progress failed for %s: %s", report_id, exc)
            return False

    async def store_phase_data(
        self, game_id: str, phase: str, source: str,
        data_type: str, content: Dict, metadata: Dict = None
    ) -> bool:
        """No-op stub — raw phase data is embedded in analysis JSONB columns."""
        return True

    async def get_report_by_id(self, report_id: str) -> Optional[Report]:
        await self._init()
        return await self._report_repo.get_by_id(report_id)
