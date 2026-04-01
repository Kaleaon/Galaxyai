"""Postgres persistence adapter (production backend)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from gma.falsification import CapturedFact, FalsificationState
from gma.infrastructure.persistence.repositories import FalsificationRepository, StructureRepository
from gma.structures import Filament, GalacticCore, Particle, Planet, Star, StarSystem

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS stars (
    star_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    mass DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS star_systems (
    system_id TEXT PRIMARY KEY,
    star_id TEXT NOT NULL REFERENCES stars(star_id) ON DELETE CASCADE,
    position_x DOUBLE PRECISION NOT NULL,
    position_y DOUBLE PRECISION NOT NULL,
    position_z DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS planets (
    planet_id TEXT PRIMARY KEY,
    system_id TEXT NOT NULL REFERENCES star_systems(system_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    orbital_radius DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS particles (
    particle_id TEXT PRIMARY KEY,
    planet_id TEXT NOT NULL REFERENCES planets(planet_id) ON DELETE CASCADE,
    weight DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS filaments (
    filament_id TEXT PRIMARY KEY,
    system_a_id TEXT NOT NULL,
    system_b_id TEXT NOT NULL,
    concept TEXT NOT NULL,
    strength DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS galactic_core_priors (
    prior_name TEXT PRIMARY KEY,
    confidence DOUBLE PRECISION NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS captured_facts (
    planet_id TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    captured_at DOUBLE PRECISION NOT NULL,
    state TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS falsification_transitions (
    transition_id BIGSERIAL PRIMARY KEY,
    planet_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    reason TEXT NOT NULL,
    changed_at DOUBLE PRECISION NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW()),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
"""


@dataclass
class PostgresRepository(StructureRepository, FalsificationRepository):
    connection: "psycopg.Connection"

    def __post_init__(self) -> None:
        with self.connection.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        self.connection.commit()

    def save_star_system(self, system: StarSystem, metadata: Optional[dict] = None) -> None:
        md = json.dumps(metadata or {})
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO stars (star_id, name, mass, metadata)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT(star_id) DO UPDATE SET name=excluded.name, mass=excluded.mass, metadata=excluded.metadata
                """,
                (system.star.star_id, system.star.name, system.star.mass, md),
            )
            x, y, z = system.position
            cur.execute(
                """
                INSERT INTO star_systems (system_id, star_id, position_x, position_y, position_z, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT(system_id) DO UPDATE SET
                    star_id=excluded.star_id,
                    position_x=excluded.position_x,
                    position_y=excluded.position_y,
                    position_z=excluded.position_z,
                    metadata=excluded.metadata
                """,
                (system.system_id, system.star.star_id, x, y, z, md),
            )
            for planet in system.planets.values():
                cur.execute(
                    """
                    INSERT INTO planets (planet_id, system_id, content, confidence, orbital_radius, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT(planet_id) DO UPDATE SET
                        system_id=excluded.system_id,
                        content=excluded.content,
                        confidence=excluded.confidence,
                        orbital_radius=excluded.orbital_radius,
                        metadata=excluded.metadata
                    """,
                    (planet.planet_id, system.system_id, planet.content, planet.confidence, planet.orbital_radius, md),
                )
                for particle in planet.particles:
                    cur.execute(
                        """
                        INSERT INTO particles (particle_id, planet_id, weight, metadata)
                        VALUES (%s, %s, %s, %s::jsonb)
                        ON CONFLICT(particle_id) DO UPDATE SET
                            planet_id=excluded.planet_id,
                            weight=excluded.weight,
                            metadata=excluded.metadata
                        """,
                        (particle.particle_id, planet.planet_id, particle.weight, md),
                    )
        self.connection.commit()

    def get_star_system(self, system_id: str) -> Optional[StarSystem]:
        with self.connection.cursor() as cur:
            cur.execute(
                """
                SELECT s.system_id, s.position_x, s.position_y, s.position_z, st.star_id, st.name, st.mass
                FROM star_systems s
                JOIN stars st ON st.star_id = s.star_id
                WHERE s.system_id = %s
                """,
                (system_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            _, x, y, z, star_id, name, mass = row
            star = Star(name=name, mass=mass, star_id=star_id)
            system = StarSystem(star=star, position=(x, y, z))
            system.system_id = system_id

            cur.execute("SELECT planet_id, content, confidence FROM planets WHERE system_id = %s", (system_id,))
            planets = cur.fetchall()
            for planet_id, content, confidence in planets:
                cur.execute("SELECT particle_id, weight FROM particles WHERE planet_id = %s", (planet_id,))
                particle_rows = cur.fetchall()
                particles = [Particle(weight=w, particle_id=pid) for pid, w in particle_rows]
                system.add_planet(Planet(content=content, confidence=confidence, particles=particles, planet_id=planet_id))
        return system

    def save_filament(self, filament: Filament, metadata: Optional[dict] = None) -> None:
        md = json.dumps(metadata or {})
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO filaments (filament_id, system_a_id, system_b_id, concept, strength, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT(filament_id) DO UPDATE SET
                    system_a_id=excluded.system_a_id,
                    system_b_id=excluded.system_b_id,
                    concept=excluded.concept,
                    strength=excluded.strength,
                    metadata=excluded.metadata
                """,
                (filament.filament_id, filament.system_a_id, filament.system_b_id, filament.concept, filament.strength, md),
            )
        self.connection.commit()

    def get_filament(self, filament_id: str) -> Optional[Filament]:
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT system_a_id, system_b_id, concept, strength, filament_id FROM filaments WHERE filament_id = %s",
                (filament_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
        return Filament(*row)

    def save_galactic_core(self, core: GalacticCore, metadata: Optional[dict] = None) -> None:
        md = json.dumps(metadata or {})
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM galactic_core_priors")
            for prior_name, confidence in core.priors.items():
                cur.execute(
                    "INSERT INTO galactic_core_priors (prior_name, confidence, metadata) VALUES (%s, %s, %s::jsonb)",
                    (prior_name, confidence, md),
                )
        self.connection.commit()

    def load_galactic_core(self) -> GalacticCore:
        core = GalacticCore()
        core.priors.clear()
        with self.connection.cursor() as cur:
            cur.execute("SELECT prior_name, confidence FROM galactic_core_priors")
            for prior_name, confidence in cur.fetchall():
                core.priors[prior_name] = confidence
        return core

    def save_captured_fact(self, captured_fact: CapturedFact, metadata: Optional[dict] = None) -> None:
        md = json.dumps(metadata or {})
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO captured_facts (planet_id, reason, captured_at, state, metadata)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT(planet_id) DO UPDATE SET
                    reason=excluded.reason,
                    captured_at=excluded.captured_at,
                    state=excluded.state,
                    metadata=excluded.metadata
                """,
                (captured_fact.planet.planet_id, captured_fact.reason, captured_fact.captured_at, captured_fact.state.value, md),
            )
        self.connection.commit()

    def record_transition(
        self,
        planet_id: str,
        from_state: FalsificationState,
        to_state: FalsificationState,
        reason: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        md = json.dumps(metadata or {})
        with self.connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO falsification_transitions (planet_id, from_state, to_state, reason, metadata)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                """,
                (planet_id, from_state.value, to_state.value, reason, md),
            )
        self.connection.commit()


def create_postgres_repository(dsn: str) -> PostgresRepository:
    if psycopg is None:
        raise RuntimeError("psycopg is required for the postgres adapter")
    connection = psycopg.connect(dsn)
    return PostgresRepository(connection=connection)
