"""
Phase 2 AI Analysis Orchestrator.

Takes scraper Mini-Contexts and runs 4 parallel AI analyses for macro-skill insights.

This is the core of Phase 2 - connects completed scraper data to AI analysis,
processing Mini-Contexts through their respective AI workers to generate
high-quality game intelligence insights.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

# Only import the models we know exist
from ....models.macro_skills.design_art_models import DesignArtInputModel, DesignArtOutputModel

from ....services.macro_skills.design_art_skill.design_art_service import DesignArtService
from ....services.macro_skills.base_skill import BaseMacroSkill

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Orchestrates AI analysis across all 4 macro-skills using scraper outputs.
    
    Takes Mini-Contexts from Phase 1 scrapers and runs them through AI workers
    to generate high-quality game intelligence analysis.
    """
    
    def __init__(self):
        """Initialize AI service workers - using real and mock implementations."""
        self.design_art_service = DesignArtService()
        
        # For Phase 2, we'll use mock implementations for other skills
        # until their models are properly defined
        logger.info("AI Orchestrator initialized with Design & Art real service + 3 mock services")
    
    def _convert_to_design_art_input(self, mini_context: Dict[str, Any], game_name: str = "Unknown", game_id: str = "unknown") -> DesignArtInputModel:
        """Convert scraper Mini-Context to Design & Art AI input model."""
        metadata = mini_context.get("metadata", {})
        
        return DesignArtInputModel(
            metadata={
                "game_id": game_id,
                "game_name": game_name,
                "macro_skill": "Design and Art",
                "worker_id": "scraper_design_art",
                "data_sources": metadata.get("data_sources", []),
                "generated_at": metadata.get("generated_at", datetime.utcnow().isoformat() + "Z"),
                "scraper_version": metadata.get("scraper_version", "1.0.0"),
                "confidence_score": metadata.get("confidence_score", 0.5),
                "evidence_count": metadata.get("evidence_count", 0),
            },
            hard_data=mini_context.get("hard_data", {}),
            semantic_data=mini_context.get("semantic_data", {}),
            evidence_count=metadata.get("evidence_count", 0),
            confidence_score=metadata.get("confidence_score", 0.5)
        )
    
    async def analyze_design_art(self, mini_context: Dict[str, Any], game_name: str, game_id: str) -> Dict[str, Any]:
        """Run Design & Art AI analysis."""
        try:
            input_data = self._convert_to_design_art_input(mini_context, game_name, game_id)
            result = await self.design_art_service.analyze(input_data)
            
            return {
                "macro_skill": "design_art",
                "status": "completed",
                "analysis": result.dict(),
                "metadata": {
                    "ai_version": "1.0.0",
                    "run_timestamp": result.metadata.generated_at,
                    "confidence_score": result.confidence.overall_score if hasattr(result, 'confidence') else 0.7,
                }
            }
        except Exception as exc:
            logger.error("Design & Art AI analysis failed: %s", exc)
            return {
                "macro_skill": "design_art",
                "status": "failed",
                "error": str(exc),
                "metadata": {"ai_version": "1.0.0"}
            }
    
    async def analyze_user_experience(self, mini_context: Dict[str, Any], game_name: str, game_id: str) -> Dict[str, Any]:
        """Run User Experience AI analysis (mock implementation for Phase 2)."""
        try:
            # Mock implementation - will be replaced with real service when models are ready
            metadata = mini_context.get("metadata", {})
            hard_data = mini_context.get("hard_data", {})
            semantic_data = mini_context.get("semantic_data", {})
            
            # Extract relevant UX information from hard_data
            system_requirements = hard_data.get("system_requirements", {})
            platforms = hard_data.get("platforms", [])
            
            # Build mock analysis based on available data
            mock_analysis = {
                "metadata": {
                    "skill_id": "user_experience",
                    "skill_name": "User Experience",
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "game_name": game_name,
                    "game_id": game_id,
                    "confidence_score": 0.6,  # Mock confidence
                },
                "ui_ux_analysis": {
                    "platform_support": {
                        "platforms": platforms,
                        "controller_support": self._extract_controller_support(hard_data),
                        "keyboard_support": "PC" in platforms,
                    },
                    "interface_complexity": "standard",  # Mock assessment
                    "accessibility_features": self._count_accessibility_features(hard_data),
                },
                "accessibility_analysis": {
                    "color_blind_support": "unknown",
                    "subtitle_options": "standard",
                    "difficulty_options": self._extract_difficulty_options(hard_data),
                    "remappable_controls": "unknown",
                },
                "localization_analysis": {
                    "languages_supported": self._extract_languages(hard_data),
                    "cultural_adaptation": "minimal",  # Mock
                    "region_specific_features": [],
                },
                "confidence": {
                    "overall_confidence": metadata.get("confidence_score", 0.6),
                    "evidence_completeness": "partial",
                }
            }
            
            return {
                "macro_skill": "user_experience",
                "status": "completed",
                "analysis": mock_analysis,
                "metadata": {
                    "ai_version": "1.0.0-mock",
                    "run_timestamp": datetime.utcnow().isoformat() + "Z",
                    "confidence_score": metadata.get("confidence_score", 0.6),
                    "note": "Mock implementation for Phase 2"
                }
            }
        except Exception as exc:
            logger.error("User Experience AI analysis failed: %s", exc)
            return {
                "macro_skill": "user_experience",
                "status": "failed",
                "error": str(exc),
                "metadata": {"ai_version": "1.0.0-mock"}
            }
    
    async def analyze_technology_systems(self, mini_context: Dict[str, Any], game_name: str, game_id: str) -> Dict[str, Any]:
        """Run Technology Systems AI analysis (mock implementation for Phase 2)."""
        try:
            # Mock implementation 
            metadata = mini_context.get("metadata", {})
            hard_data = mini_context.get("hard_data", {})
            
            # Extract technical information
            system_requirements = hard_data.get("system_requirements", {})
            platforms = hard_data.get("platforms", [])
            
            mock_analysis = {
                "metadata": {
                    "skill_id": "technology_systems",
                    "skill_name": "Technology & Systems", 
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "game_name": game_name,
                    "game_id": game_id,
                    "confidence_score": 0.65,
                },
                "technical_analysis": {
                    "engine_info": self._extract_engine_info(hard_data),
                    "graphics_technology": self._assess_graphics_tech(hard_data),
                    "performance_requirements": system_requirements,
                    "platform_optimization": platforms,
                    "network_infrastructure": self._assess_network_infrastructure(hard_data),
                },
                "system_requirements_analysis": {
                    "minimum_specs": system_requirements.get("minimum", {}),
                    "recommended_specs": system_requirements.get("recommended", {}),
                    "accessibility": "moderate",  # Mock assessment
                    "scalability": "limited",
                },
                "performance_analysis": {
                    "fps_expectations": "60fps",  # Mock
                    "loading_times": "standard",
                    "stability": "good",
                    "optimization_quality": "adequate",
                },
                "confidence": {
                    "overall_confidence": metadata.get("confidence_score", 0.65),
                    "technical_depth": "moderate",
                }
            }
            
            return {
                "macro_skill": "technology_systems",
                "status": "completed",
                "analysis": mock_analysis,
                "metadata": {
                    "ai_version": "1.0.0-mock",
                    "run_timestamp": datetime.utcnow().isoformat() + "Z",
                    "confidence_score": metadata.get("confidence_score", 0.65),
                    "note": "Mock implementation for Phase 2"
                }
            }
        except Exception as exc:
            logger.error("Technology Systems AI analysis failed: %s", exc)
            return {
                "macro_skill": "technology_systems",
                "status": "failed",
                "error": str(exc),
                "metadata": {"ai_version": "1.0.0-mock"}
            }
    
    async def analyze_strategy_market(self, mini_context: Dict[str, Any], game_name: str, game_id: str) -> Dict[str, Any]:
        """Run Strategy & Market AI analysis (mock implementation for Phase 2)."""
        try:
            # Mock implementation
            metadata = mini_context.get("metadata", {})
            hard_data = mini_context.get("hard_data", {})
            semantic_data = mini_context.get("semantic_data", {})
            
            mock_analysis = {
                "metadata": {
                    "skill_id": "strategy_market",
                    "skill_name": "Strategy & Market",
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "game_name": game_name,
                    "game_id": game_id,
                    "confidence_score": 0.7,
                },
                "market_analysis": {
                    "target_demographics": self._infer_demographics(hard_data),
                    "market_positioning": self._assess_market_position(hard_data),
                    "competitive_landscape": "moderate",  # Mock
                    "market_opportunities": [],
                },
                "monetization_analysis": {
                    "monetization_model": self._extract_monetization_model(hard_data),
                    "price_point": self._extract_price_point(hard_data),
                    "revenue_streams": [],
                    "player_spending_patterns": "unknown",
                },
                "business_metrics": {
                    "player_sentiment_score": 0.7,  # Mock
                    "engagement_metrics": "moderate",
                    "retention_factors": [],
                    "growth_potential": "steady",
                },
                "confidence": {
                    "overall_confidence": metadata.get("confidence_score", 0.7),
                    "market_data_availability": "limited",
                }
            }
            
            return {
                "macro_skill": "strategy_market",
                "status": "completed",
                "analysis": mock_analysis,
                "metadata": {
                    "ai_version": "1.0.0-mock",
                    "run_timestamp": datetime.utcnow().isoformat() + "Z",
                    "confidence_score": metadata.get("confidence_score", 0.7),
                    "note": "Mock implementation for Phase 2"
                }
            }
        except Exception as exc:
            logger.error("Strategy & Market AI analysis failed: %s", exc)
            return {
                "macro_skill": "strategy_market",
                "status": "failed",
                "error": str(exc),
                "metadata": {"ai_version": "1.0.0-mock"}
            }
    
    # Helper methods for extracting data from scraper outputs
    def _extract_controller_support(self, hard_data: Dict[str, Any]) -> str:
        """Extract controller support info from hard data."""
        platforms = hard_data.get("platforms", [])
        if any(isinstance(platform, str) and console in platform.lower() for platform in platforms for console in ["playstation", "xbox", "nintendo"]):
            return "full"
        elif any(isinstance(platform, str) and "pc" in platform.lower() for platform in platforms):
            return "partial"
        return "minimal"
    
    def _count_accessibility_features(self, hard_data: Dict[str, Any]) -> int:
        """Count accessibility features."""
        # Mock count based on typical features
        return 3
    
    def _extract_difficulty_options(self, hard_data: Dict[str, Any]) -> str:
        """Extract difficulty options."""
        # Mock assessment
        return "standard"
    
    def _extract_languages(self, hard_data: Dict[str, Any]) -> list[str]:
        """Extract supported languages."""
        # Mock language list
        return ["English", "Spanish", "French", "German"]
    
    def _extract_engine_info(self, hard_data: Dict[str, Any]) -> str:
        """Extract engine information."""
        return hard_data.get("engine", "Unknown")
    
    def _assess_graphics_tech(self, hard_data: Dict[str, Any]) -> str:
        """Assess graphics technology."""
        return "standard"  # Mock assessment
    
    def _assess_network_infrastructure(self, hard_data: Dict[str, Any]) -> str:
        """Assess network infrastructure."""
        # Mock assessment based on game modes
        game_modes = hard_data.get("game_modes", [])
        if any(multiplayer in str(game_modes).lower() for multiplayer in ["multiplayer", "online", "coop"]):
            return "multiplayer_supported"
        return "single_player"
    
    def _infer_demographics(self, hard_data: Dict[str, Any]) -> dict[str, str]:
        """Infer target demographics."""
        genres = hard_data.get("genres", [])
        if "RPG" in str(genres):
            return {"primary": "RPG fans", "secondary": "Fantasy enthusiasts"}
        elif "Action" in str(genres):
            return {"primary": "Action gamers", "secondary": "Console players"}
        return {"primary": "General gamers", "secondary": "Casual players"}
    
    def _assess_market_position(self, hard_data: Dict[str, Any]) -> str:
        """Assess market positioning."""
        return "mid_tier"  # Mock assessment
    
    def _extract_monetization_model(self, hard_data: Dict[str, Any]) -> str:
        """Extract monetization model."""
        # Mock assessment
        return "premium"
    
    def _extract_price_point(self, hard_data: Dict[str, Any]) -> str:
        """Extract price point."""
        # Mock assessment
        return "$59.99"
    
    async def run_ai_analysis(self, mini_contexts: Dict[str, Dict[str, Any]], game_name: str = "Unknown", game_id: str = "unknown") -> Dict[str, Any]:
        """
        Execute all 4 AI analyses in parallel.
        
        Args:
            mini_contexts: Dictionary with Mini-Contexts from each scraper
            game_name: Game name for metadata
            game_id: Game ID for metadata
        
        Returns:
            Dictionary with completed analyses, failures, and Master-JSON
        """
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting Phase 2 AI analysis for game: %s", game_name)
        
        # Run all 4 AI analyses in parallel
        analysis_results = await asyncio.gather(
            self.analyze_design_art(mini_contexts.get("design_art", {}), game_name, game_id),
            self.analyze_user_experience(mini_contexts.get("user_experience", {}), game_name, game_id),
            self.analyze_technology_systems(mini_contexts.get("technology_systems", {}), game_name, game_id),
            self.analyze_strategy_market(mini_contexts.get("strategy_market", {}), game_name, game_id),
            return_exceptions=True,
        )
        
        # Process results
        analyses_completed = []
        analyses_failed = []
        successful_analyses = {}
        
        macro_skills = ["design_art", "user_experience", "technology_systems", "strategy_market"]
        
        for macro_skill, result in zip(macro_skills, analysis_results):
            if isinstance(result, Exception):
                analyses_failed.append(macro_skill)
                logger.error("AI analysis %s failed with uncaught exception: %s", macro_skill, result)
                continue
            
            if result.get("status") == "completed":
                analyses_completed.append(macro_skill)
                successful_analyses[macro_skill] = result.get("analysis", {})
                logger.info("AI analysis %s completed successfully", macro_skill)
            else:
                analyses_failed.append(macro_skill)
                error_msg = result.get("error", "Unknown error")
                logger.error("AI analysis %s failed: %s", macro_skill, error_msg)
        
        # Calculate timing and success metrics
        end_time = asyncio.get_event_loop().time()
        duration_seconds = round(end_time - start_time, 2)
        
        success_rate = len(analyses_completed) / len(macro_skills)
        overall_status = "success" if success_rate >= 0.75 else "partial" if success_rate > 0 else "failure"
        
        # Assemble Master-JSON for Phase 3
        master_json = {
            "game_info": {
                "game_name": game_name,
                "game_id": game_id,
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                "pipeline_phase": 2,
                "success_rate": success_rate,
            },
            "macro_skill_analyses": successful_analyses,
            "analysis_metadata": {
                "analyses_completed": analyses_completed,
                "analyses_failed": analyses_failed,
                "total_analyses": len(macro_skills),
                "average_confidence": (
                    sum(
                        result.get("metadata", {}).get("confidence_score", 0.7)
                        for result in analysis_results
                        if not isinstance(result, Exception) and result.get("status") == "completed"
                    ) / len(analyses_completed)
                    if analyses_completed else 0.0
                ),
                "orchestrator_version": "1.0.0",
                "run_duration_seconds": duration_seconds,
            }
        }
        
        result = {
            "status": overall_status,
            "phase": 2,  # Phase 2: AI Analysis
            "analyses_completed": analyses_completed,
            "analyses_failed": analyses_failed,
            "success_rate": success_rate,
            "analysis_results": successful_analyses,
            "master_json": master_json,
            "metadata": {
                "orchestrator_version": "1.0.0",
                "run_duration_seconds": duration_seconds,
                "total_input_evidence": sum(
                    ctx.get("metadata", {}).get("evidence_count", 0)
                    for ctx in mini_contexts.values()
                ),
                "average_input_confidence": (
                    sum(
                        ctx.get("metadata", {}).get("confidence_score", 0.0)
                        for ctx in mini_contexts.values()
                    ) / len(mini_contexts)
                    if mini_contexts else 0.0
                ),
                "note": "Phase 2: 1 real AI (Design & Art) + 3 mock implementations"
            },
            "output_schema": "Master-JSON_v2.0.0",
        }
        
        logger.info(
            "Phase 2 AI analysis completed: %d/%d analyses successful (%.1fs)",
            len(analyses_completed),
            len(macro_skills),
            duration_seconds,
        )
        
        return result


# Convenience function for standalone operation
async def run_ai_analysis_pipeline(mini_contexts: Dict[str, Dict[str, Any]], game_name: str = "Unknown", game_id: str = "unknown") -> Dict[str, Any]:
    """
    Main entry point for Phase 2.  Runs all 4 macro-skill workers via Gemini in
    parallel (run_parallel_ai_workers) and adapts the result to the format the
    main orchestrator expects.
    """
    from .ai_workers import run_parallel_ai_workers

    start_time = asyncio.get_event_loop().time()

    workers_result = await run_parallel_ai_workers(
        design_art_context=mini_contexts.get("design_art", {}),
        user_experience_context=mini_contexts.get("user_experience", {}),
        technology_systems_context=mini_contexts.get("technology_systems", {}),
        strategy_market_context=mini_contexts.get("strategy_market", {}),
    )

    completed_workers: list[str] = workers_result.get("completed_workers", [])
    failed_workers: list[str] = workers_result.get("failed_workers", [])
    analyses_raw: Dict[str, Any] = workers_result.get("analyses", {})

    # Build the successful_analyses dict expected by the enrichment step
    successful_analyses: Dict[str, Any] = {}
    for skill_key, entry in analyses_raw.items():
        if entry.get("status") == "completed":
            successful_analyses[skill_key] = entry.get("analysis", {})

    # Average confidence across completed skills
    all_confidences = [
        v.get("confidence_score", 0.0)
        for v in successful_analyses.values()
        if isinstance(v, dict) and v.get("confidence_score") is not None
    ]
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

    macro_skills = ["design_art", "user_experience", "technology_systems", "strategy_market"]
    success_rate = len(completed_workers) / len(macro_skills)
    overall_status = "success" if success_rate >= 0.75 else "partial" if success_rate > 0 else "failure"

    duration_seconds = round(asyncio.get_event_loop().time() - start_time, 2)

    master_json = {
        "game_info": {
            "game_name": game_name,
            "game_id": game_id,
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "pipeline_phase": 2,
            "success_rate": success_rate,
        },
        "macro_skill_analyses": successful_analyses,
        "analysis_metadata": {
            "analyses_completed": completed_workers,
            "analyses_failed": failed_workers,
            "total_analyses": len(macro_skills),
            "average_confidence": avg_confidence,
            "orchestrator_version": "2.0.0",
            "run_duration_seconds": duration_seconds,
        },
    }

    logger.info(
        "Phase 2 AI analysis completed via Gemini workers: %d/%d successful (%.1fs)",
        len(completed_workers),
        len(macro_skills),
        duration_seconds,
    )

    return {
        "status": overall_status,
        "phase": 2,
        "analyses_completed": completed_workers,
        "analyses_failed": failed_workers,
        "success_rate": success_rate,
        "analysis_results": successful_analyses,
        "master_json": master_json,
        "metadata": {
            "orchestrator_version": "2.0.0",
            "run_duration_seconds": duration_seconds,
            "total_input_evidence": sum(
                ctx.get("metadata", {}).get("evidence_count", 0)
                for ctx in mini_contexts.values()
            ),
        },
        "output_schema": "Master-JSON_v2.0.0",
    }
