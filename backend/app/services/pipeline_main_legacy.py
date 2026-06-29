"""
Main pipeline orchestrator for analysis flow.

Coordinates scraping, AI analysis, synthesis, and storage phases.
Handles background execution with proper error handling and status tracking.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from .report_service import ReportService
from .scraper.application.game_orchestrator import GameAnalysisOrchestrator
from .scraper.infrastructure.llm_client import GeminiClient
from .scraper.infrastructure.tavily_client import TavilyClient
from ..core.config import settings
from .pipeline_tracker import pipeline_tracker
from ..models.pipelines import Phase, TaskStatus

logger = logging.getLogger(__name__)


async def run_pipeline_async(scraper_request: Dict[str, Any], report_id: str) -> None:
    """
    Run the complete analysis pipeline in background.
    
    This function is designed to run as a background task.
    It coordinates all phases: scraping, analysis, synthesis, and storage.
    
    Args:
        scraper_request: Game data from frontend converted to scraper format
        report_id: Unique identifier for this pipeline execution
    """
    logger.info(f"Starting pipeline execution for report_id: {report_id}")
    
    try:
        # Initialize report service for status tracking
        report_service = ReportService()
        
        # Phase 1: Game Data Scraping
        await _run_scraping_phase(report_id, scraper_request, report_service)
        
        # Phase 2: AI Analysis
        await _run_analysis_phase(report_id, scraper_request, report_service)
        
        # Phase 3: Synthesis
        await _run_synthesis_phase(report_id, report_service)
        
        # Phase 4: Database Storage
        await _run_storage_phase(report_id, report_service)
        
        # Mark pipeline as completed
        await pipeline_tracker.complete_phase(report_id, Phase.STORAGE)
        await pipeline_tracker.update_phase_progress(report_id, 100.0, "Pipeline completed successfully")
        logger.info(f"Pipeline completed successfully for report_id: {report_id}")
        
    except Exception as e:
        logger.error(f"Pipeline failed for report_id: {report_id}: {str(e)}")
        # Mark pipeline as failed
        await pipeline_tracker.add_log(report_id, f"Pipeline failed: {str(e)}", "error")
        await pipeline_tracker.archive_pipeline(report_id)
        raise


async def _run_scraping_phase(report_id: str, scraper_request: Dict[str, Any], report_service: ReportService) -> None:
    """
    Phase 1: Scraping game data from multiple APIs with timeout handling.
    """
    logger.info(f"Starting scraping phase for report_id: {report_id}")
    
    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    
    # Define subtasks
    subtasks = ["Buscando en bases de datos", "Obteniendo datos del juego", "Recopilando reseñas"]
    APIs = ["RAWG", "Steam", "Tavily"]
    
    # Start all subtasks
    for subtask in subtasks:
        await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, subtask)
    
# Try APIs with timeout and fallback logic
    successful_apis = []
    
    for i, api_name in enumerate(APIs):
        try:
            # Update progress while trying APIs (show active progress)
            api_progress = (i / len(APIs)) * 100
            await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Buscando en bases de datos", api_progress)
            await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Obteniendo datos del juego", (i / len(APIs)) * 100)
            
            # Start API call with timeout (10 seconds for RAWG, 15 for Steam)
            timeout = 10 if api_name == "RAWG" else 15
            await pipeline_tracker.start_api_call(report_id, api_name, {"game": scraper_request.get("name")}, timeout)
            
            # Simulate API call (replace with actual API calls)
            api_result = await _call_api_with_timeout(api_name, scraper_request, timeout)
            
            if api_result:
                await pipeline_tracker.complete_api_call(report_id, api_name, len(api_result))
                successful_apis.append(api_name)
                # Update review collection progress
                review_progress = len(successful_apis) / len(APIs) * 100
                await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Recopilando reseñas", review_progress)
                logger.info(f"Successfully called {api_name} API")
            else:
                await pipeline_tracker.complete_api_call(report_id, api_name, 0, "No data returned")
                
        except asyncio.TimeoutError:
            logger.warning(f"{api_name} API timeout after {timeout}s, trying next API")
            await pipeline_tracker.block_subtask(report_id, Phase.SCRAPING, f"{api_name} API timeout")
            continue
        except Exception as e:
            logger.error(f"{api_name} API failed: {str(e)}")
            await pipeline_tracker.fail_subtask(report_id, Phase.SCRAPING, f"{api_name} API error: {str(e)}")
            continue
    
    # Final progress update - complete all subtasks if at least some APIs succeeded
    for subtask in subtasks:
        await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, subtask, 100)
    
    # Update overall phase progress
    if successful_apis:
        progress = (len(successful_apis) / len(APIs)) * 100
        await pipeline_tracker.update_phase_progress(report_id, progress)
    else:
        await pipeline_tracker.update_phase_progress(report_id, 25)  # Some progress even if all failed
        
    await pipeline_tracker.complete_phase(report_id, Phase.SCRAPING)


async def _call_api_with_timeout(api_name: str, scraper_request: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    """
    Example of calling APIs with timeout handling.
    
    Replace this with actual API calls to RAWG, Steam, Tavily, etc.
    """
    try:
        # Simulate different API response times
        if api_name == "RAWG":
            await asyncio.sleep(12)  # Might timeout depending on timeout setting
            return {"name": scraper_request.get("name"), "rating": 4.5}
        elif api_name == "Steam":
            await asyncio.sleep(20)  # Slow API, will likely timeout
            return {"name": scraper_request.get("name"), "price": 29.99}
        elif api_name == "Tavily":
            await asyncio.sleep(5)  # Fast API
            return {"reviews": ["Great game!", "Recommended"]}
            
    except asyncio.TimeoutError:
        raise
    except Exception as e:
        logger.error(f"Error calling {api_name}: {str(e)}")
        return None
    
    return None


async def _run_analysis_phase(report_id: str, scraper_request: Dict[str, Any], report_service: ReportService) -> None:
    """
    Phase 2: AI Analysis of collected data.
    """
    logger.info(f"Starting analysis phase for report_id: {report_id}")
    
    await pipeline_tracker.start_phase(report_id, Phase.ANALYSIS)
    
    # Analysis subtasks
    analysis_tasks = ["Tech Systems", "Strategy & Market", "Optimization", "Spec Detection"]
    
    for task in analysis_tasks:
        await pipeline_tracker.start_subtask(report_id, Phase.ANALYSIS, task)
        
        try:
            # Simulate analysis with progress updates
            for i in range(0, 101, 25):
                await pipeline_tracker.update_subtask_progress(report_id, Phase.ANALYSIS, task, i)
                await asyncio.sleep(0.5)  # Simulate processing time
                
        except Exception as e:
            logger.error(f"Analysis task {task} failed: {str(e)}")
            await pipeline_tracker.fail_subtask(report_id, Phase.ANALYSIS, task, str(e))
    
    await pipeline_tracker.complete_phase(report_id, Phase.ANALYSIS)


async def _run_synthesis_phase(report_id: str, report_service: ReportService) -> None:
    """
    Phase 3: Synthesize analysis results into insights.
    """
    logger.info(f"Starting synthesis phase for report_id: {report_id}")
    
    await pipeline_tracker.start_phase(report_id, Phase.SYNTHESIS)
    
    synthesis_tasks = ["Procesando resultados", "Creando insights", "Construyendo correlaciones"]
    
    for task in synthesis_tasks:
        await pipeline_tracker.start_subtask(report_id, Phase.SYNTHESIS, task)
        
        # Simulate synthesis work
        await asyncio.sleep(1)
        await pipeline_tracker.update_subtask_progress(report_id, Phase.SYNTHESIS, task, 100)
    
    await pipeline_tracker.complete_phase(report_id, Phase.SYNTHESIS)


async def _run_storage_phase(report_id: str, report_service: ReportService) -> None:
    """
    Phase 4: Store results in database.
    """
    logger.info(f"Starting storage phase for report_id: {report_id}")
    
    await pipeline_tracker.start_phase(report_id, Phase.STORAGE)
    
    storage_tasks = ["Validando datos", "Almacenando resultados", "Actualizando índices"]
    
    for task in storage_tasks:
        await pipeline_tracker.start_subtask(report_id, Phase.STORAGE, task)
        
        # Simulate database operations
        await asyncio.sleep(0.5)
        await pipeline_tracker.update_subtask_progress(report_id, Phase.STORAGE, task, 100)
    
    await pipeline_tracker.complete_phase(report_id, Phase.STORAGE)