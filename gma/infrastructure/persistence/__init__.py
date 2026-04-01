"""Persistence interfaces and adapters for GMA."""

from gma.infrastructure.persistence.config import get_persistence_adapter
from gma.infrastructure.persistence.postgres_adapter import PostgresRepository, create_postgres_repository
from gma.infrastructure.persistence.repositories import (
    FalsificationRepository,
    PersistenceAdapter,
    StructureRepository,
)
from gma.infrastructure.persistence.sqlite_adapter import SQLiteRepository, create_sqlite_repository

__all__ = [
    "FalsificationRepository",
    "PersistenceAdapter",
    "PostgresRepository",
    "SQLiteRepository",
    "StructureRepository",
    "create_postgres_repository",
    "create_sqlite_repository",
    "get_persistence_adapter",
]
