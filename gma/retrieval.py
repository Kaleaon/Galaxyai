"""Web/Wikipedia retrieval helpers for feeding evidence into Galaxy."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class SourceEvidence:
    content: str
    source_url: str
    trust_score: float = 0.7
    recency_score: float = 0.7

    def initial_confidence(self) -> float:
        """Map evidence quality to a bounded initial confidence."""
        raw = (self.trust_score * 0.6) + (self.recency_score * 0.4)
        return min(0.95, max(0.05, raw))


class WikipediaRetriever:
    """Fetch concise summaries from Wikipedia REST API."""

    API_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary/"

    def fetch_summary(self, topic: str) -> SourceEvidence:
        encoded = urllib.parse.quote(topic.replace(" ", "_"), safe="")
        url = f"{self.API_BASE}{encoded}"
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        content = payload.get("extract") or payload.get("description") or topic
        canonical_url = payload.get("content_urls", {}).get("desktop", {}).get("page", url)
        return SourceEvidence(
            content=content,
            source_url=canonical_url,
            trust_score=0.85,
            recency_score=0.7,
        )


class WebRetriever:
    """Basic text extractor for arbitrary websites (prototype-level)."""

    def fetch_text(self, url: str, max_chars: int = 1200) -> SourceEvidence:
        with urllib.request.urlopen(url, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")

        stripped = re.sub(r"<[^>]+>", " ", html)
        normalized = re.sub(r"\s+", " ", stripped).strip()
        excerpt = normalized[:max_chars]

        return SourceEvidence(
            content=excerpt,
            source_url=url,
            trust_score=0.6,
            recency_score=0.6,
        )
