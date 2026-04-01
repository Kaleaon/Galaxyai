"""Environment-driven persistence adapter selection."""

from __future__ import annotations

import os

from gma.infrastructure.persistence.postgres_adapter import create_postgres_repository
from gma.infrastructure.persistence.repositories import PersistenceAdapter
from gma.infrastructure.persistence.sqlite_adapter import create_sqlite_repository

DEFAULT_BACKEND = "sqlite"


def get_persistence_adapter() -> PersistenceAdapter:
    """Build a persistence adapter from environment variables.

    Env vars:
      - GMA_PERSISTENCE_BACKEND: sqlite|postgres (default: sqlite)
      - GMA_SQLITE_PATH: sqlite file path (default: gma.db)
      - GMA_POSTGRES_DSN: explicit Postgres DSN
      - DATABASE_URL: fallback DSN used if GMA_POSTGRES_DSN is unset
    """
    backend = os.getenv("GMA_PERSISTENCE_BACKEND", DEFAULT_BACKEND).strip().lower()

    if backend == "sqlite":
        sqlite_path = os.getenv("GMA_SQLITE_PATH", "gma.db")
        repository = create_sqlite_repository(sqlite_path)
        return PersistenceAdapter(structures=repository, falsification=repository)

    if backend == "postgres":
        dsn = os.getenv("GMA_POSTGRES_DSN") or os.getenv("DATABASE_URL")
        if not dsn:
            raise ValueError(
                "Postgres backend selected but no DSN provided. Set GMA_POSTGRES_DSN or DATABASE_URL."
            )
        repository = create_postgres_repository(dsn)
        return PersistenceAdapter(structures=repository, falsification=repository)

    raise ValueError(f"Unsupported GMA_PERSISTENCE_BACKEND: {backend}")
