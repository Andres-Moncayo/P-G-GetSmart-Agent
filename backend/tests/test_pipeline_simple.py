import pytest
import asyncio
from app.services.pipeline_tracker import pipeline_tracker
from app.models.pipelines import Phase

@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic pipeline tracker functionality."""
    report_id = "test-simple-123"
    game_name = "Test Game Simple"
    
    # Cleanup
    if report_id in pipeline_tracker.active_pipelines:
        pipeline_tracker.archive_pipeline(report_id)

    pipeline_tracker.create_pipeline(report_id, game_name)
    
    # Start phase
    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    
    # Start subtask
    await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, "Test Subtask")
    
    # Update progress
    await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Test Subtask", 50.0)
    
    # Complete subtask
    await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Test Subtask", 100.0)
    
    # Complete phase
    await pipeline_tracker.complete_phase(report_id, Phase.SCRAPING)
    
    # Get status
    status = pipeline_tracker.get_pipeline_status(report_id)
    assert status.pipeline_id == report_id
    scraping_phase = status.phases.get(Phase.SCRAPING)
    assert scraping_phase is not None
    assert scraping_phase["status"] == "completed"
    
    # Archive
    pipeline_tracker.archive_pipeline(report_id)
    assert report_id not in pipeline_tracker.active_pipelines
