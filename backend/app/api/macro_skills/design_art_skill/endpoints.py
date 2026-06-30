"""
Design and Art Macro Skill - API Endpoints

This module provides the FastAPI endpoints for the Design and Art macro-skill
analysis service.

Routes:
- POST /: Analyze design and art mini-context and return structured intelligence

Author: GetSmart Team
"""

from fastapi import APIRouter

from ....models.macro_skills.design_art_models import DesignArtInputModel, DesignArtOutputModel
from ....services.macro_skills.design_art_skill.design_art_service import DesignArtService
from ....services.macro_skills.design_art_skill.system_prompt import (
    GAMEPLAY_ANALYSIS_PROMPT,
    LEVEL_DESIGN_ANALYSIS_PROMPT,
    NARRATIVE_ANALYSIS_PROMPT,
    ART_DIRECTION_ANALYSIS_PROMPT,
    SOUND_DESIGN_ANALYSIS_PROMPT,
    SUMMARY_ANALYSIS_PROMPT
)

router = APIRouter()
service = DesignArtService()


@router.post('/', response_model=DesignArtOutputModel, status_code=200)
async def analyze_design_art(input_data: DesignArtInputModel):
    """
    Analyze design and art mini-context and return structured intelligence.
    
    This endpoint processes game data through 5 analysis categories:
    - Gameplay Mechanics
    - Level Design
    - Narrative
    - Art Direction
    - Sound Design
    
    Returns a comprehensive analysis with confidence scores and insights.
    
    Args:
        input_data: Game context including hard data and semantic sources
        
    Returns:
        DesignArtOutputModel: Complete analysis with metadata, insights, and confidence
    """
    return await service.analyze(input_data)
