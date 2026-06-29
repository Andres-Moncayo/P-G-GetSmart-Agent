"""
User / Role / ApiKey models.

Aligned with backend/UnityGsmart.sql (PostgreSQL). The schema is applied
externally by another developer, so these models must match the `users` and
`roles` tables exactly — the backend does NOT run create_all in startup.

Auth-specific fields that don't have a dedicated column (display name, SSO
provider, preferences) live inside `profile_jsonb` / `settings_jsonb`.
"""

import uuid

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, ARRAY, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL para SSO
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)

    # Compacted profile + preferences (display_name, avatar_url, sso_provider, etc.)
    profile_jsonb = Column(JSONB, nullable=False, default=dict)
    settings_jsonb = Column(JSONB, nullable=False, default=dict)

    roles = relationship("Role", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")

    # ── Convenience accessors so existing code keeps working ──────────────────
    @property
    def name(self) -> str:
        return (self.profile_jsonb or {}).get("display_name", self.username or "")

    @property
    def sso_provider(self):
        return (self.profile_jsonb or {}).get("sso_provider")

    @property
    def preferences(self) -> dict:
        return self.settings_jsonb or {}

    def get_avatar_initials(self) -> str:
        name = self.name
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        if len(parts) == 1 and parts[0]:
            return parts[0][:2].upper()
        return "U"


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_name", "is_active", name="roles_user_role_active_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_name = Column(String(50), nullable=False)  # admin | developer | user
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="roles")


class ApiKey(Base):
    """
    NOTE: UnityGsmart.sql does not define an `api_keys` table. This model is kept
    only so the (currently unregistered) user_service API-key endpoints import
    cleanly. It is not backed by the production schema — do not query it until an
    `api_keys` table is added to UnityGsmart.sql.
    """

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    prefix = Column(String(8), nullable=False)
    scopes = Column(ARRAY(String), nullable=False, default=["read"])
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")
