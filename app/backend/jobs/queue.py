"""In-memory queue abstraction for ingestion jobs."""

from __future__ import annotations

import queue
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from app.backend.jobs.models import IngestionStage, JobRecord, JobState

JobWorker = Callable[[JobRecord], None]


class JobQueue:
    """A thread-safe internal queue with lifecycle tracking."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._pending: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._worker_thread: Optional[threading.Thread] = None
        self._worker_fn: Optional[JobWorker] = None

    def enqueue(self, job_type: str, payload: Dict[str, Any]) -> JobRecord:
        """Create and enqueue a new job."""
        job = JobRecord(job_id=str(uuid.uuid4()), job_type=job_type, payload=payload)
        job.emit(IngestionStage.QUEUED)
        with self._lock:
            self._jobs[job.job_id] = job
        self._pending.put(job.job_id)
        return job

    def get(self, job_id: str) -> Optional[JobRecord]:
        """Look up a queued job by ID."""
        return self._jobs.get(job_id)

    def retry(self, job_id: str) -> Optional[JobRecord]:
        """Re-enqueue a failed/succeeded job payload as a fresh job."""
        existing = self.get(job_id)
        if existing is None:
            return None

        payload = dict(existing.payload)
        payload["retry_of"] = existing.job_id
        payload["retry_count"] = int(payload.get("retry_count", 0)) + 1
        return self.enqueue(existing.job_type, payload)

    def start_worker(self, worker: JobWorker) -> None:
        """Start a background worker loop if not already running."""
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._worker_fn = worker
        self._worker_thread = threading.Thread(target=self._run, daemon=True)
        self._worker_thread.start()

    def _run(self) -> None:
        """Continuously process pending jobs with the configured worker."""
        if self._worker_fn is None:
            return

        while True:
            job_id = self._pending.get()
            job = self.get(job_id)
            if job is None:
                self._pending.task_done()
                continue

            try:
                job.status = JobState.RUNNING
                job.updated_at = datetime.now(timezone.utc)
                self._worker_fn(job)
                if job.status == JobState.RUNNING:
                    job.status = JobState.SUCCEEDED
                    job.updated_at = datetime.now(timezone.utc)
            except Exception as exc:  # pragma: no cover - defensive guard
                job.status = JobState.FAILED
                job.error = str(exc)
                job.emit(IngestionStage.FAILED, message=str(exc))
            finally:
                self._pending.task_done()
