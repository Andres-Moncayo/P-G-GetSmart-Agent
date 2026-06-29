"""
Simple wrapper to run pipeline with tracking.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from .pipeline_tracker import pipeline_tracker
from .scraper.application.orchestrator import run_complete_pipeline_with_db
from ..models.pipelines import Phase, TaskStatus

logger = logging.getLogger(__name__)


async def run_pipeline_with_tracking(scraper_request: Dict[str, Any], report_id: str) -> None:
    """
    Run the pipeline with tracking using the real orchestrator.
    """
    logger.info(f"Starting pipeline execution for report_id: {report_id}")

    if report_id not in pipeline_tracker.active_pipelines:
        pipeline_tracker.create_pipeline(report_id, scraper_request.get("name", "Unknown Game"))

    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    await pipeline_tracker.update_phase_progress(report_id, 0.0, "Pipeline execution started")

    try:
        await pipeline_tracker.add_log(report_id, "Executing complete pipeline with DB persistence", "info")
        pipeline_result = await run_complete_pipeline_with_db(scraper_request, tracker_report_id=report_id)
        overall_status = pipeline_result.get("status", "complete_failure")

        if overall_status in ["complete_success", "partial_success"]:
            await pipeline_tracker.update_phase_progress(report_id, 100.0, "Pipeline completed successfully")
            for phase in [Phase.SCRAPING, Phase.ANALYSIS, Phase.SYNTHESIS, Phase.STORAGE]:
                await pipeline_tracker.complete_phase(report_id, phase)
        else:
            await pipeline_tracker.update_phase_progress(report_id, 100.0, "Pipeline completed with issues")
            await pipeline_tracker.add_log(report_id, "Pipeline finished with issues", "warning")

        logger.info(
            "Pipeline completed for report_id=%s with status=%s",
            report_id,
            overall_status,
        )

    except Exception as e:
        logger.exception("Pipeline failed for report_id=%s", report_id)
        await pipeline_tracker.add_log(report_id, f"Pipeline failed: {str(e)}", "error")
        if report_id in pipeline_tracker.active_pipelines:
            for phase in [Phase.SCRAPING, Phase.ANALYSIS, Phase.SYNTHESIS, Phase.STORAGE]:
                pipeline_tracker.active_pipelines[report_id]["phases"][phase]["status"] = TaskStatus.FAILED.value
        raise