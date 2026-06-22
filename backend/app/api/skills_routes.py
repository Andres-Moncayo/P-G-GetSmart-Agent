"""
FastAPI routes for Macro-Skill execution.

POST /api/skills/user-experience  → runs UX analysis and returns the result
"""

import logging

from fastapi import APIRouter

from ..services.macro_skills.user_experience.schemas import UXMiniContext
from ..services.macro_skills.user_experience import UserExperienceSkill

logger = logging.getLogger(__name__)

skills_router = APIRouter(prefix="/skills", tags=["Skills"])


@skills_router.post("/user-experience")
async def analyze_user_experience(mini_context: UXMiniContext) -> dict:
    skill = UserExperienceSkill()
    return await skill.analyze(mini_context.model_dump())
