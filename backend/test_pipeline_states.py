"""
Test script to verify pipeline progress states and subtask tracking.
"""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.pipeline_tracker import pipeline_tracker
from app.models.pipelines import Phase, TaskStatus


async def test_pipeline_progress():
    """Test the pipeline progress tracking with subtasks."""
    
    print("Testing Pipeline Progress Tracking")
    print("=" * 50)
    
    # Create test pipeline
    report_id = "test-report-123"
    game_name = "Test Game"
    
    pipeline_tracker.create_pipeline(report_id, game_name)
    print(f"Pipeline created for {game_name}")
    
    # Start scraping phase
    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    print("Started scraping phase")
    
    # Start subtasks
    subtasks = ["Buscando en bases de datos", "Obteniendo datos del juego", "Recopilando rese�as"]
    for subtask in subtasks:
        await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, subtask)
        print(f"Started subtask: {subtask}")
    
    # Simulate API calls with progress
    APIs = ["RAWG", "Steam", "Tavily"]
    successful_apis = []
    
    for i, api_name in enumerate(APIs):
        try:
            # Update progress while trying APIs
            api_progress = (i / len(APIs)) * 100
            await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Buscando en bases de datos", api_progress)
            await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Obteniendo datos del juego", (i / len(APIs)) * 100)
            print(f"Updated progress: {api_progress:.0f}% for searching APIs")
            
            # Simulate API call timing
            if api_name == "RAWG":
                await asyncio.sleep(1.5)
                successful_apis.append(api_name)
                await pipeline_tracker.complete_api_call(report_id, api_name, 3)
                print(f"API {api_name} completed successfully")
            elif api_name == "Steam":
                await asyncio.sleep(2)
                # Simulate timeout
                await pipeline_tracker.block_subtask(report_id, Phase.SCRAPING, "Steam API timeout - using fallback")
                print(f"API {api_name} timed out - blocked")
            elif api_name == "Tavily":
                await asyncio.sleep(0.5)
                successful_apis.append(api_name)
                await pipeline_tracker.complete_api_call(report_id, api_name, 10)
                print(f"API {api_name} completed successfully")
                
            # Update review collection progress 
            if successful_apis:
                review_progress = len(successful_apis) / len(APIs) * 100
                await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Recopilando rese�as", review_progress)
                
        except Exception as e:
            print(f"API {api_name} failed: {e}")
            await pipeline_tracker.fail_subtask(report_id, Phase.SCRAPING, f"{api_name} error")
    
    # Complete all subtasks
    for subtask in subtasks:
        await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, subtask, 100)
        print(f"Completed subtask: {subtask}")
    
    # Update phase progress and complete
    if successful_apis:
        progress = (len(successful_apis) / len(APIs)) * 100
        await pipeline_tracker.update_phase_progress(report_id, progress)
        print(f"Phase progress: {progress:.0f}%")
    
    await pipeline_tracker.complete_phase(report_id, Phase.SCRAPING)
    print("Completed scraping phase")
    
    # Test other phases briefly
    await pipeline_tracker.start_phase(report_id, Phase.ANALYSIS)
    analysis_tasks = ["Tech Systems", "Strategy & Market", "Optimization", "Spec Detection"]
    
    for task in analysis_tasks:
        await pipeline_tracker.start_subtask(report_id, Phase.ANALYSIS, task)
        
        # Simulate progress updates
        for i in range(0, 101, 25):
            await pipeline_tracker.update_subtask_progress(report_id, Phase.ANALYSIS, task, i)
            await asyncio.sleep(0.1)
    
    await pipeline_tracker.complete_phase(report_id, Phase.ANALYSIS)
    print("Completed analysis phase")
    
    # Get final status
    status = pipeline_tracker.get_pipeline_status(report_id)
    
    print("\nFINAL PIPELINE STATUS:")
    print("=" * 50)
    print(f"Pipeline ID: {status.pipeline_id}")
    print(f"Current Phase: {status.phase}")
    print(f"Overall Progress: {status.overall_progress:.1f}%")
    
    for phase_key, phase_data in status.phases.items():
        print(f"\n{phase_key.upper()} Phase:")
        print(f"  Status: {phase_data['status']}")
        print(f"  Progress: {phase_data['progress']:.1f}%")
        
        tasks = phase_data.get('tasks') if isinstance(phase_data, dict) else getattr(phase_data, 'tasks', None)
        if tasks:
            for task in tasks:
                print(f"  Task: {task.get('name', task.get('task_name', 'unknown'))}")
                print(f"    Status: {task.get('status', 'unknown')}")
                print(f"    Progress: {task.get('progress', 0):.1f}%")
    
    # Test API calls tracking
    print("\nAPI CALLS SUMMARY:")
    print("=" * 50)
    api_calls = status.api_calls
    if api_calls:
        for call_data in api_calls:
            print(f"{call_data.get('api_name', 'unknown')}:")
            print(f"   Records: {call_data.get('records_count', 0)}")
            print(f"   Duration: {call_data.get('duration_seconds', 0):.2f}s")
            print(f"   Status: {call_data.get('status', 'unknown')}")
    else:
        print("No API calls recorded")
    
    # Test logs
    print("\nPIPELINE LOGS:")
    print("=" * 50)
    logs = status.logs[-5:]  # Show last 5 logs
    for log in logs:
        print(f"  [{log.get('level', 'INFO')}] {log.get('message', '')}")
    
    print("\nTest completed successfully!")
    
    # Archive the test pipeline
    pipeline_tracker.archive_pipeline(report_id)
    print("Pipeline archived")


if __name__ == "__main__":
    asyncio.run(test_pipeline_progress())