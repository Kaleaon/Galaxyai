"""Tests for gma.galaxy (Galaxy top-level orchestrator)"""

import pytest

from gma.falsification import FalsificationState
from gma.galaxy import Galaxy
from gma.structures import StarSystem


class TestGalaxy:
    # ------------------------------------------------------------------
    # Domain management
    # ------------------------------------------------------------------

    def test_register_domain(self):
        g = Galaxy()
        system = g.register_domain("geography")
        assert isinstance(system, StarSystem)

    def test_get_domain_registered(self):
        g = Galaxy()
        g.register_domain("geography")
        assert g.get_domain("geography") is not None

    def test_get_domain_unregistered(self):
        g = Galaxy()
        assert g.get_domain("unknown") is None

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def test_ingest_basic(self):
        g = Galaxy()
        g.register_domain("geography")
        planet = g.ingest("Paris is the capital of France", domain="geography")
        assert planet.content == "Paris is the capital of France"

    def test_ingest_accretes_to_stable_orbit(self):
        from gma.learning import STABLE_ORBIT_THRESHOLD
        g = Galaxy()
        g.register_domain("geography")
        planet = g.ingest("Paris is the capital of France", domain="geography")
        assert planet.confidence >= STABLE_ORBIT_THRESHOLD

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def test_query_finds_planet(self):
        g = Galaxy()
        g.register_domain("geography")
        g.ingest("Paris is the capital of France", domain="geography")
        results = g.query("Paris")
        assert len(results) == 1
        assert "Paris" in results[0].content

    def test_query_excludes_beyond_event_horizon(self):
        g = Galaxy()
        g.register_domain("geography")
        planet = g.ingest("Paris is the capital of Germany", domain="geography")
        # Force the planet across the event horizon.
        g.sink.event_horizon_threshold = 0.99
        g.sink.challenge(planet, reason="test")
        results = g.query("Germany")
        assert all(p.planet_id != planet.planet_id for p in results)

    def test_query_case_insensitive(self):
        g = Galaxy()
        g.register_domain("geography")
        g.ingest("Paris is the capital of France", domain="geography")
        results = g.query("paris")
        assert len(results) >= 1

    def test_query_by_domain(self):
        g = Galaxy()
        g.register_domain("geography")
        g.register_domain("science")
        g.ingest("Paris is the capital of France", domain="geography")
        g.ingest("Water boils at 100C", domain="science")
        geo_results = g.query("Paris", domain="geography")
        assert all("Paris" in p.content for p in geo_results)
        sci_results = g.query("Paris", domain="science")
        assert len(sci_results) == 0

    def test_query_sorted_by_confidence(self):
        g = Galaxy()
        g.register_domain("geography")
        g.ingest("Paris is the capital of France", domain="geography")
        g.ingest("Paris has the Eiffel Tower", domain="geography")
        results = g.query("Paris")
        confidences = [p.confidence for p in results]
        assert confidences == sorted(confidences, reverse=True)

    # ------------------------------------------------------------------
    # Falsification
    # ------------------------------------------------------------------

    def test_falsify_known_fact(self):
        g = Galaxy()
        g.register_domain("geography")
        g.ingest("Paris is the capital of Germany", domain="geography")
        state = g.falsify("Paris is the capital of Germany", domain="geography")
        assert state != FalsificationState.STABLE

    def test_falsify_unknown_fact_returns_stable(self):
        g = Galaxy()
        state = g.falsify("This fact does not exist")
        assert state == FalsificationState.STABLE

    def test_ingest_with_contradiction(self):
        g = Galaxy()
        g.register_domain("geography")
        old = g.ingest("Paris is the capital of Germany", domain="geography")
        old_confidence = old.confidence
        g.ingest(
            "Paris is the capital of France",
            domain="geography",
            contradicts="Paris is the capital of Germany",
        )
        assert old.confidence < old_confidence

    # ------------------------------------------------------------------
    # Filaments
    # ------------------------------------------------------------------

    def test_add_filament(self):
        g = Galaxy()
        g.register_domain("geography")
        g.register_domain("thermodynamics")
        filament = g.add_filament("geography", "thermodynamics", concept="climate")
        assert filament is not None
        assert filament.concept == "climate"

    def test_add_filament_missing_domain_returns_none(self):
        g = Galaxy()
        g.register_domain("geography")
        result = g.add_filament("geography", "nonexistent", concept="test")
        assert result is None

    def test_add_filament_idempotent(self):
        g = Galaxy()
        g.register_domain("geography")
        g.register_domain("thermodynamics")
        f1 = g.add_filament("geography", "thermodynamics", concept="climate")
        f2 = g.add_filament("geography", "thermodynamics", concept="climate")
        assert f1 is f2

    # ------------------------------------------------------------------
    # Identity / Core
    # ------------------------------------------------------------------

    def test_add_identity_prior(self):
        g = Galaxy()
        g.add_identity_prior("ethics", confidence=0.95)
        assert "ethics" in g.core.priors

    def test_core_immovable_priors_always_present(self):
        g = Galaxy()
        from gma.structures import GalacticCore
        for prior in GalacticCore._IMMOVABLE_PRIORS:
            assert prior in g.core.priors

    # ------------------------------------------------------------------
    # Maturity
    # ------------------------------------------------------------------

    def test_maturity_level_default(self):
        g = Galaxy()
        assert g.maturity_level() == pytest.approx(1.0)

    def test_increase_maturity(self):
        g = Galaxy()
        g.increase_maturity(0.5)
        assert g.maturity_level() == pytest.approx(1.5)
