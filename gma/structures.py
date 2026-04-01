"""
gma.structures
==============
Core data-structures that model the galactic hierarchy.

Hierarchy (smallest → largest):
    Particle → Planet → Star → StarSystem → Galaxy
                                      ↕
                                  Filament (cross-system bridge)
                                      ↕
                                GalacticCore (immovable identity anchor)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------

@dataclass
class Particle:
    """The smallest unit — analogous to a single weight parameter.

    Attributes:
        weight: Numerical value of this parameter.
        particle_id: Unique identifier (auto-generated).
    """

    weight: float = 0.0
    particle_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __repr__(self) -> str:  # pragma: no cover
        return f"Particle(id={self.particle_id[:8]}, weight={self.weight:.4f})"


# ---------------------------------------------------------------------------
# Planet  (Fact Cluster)
# ---------------------------------------------------------------------------

@dataclass
class Planet:
    """A coherent grouping of weights encoding a single piece of knowledge.

    The *orbital_radius* encodes epistemic certainty:
      - Small radius  → high confidence, strong influence on inference.
      - Large radius  → provisional knowledge, low influence.
      - Radius == inf → fact has crossed the event horizon (falsified).

    Attributes:
        content: Human-readable statement of the fact.
        confidence: Confidence score in [0, 1].  Maps to 1/orbital_radius.
        orbital_radius: Derived from confidence (set automatically).
        particles: Low-level weight particles that constitute this fact.
        planet_id: Unique identifier.
    """

    content: str
    confidence: float = 0.5
    particles: List[Particle] = field(default_factory=list)
    planet_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Derived; updated whenever confidence changes.
    orbital_radius: float = field(init=False)

    def __post_init__(self) -> None:
        self._update_orbital_radius()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_confidence(self, new_confidence: float) -> None:
        """Update confidence and recalculate orbital radius."""
        if not 0.0 <= new_confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {new_confidence}")
        self.confidence = new_confidence
        self._update_orbital_radius()

    def gravitational_influence(self) -> float:
        """Return the gravitational pull this planet exerts on nearby inference.

        High confidence → high influence.  Falsified facts return 0.
        """
        if self.orbital_radius == float("inf"):
            return 0.0
        return self.confidence

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _update_orbital_radius(self) -> None:
        if self.confidence <= 0.0:
            self.orbital_radius = float("inf")
        else:
            # Radius is inversely proportional to confidence.
            self.orbital_radius = 1.0 / self.confidence

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Planet(id={self.planet_id[:8]}, "
            f"confidence={self.confidence:.2f}, "
            f"content={self.content!r})"
        )


# ---------------------------------------------------------------------------
# Star  (Concept Anchor)
# ---------------------------------------------------------------------------

@dataclass
class Star:
    """A higher-order attractor around which fact clusters orbit.

    Stars have significantly more gravitational influence than planets.
    They define the topology of their local region.

    Attributes:
        name: Human-readable concept label (e.g. "Geography").
        mass: Relative gravitational mass — higher mass → stronger pull.
        star_id: Unique identifier.
    """

    name: str
    mass: float = 1.0
    star_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def gravitational_influence(self) -> float:
        """Return the gravitational pull this star exerts."""
        return self.mass

    def __repr__(self) -> str:  # pragma: no cover
        return f"Star(name={self.name!r}, mass={self.mass:.2f})"


# ---------------------------------------------------------------------------
# StarSystem  (Knowledge Domain)
# ---------------------------------------------------------------------------

class StarSystem:
    """A star and its orbiting planets — a full knowledge domain.

    The system has emergent properties: inference patterns, reasoning chains,
    and default assumptions arise from the gravitational relationships between
    its components.

    Attributes:
        star: The central concept anchor.
        planets: Fact clusters orbiting the star.
        system_id: Unique identifier.
    """

    def __init__(self, star: Star) -> None:
        self.star: Star = star
        self.planets: Dict[str, Planet] = {}
        self.system_id: str = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_planet(self, planet: Planet) -> None:
        """Add a fact cluster to this star system."""
        self.planets[planet.planet_id] = planet

    def remove_planet(self, planet_id: str) -> Optional[Planet]:
        """Remove and return a planet by ID (returns None if not found)."""
        return self.planets.pop(planet_id, None)

    def total_mass(self) -> float:
        """Return the total gravitational mass of the system.

        The star's mass plus the summed confidence of all orbiting planets.
        """
        planet_mass = sum(p.confidence for p in self.planets.values())
        return self.star.mass + planet_mass

    def find_planet_by_content(self, content: str) -> Optional[Planet]:
        """Return the first planet whose content matches *content* (exact)."""
        for planet in self.planets.values():
            if planet.content == content:
                return planet
        return None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StarSystem(star={self.star.name!r}, "
            f"planets={len(self.planets)}, "
            f"total_mass={self.total_mass():.2f})"
        )


# ---------------------------------------------------------------------------
# Filament  (Domain Bridge)
# ---------------------------------------------------------------------------

@dataclass
class Filament:
    """A cross-domain bridge connecting two star systems.

    Just as galactic filaments connect galaxy clusters through shared matter,
    GMA filaments connect knowledge domains through bridging concepts.

    Attributes:
        system_a_id: ID of the first star system.
        system_b_id: ID of the second star system.
        concept: The bridging concept label.
        strength: How strongly the domains are linked (0–1).
        filament_id: Unique identifier.
    """

    system_a_id: str
    system_b_id: str
    concept: str
    strength: float = 0.5
    filament_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def reinforce(self, delta: float = 0.05) -> None:
        """Strengthen this filament, capped at 1.0."""
        self.strength = min(1.0, self.strength + delta)

    def weaken(self, delta: float = 0.05) -> None:
        """Weaken this filament, floored at 0.0."""
        self.strength = max(0.0, self.strength - delta)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Filament(concept={self.concept!r}, "
            f"strength={self.strength:.2f})"
        )


# ---------------------------------------------------------------------------
# GalacticCore  (Identity / Ground Truth)
# ---------------------------------------------------------------------------

class GalacticCore:
    """The densest region of the galaxy — fundamental priors and identity.

    Contains the model's most fundamental priors:
      - Logical consistency
      - Causal reasoning
      - Core identity

    Extremely high gravitational influence; hardest to perturb.
    In EWC terms, these are the *high-Fisher* weights that resist change.

    Attributes:
        priors: Mapping of prior name → confidence value.
        mass: Effective gravitational mass of the core (sum of prior confidences).
    """

    # The core starts with these immovable logical priors.
    _IMMOVABLE_PRIORS: tuple = (
        "logical_consistency",
        "causal_reasoning",
        "non_contradiction",
    )

    def __init__(self) -> None:
        self.priors: Dict[str, float] = {p: 1.0 for p in self._IMMOVABLE_PRIORS}

    @property
    def mass(self) -> float:
        """Total gravitational mass of the core."""
        return sum(self.priors.values())

    def add_prior(self, name: str, confidence: float = 1.0) -> None:
        """Add or update an identity prior."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {confidence}")
        self.priors[name] = confidence

    def is_immovable(self, name: str) -> bool:
        """Return True if *name* is one of the protected foundational priors."""
        return name in self._IMMOVABLE_PRIORS

    def gravitational_influence(self) -> float:
        """Return the total gravitational influence of the core."""
        return self.mass

    def __repr__(self) -> str:  # pragma: no cover
        return f"GalacticCore(priors={len(self.priors)}, mass={self.mass:.2f})"
