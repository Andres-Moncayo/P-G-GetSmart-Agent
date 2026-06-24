"""
Pydantic schemas for the Strategy and Market Macro-Skill.

Input:  mini_context_strategy_market (from master_json_schema.yaml)
Output: Strategy & Market analysis result consumed by the Phase 4 Synthesizer.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# INPUT SCHEMAS  (mini_context_strategy_market)
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


class StrategyMarketHardData(BaseModel):
    genres: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    game_modes: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    release_date: Optional[str] = None
    first_release_date: Optional[str] = None
    involved_companies: list[str] = Field(default_factory=list)
    developers: list[str] = Field(default_factory=list)
    publishers: list[str] = Field(default_factory=list)
    metacritic: Optional[int] = None
    ratings_distribution: Optional[dict] = None
    price_usd: Optional[float] = None
    price_history: Optional[dict] = None
    player_count_peak: Optional[int] = None
    player_count_current: Optional[int] = None
    estimated_owners: Optional[str] = None
    estimated_revenue: Optional[str] = None
    review_score: Optional[float] = None
    review_count: Optional[int] = None
    achievements_schema: Optional[dict] = None
    dlc_count: Optional[int] = None
    dlc_price_total: Optional[float] = None
    tags: list[str] = Field(default_factory=list)


class StrategyMarketSemanticData(BaseModel):
    audience: SemanticCategory = Field(default_factory=SemanticCategory)
    business_model: SemanticCategory = Field(default_factory=SemanticCategory)
    retention_live_ops: SemanticCategory = Field(default_factory=SemanticCategory)
    production_business: SemanticCategory = Field(default_factory=SemanticCategory)
    marketing: SemanticCategory = Field(default_factory=SemanticCategory)
    cultural_impact: SemanticCategory = Field(default_factory=SemanticCategory)


class MiniContextMetadata(BaseModel):
    game_id: str
    game_name: str
    macro_skill: str = "Strategy and Market"
    worker_id: str = "scraper_strategy_market"
    data_sources: list[str] = Field(default_factory=list)


class StrategyMarketMiniContext(BaseModel):
    """Input contract — matches master_json_schema.yaml#/definitions/mini_context_strategy_market"""
    metadata: MiniContextMetadata
    hard_data: StrategyMarketHardData
    semantic_data: StrategyMarketSemanticData
    evidence_count: int = 0
    confidence_score: float = 0.0


# =====================================================================
# OUTPUT SCHEMAS  (Strategy & Market analysis result)
# =====================================================================

class LLMOutput(BaseModel):
    """Base for all LLM-generated objects. Allows extra fields for forward compatibility."""
    model_config = ConfigDict(extra="allow")


class SkillOutputMetadata(LLMOutput):
    skill_id: str = "strategy_market"
    skill_name: str = "Strategy and Market"
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


class StrategyMarketOutputModel(LLMOutput):
    """Output contract — structured intelligence ready for Phase 4 Synthesizer."""
    metadata: SkillOutputMetadata
    analysis: dict[str, Any]
    summary: dict[str, Any]
    confidence: ConfidenceMetrics
