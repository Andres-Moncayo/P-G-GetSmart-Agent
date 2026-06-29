"""
Simple test script to verify pipeline tracker works.
"""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.pipeline_tracker import pipeline_tracker
from app.models.pipelines import Phase, TaskStatus


async def test_basic_functionality():
    """Test basic pipeline tracker functionality."""
    
    print("Testing Pipeline Tracker")
    print("=" * 40)
    
    # Create test pipeline
    report_id = "test-123"
    game_name = "Test Game"
    
    pipeline_tracker.create_pipeline(report_id, game_name)
    print(f"Created pipeline: {game_name}")
    
    # Start phase
    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    print("Started scraping phase")
    
    # Start subtask
    await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, "Test Subtask")
    print("Started test subtask")
    
    # Update progress
    await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Test Subtask", 50.0)
    print("Updated progress to 50%")
    
    # Complete subtask
    await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Test Subtask", 100.0)
    print("Completed test subtask")
    
    # Complete phase
    await pipeline_tracker.complete_phase(report_id, Phase.SCRAPING)
    print("Completed scraping phase")
    
    # Get status
    status = pipeline_tracker.get_pipeline_status(report_id)
    print(f"Final status: {status.phase}")
    print(f"Overall progress: {status.overall_progress:.1f}%")
    
# Archive
    pipeline_tracker.archive_pipeline(report_id)
    print("Pipeline archived")
    
    print("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())