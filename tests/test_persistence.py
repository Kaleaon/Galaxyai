"""Tests for persistence repositories and adapter selection."""

from __future__ import annotations

import os

import pytest

from gma.falsification import CapturedFact, FalsificationState
from gma.infrastructure.persistence import get_persistence_adapter
from gma.infrastructure.persistence.postgres_adapter import create_postgres_repository, psycopg
from gma.infrastructure.persistence.sqlite_adapter import create_sqlite_repository
from gma.structures import Filament, GalacticCore, Particle, Planet, Star, StarSystem


def _sample_system() -> StarSystem:
    star = Star(name="Geography", mass=2.5)
    system = StarSystem(star=star, position=(1.0, 2.0, 3.0))
    planet = Planet(
        content="Paris is the capital of France",
        confidence=0.9,
        particles=[Particle(weight=0.2), Particle(weight=0.5)],
    )
    system.add_planet(planet)
    return system


def test_sqlite_persists_star_system_and_planets():
    repo = create_sqlite_repository(":memory:")
    system = _sample_system()

    repo.save_star_system(system, metadata={"source": "unit-test"})
    loaded = repo.get_star_system(system.system_id)

    assert loaded is not None
    assert loaded.star.name == system.star.name
    assert loaded.position == pytest.approx(system.position)
    assert len(loaded.planets) == 1
    loaded_planet = next(iter(loaded.planets.values()))
    assert loaded_planet.content == "Paris is the capital of France"
    assert len(loaded_planet.particles) == 2


def test_sqlite_persists_filaments_and_core_and_falsification():
    repo = create_sqlite_repository(":memory:")

    filament = Filament(system_a_id="sys-a", system_b_id="sys-b", concept="climate", strength=0.7)
    repo.save_filament(filament, metadata={"tag": "bridge"})
    loaded_filament = repo.get_filament(filament.filament_id)
    assert loaded_filament is not None
    assert loaded_filament.concept == "climate"

    core = GalacticCore()
    core.add_prior("ethics", 0.8)
    repo.save_galactic_core(core, metadata={"version": 1})
    loaded_core = repo.load_galactic_core()
    assert loaded_core.priors["ethics"] == pytest.approx(0.8)

    planet = Planet(content="deprecated fact", confidence=0.2)
    captured = CapturedFact(planet=planet, reason="new evidence", state=FalsificationState.BEYOND_EVENT_HORIZON)
    repo.save_captured_fact(captured, metadata={"reviewer": "qa"})
    repo.record_transition(
        planet_id=planet.planet_id,
        from_state=FalsificationState.CONTESTED,
        to_state=FalsificationState.BEYOND_EVENT_HORIZON,
        reason="threshold reached",
    )


def test_env_selection_defaults_to_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path):
    db_path = tmp_path / "gma.sqlite"
    monkeypatch.delenv("GMA_PERSISTENCE_BACKEND", raising=False)
    monkeypatch.setenv("GMA_SQLITE_PATH", str(db_path))

    adapter = get_persistence_adapter()
    system = _sample_system()
    adapter.structures.save_star_system(system)

    loaded = adapter.structures.get_star_system(system.system_id)
    assert loaded is not None


def test_env_selection_postgres_missing_dsn_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GMA_PERSISTENCE_BACKEND", "postgres")
    monkeypatch.delenv("GMA_POSTGRES_DSN", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValueError, match="no DSN"):
        get_persistence_adapter()


@pytest.mark.integration
@pytest.mark.skipif(psycopg is None, reason="psycopg not installed")
def test_postgres_repository_round_trip():
    if os.getenv("GMA_RUN_POSTGRES_TESTS") != "1":
        pytest.skip("Set GMA_RUN_POSTGRES_TESTS=1 to run postgres integration tests")

    dsn = os.getenv("GMA_POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        pytest.skip("No Postgres DSN configured")

    repo = create_postgres_repository(dsn)
    system = _sample_system()
    repo.save_star_system(system, metadata={"suite": "integration"})
    loaded = repo.get_star_system(system.system_id)
    assert loaded is not None
    assert loaded.star.name == system.star.name
