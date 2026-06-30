import pytest
import asyncio
from app.services.pipeline_tracker import pipeline_tracker
from app.models.pipelines import Phase

@pytest.mark.asyncio
async def test_pipeline_progress():
    """Test the pipeline progress tracking with subtasks."""
    report_id = "test-report-123"
    game_name = "Test Game"
    
    # Clean up previous state if any
    if report_id in pipeline_tracker.active_pipelines:
        pipeline_tracker.archive_pipeline(report_id)

    pipeline_tracker.create_pipeline(report_id, game_name)
    
    # Start scraping phase
    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    
    # Start subtasks
    subtasks = ["Searching in databases", "Fetching game data", "Gathering reviews"]
    for subtask in subtasks:
        await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, subtask)
    
    # Simulate API calls with progress
    APIs = ["RAWG", "Steam", "Tavily"]
    successful_apis = []
    
    for i, api_name in enumerate(APIs):
        api_progress = (i / len(APIs)) * 100
        await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Searching in databases", api_progress)
        await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Fetching game data", api_progress)
        
        if api_name == "RAWG":
            successful_apis.append(api_name)
            await pipeline_tracker.start_api_call(report_id, api_name)
            await pipeline_tracker.complete_api_call(report_id, api_name, 3)
        elif api_name == "Steam":
            await pipeline_tracker.block_subtask(report_id, Phase.SCRAPING, "Steam API timeout - using fallback")
        elif api_name == "Tavily":
            successful_apis.append(api_name)
            await pipeline_tracker.start_api_call(report_id, api_name)
            await pipeline_tracker.complete_api_call(report_id, api_name, 10)
            
        if successful_apis:
            review_progress = len(successful_apis) / len(APIs) * 100
            await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Gathering reviews", review_progress)
            
    # Complete all subtasks
    for subtask in subtasks:
        await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, subtask, 100)
    
    # Update phase progress and complete
    if successful_apis:
        progress = (len(successful_apis) / len(APIs)) * 100
        await pipeline_tracker.update_phase_progress(report_id, progress)
    
    await pipeline_tracker.complete_phase(report_id, Phase.SCRAPING)
    
    # Test other phases briefly
    await pipeline_tracker.start_phase(report_id, Phase.ANALYSIS)
    analysis_tasks = ["Tech Systems", "Strategy & Market", "Optimization", "Spec Detection"]
    
    for task in analysis_tasks:
        await pipeline_tracker.start_subtask(report_id, Phase.ANALYSIS, task)
        await pipeline_tracker.update_subtask_progress(report_id, Phase.ANALYSIS, task, 100)
    
    await pipeline_tracker.complete_phase(report_id, Phase.ANALYSIS)
    
    # Get final status
    status = pipeline_tracker.get_pipeline_status(report_id)
    
    assert status.pipeline_id == report_id
    assert status.phase in [Phase.ANALYSIS, Phase.SYNTHESIS] # Synthesis is next phase, or Analysis is marked complete
    
    # The scraping phase should be marked complete
    scraping_phase = status.phases.get(Phase.SCRAPING)
    assert scraping_phase["status"] == "completed"
    
    # The analysis phase should be completed
    analysis_phase = status.phases.get(Phase.ANALYSIS)
    assert analysis_phase["status"] == "completed"

    # API calls tracking
    assert len(status.api_calls) > 0
    assert any(call.name == "RAWG" for call in status.api_calls)

    # Archive the test pipeline
    pipeline_tracker.archive_pipeline(report_id)
    assert report_id not in pipeline_tracker.active_pipelines
