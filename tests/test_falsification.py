"""Tests for gma.falsification"""

import pytest

from gma.falsification import CapturedFact, FalsificationSink, FalsificationState
from gma.structures import Planet


def make_planet(content: str = "test fact", confidence: float = 0.8) -> Planet:
    return Planet(content=content, confidence=confidence)


class TestFalsificationSink:
    def test_default_state_is_stable(self):
        sink = FalsificationSink()
        planet = make_planet()
        assert sink.get_state(planet.planet_id) == FalsificationState.STABLE

    def test_challenge_moves_to_accretion_disk(self):
        sink = FalsificationSink()
        planet = make_planet(confidence=0.8)
        state = sink.challenge(planet)
        assert state == FalsificationState.ACCRETION_DISK

    def test_repeated_challenges_reduce_confidence(self):
        sink = FalsificationSink()
        planet = make_planet(confidence=0.8)
        initial_confidence = planet.confidence
        sink.challenge(planet)
        assert planet.confidence < initial_confidence

    def test_crosses_event_horizon_when_confidence_low(self):
        sink = FalsificationSink(event_horizon_threshold=0.3, maturity_factor=3.0)
        planet = make_planet(confidence=0.4)
        state = sink.challenge(planet)
        assert state == FalsificationState.BEYOND_EVENT_HORIZON
        assert sink.is_beyond_event_horizon(planet.planet_id)

    def test_captured_planet_returns_beyond_event_horizon(self):
        sink = FalsificationSink(event_horizon_threshold=0.3, maturity_factor=3.0)
        planet = make_planet(confidence=0.4)
        sink.challenge(planet)
        # Challenging again should still return BEYOND_EVENT_HORIZON
        state = sink.challenge(planet)
        assert state == FalsificationState.BEYOND_EVENT_HORIZON

    def test_accretion_disk_contents(self):
        sink = FalsificationSink()
        planet = make_planet(confidence=0.9)
        sink.challenge(planet)
        disk = sink.accretion_disk_contents()
        assert len(disk) == 1
        assert disk[0].planet is planet

    def test_captured_contents(self):
        sink = FalsificationSink(event_horizon_threshold=0.3, maturity_factor=3.0)
        planet = make_planet(confidence=0.4)
        sink.challenge(planet)
        captured = sink.captured_contents()
        assert len(captured) == 1
        assert captured[0].planet is planet

    def test_beyond_event_horizon_not_in_disk(self):
        sink = FalsificationSink(event_horizon_threshold=0.3, maturity_factor=3.0)
        planet = make_planet(confidence=0.4)
        sink.challenge(planet)
        assert len(sink.accretion_disk_contents()) == 0

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            FalsificationSink(event_horizon_threshold=0.0)
        with pytest.raises(ValueError):
            FalsificationSink(event_horizon_threshold=1.0)

    def test_set_maturity_factor(self):
        sink = FalsificationSink()
        sink.set_maturity_factor(2.5)
        assert sink.maturity_factor == pytest.approx(2.5)

    def test_set_invalid_maturity_factor_raises(self):
        sink = FalsificationSink()
        with pytest.raises(ValueError):
            sink.set_maturity_factor(0.0)
        with pytest.raises(ValueError):
            sink.set_maturity_factor(-1.0)

    def test_higher_maturity_faster_capture(self):
        """Higher maturity factor should push a planet across event horizon faster."""
        sink_slow = FalsificationSink(maturity_factor=0.5)
        sink_fast = FalsificationSink(maturity_factor=2.0)
        planet_slow = make_planet(confidence=0.4)
        planet_fast = make_planet(confidence=0.4)
        sink_slow.challenge(planet_slow)
        sink_fast.challenge(planet_fast)
        # Fast sink applies more decay
        assert planet_fast.confidence <= planet_slow.confidence

    def test_reason_stored(self):
        sink = FalsificationSink()
        planet = make_planet(confidence=0.9)
        sink.challenge(planet, reason="New evidence contradicts this")
        disk = sink.accretion_disk_contents()
        assert disk[0].reason == "New evidence contradicts this"
