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
    """Legacy game model."""
    id: str
    name: str
    slug: Optional[str] = None
    release_year: Optional[int] = None
    developer: Optional[str] = None
    genres: List[str]
    platforms: List[str]

class Pagination(BaseModel):
    """Legacy pagination model."""
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

class Report(BaseModel):
    """Legacy report model."""
    id: str
    game: Game
    status: str
    current_phase: Optional[str] = None
    progress_percent: int
    outputs: dict
    metadata: dict
    summary: Optional[str] = None
    tags: List[str]
    created_at: Any
    updated_at: Any

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