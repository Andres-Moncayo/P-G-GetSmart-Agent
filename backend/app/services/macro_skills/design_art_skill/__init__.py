"""
Design and Art Macro Skill Module

This package contains the complete implementation of the Design and Art macro-skill
for the GetSmart Game Intelligence Platform.

Components:
- DesignArtService: Main analysis service with LLM integration
- system_prompt: Centralized prompts for all analysis categories
- endpoints: FastAPI route handlers

Author: GetSmart Team
Purpose: Professional design and art analysis for video games
"""

from .design_art_service import DesignArtService

__all__ = ['DesignArtService']
