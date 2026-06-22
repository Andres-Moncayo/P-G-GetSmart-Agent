from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

# ============================================================
# Game Schema
# ============================================================
class Game(BaseModel):
    id: str
    name: str
    slug: str
    release_year: Optional[int] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genres: List[str] = []
    platforms: List[str] = []
    cover_url: Optional[str] = None

# ============================================================
# Report Schema
# ============================================================
class Report(BaseModel):
    id: UUID
    game: Game
    status: str
    current_phase: Optional[int] = None
    progress_percent: int = 0
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
    format: str = Field(..., regex="^(markdown|json|json_rag)$")

class ReportContentResponse(BaseModel):
    format: str
    content: str
    download_url: Optional[str] = None

class ReportUpdateRequest(BaseModel):
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=1000)

# ============================================================
# Filter Parameters
# ============================================================
class ReportFilters(BaseModel):
    genre: Optional[List[str]] = None
    developer: Optional[List[str]] = None
    platform: Optional[List[str]] = None
    status: Optional[List[str]] = None
    year_from: Optional[int] = Field(None, ge=1980, le=2030)
    year_to: Optional[int] = Field(None, ge=1980, le=2030)
    search: Optional[str] = Field(None, max_length=100)
    sort_by: Optional[str] = Field("created_at", regex="^(created_at|game\.name|game\.release_year|updated_at|progress_percent)$")
    sort_dir: Optional[str] = Field("desc", regex="^(asc|desc)$")
    page: Optional[int] = Field(1, ge=1)
    page_size: Optional[int] = Field(12, ge=1, le=50)