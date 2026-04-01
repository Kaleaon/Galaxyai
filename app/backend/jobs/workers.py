"""Job workers for URL/Wikipedia retrieval and scoring."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from app.backend.jobs.models import IngestionStage, JobRecord, JobState
from gma.galaxy import Galaxy
from gma.retrieval import SourceEvidence


class IngestionWorkers:
    """Executes ingestion job types against a Galaxy instance."""

    JOB_TYPE_URL = "ingest_url"
    JOB_TYPE_WIKIPEDIA = "ingest_wikipedia"

    def __init__(
        self,
        galaxy: Galaxy,
        score_fn: Optional[Callable[[SourceEvidence], float]] = None,
    ) -> None:
        self._galaxy = galaxy
        self._score_fn = score_fn or (lambda evidence: evidence.initial_confidence())

    def __call__(self, job: JobRecord) -> None:
        """Dispatch to the correct worker by job type."""
        if job.job_type == self.JOB_TYPE_URL:
            self._handle_url(job)
            return
        if job.job_type == self.JOB_TYPE_WIKIPEDIA:
            self._handle_wikipedia(job)
            return
        raise ValueError(f"Unsupported job type: {job.job_type}")

    def _handle_url(self, job: JobRecord) -> None:
        url = str(job.payload["url"])
        domain = job.payload.get("domain")
        evidence = self._galaxy.web.fetch_text(url)
        self._ingest_evidence(job, evidence=evidence, domain=domain)

    def _handle_wikipedia(self, job: JobRecord) -> None:
        topic = str(job.payload["topic"])
        domain = job.payload.get("domain")
        evidence = self._galaxy.wikipedia.fetch_summary(topic)
        self._ingest_evidence(job, evidence=evidence, domain=domain)

    def _ingest_evidence(self, job: JobRecord, evidence: SourceEvidence, domain: Optional[str]) -> None:
        job.emit(IngestionStage.FETCHED, source_url=evidence.source_url)

        scored_confidence = self._score_fn(evidence)
        job.emit(IngestionStage.SCORED, confidence=scored_confidence)

        planet = self._galaxy.ingest(
            content=evidence.content,
            domain=domain,
            initial_confidence=scored_confidence,
        )
        job.emit(
            IngestionStage.INGESTED,
            planet_id=planet.planet_id,
            confidence=planet.confidence,
            domain=domain,
        )
        job.status = JobState.SUCCEEDED
        job.result = {
            "planet_id": planet.planet_id,
            "content": planet.content,
            "confidence": planet.confidence,
            "domain": domain,
            "source_url": evidence.source_url,
        }
