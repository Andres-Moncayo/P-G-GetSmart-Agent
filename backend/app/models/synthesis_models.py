"""
Pydantic models for Phase 3 synthesis operations.

Defines data structures for synthesis input/output, confidence scoring,
and quality metrics for the AI game intelligence system.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class SynthesisAnalysis(BaseModel):
    """Individual synthesis analysis result."""
    
    model_config = ConfigDict(extra="forbid")
    
    text: str = Field(description="Synthesized markdown text content")
    synthesis_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in synthesis quality")
    key_analyses: List[str] = Field(description="List of macro-skill analyses incorporated")
    synthesis_stats: Dict[str, Any] = Field(description="Detailed synthesis statistics")
    
    def __str__(self) -> str:
        return f"SynthesisAnalysis({len(self.text)} chars, confidence={self.synthesis_confidence:.1%})"


class SynthesisInput(BaseModel):
    """Input for synthesis operation - Master-JSON from Phase 2."""
    
    model_config = ConfigDict(extra="forbid")
    
    master_json: Dict[str, Any] = Field(description="Complete Master-JSON from Phase 2 AI analysis")
    synthesis_options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Options for synthesis (model, verbosity, etc.)"
    )
    
    @classmethod
    def from_master_json(cls, master_json: Dict[str, Any]) -> "SynthesisInput":
        """Create from Master-JSON output of Phase 2."""
        return cls(master_json=master_json)


class SynthesisOutput(BaseModel):
    """Output from synthesis operation with structured report."""
    
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(description="Status: success, partial_success, or failed")
    synthesis: SynthesisAnalysis = Field(description="Synthesis analysis result")
    game_name: str = Field(description="Name of the analyzed game")
    game_id: str = Field(description="ID of the analyzed game")
    synthesis_timestamp: str = Field(description="ISO timestamp of synthesis completion")
    source_analyses_count: int = Field(description="Number of source analyses used")
    word_count: int = Field(description="Total word count of synthesized report")
    metadata: Dict[str, Any] = Field(description="Additional synthesis metadata")
    
    @property
    def is_successful(self) -> bool:
        """Check if synthesis was successful."""
        return self.status in ("success", "partial_success")
    
    @property
    def markdown_content(self) -> str:
        """Get the markdown content for display."""
        return self.synthesis.text
    
    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class SynthesisQualityMetrics(BaseModel):
    """Quality metrics for synthesis validation."""
    
    model_config = ConfigDict(extra="forbid")
    
    overall_score: str = Field(description="overall quality: high, medium, or low")
    structure_valid: bool = Field(description="Report structure is valid")
    content_completeness: Dict[str, bool] = Field(description="Required sections presence")
    readability_metrics: Dict[str, Union[str, float]] = Field(description="Readability and length metrics")
    recommendations: List[str] = Field(description="Improvement recommendations")
    
    @property
    def needs_improvement(self) -> bool:
        """Check if synthesis needs improvement."""
        return self.overall_score != "high" or len(self.recommendations) > 0


class SynthesisCacheEntry(BaseModel):
    """Cache entry for synthesis results to avoid reprocessing."""
    
    model_config = ConfigDict(extra="forbid")
    
    game_id: str = Field(description="Game identifier")
    game_name: str = Field(description="Game name")
    master_json_hash: str = Field(description="Hash of input Master-JSON for cache validation")
    synthesis_result: SynthesisOutput = Field(description="Cached synthesis output")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Cache expiration time")
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return bool(self.expires_at and datetime.utcnow() > self.expires_at)
    
    @property
    def is_valid_for(self, master_json: Dict[str, Any]) -> bool:
        """Check if cache entry is valid for given Master-JSON."""
        from hashlib import md5
        import json
        
        # Create hash of input Master-JSON key fields
        key_fields = {
            "game_name": master_json.get("game_info", {}).get("game_name"),
            "analyses": len(master_json.get("macro_skill_analyses", [])),
            "success_rate": master_json.get("game_info", {}).get("success_rate")
        }
        
        current_hash = md5(json.dumps(key_fields, sort_keys=True).encode()).hexdigest()
        return not self.is_expired and current_hash == self.master_json_hash


class SynthesisJob(BaseModel):
    """Background synthesis job for tracking and management."""
    
    model_config = ConfigDict(extra="forbid")
    
    job_id: UUID = Field(description="Unique job identifier")
    game_id: str = Field(description="Game being analyzed")
    game_name: str = Field(description="Name of the game")
    status: str = Field(description="Job status: queued, processing, completed, failed")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    result: Optional[SynthesisOutput] = Field(None, description="Synthesis result when complete")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    progress: float = Field(ge=0.0, le=1.0, default=0.0, description="Progress percentage")
    
    @property
    def duration_seconds(self) -> float:
        """Get job duration in seconds."""
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def is_complete(self) -> bool:
        """Check if job is complete."""
        return self.status in ("completed", "failed")


# Synthesis detailed models for integration with new synthesis services
CategoryId = Literal[
    "gameplay",
    "ui_ux",
    "production_business",
    "audience",
    "business_model",
    "retention_live_ops",
    "marketing",
    "cultural_impact",
]

SkillId = Literal[
    "design_art",
    "user_experience",
    "technology_systems",
    "strategy_market",
]

CATEGORY_NAMES: dict[CategoryId, str] = {
    "gameplay": "Gameplay",
    "ui_ux": "UI/UX",
    "production_business": "Production/Business",
    "audience": "Audience",
    "business_model": "Business Model",
    "retention_live_ops": "Retention / Live Ops",
    "marketing": "Marketing",
    "cultural_impact": "Cultural Impact",
}

CATEGORY_OWNERSHIP: dict[CategoryId, dict[str, list[str] | str]] = {
    "gameplay": {
        "primary": "design_art",
        "cross_refs": ["technology_systems", "user_experience"],
    },
    "ui_ux": {
        "primary": "user_experience",
        "cross_refs": ["design_art", "strategy_market"],
    },
    "production_business": {
        "primary": "strategy_market",
        "cross_refs": ["technology_systems"],
    },
    "audience": {
        "primary": "strategy_market",
        "cross_refs": ["user_experience", "design_art"],
    },
    "business_model": {
        "primary": "strategy_market",
        "cross_refs": ["technology_systems"],
    },
    "retention_live_ops": {
        "primary": "strategy_market",
        "cross_refs": ["user_experience"],
    },
    "marketing": {
        "primary": "strategy_market",
        "cross_refs": ["design_art", "user_experience"],
    },
    "cultural_impact": {
        "primary": "strategy_market",
        "cross_refs": ["design_art"],
    },
}


class SourceIndexEntry(BaseModel):
    url: str
    platform: str
    first_cited_by: str
    citation_count: int


class ConfidenceBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    per_category: Dict[str, float]
    per_skill: Dict[str, float]
    adjustment_rationale: List[str]


class ExecutiveSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    game_identity: str
    market_position: str
    key_insights: List[str]
    critical_risks: List[str]
    recommended_actions: List[str]
    overall_confidence: float


class CrossCuttingInsight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insight_id: str
    title: str
    narrative: str
    contributing_skills: List[str]
    confidence: float


class CrossCuttingInsights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    design_technology_synergy: CrossCuttingInsight
    player_experience_arc: CrossCuttingInsight
    commercial_viability: CrossCuttingInsight
    competitive_moat: CrossCuttingInsight
    development_health: CrossCuttingInsight


class StrategicRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    rationale: str
    supporting_categories: List[str]
    impact: str
    effort: str
    time_horizon: str
    confidence: float
    risk_if_ignored: str
    owner: str


class RiskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    risk_statement: str
    categories_affected: List[str]
    likelihood: str
    impact: str
    mitigation: str
    owner: str
    timeline: str


class SupportingEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    claim: str
    confidence: float
    urls: List[str]


class ThematicCategory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: CategoryId
    category_name: str
    overview: str
    key_findings: List[str]
    supporting_evidence: List[SupportingEvidence]
    confidence: float
    cross_skill_notes: List[str]


class ThematicAnalysis(BaseModel):
    model_config = ConfigDict(extra="allow")


class Appendices(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_index: List[SourceIndexEntry]
    confidence_breakdown: ConfidenceBreakdown
    conflict_log: List[str]
    data_gaps: List[str]
    methodology_notes: str


class ReportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: str
    game_id: str
    game_name: str
    generated_at: str
    pipeline_version: str
    synthesis_model: str
    input_skills: List[str]
    input_confidence_range: Dict[str, float]
    output_formats: List[str]
    report_classification: str


class ConfidenceMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_score: float
    category_scores: Dict[str, float]
    skill_contribution_weights: Dict[str, float]
    data_quality_notes: List[str]


class MacroOutputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    design_art: Dict[str, Any] = Field(default_factory=dict)
    user_experience: Dict[str, Any] = Field(default_factory=dict)
    technology_systems: Dict[str, Any] = Field(default_factory=dict)
    strategy_market: Dict[str, Any] = Field(default_factory=dict)


class FinalReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: ReportMetadata
    executive_summary: ExecutiveSummary
    thematic_analysis: ThematicAnalysis
    cross_cutting_insights: CrossCuttingInsights
    strategic_recommendations: List[StrategicRecommendation]
    risk_assessment: List[RiskItem]
    appendices: Appendices
    confidence: ConfidenceMetrics


class SynthesisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: FinalReport
    markdown: str
    pdf_html: str
    synthesis_mode: str
    workflow_steps_completed: List[str]


# Type aliases for convenience
SynthesisStatus = str  # "success" | "partial_success" | "failed"
JobStatus = str  # "queued" | "processing" | "completed" | "failed"
QualityScore = str  # "high" | "medium" | "low"


# Constants for validation
VALID_SYNTHESIS_STATUSES = ["success", "partial_success", "failed"]
VALID_JOB_STATUSES = ["queued", "processing", "completed", "failed"]
VALID_QUALITY_SCORES = ["high", "medium", "low"]

MIN_WORD_COUNT = 500
MAX_WORD_COUNT = 10000
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 1.0