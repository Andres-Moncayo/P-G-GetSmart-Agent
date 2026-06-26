"""Proxy definitions for synthesis models used by the legacy synthesis_Skill package."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime

# Re-export commonly used synthesis model types from app.models.synthesis_models

from app.models.synthesis_models import (
    Appendices,
    CategoryId,
    CATEGORY_NAMES,
    CATEGORY_OWNERSHIP,
    ConfidenceBreakdown,
    ConfidenceMetrics,
    CrossCuttingInsight,
    CrossCuttingInsights,
    ExecutiveSummary,
    FinalReport,
    MacroOutputs,
    ReportMetadata,
    RiskItem,
    SkillId,
    SourceIndexEntry,
    SynthesisAnalysis,
    SynthesisCacheEntry,
    SynthesisInput,
    SynthesisJob,
    SynthesisOutput,
    SynthesisQualityMetrics,
    SynthesisResponse,
    StrategicRecommendation,
    SupportingEvidence,
    ThematicAnalysis,
    ThematicCategory,
)

__all__ = [
    "Appendices",
    "CategoryId",
    "CATEGORY_NAMES",
    "CATEGORY_OWNERSHIP",
    "ConfidenceBreakdown",
    "ConfidenceMetrics",
    "CrossCuttingInsight",
    "CrossCuttingInsights",
    "ExecutiveSummary",
    "FinalReport",
    "MacroOutputs",
    "ReportMetadata",
    "RiskItem",
    "SynthesisAnalysis",
    "SynthesisCacheEntry",
    "SynthesisInput",
    "SynthesisJob",
    "SynthesisOutput",
    "StrategicRecommendation",
    "SupportingEvidence",
    "ThematicAnalysis",
    "ThematicCategory",
]
