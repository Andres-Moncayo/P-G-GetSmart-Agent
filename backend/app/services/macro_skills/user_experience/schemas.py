"""
Pydantic schemas for the User Experience Macro-Skill.

Input:  mini_context_user_experience (from master_json_schema.yaml)
Output: UX analysis result consumed by the Phase 4 Synthesizer.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# INPUT SCHEMAS  (mini_context_user_experience)
# =====================================================================

class SemanticSource(BaseModel):
    url: str
    title: str
    snippet: str
    platform: str
    published_at: Optional[str] = None
    author: Optional[str] = None


class SemanticCategory(BaseModel):
    sources: list[SemanticSource] = Field(default_factory=list)
    summary: Optional[str] = None


class SteamReview(BaseModel):
    review: str
    voted_up: bool
    playtime_hours: Optional[float] = None
    language: Optional[str] = None


class SteamReviewsSample(BaseModel):
    positive_count: int = 0
    negative_count: int = 0
    review_score: Optional[float] = None
    sample_reviews: list[SteamReview] = Field(default_factory=list)


class SystemRequirements(BaseModel):
    minimum: Optional[str] = None
    recommended: Optional[str] = None


class UXHardData(BaseModel):
    platforms: list[str] = Field(default_factory=list)
    languages_supported: list[str] = Field(default_factory=list)
    system_requirements: Optional[SystemRequirements] = None
    controller_support: bool = False
    full_controller_support: bool = False
    steam_cloud: bool = False
    steam_achievements: bool = False


class UXSemanticData(BaseModel):
    ui_ux: SemanticCategory = Field(default_factory=SemanticCategory)
    accessibility: SemanticCategory = Field(default_factory=SemanticCategory)
    localization: SemanticCategory = Field(default_factory=SemanticCategory)
    steam_reviews_sample: Optional[SteamReviewsSample] = None


class MiniContextMetadata(BaseModel):
    game_id: str
    game_name: str
    macro_skill: str = "User Experience"
    worker_id: str = "scraper_user_experience"
    generated_at: str
    data_sources: list[str] = Field(default_factory=list)


class UXMiniContext(BaseModel):
    """Input contract — matches master_json_schema.yaml#/definitions/mini_context_user_experience"""
    metadata: MiniContextMetadata
    hard_data: UXHardData
    semantic_data: UXSemanticData
    evidence_count: int = 0
    confidence_score: float = 0.0


# =====================================================================
# OUTPUT SCHEMAS  (UX analysis result)
# =====================================================================

class LLMOutput(BaseModel):
    """Base for all LLM-generated objects. Allows extra fields for forward compatibility."""
    model_config = ConfigDict(extra="allow")


class SkillOutputMetadata(LLMOutput):
    skill_id: str = "user_experience"
    skill_name: str = "User Experience"
    game_id: str
    game_name: str
    generated_at: str
    model_used: str = "gemini-2.5-flash"
    input_evidence_count: Optional[int] = None
    input_confidence_score: Optional[float] = None


class ConfidenceMetrics(LLMOutput):
    overall_score: float
    category_scores: dict[str, float]
    data_quality_notes: list[str] = Field(default_factory=list)


class UXAnalysisOutput(LLMOutput):
    """Output contract — structured intelligence ready for Phase 4 Synthesizer."""
    metadata: SkillOutputMetadata
    analysis: dict[str, Any]
    summary: dict[str, Any]
    confidence: ConfidenceMetrics


# =====================================================================
# API RESPONSE SCHEMAS
# =====================================================================

class TaskResponse(BaseModel):
    """Response returned when analysis is dispatched as a Celery task."""
    job_id: str
    status: str
    skill_id: str = "user_experience"
    game_id: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
