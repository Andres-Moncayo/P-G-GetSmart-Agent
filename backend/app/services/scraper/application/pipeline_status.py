from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


VALID_PIPELINE_STATUSES = {"queued", "processing", "completed", "failed"}


@dataclass
class PipelineStatusRecord:
    report_id: str
    status: str
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "status": self.status,
            "updated_at": self.updated_at.isoformat(),
            "message": self.message,
            "details": self.details,
        }


class PipelineStatusStore:
    """In-memory status store for HTTP short polling."""

    def __init__(self) -> None:
        self._records: dict[str, PipelineStatusRecord] = {}

    def set_status(
        self,
        *,
        report_id: str,
        status: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if status not in VALID_PIPELINE_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        self._records[report_id] = PipelineStatusRecord(
            report_id=report_id,
            status=status,
            message=message,
            details=details or {},
        )

    def get_status(self, report_id: str) -> PipelineStatusRecord | None:
        return self._records.get(report_id)


pipeline_status_store = PipelineStatusStore()
