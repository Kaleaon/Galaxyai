"""Tests for gma.structures"""

import pytest

from gma.structures import (
    Filament,
    GalacticCore,
    Particle,
    Planet,
    Star,
    StarSystem,
)


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------

class TestParticle:
    def test_default_weight(self):
        p = Particle()
        assert p.weight == 0.0

    def test_custom_weight(self):
        p = Particle(weight=0.42)
        assert p.weight == pytest.approx(0.42)

    def test_unique_ids(self):
        a, b = Particle(), Particle()
        assert a.particle_id != b.particle_id


# ---------------------------------------------------------------------------
# Planet
# ---------------------------------------------------------------------------

class TestPlanet:
    def test_orbital_radius_from_confidence(self):
        planet = Planet(content="test", confidence=0.5)
        assert planet.orbital_radius == pytest.approx(2.0)

    def test_high_confidence_tight_orbit(self):
        planet = Planet(content="test", confidence=1.0)
        assert planet.orbital_radius == pytest.approx(1.0)

    def test_zero_confidence_infinite_orbit(self):
        planet = Planet(content="test", confidence=0.0)
        assert planet.orbital_radius == float("inf")

    def test_update_confidence(self):
        planet = Planet(content="test", confidence=0.5)
        planet.update_confidence(0.8)
        assert planet.confidence == pytest.approx(0.8)
        assert planet.orbital_radius == pytest.approx(1.0 / 0.8)

    def test_update_confidence_invalid(self):
        planet = Planet(content="test")
        with pytest.raises(ValueError):
            planet.update_confidence(1.5)
        with pytest.raises(ValueError):
            planet.update_confidence(-0.1)

    def test_gravitational_influence_normal(self):
        planet = Planet(content="test", confidence=0.7)
        assert planet.gravitational_influence() == pytest.approx(0.7)

    def test_gravitational_influence_falsified(self):
        planet = Planet(content="test", confidence=0.0)
        assert planet.gravitational_influence() == 0.0

    def test_unique_ids(self):
        a = Planet(content="fact A")
        b = Planet(content="fact B")
        assert a.planet_id != b.planet_id


# ---------------------------------------------------------------------------
# Star
# ---------------------------------------------------------------------------

class TestStar:
    def test_default_mass(self):
        star = Star(name="Geography")
        assert star.mass == pytest.approx(1.0)

    def test_gravitational_influence(self):
        star = Star(name="Physics", mass=3.0)
        assert star.gravitational_influence() == pytest.approx(3.0)

    def test_unique_ids(self):
        a = Star(name="A")
        b = Star(name="B")
        assert a.star_id != b.star_id


# ---------------------------------------------------------------------------
# StarSystem
# ---------------------------------------------------------------------------

class TestStarSystem:
    def _make_system(self) -> StarSystem:
        return StarSystem(star=Star(name="Geography", mass=2.0))

    def test_add_and_find_planet(self):
        system = self._make_system()
        planet = Planet(content="Paris is in France", confidence=0.9)
        system.add_planet(planet)
        found = system.find_planet_by_content("Paris is in France")
        assert found is planet

    def test_find_planet_missing(self):
        system = self._make_system()
        assert system.find_planet_by_content("unknown") is None

    def test_remove_planet(self):
        system = self._make_system()
        planet = Planet(content="test")
        system.add_planet(planet)
        removed = system.remove_planet(planet.planet_id)
        assert removed is planet
        assert system.find_planet_by_content("test") is None

    def test_remove_missing_planet(self):
        system = self._make_system()
        assert system.remove_planet("nonexistent") is None

    def test_total_mass(self):
        system = self._make_system()
        planet = Planet(content="test", confidence=0.4)
        system.add_planet(planet)
        expected = 2.0 + 0.4
        assert system.total_mass() == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Filament
# ---------------------------------------------------------------------------

class TestFilament:
    def test_reinforce(self):
        f = Filament(system_a_id="a", system_b_id="b", concept="climate", strength=0.5)
        f.reinforce(0.1)
        assert f.strength == pytest.approx(0.6)

    def test_reinforce_capped_at_one(self):
        f = Filament(system_a_id="a", system_b_id="b", concept="climate", strength=0.98)
        f.reinforce(0.1)
        assert f.strength == pytest.approx(1.0)

    def test_weaken(self):
        f = Filament(system_a_id="a", system_b_id="b", concept="climate", strength=0.5)
        f.weaken(0.1)
        assert f.strength == pytest.approx(0.4)

    def test_weaken_floored_at_zero(self):
        f = Filament(system_a_id="a", system_b_id="b", concept="climate", strength=0.02)
        f.weaken(0.1)
        assert f.strength == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# GalacticCore
# ---------------------------------------------------------------------------

class TestGalacticCore:
    def test_immovable_priors_present(self):
        core = GalacticCore()
        for prior in GalacticCore._IMMOVABLE_PRIORS:
            assert prior in core.priors
            assert core.priors[prior] == pytest.approx(1.0)

    def test_is_immovable(self):
        core = GalacticCore()
        assert core.is_immovable("logical_consistency")
        assert not core.is_immovable("some_custom_prior")

    def test_add_prior(self):
        core = GalacticCore()
        core.add_prior("ethics", 0.9)
        assert core.priors["ethics"] == pytest.approx(0.9)

    def test_add_prior_invalid(self):
        core = GalacticCore()
        with pytest.raises(ValueError):
            core.add_prior("ethics", 1.5)

    def test_mass(self):
        core = GalacticCore()
        expected = float(len(GalacticCore._IMMOVABLE_PRIORS))
        assert core.mass == pytest.approx(expected)
