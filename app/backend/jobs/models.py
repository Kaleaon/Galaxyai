"""Job models for asynchronous ingestion workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class JobState(str, Enum):
    """Lifecycle state of an ingestion job."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class IngestionStage(str, Enum):
    """Audit stages for ingestion events."""

    QUEUED = "queued"
    FETCHED = "fetched"
    SCORED = "scored"
    INGESTED = "ingested"
    FAILED = "failed"


@dataclass
class IngestionEvent:
    """Point-in-time event emitted during a job's ingestion lifecycle."""

    stage: IngestionStage
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class JobRecord:
    """Persistent in-memory representation of a queued job."""

    job_id: str
    job_type: str
    payload: Dict[str, Any]
    status: JobState = JobState.QUEUED
    events: List[IngestionEvent] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def emit(self, stage: IngestionStage, **details: Any) -> None:
        """Append a new lifecycle event and update timestamps."""
        self.events.append(IngestionEvent(stage=stage, details=details))
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses."""
        return {
            "id": self.job_id,
            "type": self.job_type,
            "status": self.status.value,
            "payload": self.payload,
            "result": self.result,
            "error": self.error,
            "events": [
                {
                    "stage": e.stage.value,
                    "details": e.details,
                    "created_at": e.created_at.isoformat(),
                }
                for e in self.events
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
