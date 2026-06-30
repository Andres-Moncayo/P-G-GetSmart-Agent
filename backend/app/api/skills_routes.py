"""
FastAPI routes for Macro-Skill execution.

POST /api/skills/user-experience  → runs UX analysis and returns the result
POST /api/skills/tech-systems     → runs Technology & Systems analysis and returns the result
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter

from ..services.macro_skills.user_experience.schemas import UXMiniContext
from ..services.macro_skills.user_experience import UserExperienceSkill
from ..services.macro_skills.tech_system_skill import TechSystemService
from ..services.macro_skills.strategy_market_skill import StrategyMarketService
from ..services.macro_skills.design_art_skill.design_art_service import DesignArtService

logger = logging.getLogger(__name__)

skills_router = APIRouter(prefix="/skills", tags=["Skills"])


@skills_router.post("/user-experience")
async def analyze_user_experience(mini_context: UXMiniContext) -> dict:
    skill = UserExperienceSkill()
    return await skill.analyze(mini_context.model_dump())


@skills_router.post("/tech-systems")
async def analyze_tech_systems(mini_context: Dict[str, Any]) -> dict:
    """Analyze Technology and Systems aspects of a game."""
    skill = TechSystemService()
    return await skill.analyze(mini_context)


@skills_router.post("/strategy-market")
async def analyze_strategy_market(mini_context: Dict[str, Any]) -> dict:
    """Analyze Strategy and Market aspects of a game."""
    skill = StrategyMarketService()
    return await skill.analyze(mini_context)

from ..models.macro_skills.design_art_models import DesignArtInputModel

@skills_router.post("/design-art")
async def analyze_design_art(mini_context: DesignArtInputModel) -> dict:
    """Analyze Design and Art aspects of a game."""
    skill = DesignArtService()
    result = await skill.analyze(mini_context)
    # The analyze method returns a Pydantic model (DesignArtOutputModel), 
    # we need to dump it to a dict for the endpoint response if we declared -> dict,
    # or let FastAPI serialize it if we return it directly.
    return result.model_dump()
