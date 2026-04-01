"""Tests for gma.learning (AccretionEngine)"""

import pytest

from gma.falsification import FalsificationSink, FalsificationState
from gma.learning import (
    STABLE_ORBIT_THRESHOLD,
    AccretionEngine,
    DustParcel,
)
from gma.structures import StarSystem


class TestAccretionEngine:
    def test_register_system(self):
        engine = AccretionEngine()
        system = engine.register_system("geography")
        assert isinstance(system, StarSystem)
        assert system.star.name == "geography"

    def test_register_system_idempotent(self):
        engine = AccretionEngine()
        s1 = engine.register_system("geography")
        s2 = engine.register_system("geography")
        assert s1 is s2

    def test_get_system_none_when_missing(self):
        engine = AccretionEngine()
        assert engine.get_system("unknown") is None

    def test_ingest_creates_planet(self):
        engine = AccretionEngine()
        engine.register_system("geography")
        dust = DustParcel(content="Paris is the capital of France", domain_hint="geography")
        planet = engine.ingest(dust)
        assert planet.content == "Paris is the capital of France"

    def test_ingest_reaches_stable_orbit(self):
        engine = AccretionEngine()
        engine.register_system("geography")
        dust = DustParcel(content="Paris is the capital of France", domain_hint="geography")
        planet = engine.ingest(dust)
        assert planet.confidence >= STABLE_ORBIT_THRESHOLD

    def test_ingest_without_domain_hint_creates_default_system(self):
        engine = AccretionEngine()
        dust = DustParcel(content="Some fact")
        planet = engine.ingest(dust)
        assert planet.confidence >= STABLE_ORBIT_THRESHOLD
        assert "general" in engine.systems

    def test_ingest_routes_to_heaviest_system_without_hint(self):
        engine = AccretionEngine()
        engine.register_system("light_domain", star_mass=0.5)
        engine.register_system("heavy_domain", star_mass=5.0)
        dust = DustParcel(content="Some fact")
        engine.ingest(dust)
        heavy = engine.get_system("heavy_domain")
        assert len(heavy.planets) == 1

    def test_contradiction_reduces_existing_confidence(self):
        engine = AccretionEngine()
        engine.register_system("geography")
        old_dust = DustParcel(
            content="Paris is the capital of Germany",
            domain_hint="geography",
        )
        old_planet = engine.ingest(old_dust)
        old_confidence = old_planet.confidence

        new_dust = DustParcel(
            content="Paris is the capital of France",
            domain_hint="geography",
            contradicts="Paris is the capital of Germany",
        )
        engine.ingest(new_dust)
        assert old_planet.confidence < old_confidence

    def test_contradiction_triggers_falsification_sink(self):
        sink = FalsificationSink()
        engine = AccretionEngine(falsification_sink=sink)
        engine.register_system("geography")

        old_dust = DustParcel(
            content="Paris is the capital of Germany",
            domain_hint="geography",
        )
        old_planet = engine.ingest(old_dust)

        new_dust = DustParcel(
            content="Paris is the capital of France",
            domain_hint="geography",
            contradicts="Paris is the capital of Germany",
        )
        engine.ingest(new_dust)

        state = sink.get_state(old_planet.planet_id)
        # Planet should at minimum be challenged (ACCRETION_DISK or beyond).
        assert state != FalsificationState.STABLE

    def test_no_contradiction_when_content_absent(self):
        """Contradicting a non-existent fact should not raise an error."""
        engine = AccretionEngine()
        engine.register_system("geography")
        dust = DustParcel(
            content="Paris is the capital of France",
            domain_hint="geography",
            contradicts="This fact does not exist",
        )
        planet = engine.ingest(dust)
        assert planet is not None
