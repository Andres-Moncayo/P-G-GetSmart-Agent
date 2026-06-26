"""Pipeline task tracking management."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Phase(str, Enum):
    SCRAPING = "scraping"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    STORAGE = "storage"


class APIStatus(BaseModel):
    """Individual API call status."""
    name: str = Field(description="API name (e.g., 'RAWG', 'Steam', 'Tavily')")
    status: TaskStatus = Field(default=TaskStatus.WAITING, description="Current status")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    data_items_found: int = 0
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    pipeline_id: UUID
    phase: Phase
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.WAITING
    progress_percentage: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
    api_calls: List[APIStatus] = Field(default_factory=list)
    sub_tasks: List['Task'] = Field(default_factory=list)
    result_summary: Dict[str, Any] = Field(default_factory=dict)


class DetailedPipelineResponse(BaseModel):
    """Enhanced pipeline response with detailed progress tracking."""
    pipeline_id: str = Field(..., alias="report_id", description="Unique pipeline identifier")
    phase: Phase = Field(..., description="Current pipeline phase")
    status: TaskStatus = Field(..., description="Overall pipeline status")
    is_complete: bool = Field(..., description="Is the pipeline complete")
    message: str = Field(..., description="Current status message")
    result: Optional[Dict[str, Any]] = None
    
    # Progress tracking
    seconds_elapsed: float = 0.0
    seconds_remaining: Optional[float] = None
    current_phase_progress: float = 0.0  # Progress within current phase (0-100)
    overall_progress: float = 0.0  # Overall pipeline progress (0-100)
    
    # Task counts
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    tasks_total: int = 0
    
    # Detailed breakdown
    phases: Dict[Phase, Dict[str, Any]] = Field(default_factory=dict)
    api_calls: List[APIStatus] = Field(default_factory=list)
    current_task: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    
# Performance metrics
    scraping_durations: Dict[str, float] = Field(default_factory=dict)
    analysis_durations: Dict[str, float] = Field(default_factory=dict)
    total_records_processed: int = 0
    
    class Config:
        validate_by_name = True


class PipelineResponse(BaseModel):
    """Basic pipeline response for start endpoint."""
    report_id: str
    phase: str
    status: str
    is_complete: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    seconds_elapsed: float = 0.0
    seconds_remaining: Optional[float] = None
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    tasks_total: int = 0


class Pipeline(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: int
    report_id: Optional[str] = None
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    tasks: list[Task] = Field(default_factory=list)
    
    # Enhanced tracking
    current_phase: Optional[Phase] = None
    phase_progress: Dict[Phase, float] = Field(default_factory=dict)
    api_status: Dict[str, APIStatus] = Field(default_factory=dict)
    execution_log: List[str] = Field(default_factory=list)