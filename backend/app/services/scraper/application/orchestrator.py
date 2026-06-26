"""
Main Pipeline Orchestrator - Coordinates Phase 1, 2, and 3 execution.

This module provides the main orchestration functions for the complete
game intelligence pipeline: scraping, AI analysis, and synthesis.
"""

import asyncio
import logging
from typing import Dict, Any, List

from ..domain.design_art_service import DesignArtService
from ..domain.user_experience_service import UserExperienceService
from ..domain.technology_systems_service import TechnologySystemsService
from ..domain.strategy_market_service import StrategyMarketService


logger = logging.getLogger(__name__)


async def run_scrape_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute all four scraper services and aggregate results.
    
    Args:
        payload: Dictionary with game IDs and metadata
        
    Returns:
        Dict with aggregated scraper results and Mini-Contexts
    """
    start_time = asyncio.get_event_loop().time()
    
    logger.info("Starting Phase 1: Parallel scraper execution")
    
    # Define all scraper tasks
    scraper_tasks = [
        scrape_design_art(payload),
        scrape_user_experience(payload),
        scrape_technology_systems(payload),
        scrape_strategy_market(payload),
    ]
    
    # Execute all scrapers in parallel
    results = await asyncio.gather(*scraper_tasks, return_exceptions=True)
    
    # Process results
    mini_contexts = {}
    workers_completed = []
    workers_failed = []
    workers_total = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Scraper {i} failed: {result}")
            failed_result = {
                "macro_skill": f"scraper_{i}",
                "status": "failed",
                "error": str(result),
            }
            workers_total.append(failed_result)
            workers_failed.append(failed_result)
        elif result.get("status") == "completed":
            macro_skill = result.get("macro_skill", f"scraper_{i}")
            mini_contexts[macro_skill] = result.get("mini_context", {})
            workers_completed.append(result)
            workers_total.append(result)
            logger.info(f"Scraper {macro_skill} completed successfully")
        else:
            workers_total.append(result)
            workers_failed.append(result)
            logger.warning(f"Scraper {i} returned non-success status: {result}")
    
    # Calculate metrics
    duration = round(asyncio.get_event_loop().time() - start_time, 2)
    success_rate = len(workers_completed) / len(results) if results else 0
    
    # Determine overall status
    if success_rate == 0:
        overall_status = "failed"
    elif success_rate >= 1:
        overall_status = "completed"
    else:
        overall_status = "partial"
    
    result = {
        "status": overall_status,
        "phase": 1,  # Phase 1: Scraping
        "workers_completed": workers_completed,
        "workers_failed": workers_failed,
        "workers_total": workers_total,
        "success_rate": success_rate,
        "mini_contexts": mini_contexts,
        "metadata": {
            "run_duration_seconds": duration,
            "scraper_version": "1.0.0",
            "parallel_execution": True,
            "game_id": payload.get("game_id"),
            "game_name": payload.get("name"),
        },
    }
    
    logger.info(
        f"Phase 1 complete: {len(workers_completed)}/{len(results)} scrapers successful in {duration}s"
    )
    return result


# Scraper implementations
async def scrape_design_art(game_payload: dict[str, Any]) -> dict[str, Any]:
    """Design & Art scraper - extracts visual, aesthetic, art direction data."""
    service = DesignArtService()
    
    try:
        mini_context = await service.extract_design_art_context(
            game_id=str(game_payload["game_id"]),
            game_name=game_payload["name"],
            rawg_id=game_payload.get("rawg_id"),
            steam_app_id=game_payload.get("steam_app_id"),
            aliases=game_payload.get("aliases", []),
        )
        
        return {
            "macro_skill": "design_art",
            "status": "completed",
            "mini_context": mini_context,
            "metadata": {
                "scraper_version": "1.0.0",
                "run_timestamp": mini_context["metadata"].get("generated_at"),
            },
        }
    except Exception as exc:
        logger.error("Design & Art scraper failed: %s", exc)
        return {
            "macro_skill": "design_art",
            "status": "failed",
            "error": str(exc),
            "game_id": game_payload.get("game_id"),
        }


async def scrape_user_experience(game_payload: dict[str, Any]) -> dict[str, Any]:
    """User Experience scraper - extracts UI, accessibility, localization data."""
    service = UserExperienceService()
    
    try:
        mini_context = await service.extract_user_experience_context(
            game_id=str(game_payload["game_id"]),
            game_name=game_payload["name"],
            rawg_id=game_payload.get("rawg_id"),
            steam_app_id=game_payload.get("steam_app_id"),
            aliases=game_payload.get("aliases", []),
        )
        
        return {
            "macro_skill": "user_experience",
            "status": "completed",
            "mini_context": mini_context,
            "metadata": {
                "scraper_version": "1.0.0",
                "run_timestamp": mini_context["metadata"].get("generated_at"),
            },
        }
    except Exception as exc:
        logger.error("User Experience scraper failed: %s", exc)
        return {
            "macro_skill": "user_experience",
            "status": "failed",
            "error": str(exc),
            "game_id": game_payload.get("game_id"),
        }


async def scrape_technology_systems(game_payload: dict[str, Any]) -> dict[str, Any]:
    """Technology Systems scraper - extracts engine, performance, technical specs."""
    service = TechnologySystemsService()
    
    try:
        mini_context = await service.extract_technology_systems_context(
            game_id=str(game_payload["game_id"]),
            game_name=game_payload["name"],
            rawg_id=game_payload.get("rawg_id"),
            steam_app_id=game_payload.get("steam_app_id"),
            aliases=game_payload.get("aliases", []),
        )
        
        return {
            "macro_skill": "technology_systems",
            "status": "completed",
            "mini_context": mini_context,
            "metadata": {
                "scraper_version": "1.0.0",
                "run_timestamp": mini_context["metadata"].get("generated_at"),
            },
        }
    except Exception as exc:
        logger.error("Technology Systems scraper failed: %s", exc)
        return {
            "macro_skill": "technology_systems",
            "status": "failed",
            "error": str(exc),
            "game_id": game_payload.get("game_id"),
        }


async def scrape_strategy_market(game_payload: dict[str, Any]) -> dict[str, Any]:
    """Strategy & Market scraper - extracts business model, market positioning data."""
    service = StrategyMarketService()
    
    try:
        mini_context = await service.extract_strategy_market_context(
            game_id=str(game_payload["game_id"]),
            game_name=game_payload["name"],
            rawg_id=game_payload.get("rawg_id"),
            steam_app_id=game_payload.get("steam_app_id"),
            aliases=game_payload.get("aliases", []),
        )
        
        return {
            "macro_skill": "strategy_market",
            "status": "completed",
            "mini_context": mini_context,
            "metadata": {
                "scraper_version": "1.0.0",
                "run_timestamp": mini_context["metadata"].get("generated_at"),
            },
        }
    except Exception as exc:
        logger.error("Strategy & Market scraper failed: %s", exc)
        return {
            "macro_skill": "strategy_market",
            "status": "failed",
            "error": str(exc),
            "game_id": game_payload.get("game_id"),
        }


async def run_complete_pipeline_with_db(game_payload: dict[str, Any], tracker_report_id: str | None = None) -> dict[str, Any]:
    """
    Execute complete Phase 1 + 2 + 3 pipeline with Phase 4 database storage:
    Scraping -> AI Analysis -> Synthesis -> Database Persistence
    
    This function runs:
    Phase 1: 4 parallel scrapers to generate Mini-Contexts
    Phase 2: 4 parallel AI analyses on Mini-Contexts  
    Phase 3: Synthesis of AI analyses into comprehensive report
    Phase 4: Store results in database
    
    Args:
        game_payload: Game search confirmation payload with IDs and metadata
        tracker_report_id: Optional pipeline tracker report ID for live progress updates
        
    Returns:
        Dictionary with complete pipeline results including database storage status
"""
    from datetime import datetime
    from app.models.pipelines import Phase
    from app.services.pipeline_tracker import pipeline_tracker
    from ...report_service import ReportService
    
    pipeline_start = asyncio.get_event_loop().time()
    game_name = game_payload.get("name", "Unknown")
    game_id = str(game_payload.get("game_id", "unknown"))
    platform = game_payload.get("platform", "unknown")
    
    logger.info("Starting complete pipeline with DB storage (Phase 1 + 2 + 3 + 4) for %s", game_name)
    
    # Initialize report service for Phase 4
    report_service = ReportService()
    
    # Preserve tracker report id separately from DB report id
    tracker_id = tracker_report_id
    
# Create initial report record (TEMP DISABLED for testing)
    try:
        # TEMP: Skip database creation to bypass stuck pipelines
        # report = await report_service.create_new_report(game_id, game_name, platform)
        # db_report_id = report.id
        # logger.info(f"Created initial report record: {db_report_id}")
        
        # TEMP: Use fake db_report_id for testing
        db_report_id = hash(game_name) % 10000 + 1  # Simple hash for testing
        logger.info(f"TEMP: Using fake db_report_id: {db_report_id}")

        if tracker_id and tracker_id in pipeline_tracker.active_pipelines:
            pipeline_tracker.active_pipelines[tracker_id]["db_report_id"] = db_report_id
    except Exception as exc:
        logger.error("Failed to create initial report record: %s", exc)
        db_report_id = hash(game_name) % 10000 + 1  # Fallback fake ID
        if tracker_id:
            await pipeline_tracker.update_phase_progress(tracker_id, 0.0, "Using fallback report ID due to DB issues")
            await pipeline_tracker.add_log(tracker_id, f"Using fallback ID due to DB issues: {exc}", "warning")
# Continue with pipeline instead of returning early

    if tracker_id:
        await pipeline_tracker.update_phase_progress(tracker_id, 0.0, "Phase 1 scraping started")
    
    scraper_result = await run_scrape_task(game_payload)
    
    # Store scraping results in DB
    if db_report_id and scraper_result.get("mini_contexts"):
        await report_service.store_phase_data(
            game_id=game_id,
            phase="phase1",
            source="scrapers",
            data_type="mini_contexts",
            content=scraper_result.get("mini_contexts"),
            metadata=scraper_result.get("metadata", {})
        )
    
    scraper_success = scraper_result.get("success_rate", 0)
    
    if scraper_success == 0:
        logger.error("Phase 1 failed completely - cannot proceed")
        if db_report_id:
            await report_service.update_pipeline_progress(db_report_id, "phase1", "failed", 0.0, "All scrapers failed")
        if tracker_id:
            await pipeline_tracker.update_phase_progress(tracker_id, 100.0, "Phase 1 failed")
            await pipeline_tracker.complete_phase(tracker_id, Phase.SCRAPING)
        return {
            "status": "scraping_failure",
            "phase": "1_failed",
            "scraper_result": scraper_result,
            "game_id": game_id,
            "game_name": game_name,
            "report_id": db_report_id or tracker_id
        }
    
    if db_report_id:
        await report_service.update_pipeline_progress(db_report_id, "phase1", "completed", 100.0)
    if tracker_id:
        await pipeline_tracker.update_phase_progress(tracker_id, 100.0, "Phase 1 scraping completed")
        await pipeline_tracker.complete_phase(tracker_id, Phase.SCRAPING)
    
    mini_contexts = scraper_result.get("mini_contexts", {})
    logger.info("Phase 1 completed with %d mini-contexts", len(mini_contexts))
    
    # PHASE 2: Run AI analyses with DB tracking
    logger.info("=== PHASE 2: AI ANALYSIS EXECUTION ===")
    if db_report_id:
        await report_service.update_pipeline_progress(db_report_id, "phase2", "running", 0.0)
    if tracker_id:
        await pipeline_tracker.start_phase(tracker_id, Phase.ANALYSIS)
        await pipeline_tracker.update_phase_progress(tracker_id, 15.0, "Phase 2 AI analysis started")
    
    from .ai_orchestrator import run_ai_analysis_pipeline
    ai_result = await run_ai_analysis_pipeline(mini_contexts, game_name, game_id)
    
    # Store AI analysis results in DB
    if db_report_id and ai_result.get("analysis_results"):
        await report_service.store_phase_data(
            game_id=game_id,
            phase="phase2",
            source="ai_analysis",
            data_type="ai_analyses",
            content=ai_result.get("analysis_results"),
            metadata=ai_result.get("metadata", {})
        )
    
    ai_success_rate = ai_result.get("success_rate", 0)
    
    if db_report_id:
        status = "completed" if ai_success_rate >= 0.5 else "failed"
        await report_service.update_pipeline_progress(db_report_id, "phase2", status, 100.0 if status == "completed" else ai_success_rate * 100)
    if tracker_id:
        await pipeline_tracker.update_phase_progress(tracker_id, 100.0 if ai_success_rate >= 0.5 else ai_success_rate * 100, "Phase 2 AI analysis completed")
        await pipeline_tracker.complete_phase(tracker_id, Phase.ANALYSIS)
    
    # PHASE 3: Synthesis with DB tracking
    synthesis_result = None
    synthesis_content = None
    master_json = ai_result.get("master_json", {})
    
    if ai_success_rate >= 0.5 and master_json:
        logger.info("=== PHASE 3: SYNTHESIS EXECUTION ===")
        if db_report_id:
            await report_service.update_pipeline_progress(db_report_id, "phase3", "running", 0.0)
        if tracker_id:
            await pipeline_tracker.start_phase(tracker_id, Phase.SYNTHESIS)
            await pipeline_tracker.update_phase_progress(tracker_id, 10.0, "Phase 3 synthesis started")
        
        try:
            from .synthesizer import synthesizer
            syn_engine = synthesizer()
            synthesis_result_obj = await syn_engine.synthesize_master_analysis(master_json)
            synthesis_content = synthesis_result_obj.markdown_content
            
            synthesis_result = {
                "status": synthesis_result_obj.status,
                "word_count": synthesis_result_obj.word_count,
                "confidence": synthesis_result_obj.synthesis.synthesis_confidence,
                "markdown_content": synthesis_content,
                "metadata": synthesis_result_obj.metadata
            }
            
            logger.info(f"Phase 3 synthesis completed: {synthesis_result['word_count']} words")
            
            if db_report_id:
                await report_service.update_pipeline_progress(db_report_id, "phase3", "completed", 100.0)
                await report_service.store_phase_data(
                    game_id=game_id,
                    phase="phase3",
                    source="synthesizer",
                    data_type="synthesis_result",
                    content=synthesis_result,
                    metadata=synthesis_result_obj.metadata
                )
            if tracker_id:
                await pipeline_tracker.update_phase_progress(tracker_id, 100.0, "Phase 3 synthesis completed")
                await pipeline_tracker.complete_phase(tracker_id, Phase.SYNTHESIS)
            
        except Exception as synthesis_error:
            logger.warning(f"Phase 3 synthesis failed: {str(synthesis_error)}")
            synthesis_result = {
                "status": "failed",
                "error": str(synthesis_error),
                "word_count": 0,
                "markdown_content": f"**Synthesis Error:** {str(synthesis_error)}",
                "confidence": 0.0
            }
            if db_report_id:
                await report_service.update_pipeline_progress(db_report_id, "phase3", "failed", 0.0, str(synthesis_error))
            if tracker_id:
                await pipeline_tracker.update_phase_progress(tracker_id, 100.0, "Phase 3 synthesis failed")
                await pipeline_tracker.complete_phase(tracker_id, Phase.SYNTHESIS)
    else:
        logger.info(f"Skipping Phase 3 (AI success rate {ai_success_rate:.1%} too low)")
        synthesis_result = {
            "status": "skipped",
            "reason": f"Insufficient AI analysis data (success rate: {ai_success_rate:.1%})",
            "word_count": 0,
            "markdown_content": f"**Synthesis Skipped:** Insufficient AI analysis data ({ai_success_rate:.1%} success rate)",
            "confidence": 0.0
        }
        if db_report_id:
            await report_service.update_pipeline_progress(db_report_id, "phase3", "skipped", 0.0, "Insufficient AI data")
        if tracker_id:
            await pipeline_tracker.update_phase_progress(tracker_id, 0.0, "Phase 3 skipped")
            await pipeline_tracker.complete_phase(tracker_id, Phase.SYNTHESIS)
    
    # PHASE 4: Database storage
    logger.info("=== PHASE 4: DATABASE STORAGE ===")
    db_storage_result = {"status": "pending", "report_id": None}
    
    if db_report_id and master_json and synthesis_content:
        try:
            if db_report_id:
                await report_service.update_pipeline_progress(db_report_id, "phase4", "running", 0.0)
            if tracker_id:
                await pipeline_tracker.start_phase(tracker_id, Phase.STORAGE)
                await pipeline_tracker.update_phase_progress(tracker_id, 5.0, "Phase 4 storage started")

            saved_report = await report_service.save_analysis_results(
                db_report_id,
                game_id,
                game_name,
                platform,
                master_json,
                synthesis_content,
            )

            db_storage_result = {
                "status": "success",
                "report_id": saved_report.id,
                "report_url": f"/api/reports/{saved_report.id}",
                "report_created_at": saved_report.created_at.isoformat(),
                "word_count": saved_report.word_count,
                "confidence_score": saved_report.confidence_score
            }
            
            logger.info(f"Phase 4 completed: Report saved to database with ID {saved_report.id}")
            if tracker_id and tracker_id in pipeline_tracker.active_pipelines:
                pipeline_tracker.active_pipelines[tracker_id]["result"] = db_storage_result
                pipeline_tracker.active_pipelines[tracker_id]["db_report_id"] = saved_report.id
            if tracker_id:
                await pipeline_tracker.update_phase_progress(tracker_id, 100.0, "Phase 4 storage completed")
                await pipeline_tracker.complete_phase(tracker_id, Phase.STORAGE)
        except Exception as db_error:
            logger.error(f"Phase 4 database storage failed: {db_error}")
            db_storage_result = {
                "status": "failed",
                "error": str(db_error),
                "report_id": db_report_id
            }
            if db_report_id:
                await report_service.update_pipeline_progress(db_report_id, "phase4", "failed", 0.0, str(db_error))
            if tracker_id:
                await pipeline_tracker.update_phase_progress(tracker_id, 100.0, "Phase 4 storage failed")
                await pipeline_tracker.complete_phase(tracker_id, Phase.STORAGE)
    elif db_report_id:
        db_storage_result = {"status": "skipped", "reason": "No synthesis content available", "report_id": db_report_id}
        await report_service.update_pipeline_progress(db_report_id, "phase4", "skipped", 0.0, "No content available")
        if tracker_id:
            await pipeline_tracker.update_phase_progress(tracker_id, 0.0, "Phase 4 skipped")
            await pipeline_tracker.complete_phase(tracker_id, Phase.STORAGE)
    
    # Calculate overall pipeline metrics
    pipeline_end = asyncio.get_event_loop().time()
    pipeline_duration = round(pipeline_end - pipeline_start, 2)

    if report_service:
        await report_service.close()
    
    try:
        # Determine overall pipeline status
        scraper_success = scraper_result.get("success_rate", 0)
        ai_success = ai_result.get("success_rate", 0)
        synthesis_success = 1.0 if synthesis_result.get("status") in ["success", "completed"] else 0.0
        db_success = 1.0 if db_storage_result.get("status") == "success" else 0.0
        
        if scraper_success >= 0.75 and ai_success >= 0.75 and synthesis_success >= 0.75 and db_success >= 0.75:
            overall_status = "complete_success"
        elif scraper_success > 0 or ai_success > 0 or synthesis_success > 0:
            overall_status = "partial_success" 
        else:
            overall_status = "complete_failure"
        
        pipeline_result = {
        "status": overall_status,
        "game_name": game_name,
        "game_id": game_id,
        "pipeline_duration_seconds": pipeline_duration,
        "phase_1_scraper": scraper_result,
        "phase_2_ai_analysis": ai_result,
        "phase_3_synthesis": synthesis_result,
        "master_json": master_json,
        "final_report": synthesis_content,
        "report_ready": overall_status in ["complete_success", "partial_success"],
        "metadata": {
            "pipeline_version": "1.1.0",  # Updated with Phase 3
            "total_phases_completed": 3 if synthesis_result.get("status") in ["success", "partial_success"] else 2,
            "total_analyses_produced": len(ai_result.get("analyses_completed", [])),
            "total_scrapers_successful": len(scraper_result.get("workers_completed", [])),
            "synthesis_performed": synthesis_result.get("status") in ["success", "partial_success"],
            "word_count": synthesis_result.get("word_count", 0),
            "overall_confidence": (
                scraper_result.get("metadata", {}).get("average_confidence", 0.0) * 0.3 +
                ai_result.get("metadata", {}).get("average_input_confidence", 0.0) * 0.4 +
                synthesis_result.get("confidence", 0.0) * 0.3
            ),
            "pipeline_stages": [
                {
                    "stage": "scraping",
                    "status": scraper_result.get("status"),
                    "success_rate": scraper_result.get("success_rate", 0),
                    "duration": scraper_result.get("metadata", {}).get("run_duration_seconds", 0),
                },
                {
                    "stage": "ai_analysis", 
                    "status": ai_result.get("status"),
                    "success_rate": ai_result.get("success_rate", 0),
                    "duration": ai_result.get("metadata", {}).get("run_duration_seconds", 0),
                },
                {
                    "stage": "synthesis",
                    "status": synthesis_result.get("status", "skipped"),
                    "success_rate": synthesis_success,
                    "word_count": synthesis_result.get("word_count", 0),
                    "duration": 0,  # Synthesis time calculated separately if needed
                },
            ],
        },
        "outputs": {
            "mini_contexts": scraper_result.get("mini_contexts", {}),
            "ai_analyses": ai_result.get("analysis_results", []),
            "master_json": master_json,
            "final_report": synthesis_content,
        },
        "next_phase": 4 if overall_status in ["complete_success", "partial_success"] else "retry",
        "output_schema": "Pipeline-Complete_v1.1.0",
    }
    
        logger.info(
            "Complete pipeline finished for %s: Status=%s, Duration=%.1fs, "
            "Scrapers=%d/%d, AI=%d/%d, Synthesis=%s",
            game_name,
            overall_status,
            pipeline_duration,
            len(scraper_result.get("workers_completed", [])),
            len(scraper_result.get("workers_completed", [])) + len(scraper_result.get("workers_failed", [])),
            len(ai_result.get("analyses_completed", [])),
            len(ai_result.get("analyses_completed", [])) + len(ai_result.get("analyses_failed", [])),
            synthesis_result.get("status", "skipped")
        )
        
        return pipeline_result
    finally:
        if report_service:
            await report_service.close()


async def run_phase_3_synthesis(master_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run just Phase 3 synthesis on existing Master-JSON.
    
    Args:
        master_json: Output from Phase 2 AI analysis
        
    Returns:
        Dict with synthesis result
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        from .synthesizer import synthesizer
        
        syn_engine = synthesizer()
        synthesis_result_obj = await syn_engine.synthesize_master_analysis(master_json)
        
        duration_seconds = round(asyncio.get_event_loop().time() - start_time, 2)
        
        logger.info(f"Phase 3 synthesis completed in {duration_seconds:.2f}s")
        
        return {
            "status": "success",
            "synthesis_result": synthesis_result_obj.model_dump(),
            "synthesis_content": synthesis_result_obj.markdown_content,
            "duration_seconds": duration_seconds,
            "metadata": {
                "word_count": synthesis_result_obj.word_count,
                "confidence": synthesis_result_obj.synthesis.synthesis_confidence,
                "synthesis_version": "1.0.0"
            }
        }
        
    except Exception as e:
        duration_seconds = round(asyncio.get_event_loop().time() - start_time, 2)
        logger.error(f"Phase 3 synthesis failed after {duration_seconds:.2f}s: {str(e)}")
        
        return {
            "status": "failed",
            "error": str(e),
            "duration_seconds": duration_seconds,
            "synthesis_content": f"**Synthesis Error:** {str(e)}"
        }