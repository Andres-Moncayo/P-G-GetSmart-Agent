"""
Database models for reports and pipeline status.
"""

from typing import Optional, Dict, Any
from sqlalchemy import Column, DateTime, String, Text, Integer, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, UUIDMixin, TimestampMixin, StatusMixin, QualityMetricsMixin


class AnalysisReport(Base, UUIDMixin, TimestampMixin, StatusMixin, QualityMetricsMixin):
    """Main report entity storing synthesized analysis results."""
    
    __tablename__ = "analysis_reports"
    
    # Game identification
    game_id = Column(String(100), nullable=False, index=True)
    game_title = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False)  # steam, epic, etc.
    
    # Report content
    title = Column(String(1000), nullable=False)
    markdown_content = Column(Text, nullable=False)
    json_content = Column(JSON, nullable=False)  # Master-JSON structure
    summary = Column(Text)  # Executive summary
    
    # Analysis metadata
    report_type = Column(String(50), default="comprehensive", nullable=False)  # comprehensive, quick, etc.
    version = Column(String(20), default="1.0", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Processing metadata
    phases_completed = Column(JSON, default=list)  # List of completed phases
    total_phases = Column(Integer, default=4, nullable=False)
    processing_time_ms = Column(Integer, default=0)
    
    # Relationships
    status_updates = relationship("PipelineStatus", back_populates="report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AnalysisReport(id={self.id}, game_id={self.game_id}, status={self.status})>"


class PipelineStatus(Base, UUIDMixin, TimestampMixin):
    """Track pipeline execution status for each report."""
    
    __tablename__ = "pipeline_status"
    
    # Foreign key to report
    report_id = Column(String, ForeignKey("analysis_reports.id"), nullable=False)
    
    # Status information
    phase_name = Column(String(50), nullable=False)  # phase1, phase2, phase3, phase4
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Execution details
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Phase-specific data
    phase_data = Column(JSON)  # Store phase-specific metadata
    
    # Relationships
    report = relationship("AnalysisReport", back_populates="status_updates")
    
    def __repr__(self):
        return f"<PipelineStatus(phase={self.phase_name}, status={self.status}, progress={self.progress_percentage}%)"


class RawAnalysisData(Base, UUIDMixin, TimestampMixin):
    """Store raw analysis data from individual phases for debugging/reprocessing."""
    
    __tablename__ = "raw_analysis_data"
    
    # Identification
    game_id = Column(String(100), nullable=False, index=True)
    phase = Column(String(50), nullable=False)
    source = Column(String(100), nullable=False)  # steam, epic, custom
    
    # Raw data
    data_type = Column(String(50), nullable=False)  # scraping_result, ai_analysis, synthesis
    content = Column(JSON, nullable=False)
    raw_metadata = Column(JSON)
    
    # Quality indicators
    is_valid = Column(Boolean, default=True, nullable=False)
    validation_errors = Column(JSON)
    
    def __repr__(self):
        return f"<RawAnalysisData(game={self.game_id}, phase={self.phase}, type={self.data_type})>"