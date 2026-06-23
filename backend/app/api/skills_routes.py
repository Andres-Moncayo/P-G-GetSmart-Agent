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