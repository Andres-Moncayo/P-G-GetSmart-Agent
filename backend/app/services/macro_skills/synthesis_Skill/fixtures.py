"""Sample fixture data for synthesis demo and tests."""

from __future__ import annotations

from typing import Any, Dict

from app.models.synthesis.synthesis_models import MacroOutputs, SynthesisInput

GAME_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
GAME_NAME = "Elden Ring"


def _design_art_output() -> Dict[str, Any]:
    return {
        "metadata": {
            "skill_id": "design_art",
            "game_id": GAME_ID,
            "game_name": GAME_NAME,
        },
        "analysis": {
            "gameplay": {
                "category_id": "gameplay",
                "category_name": "Gameplay Mechanics",
                "overview": "Elden Ring evolves FromSoftware combat into an open-world structure with mounted combat and Spirit Ashes.",
                "sources_cited": [
                    {
                        "url": "https://www.reddit.com/r/Eldenring/",
                        "platform": "reddit",
                        "claim": "Combat depth is consistently praised across community reviews.",
                        "confidence": 0.9,
                    }
                ],
                "player_feedback": {
                    "strengths": ["Combat depth rewards mastery", "Boss design is exceptional"],
                    "weaknesses": ["Late-game damage scaling frustrates some players"],
                },
            },
            "level_design": {
                "category_id": "level_design",
                "overview": "Open-world structure allows non-linear exploration with soft difficulty gating.",
                "sources_cited": [],
            },
            "narrative": {
                "category_id": "narrative",
                "overview": "Environmental storytelling and cryptic lore maintain FromSoftware's signature narrative style.",
                "sources_cited": [],
            },
            "art_direction": {
                "category_id": "art_direction",
                "overview": "Distinctive dark fantasy aesthetic with strong art direction across biomes.",
                "sources_cited": [],
            },
            "sound_design": {
                "category_id": "sound_design",
                "overview": "Music and SFX reinforce tension and discovery throughout the open world.",
                "sources_cited": [],
            },
        },
        "summary": {
            "design_philosophy": "Difficulty as discovery with open-world player agency.",
            "standout_strengths": ["Combat systems", "World design"],
            "critical_weaknesses": ["Reused boss encounters in late game"],
        },
        "confidence": {
            "overall_score": 0.85,
            "category_scores": {
                "gameplay": 0.9,
                "level_design": 0.86,
                "narrative": 0.8,
                "art_direction": 0.85,
                "sound_design": 0.82,
            },
        },
    }


def _ux_output() -> Dict[str, Any]:
    return {
        "metadata": {"skill_id": "user_experience", "game_id": GAME_ID, "game_name": GAME_NAME},
        "analysis": {
            "ui_ux": {
                "category_id": "ui_ux",
                "overview": "Menus are functional but dense; HUD clarity is strong once learned.",
                "sources_cited": [],
            },
            "accessibility": {
                "category_id": "accessibility",
                "overview": "Limited accessibility options and no difficulty presets remain a major barrier.",
                "sources_cited": [
                    {
                        "url": "https://caniplaythat.com/",
                        "platform": "web",
                        "claim": "No difficulty options limit audience reach.",
                        "confidence": 0.85,
                    }
                ],
            },
            "localization": {
                "category_id": "localization",
                "overview": "Broad language support with generally solid translation quality.",
                "sources_cited": [],
            },
        },
        "summary": {
            "ux_philosophy": "Minimal hand-holding reinforces discovery but increases onboarding friction.",
            "critical_weaknesses": ["Accessibility gaps", "Camera issues in tight spaces"],
        },
        "confidence": {"overall_score": 0.79, "category_scores": {"ui_ux": 0.79, "accessibility": 0.72, "localization": 0.8}},
    }


def _tech_output() -> Dict[str, Any]:
    return {
        "metadata": {"skill_id": "technology_systems", "game_id": GAME_ID, "game_name": GAME_NAME},
        "analysis": {
            "technology_performance": {
                "category_id": "technology_performance",
                "overview": "Proprietary engine is efficient but shows age compared to UE5 competitors.",
                "sources_cited": [],
            },
            "multiplayer_social": {
                "category_id": "multiplayer_social",
                "overview": "Asynchronous multiplayer co-op via summons; limited social infrastructure.",
                "sources_cited": [],
            },
            "platforms_distribution": {
                "category_id": "platforms_distribution",
                "overview": "Multi-platform release with strong PC and console performance profiles.",
                "sources_cited": [],
            },
        },
        "summary": {"technical_posture": "Conservative but reliable technical execution."},
        "confidence": {
            "overall_score": 0.81,
            "category_scores": {
                "technology_performance": 0.81,
                "multiplayer_social": 0.74,
                "platforms_distribution": 0.82,
            },
        },
    }


def _strategy_output() -> Dict[str, Any]:
    return {
        "metadata": {"skill_id": "strategy_market", "game_id": GAME_ID, "game_name": GAME_NAME},
        "analysis": {
            "audience": {
                "category_id": "audience",
                "overview": "Core Souls audience expanded by open-world appeal; difficulty excludes casual players.",
                "sources_cited": [],
            },
            "business_model": {
                "category_id": "business_model",
                "overview": "Premium plus DLC model generated extraordinary revenue without live-service mechanics.",
                "sources_cited": [],
            },
            "retention_live_ops": {
                "category_id": "retention_live_ops",
                "overview": "Retention driven by content depth rather than ongoing live ops.",
                "sources_cited": [],
            },
            "production_business": {
                "category_id": "production_business",
                "overview": "FromSoftware's efficient engine workflow supports rapid iteration.",
                "sources_cited": [],
            },
            "marketing": {
                "category_id": "marketing",
                "overview": "Collaboration with George R.R. Martin amplified pre-launch awareness.",
                "sources_cited": [],
            },
            "cultural_impact": {
                "category_id": "cultural_impact",
                "overview": "Elevated FromSoftware to must-play developer status with mainstream recognition.",
                "sources_cited": [],
            },
        },
        "summary": {
            "market_position": "Over 25M units sold; one of the best-selling games of the 2020s.",
            "critical_weaknesses": ["No live service infrastructure", "Difficulty barrier limits TAM"],
        },
        "confidence": {
            "overall_score": 0.82,
            "category_scores": {
                "audience": 0.8,
                "business_model": 0.85,
                "retention_live_ops": 0.77,
                "production_business": 0.75,
                "marketing": 0.87,
                "cultural_impact": 0.9,
            },
        },
    }


def build_demo_synthesis_input() -> SynthesisInput:
    return SynthesisInput(
        metadata={
            "game_id": GAME_ID,
            "game_name": GAME_NAME,
            "pipeline_version": "3.0.0",
            "synthesis_job_id": "syn-demo-001",
            "macro_skills_completed": [
                "design_art",
                "user_experience",
                "technology_systems",
                "strategy_market",
            ],
        },
        master_json={
            "metadata": {"game_id": GAME_ID, "game_name": GAME_NAME, "pipeline_version": "3.0.0"},
            "evidence_count": 142,
            "confidence_score": 0.82,
            "hard_data": {"rawg": {}, "steam": {}},
            "semantic_data": {},
        },
        macro_outputs=MacroOutputs(
            design_art=_design_art_output(),
            user_experience=_ux_output(),
            technology_systems=_tech_output(),
            strategy_market=_strategy_output(),
        ),
    )
