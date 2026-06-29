"""
Models package exports.
"""

from .base import Base
# ORM models aligned with UnityGsmart.sql. Imported under aliases so they don't
# shadow the legacy pydantic `Report` model defined below (used by services/__init__.py).
from .report import Report as ReportORM, Analysis as AnalysisORM
from .synthesis_models import (
    SynthesisAnalysis, SynthesisInput, SynthesisOutput, 
    SynthesisQualityMetrics, SynthesisCacheEntry, SynthesisJob
)
from .user import User, ApiKey, Role

# Legacy models for backwards compatibility - temporary fix
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class FacetCount(BaseModel):
    """Legacy facet count model."""
    value: str
    count: int
    label: str

class Facets(BaseModel):
    """Legacy facets model."""
    genre: List[FacetCount]
    developer: List[FacetCount]
    platform: List[FacetCount]
    status: List[FacetCount]
    year_range: dict

class Game(BaseModel):
    """Game sub-object returned inside Report responses."""
    id: str
    name: str
    slug: Optional[str] = None
    release_year: Optional[int] = None
    developer: Optional[str] = None
    primary_genre: Optional[str] = None
    primary_platform: Optional[str] = None
    all_genres: List[str]
    all_platforms: List[str]
    cover_url: Optional[str] = None

class Pagination(BaseModel):
    """Legacy pagination model."""
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

class Report(BaseModel):
    """Report item returned by list and detail endpoints."""
    id: str
    game: Game
    status: str
    current_phase: Optional[str] = None
    pipeline_progress: int
    confidence_score: Optional[float] = None
    tags: List[str]
    created_at: Any
    updated_at: Any
    executive_summary: Optional[dict] = None
    thematic_analysis: Optional[dict] = None
    confidence_analysis: Optional[dict] = None

class ReportListResponse(BaseModel):
    """Legacy report list response model."""
    items: List[Report]
    pagination: Pagination
    facets: Facets

__all__ = [
    "Base",
    "ReportORM",
    "AnalysisORM",
    "SynthesisAnalysis",
    "SynthesisInput", 
    "SynthesisOutput",
    "SynthesisQualityMetrics",
    "SynthesisCacheEntry",
    "SynthesisJob",
    "User",
    "ApiKey",
    "Role",
    # Legacy models
    "FacetCount",
    "Facets", 
    "Game",
    "Pagination",
    "Report",
    "ReportListResponse"
]