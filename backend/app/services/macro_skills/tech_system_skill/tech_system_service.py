"""
Technology and Systems Macro-Skill Implementation.

Analyzes technical architecture, performance, multiplayer infrastructure,
and platform distribution strategy for games.

Extends BaseMacroSkill for consistent caching, retry logic, and error handling.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict

from ..base_skill import BaseMacroSkill
from .system_prompt import (
    TECH_SYSTEMS_MAIN_PROMPT,
    TECHNOLOGY_PERFORMANCE_PROMPT,
    MULTIPLAYER_SOCIAL_PROMPT,
    PLATFORMS_DISTRIBUTION_PROMPT,
    CROSS_CATEGORY_SYNTHESIS_PROMPT,
    FALLBACK_ANALYSIS_PROMPT
)

logger = logging.getLogger(__name__)


class TechSystemService(BaseMacroSkill):
    """Technology and Systems macro-skill service implementation."""
    
    skill_id: str = "tech_systems"
    skill_name: str = "Technology and Systems"
    
    def __init__(self) -> None:
        super().__init__()
        logger.info("TechSystemService initialized")
    
    # ------------------------------------------------------------------
    # Abstract interface implementation
    # ------------------------------------------------------------------
    
    @property
    def system_prompt(self) -> str:
        """Main system prompt for the Technology and Systems Analyst."""
        return TECH_SYSTEMS_MAIN_PROMPT
    
    def build_user_prompt(self, mini_context: Dict[str, Any]) -> str:
        """Build the comprehensive user prompt from mini-context data."""
        
        # Extract metadata
        metadata = mini_context.get("metadata", {})
        game_name = metadata.get("game_name", "Unknown Game")
        game_id = metadata.get("game_id", "unknown")
        
        # Extract hard data
        hard_data = mini_context.get("hard_data", {})
        game_engines = hard_data.get("game_engines", [])
        platforms = hard_data.get("platforms", [])
        multiplayer_modes = hard_data.get("multiplayer_modes", [])
        pc_requirements = hard_data.get("pc_requirements", {})
        mac_requirements = hard_data.get("mac_requirements", {})
        linux_requirements = hard_data.get("linux_requirements", {})
        current_player_count = hard_data.get("current_player_count", 0)
        
        # Extract semantic data sources
        semantic_data = mini_context.get("semantic_data", {})
        
        #Technology Performance sources
        tech_sources = semantic_data.get("technology_performance", {}).get("sources", [])
        tech_sources_text = self._format_sources_for_prompt(tech_sources)
        
        # Multiplayer Social sources
        multiplayer_sources = semantic_data.get("multiplayer_social", {}).get("sources", [])
        multiplayer_sources_text = self._format_sources_for_prompt(multiplayer_sources)
        
        # Platforms Distribution sources
        platforms_sources = semantic_data.get("platforms_distribution", {}).get("sources", [])
        platforms_sources_text = self._format_sources_for_prompt(platforms_sources)
        
        # Build comprehensive prompt
        prompt_parts = [
            f"GAME: {game_name} (ID: {game_id})",
            f"EVIDENCE COUNT: {mini_context.get('evidence_count', 0)} sources",
            f"INPUT CONFIDENCE: {mini_context.get('confidence_score', 0.0):.2f}",
            "",
            "# HARD DATA",
            f"Game Engines: {', '.join(game_engines) if game_engines else 'None specified'}",
            f"Platforms: {', '.join(platforms) if platforms else 'None specified'}",
            f"Multiplayer Modes: {', '.join(multiplayer_modes) if multiplayer_modes else 'None specified'}",
            f"PC Requirements: {json.dumps(pc_requirements) if pc_requirements else 'None specified'}",
            f"Mac Requirements: {json.dumps(mac_requirements) if mac_requirements else 'None specified'}",
            f"Linux Requirements: {json.dumps(linux_requirements) if linux_requirements else 'None specified'}",
            f"Current Player Count: {current_player_count}",
            "",
            "# ANALYSIS TASKS",
            self._build_technology_analysis_section(hard_data, tech_sources_text),
            "",
            self._build_multiplayer_analysis_section(hard_data, multiplayer_sources_text),
            "",
            self._build_platforms_analysis_section(hard_data, platforms_sources_text),
            "",
            "# SYNTHESIS REQUIREMENTS",
            "After analyzing all 3 categories, provide cross-category synthesis including:",
            "- Technical philosophy unifying all categories",
            "- Standout strengths (3-5 items)",
            "- Critical weaknesses (2-4 items)",
            "- Engineering risks with likelihood/impact/mitigation",
            "- Competitive positioning vs genre standards",
            "- Future readiness assessment",
            "",
            "# OUTPUT REQUIREMENTS",
            "Respond ONLY with valid JSON following the exact schema structure:",
            "{",
            '  "metadata": {...},',
            '  "analysis": {',
            '    "technology_performance": {...},',
            '    "multiplayer_social": {...},',
            '    "platforms_distribution": {...}',
            "  },",
            '  "summary": {...},',
            '  "confidence": {...}',
            "}",
            "",
            "CRITICAL: Use only enum values defined in the schema. Do not invent enum values.",
            "CRITICAL: Cite sources for all technical claims.",
            "CRITICAL: Adjust confidence scores based on evidence availability."
        ]
        
        return "\n".join(prompt_parts)
    
    def _build_technology_analysis_section(self, hard_data: Dict[str, Any], sources_text: str) -> str:
        """Build the Technology/Performance analysis section."""
        return TECHNOLOGY_PERFORMANCE_PROMPT.format(
            game_engines=', '.join(hard_data.get("game_engines", [])),
            platforms=', '.join(hard_data.get("platforms", [])),
            pc_requirements=json.dumps(hard_data.get("pc_requirements", {})),
            mac_requirements=json.dumps(hard_data.get("mac_requirements", {})),
            linux_requirements=json.dumps(hard_data.get("linux_requirements", {})),
            current_player_count=hard_data.get("current_player_count", 0),
            tech_sources_count=sources_text.count("URL:"),
            tech_performance_sources=sources_text
        )
    
    def _build_multiplayer_analysis_section(self, hard_data: Dict[str, Any], sources_text: str) -> str:
        """Build the Multiplayer/Social analysis section."""
        return MULTIPLAYER_SOCIAL_PROMPT.format(
            multiplayer_modes=', '.join(hard_data.get("multiplayer_modes", [])),
            online_coop=hard_data.get("online_coop", False),
            offline_coop=hard_data.get("offline_coop", False),
            lan_coop=hard_data.get("lan_coop", False),
            split_screen=hard_data.get("split_screen", False),
            cross_play=hard_data.get("cross_play", False),
            current_player_count=hard_data.get("current_player_count", 0),
            multiplayer_sources_count=sources_text.count("URL:"),
            multiplayer_social_sources=sources_text
        )
    
    def _build_platforms_analysis_section(self, hard_data: Dict[str, Any], sources_text: str) -> str:
        """Build the Platforms/Distribution analysis section."""
        return PLATFORMS_DISTRIBUTION_PROMPT.format(
            platforms=', '.join(hard_data.get("platforms", [])),
            pc_requirements=json.dumps(hard_data.get("pc_requirements", {})),
            mac_requirements=json.dumps(hard_data.get("mac_requirements", {})),
            linux_requirements=json.dumps(hard_data.get("linux_requirements", {})),
            current_player_count=hard_data.get("current_player_count", 0),
            platforms_sources_count=sources_text.count("URL:"),
            platforms_distribution_sources=sources_text
        )
    
    def _format_sources_for_prompt(self, sources: list) -> str:
        """Format sources for inclusion in prompts."""
        if not sources:
            return "No sources available for this category."
        
        formatted_sources = []
        for i, source in enumerate(sources[:10], 1):  # Limit to 10 sources for prompt length
            url = source.get("url", "No URL")
            title = source.get("title", "No title")
            platform = source.get("platform", "unknown")
            snippet = source.get("snippet", "")[:200]  # Truncate long snippets
            
            formatted_sources.append(
                f"[{i}] {title}\n"
                f"Platform: {platform}\n"
                f"URL: {url}\n"
                f"Snippet: {snippet}\n"
            )
        
        return "\n".join(formatted_sources)
    
    def _fallback_output(self, game_id: str, game_name: str) -> Dict[str, Any]:
        """Generate safe fallback output when analysis fails."""
        
        generated_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        
        return {
            "metadata": {
                "skill_id": self.skill_id,
                "skill_name": self.skill_name,
                "game_id": game_id,
                "game_name": game_name,
                "generated_at": generated_at,
                "model_used": self.model_name
            },
            "analysis": {
                "technology_performance": {
                    "category_id": "technology_performance",
                    "category_name": "Technology/Performance", 
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                    "engine_architecture": {
                        "engine_type": "other",
                        "engine_name": "Unknown",
                        "custom_modifications": "Not analyzed",
                        "known_limitations": "Analysis failed"
                    },
                    "rendering_pipeline": {
                        "graphics_api": "multiple",
                        "ray_tracing": False,
                        "dlss_fsr": "none",
                        "resolution_scaling": "Not analyzed",
                        "notable_features": "Analysis failed"
                    },
                    "performance_profile": {
                        "pc_benchmarks": "Not analyzed",
                        "console_performance": "Not analyzed",
                        "stability": "unstable",
                        "load_times": "excessive"
                    },
                    "optimization_quality": {
                        "cpu_utilization": "Not analyzed",
                        "gpu_utilization": "Not analyzed", 
                        "asset_streaming": "Not analyzed",
                        "lod_system": "Not analyzed"
                    },
                    "technical_debt": {
                        "debt_level": "significant",
                        "known_issues": ["System error prevented analysis"],
                        "patch_history": "Not analyzed",
                        "engine_limitations": "Unknown due to analysis failure"
                    },
                    "sources_cited": []
                },
                "multiplayer_social": {
                    "category_id": "multiplayer_social",
                    "category_name": "Multiplayer/Social",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                    "netcode_architecture": {
                        "netcode_type": "listen_server",
                        "implementation_quality": "Not analyzed",
                        "latency_handling": "Not analyzed",
                        "host_advantage": "Not analyzed"
                    },
                    "latency_compensation": {
                        "input_lag": "unplayable",
                        "hit_registration": "Not analyzed",
                        "desync_handling": "Not analyzed"
                    },
                    "session_management": {
                        "matchmaking": "broken",
                        "lobby_system": "Not analyzed",
                        "session_stability": "frequent_drops",
                        "session_notes": "Analysis failed"
                    },
                    "social_features": {
                        "friends_integration": "none",
                        "voice_chat": "none",
                        "messaging": "none",
                        "community_tools": "Not analyzed",
                        "notes": "Analysis failed"
                    },
                    "anti_cheat": {
                        "anti_cheat_solution": "none",
                        "solution_name": "Not analyzed",
                        "effectiveness": "Not analyzed",
                        "controversies": "Not analyzed",
                        "false_positives": "Not analyzed"
                    },
                    "backend_scalability": {
                        "server_capacity": "Not analyzed",
                        "matchmaking_infrastructure": "Not analyzed",
                        "maintenance_windows": "Not analyzed",
                        "ddos_resilience": "Not analyzed"
                    },
                    "sources_cited": []
                },
                "platforms_distribution": {
                    "category_id": "platforms_distribution",
                    "category_name": "Platforms/Distribution",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                    "platform_parity": {
                        "parity_level": "fragmented",
                        "feature_equivalence": "Not analyzed",
                        "version_alignment": "Not analyzed",
                        "notes": "Analysis failed"
                    },
                    "port_quality": {
                        "pc": {
                            "resolution": "Not analyzed",
                            "fps_target": "Not analyzed",
                            "optimization": "Not analyzed",
                            "rating": "unplayable"
                        },
                        "ps5": {
                            "resolution": "Not analyzed",
                            "fps_target": "Not analyzed", 
                            "optimization": "Not analyzed",
                            "rating": "unplayable"
                        },
                        "xbox_series_x": {
                            "resolution": "Not analyzed",
                            "fps_target": "Not analyzed",
                            "optimization": "Not analyzed",
                            "rating": "unplayable"
                        },
                        "ps4_xbox_one": {
                            "resolution": "Not analyzed",
                            "fps_target": "Not analyzed",
                            "optimization": "Not analyzed",
                            "rating": "unplayable"
                        }
                    },
                    "distribution_strategy": {
                        "stores": [],
                        "exclusivity": "Not analyzed",
                        "subscription_services": "Not analyzed",
                        "retail": "Not analyzed",
                        "notes": "Analysis failed"
                    },
                    "hardware_accessibility": {
                        "minimum_specs": "Not analyzed",
                        "recommended_specs": "Not analyzed",
                        "scalability": "demanding",
                        "storage_required": "Not analyzed",
                        "ssd_recommended": False,
                        "notes": "Analysis failed"
                    },
                    "cross_platform_features": {
                        "save_sync": "not_supported",
                        "cross_play": "not_supported",
                        "cross_progression": "not_supported",
                        "notes": "Analysis failed"
                    },
                    "patch_cadence": {
                        "update_frequency": "rare",
                        "major_patches": "Not analyzed",
                        "hotfix_speed": "Not analyzed",
                        "certification_delays": "Not analyzed",
                        "rollback_capability": "Not analyzed"
                    },
                    "sources_cited": []
                }
            },
            "summary": {
                "technical_philosophy": "Analysis could not be completed due to system error.",
                "standout_strengths": [],
                "critical_weaknesses": ["System error prevented analysis"],
                "engineering_risks": [
                    {
                        "risk": "System error in analysis pipeline",
                        "category": "technology_performance", 
                        "likelihood": "high",
                        "impact": "critical",
                        "mitigation": "Investigate error logs and retry analysis",
                        "timeline_concern": "Immediate attention required"
                    }
                ],
                "competitive_positioning": {
                    "genre_benchmark": "Analysis failed",
                    "unique_selling_points": [],
                    "comparable_titles": []
                },
                "future_readiness": {
                    "dlc_support": "unknown",
                    "live_service_viability": "unknown",
                    "sequel_reusability": "unknown", 
                    "technology_obsolescence_risk": "unknown",
                    "recommended_upgrades": []
                }
            },
            "confidence": {
                "overall_score": 0.0,
                "category_scores": {
                    "technology_performance": 0.0,
                    "multiplayer_social": 0.0,
                    "platforms_distribution": 0.0
                },
                "data_quality_notes": [
                    "System error prevented analysis of all categories",
                    "No confidence in generated technical assessments"
                ]
            }
        }