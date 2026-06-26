"""
Report / Analysis models.

Aligned 1:1 with the `reports` and `analysis` tables in backend/UnityGsmart.sql.
The schema is applied externally; these models must match it exactly so the
synthesizer (Phase 4) can write and the dashboard endpoints can read. The
backend does NOT run create_all.
"""

import uuid

from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, Date, Numeric, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func

from .base import Base


class Analysis(Base):
    """One row per macro-skill execution (+ one `synthesis` row) for a report."""

    __tablename__ = "analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    game_id = Column(UUID(as_uuid=True), nullable=False)

    # design_art | user_experience | technology_systems | strategy_market | synthesis
    analysis_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    confidence_score = Column(Numeric(3, 2))

    query_params = Column(JSONB, nullable=False, default=dict)
    target_game_filters = Column(JSONB, nullable=False, default=dict)
    pipeline_config = Column(JSONB, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    processing_time_ms = Column(Integer)
    priority = Column(Integer, default=5)

    input_data_jsonb = Column(JSONB, nullable=False, default=dict)
    raw_output_jsonb = Column(JSONB, nullable=False, default=dict)
    processed_output_jsonb = Column(JSONB, nullable=False, default=dict)
    metrics_jsonb = Column(JSONB, nullable=False, default=dict)
    error_details_jsonb = Column(JSONB, nullable=False, default=dict)

    final_report_id = Column(UUID(as_uuid=True))

    def __repr__(self):
        return f"<Analysis(id={self.id}, type={self.analysis_type}, status={self.status})>"


class Report(Base):
    """Main report entity — the synthesized final result for a game."""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    game_id = Column(UUID(as_uuid=True), nullable=False)

    # Filtros principales
    report_status = Column(String(20), nullable=False, default="queued")
    report_type = Column(String(50), nullable=False, default="comprehensive")
    confidence_score = Column(Numeric(3, 2))

    # Columnas de búsqueda / filtro (indexadas)
    search_query = Column(Text)
    game_name = Column(String(255), nullable=False)
    game_slug = Column(String(255))
    release_year = Column(Integer)
    primary_genre = Column(String(100))
    primary_platform = Column(String(100))
    developer_name = Column(String(255))
    cover_url = Column(String(1000))
    all_genres = Column(ARRAY(Text))
    all_platforms = Column(ARRAY(Text))
    tags = Column(ARRAY(Text))

    # Progreso del pipeline (tarjeta "In Pipeline")
    current_phase = Column(String(50))
    pipeline_progress = Column(Integer, default=0)

    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    report_date = Column(Date, server_default=func.current_date())

    # Métricas
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    file_size_mb = Column(Numeric(8, 2))

    # Contenido
    markdown_content = Column(Text)
    markdown_summary = Column(Text)
    pdf_html_content = Column(Text)

    # URLs de archivos generados
    url_json = Column(String(1000))
    url_json_rag = Column(String(1000))
    url_markdown = Column(String(1000))
    url_pdf = Column(String(1000))

    # Flags de generación de archivos
    json_generated = Column(Boolean, default=False)
    markdown_generated = Column(Boolean, default=False)
    pdf_generated = Column(Boolean, default=False)
    json_rag_generated = Column(Boolean, default=False)

    # Secciones estructuradas (final_report_schema)
    report_metadata_jsonb = Column(JSONB, nullable=False, default=dict)
    executive_summary_jsonb = Column(JSONB, nullable=False, default=dict)
    thematic_analysis_jsonb = Column(JSONB, nullable=False, default=dict)
    cross_cutting_insights_jsonb = Column(JSONB, nullable=False, default=dict)
    strategic_recommendations_jsonb = Column(JSONB, nullable=False, default=dict)
    risk_assessment_jsonb = Column(JSONB, nullable=False, default=dict)
    appendices_jsonb = Column(JSONB, nullable=False, default=dict)
    confidence_analysis_jsonb = Column(JSONB, nullable=False, default=dict)

    # Datos adicionales
    game_data_jsonb = Column(JSONB, nullable=False, default=dict)
    pipeline_data_jsonb = Column(JSONB, nullable=False, default=dict)
    performance_metrics_jsonb = Column(JSONB, nullable=False, default=dict)
    user_metadata_jsonb = Column(JSONB, nullable=False, default=dict)

    # Referencias a los análisis individuales
    analysis_design_art = Column(UUID(as_uuid=True), ForeignKey("analysis.id"))
    analysis_user_experience = Column(UUID(as_uuid=True), ForeignKey("analysis.id"))
    analysis_technology_systems = Column(UUID(as_uuid=True), ForeignKey("analysis.id"))
    analysis_strategy_market = Column(UUID(as_uuid=True), ForeignKey("analysis.id"))
    analysis_synthesis = Column(UUID(as_uuid=True), ForeignKey("analysis.id"))

    def __repr__(self):
        return f"<Report(id={self.id}, game={self.game_name}, status={self.report_status})>"
