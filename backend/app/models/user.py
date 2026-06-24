from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="viewer")
    avatar_url = Column(Text, nullable=True)
    avatar_initials = Column(String(2), nullable=True)
    department = Column(String(255), nullable=True)
    sso_provider = Column(String(50), nullable=True)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")

    def get_avatar_initials(self):
        if self.avatar_initials:
            return self.avatar_initials
        name_parts = self.name.split()
        if len(name_parts) >= 2:
            return f"{name_parts[0][0]}{name_parts[-1][0]}".upper()
        elif len(name_parts) == 1:
            return name_parts[0][:2].upper()
        return "U"

class ApiKey(Base):
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