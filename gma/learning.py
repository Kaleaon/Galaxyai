"""
gma.learning
============
Continuous learning via gravitational accretion dynamics.

New information enters the galaxy as low-confidence "dust" and accretes
toward the star system with the strongest relevance pull, gaining confidence
through validation against existing knowledge.

    Dust → Accretion → Orbital Stabilisation → Planet

The AccretionEngine is responsible for:
  1. Receiving new raw information (dust).
  2. Routing it to the most relevant StarSystem.
  3. Integrating it: raising confidence until a stable orbit is achieved.
  4. Detecting contradictions and triggering the FalsificationSink.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING, Tuple

from gma.structures import Planet, Star, StarSystem

if TYPE_CHECKING:
    from gma.falsification import FalsificationSink


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DUST_INITIAL_CONFIDENCE: float = 0.1
"""New information enters with near-zero confidence."""

ACCRETION_CONFIDENCE_GAIN: float = 0.1
"""Confidence gained per accretion cycle when new fact is compatible."""

STABLE_ORBIT_THRESHOLD: float = 0.6
"""Confidence required for a fact to be considered in a stable orbit."""

CONTRADICTION_CONFIDENCE_PENALTY: float = 0.2
"""Confidence decay applied to an existing fact when contradicted."""


# ---------------------------------------------------------------------------
# DustParcel  (raw unintegrated information)
# ---------------------------------------------------------------------------

@dataclass
class DustParcel:
    """A piece of raw unintegrated information.

    Attributes:
        content: Human-readable statement of the fact.
        domain_hint: Optional hint for which domain this belongs to.
        confidence: Initial confidence (low by default).
        contradicts: Content string of the fact this contradicts (if any).
    """

    content: str
    domain_hint: Optional[str] = None
    confidence: float = DUST_INITIAL_CONFIDENCE
    contradicts: Optional[str] = None


# ---------------------------------------------------------------------------
# AccretionEngine
# ---------------------------------------------------------------------------

class AccretionEngine:
    """Routes new knowledge to appropriate star systems and integrates it.

    Attributes:
        systems: Registered star systems keyed by domain name.
        falsification_sink: Optional sink for contradicted facts.
    """

    def __init__(
        self,
        falsification_sink: Optional["FalsificationSink"] = None,
    ) -> None:
        self.systems: Dict[str, StarSystem] = {}
        self.falsification_sink = falsification_sink

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_system(
        self,
        domain: str,
        star_mass: float = 1.0,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> StarSystem:
        """Create and register a new star system for *domain*.

        If a system for *domain* already exists, return it unchanged.
        """
        if domain not in self.systems:
            star = Star(name=domain, mass=star_mass)
            self.systems[domain] = StarSystem(star=star, position=position)
        return self.systems[domain]

    def get_system(self, domain: str) -> Optional[StarSystem]:
        """Return the star system for *domain*, or None if not registered."""
        return self.systems.get(domain)

    # ------------------------------------------------------------------
    # Accretion
    # ------------------------------------------------------------------

    def ingest(self, dust: DustParcel) -> Planet:
        """Integrate a DustParcel into the galaxy.

        Steps:
          1. Determine the target star system.
          2. Handle any contradiction (lower existing planet's confidence).
          3. Create a new Planet and add it to the system.
          4. Apply accretion cycles until stable orbit is achieved.

        Returns:
            The newly accreted Planet.
        """
        system = self._route(dust)

        # Handle contradiction before integrating new fact.
        if dust.contradicts:
            self._handle_contradiction(system, contradicted_content=dust.contradicts)

        planet = Planet(content=dust.content, confidence=dust.confidence)
        system.add_planet(planet)

        # Accretion cycles: raise confidence until stable orbit.
        self._accrete(planet)

        return planet

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _route(self, dust: DustParcel) -> StarSystem:
        """Route dust to the most appropriate star system.

        If a domain hint is provided and a matching system exists, use it.
        Otherwise fall back to the system with the highest total mass
        (strongest gravitational pull).  If no systems exist, create a
        default one.
        """
        if dust.domain_hint and dust.domain_hint in self.systems:
            return self.systems[dust.domain_hint]

        if self.systems:
            return max(self.systems.values(), key=lambda s: s.total_mass())

        # No systems registered — create a default one.
        return self.register_system(dust.domain_hint or "general")

    def _accrete(self, planet: Planet) -> None:
        """Raise planet confidence until it reaches a stable orbit."""
        while planet.confidence < STABLE_ORBIT_THRESHOLD:
            new_confidence = min(
                STABLE_ORBIT_THRESHOLD,
                planet.confidence + ACCRETION_CONFIDENCE_GAIN,
            )
            planet.update_confidence(new_confidence)

    def _handle_contradiction(
        self,
        system: StarSystem,
        contradicted_content: str,
    ) -> None:
        """Lower confidence of the contradicted fact and challenge it."""
        existing = system.find_planet_by_content(contradicted_content)
        if existing is None:
            return

        new_confidence = max(0.0, existing.confidence - CONTRADICTION_CONFIDENCE_PENALTY)
        existing.update_confidence(new_confidence)

        if self.falsification_sink is not None:
            self.falsification_sink.challenge(
                existing,
                reason=f"Contradicted by new information",
            )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AccretionEngine("
            f"systems={list(self.systems.keys())}, "
            f"sink={'yes' if self.falsification_sink else 'no'})"
        )
