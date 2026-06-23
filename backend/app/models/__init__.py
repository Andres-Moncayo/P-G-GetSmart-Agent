from .user import User, ApiKey
from .base import Base

__all__ = ["User", "ApiKey", "Base"]
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

# ============================================================
# Game Schema (Exact match to data_crud_contract.yaml)
# ============================================================
class Game(BaseModel):
    id: str
    name: str
    slug: Optional[str] = None
    release_year: Optional[int] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genres: List[str] = []
    platforms: List[str] = []
    cover_url: Optional[str] = None

# ============================================================
# Report Schema (Exact match to data_crud_contract.yaml)
# ============================================================
class Report(BaseModel):
    id: UUID
    game: Game
    status: str = Field(..., pattern=r"^(queued|processing|completed|failed|cancelled)$")
    current_phase: Optional[int] = Field(None, ge=0, le=4)
    progress_percent: int = Field(0, ge=0, le=100)
    outputs: Dict[str, Optional[str]] = {}
    metadata: Dict[str, Any] = {}
    summary: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================
# Pagination Schema
# ============================================================
class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

# ============================================================
# Facet Count Schema
# ============================================================
class FacetCount(BaseModel):
    value: str
    count: int
    label: str

class Facets(BaseModel):
    genre: List[FacetCount] = []
    developer: List[FacetCount] = []
    platform: List[FacetCount] = []
    status: List[FacetCount] = []
    year_range: Dict[str, int] = {}

# ============================================================
# Request/Response Schemas
# ============================================================
class ReportListResponse(BaseModel):
    items: List[Report]
    pagination: Pagination
    facets: Facets

class ReportContentRequest(BaseModel):
    format: str = Field(..., pattern=r"^(markdown|json|json_rag)$")

class ReportContentResponse(BaseModel):
    format: str
    content: str
    download_url: Optional[str] = None

class ReportUpdateRequest(BaseModel):
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=1000)

# ============================================================
# Filter Parameters (Matching data_crud_contract.yaml exactly)
# ============================================================
class ReportFilters(BaseModel):
    genre: Optional[List[str]] = Field(None, description="Filter by genre")
    developer: Optional[List[str]] = Field(None, description="Filter by developer")
    platform: Optional[List[str]] = Field(None, description="Filter by platform")
    status: Optional[List[str]] = Field(None, description="Filter by status")
    year_from: Optional[int] = Field(None, ge=1980, le=2030, description="Filter from release year")
    year_to: Optional[int] = Field(None, ge=1980, le=2030, description="Filter to release year")
    search: Optional[str] = Field(None, max_length=100, description="Search term")
    sort_by: Optional[str] = Field("created_at", pattern=r"^(created_at|game\.name|game\.release_year|updated_at|progress_percent)$")
    sort_dir: Optional[str] = Field("desc", pattern=r"^(asc|desc)$")
    page: Optional[int] = Field(1, ge=1)
    page_size: Optional[int] = Field(12, ge=1, le=50)

# Enum values from spec for validation
class GenreEnum:
    VALUES = ["Action RPG", "Battle Royale", "MOBA", "Open World", "Adventure", "Action", "RPG", "Strategy", "Shooter", "Fighting", "Racing", "Simulation", "Sports", "Puzzle", "Platformer"]

class DeveloperEnum:
    VALUES = ["Riot Games", "Epic Games", "FromSoftware", "CD Projekt Red", "Nintendo", "Santa Monica Studio", "Naughty Dog", "Bungie", "Valve", "Blizzard"]

class PlatformEnum:
    VALUES = ["PC", "PlayStation", "Xbox", "Switch", "Mobile"]

class StatusEnum:
    VALUES = ["completed", "processing", "queued", "failed"]
