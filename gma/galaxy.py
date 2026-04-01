"""
gma.galaxy
==========
Top-level Galaxy orchestrator.

The Galaxy is the entry-point for all interactions with the GMA.  It wires
together:
  - GalacticCore   (immovable identity anchors)
  - StarSystems    (knowledge domains, managed via AccretionEngine)
  - Filaments      (cross-domain bridges)
  - FalsificationSink  (black hole for false / superseded knowledge)

Typical usage::

    from gma import Galaxy

    g = Galaxy()
    g.register_domain("geography", star_mass=2.0)
    g.ingest("Paris is the capital of France", domain="geography")
    g.falsify("Paris is the capital of Germany", domain="geography")

    result = g.query("capital of France")
    print(result)
"""

from __future__ import annotations

from typing import Dict, List, Optional

from gma.falsification import FalsificationSink, FalsificationState
from gma.learning import AccretionEngine, DustParcel
from gma.structures import Filament, GalacticCore, Planet, StarSystem


class Galaxy:
    """Top-level orchestrator for the Galactic Memory Architecture.

    Attributes:
        core: The immovable identity / ground-truth anchor.
        sink: The falsification sink (black hole).
        engine: The accretion engine responsible for integrating new facts.
        filaments: Cross-domain bridges keyed by ``(system_a_id, system_b_id)``.
    """

    def __init__(
        self,
        event_horizon_threshold: float = FalsificationSink.DEFAULT_EVENT_HORIZON_THRESHOLD,
        maturity_factor: float = 1.0,
    ) -> None:
        self.core = GalacticCore()
        self.sink = FalsificationSink(
            event_horizon_threshold=event_horizon_threshold,
            maturity_factor=maturity_factor,
        )
        self.engine = AccretionEngine(falsification_sink=self.sink)
        self.filaments: Dict[tuple, Filament] = {}

    # ------------------------------------------------------------------
    # Domain management
    # ------------------------------------------------------------------

    def register_domain(self, domain: str, star_mass: float = 1.0) -> StarSystem:
        """Register a knowledge domain (star system).

        If the domain already exists, return the existing system.

        Args:
            domain: Human-readable domain name (e.g. "geography").
            star_mass: Initial gravitational mass of the domain star.

        Returns:
            The StarSystem for this domain.
        """
        return self.engine.register_system(domain, star_mass=star_mass)

    def get_domain(self, domain: str) -> Optional[StarSystem]:
        """Return the StarSystem for *domain*, or None if not registered."""
        return self.engine.get_system(domain)

    # ------------------------------------------------------------------
    # Knowledge ingestion
    # ------------------------------------------------------------------

    def ingest(
        self,
        content: str,
        domain: Optional[str] = None,
        initial_confidence: float = 0.1,
        contradicts: Optional[str] = None,
    ) -> Planet:
        """Ingest a new fact into the galaxy.

        The fact enters as low-confidence dust and accretes toward the target
        domain.  If it contradicts an existing fact, that fact's confidence is
        reduced and it is challenged in the falsification sink.

        Args:
            content: Human-readable fact statement.
            domain: Target domain hint (routed automatically if omitted).
            initial_confidence: Starting confidence before accretion.
            contradicts: Content of an existing fact this new fact contradicts.

        Returns:
            The accreted Planet.
        """
        dust = DustParcel(
            content=content,
            domain_hint=domain,
            confidence=initial_confidence,
            contradicts=contradicts,
        )
        return self.engine.ingest(dust)

    # ------------------------------------------------------------------
    # Falsification
    # ------------------------------------------------------------------

    def falsify(
        self,
        content: str,
        domain: Optional[str] = None,
        reason: str = "",
    ) -> FalsificationState:
        """Directly challenge a fact and begin the falsification process.

        Args:
            content: The fact statement to falsify.
            domain: Domain to search in (searches all domains if omitted).
            reason: Human-readable reason for the challenge.

        Returns:
            The new FalsificationState of the challenged fact.
        """
        planet = self._find_planet(content, domain)
        if planet is None:
            return FalsificationState.STABLE
        return self.sink.challenge(planet, reason=reason)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def query(
        self,
        keyword: str,
        domain: Optional[str] = None,
        include_uncertain: bool = False,
    ) -> List[Planet]:
        """Return planets whose content contains *keyword*.

        Planets that have crossed the event horizon are always excluded.
        Planets in the accretion disk (uncertain) are excluded by default;
        set ``include_uncertain=True`` to include them.

        Args:
            keyword: Substring to search for in planet content.
            domain: Restrict search to this domain (searches all if omitted).
            include_uncertain: Whether to include accretion-disk planets.

        Returns:
            List of matching Planet objects, sorted by confidence descending.
        """
        results: List[Planet] = []
        systems = (
            [self.engine.get_system(domain)]
            if domain and self.engine.get_system(domain)
            else list(self.engine.systems.values())
        )

        for system in systems:
            if system is None:
                continue
            for planet in system.planets.values():
                if keyword.lower() not in planet.content.lower():
                    continue
                state = self.sink.get_state(planet.planet_id)
                if state == FalsificationState.BEYOND_EVENT_HORIZON:
                    continue
                if state == FalsificationState.ACCRETION_DISK and not include_uncertain:
                    continue
                results.append(planet)

        return sorted(results, key=lambda p: p.confidence, reverse=True)

    # ------------------------------------------------------------------
    # Filaments
    # ------------------------------------------------------------------

    def add_filament(
        self,
        domain_a: str,
        domain_b: str,
        concept: str,
        strength: float = 0.5,
    ) -> Optional[Filament]:
        """Create a cross-domain bridge between *domain_a* and *domain_b*.

        Returns None if either domain is not registered.
        """
        sys_a = self.engine.get_system(domain_a)
        sys_b = self.engine.get_system(domain_b)
        if sys_a is None or sys_b is None:
            return None

        key = (sys_a.system_id, sys_b.system_id)
        if key not in self.filaments:
            self.filaments[key] = Filament(
                system_a_id=sys_a.system_id,
                system_b_id=sys_b.system_id,
                concept=concept,
                strength=strength,
            )
        return self.filaments[key]

    # ------------------------------------------------------------------
    # Identity / Core
    # ------------------------------------------------------------------

    def add_identity_prior(self, name: str, confidence: float = 1.0) -> None:
        """Add or update an identity prior in the galactic core."""
        self.core.add_prior(name, confidence)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def maturity_level(self) -> float:
        """Return the current maturity factor of the falsification sink."""
        return self.sink.maturity_factor

    def increase_maturity(self, delta: float = 0.1) -> None:
        """Increase the maturity factor, steepening the falsification gradient.

        As the model matures it becomes better at distinguishing truth from
        falsehood because the gradient steepens automatically.
        """
        self.sink.set_maturity_factor(self.sink.maturity_factor + delta)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_planet(
        self,
        content: str,
        domain: Optional[str] = None,
    ) -> Optional[Planet]:
        """Find a planet by exact content match across specified or all domains."""
        systems = (
            [self.engine.get_system(domain)]
            if domain and self.engine.get_system(domain)
            else list(self.engine.systems.values())
        )
        for system in systems:
            if system is None:
                continue
            planet = system.find_planet_by_content(content)
            if planet is not None:
                return planet
        return None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Galaxy("
            f"domains={list(self.engine.systems.keys())}, "
            f"core_mass={self.core.mass:.2f}, "
            f"maturity={self.sink.maturity_factor:.2f})"
        )
