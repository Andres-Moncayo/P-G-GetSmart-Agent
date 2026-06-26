from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MasterMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    game_id: UUID
    game_name: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    workers_executed: list[str]
    workers_failed: list[str]
    total_evidence_count: int = Field(ge=0)
    overall_confidence_score: float = Field(ge=0.0, le=1.0)


class GameMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    game_id: UUID
    name: str
    release_year: int = Field(ge=1970, le=2100)
    aliases: list[str] = Field(default_factory=list)


class MiniContexts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    design_art: dict[str, Any]
    user_experience: dict[str, Any]
    technology_systems: dict[str, Any]
    strategy_market: dict[str, Any]


class MasterPartitions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    design_and_art: dict[str, Any]
    user_experience: dict[str, Any]
    technology_and_systems: dict[str, Any]
    strategy_and_market: dict[str, Any]


class MasterContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: MasterMetadata
    game_metadata: GameMetadata
    mini_contexts: MiniContexts
    partitions: MasterPartitions
