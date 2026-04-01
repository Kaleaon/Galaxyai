"""Tests for backend ingestion queue and lifecycle events."""

from __future__ import annotations

import time

from app.backend import api
from gma.retrieval import SourceEvidence


def _wait_for_terminal(job_id: str, timeout_seconds: float = 2.0):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        state = api.get_job_status(job_id)
        if state.get("status") in {"succeeded", "failed"}:
            return state
        time.sleep(0.01)
    raise AssertionError(f"Job {job_id} did not finish before timeout")


def test_url_ingestion_is_queued_and_exposes_status(monkeypatch):
    api.galaxy.register_domain("web")

    def fake_fetch_text(_url: str):
        return SourceEvidence(
            content="Example article about galaxies.",
            source_url="https://example.com/article",
            trust_score=0.8,
            recency_score=0.6,
        )

    monkeypatch.setattr(api.galaxy.web, "fetch_text", fake_fetch_text)
    queued = api.enqueue_url_ingestion("https://example.com", domain="web")
    assert queued["status"] == "queued"

    finished = _wait_for_terminal(queued["job_id"])
    assert finished["status"] == "succeeded"
    stages = [event["stage"] for event in finished["events"]]
    assert stages == ["queued", "fetched", "scored", "ingested"]


def test_wikipedia_ingestion_records_lifecycle_and_retry(monkeypatch):
    api.galaxy.register_domain("history")

    def fake_summary(_topic: str):
        return SourceEvidence(
            content="Apollo 11 landed on the moon in 1969.",
            source_url="https://en.wikipedia.org/wiki/Apollo_11",
            trust_score=0.9,
            recency_score=0.8,
        )

    monkeypatch.setattr(api.galaxy.wikipedia, "fetch_summary", fake_summary)
    queued = api.enqueue_wikipedia_ingestion("Apollo 11", domain="history")

    finished = _wait_for_terminal(queued["job_id"])
    assert finished["status"] == "succeeded"
    assert finished["result"]["domain"] == "history"

    retry = api.retry_job(queued["job_id"])
    retried = _wait_for_terminal(retry["job_id"])
    assert retried["status"] == "succeeded"
    assert retried["payload"]["retry_of"] == queued["job_id"]
