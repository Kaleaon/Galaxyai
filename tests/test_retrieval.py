"""Tests for source evidence and retrieval-backed ingest flows."""

from gma.galaxy import Galaxy
from gma.retrieval import SourceEvidence


def test_source_evidence_initial_confidence_bounded():
    evidence = SourceEvidence(content="fact", source_url="https://example.com", trust_score=2.0, recency_score=-1.0)
    confidence = evidence.initial_confidence()
    assert 0.05 <= confidence <= 0.95


def test_ingest_evidence_uses_computed_confidence():
    g = Galaxy()
    g.register_domain("science")
    evidence = SourceEvidence(
        content="Water boils at 100C at sea level",
        source_url="https://example.com",
        trust_score=0.8,
        recency_score=0.6,
    )
    planet = g.ingest_evidence(evidence, domain="science")
    assert planet.content.startswith("Water boils")
    assert planet.confidence >= 0.6


def test_ingest_from_wikipedia_uses_retriever_output(monkeypatch):
    g = Galaxy()
    g.register_domain("history")

    def fake_summary(_topic: str):
        return SourceEvidence(
            content="The moon landing happened in 1969.",
            source_url="https://en.wikipedia.org/wiki/Apollo_11",
            trust_score=0.9,
            recency_score=0.7,
        )

    monkeypatch.setattr(g.wikipedia, "fetch_summary", fake_summary)
    planet = g.ingest_from_wikipedia("Apollo 11", domain="history")
    assert "1969" in planet.content
