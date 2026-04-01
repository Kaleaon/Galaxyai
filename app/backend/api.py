"""Backend request handlers for asynchronous retrieval ingestion."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.backend.jobs import JobQueue
from app.backend.jobs.workers import IngestionWorkers
from gma.galaxy import Galaxy


galaxy = Galaxy()
job_queue = JobQueue()
workers = IngestionWorkers(galaxy)
job_queue.start_worker(workers)


def enqueue_url_ingestion(url: str, domain: Optional[str] = None) -> Dict[str, Any]:
    """Queue URL retrieval ingestion and return a job handle."""
    job = job_queue.enqueue(IngestionWorkers.JOB_TYPE_URL, {"url": url, "domain": domain})
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "status_url": f"/jobs/{job.job_id}",
    }


def enqueue_wikipedia_ingestion(topic: str, domain: Optional[str] = None) -> Dict[str, Any]:
    """Queue Wikipedia retrieval ingestion and return a job handle."""
    job = job_queue.enqueue(IngestionWorkers.JOB_TYPE_WIKIPEDIA, {"topic": topic, "domain": domain})
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "status_url": f"/jobs/{job.job_id}",
    }


def get_job_status(job_id: str) -> Dict[str, Any]:
    """GET /jobs/{id} endpoint payload."""
    job = job_queue.get(job_id)
    if job is None:
        return {"error": "job_not_found", "job_id": job_id}
    return job.to_dict()


def retry_job(job_id: str) -> Dict[str, Any]:
    """Retry a previous ingestion job by ID."""
    job = job_queue.retry(job_id)
    if job is None:
        return {"error": "job_not_found", "job_id": job_id}
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "status_url": f"/jobs/{job.job_id}",
    }
