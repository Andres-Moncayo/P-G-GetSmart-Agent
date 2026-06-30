"""
Repository layer — reads/writes to `reports` and `analysis` tables
as defined in backend/UnityGsmart.sql.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.report import Report, Analysis

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(self, data: Dict[str, Any]) -> Report:
        report = Report(**data)
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_by_id(self, report_id: str) -> Optional[Report]:
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def update_report(self, report_id: str, data: Dict[str, Any]) -> Optional[Report]:
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        if report:
            for key, value in data.items():
                setattr(report, key, value)
            await self.db.commit()
            await self.db.refresh(report)
        return report

    async def save_synthesis_result(
        self,
        report_id: str,
        master_json: Dict[str, Any],
        markdown_content: str,
        started_at: Optional[datetime] = None,
        analysis_ids: Optional[Dict[str, str]] = None,
    ) -> Optional[Report]:
        """Update an existing report row with the final synthesis output."""
        meta = master_json.get("metadata", {})
        confidence = meta.get("overall_confidence") or meta.get("confidence_score")
        summary = (markdown_content[:500] + "...") if len(markdown_content) > 500 else markdown_content
        now = datetime.now(timezone.utc)
        processing_ms = (
            int((now - started_at).total_seconds() * 1000) if started_at else None
        )

        update_data = {
            "report_status": "completed",
            "markdown_content": markdown_content,
            "markdown_summary": summary,
            "markdown_generated": bool(markdown_content),
            "confidence_score": confidence,
            "completed_at": now,
            "current_phase": "completed",
            "pipeline_progress": 100,
            "processing_time_ms": processing_ms,
            # Structured JSONB sections from master_json
            "executive_summary_jsonb": master_json.get("executive_summary", {}),
            "thematic_analysis_jsonb": master_json.get("thematic_analysis", {}),
            "cross_cutting_insights_jsonb": master_json.get("cross_cutting_insights", {}),
            "strategic_recommendations_jsonb": master_json.get("strategic_recommendations", {}),
            "risk_assessment_jsonb": master_json.get("risk_assessment", {}),
            "appendices_jsonb": master_json.get("appendices", {}),
            "confidence_analysis_jsonb": master_json.get("confidence_analysis", {}),
            "report_metadata_jsonb": meta,
        }
        
        if analysis_ids:
            update_data.update(analysis_ids)
            
        return await self.update_report(report_id, update_data)


class AnalysisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_analysis(self, data: Dict[str, Any]) -> Analysis:
        analysis = Analysis(**data)
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def create_skill_analysis(
        self,
        report_id: str,
        user_id: str,
        game_id: str,
        analysis_type: str,
        raw_output: Dict[str, Any],
        processed_output: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None,
    ) -> Analysis:
        data = {
            "id": uuid.uuid4(),
            "user_id": user_id,
            "game_id": game_id,
            "analysis_type": analysis_type,
            "status": "completed",
            "confidence_score": confidence_score,
            "input_data_jsonb": {},
            "raw_output_jsonb": raw_output,
            "processed_output_jsonb": processed_output or {},
            "metrics_jsonb": {},
            "error_details_jsonb": {},
            "final_report_id": report_id,
            "completed_at": datetime.now(timezone.utc),
        }
        return await self.create_analysis(data)
