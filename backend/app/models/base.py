"""
Base database configuration and common models.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text, Integer, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class TimestampMixin:
    """Add created_at and updated_at timestamps to models."""
    
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class UUIDMixin:
    """Add UUID primary key to models."""
    
    @declared_attr
    def id(cls):
        return Column(
            String, 
            primary_key=True, 
            default=lambda: str(uuid4())
        )


class StatusMixin:
    """Add status fields to models."""
    
    status = Column(String(50), default="pending", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


class QualityMetricsMixin:
    """Add quality metrics fields to models."""
    
    confidence_score = Column(Float, default=0.0, nullable=False)
    quality_rating = Column(String(10), default="unknown")  # excellent, good, fair, poor, unknown
    word_count = Column(Integer, default=0, nullable=False)
    data_completeness = Column(Float, default=0.0, nullable=False)  # percentage of expected data present


# Legacy database dependency function for backwards compatibility
def get_db():
    """Legacy database dependency - returns async session generator."""
    from ..db.connection import get_async_session
    return get_async_session()
