from __future__ import annotations

from functools import lru_cache

from app.backend.services.galaxy_service import GalaxyService


@lru_cache
def get_galaxy_service() -> GalaxyService:
    return GalaxyService()
