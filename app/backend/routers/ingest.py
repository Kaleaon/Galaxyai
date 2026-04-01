from __future__ import annotations

from fastapi import APIRouter, Depends

from app.backend.dependencies import get_galaxy_service
from app.backend.schemas import IngestRequest, PlanetResponse
from app.backend.services.galaxy_service import GalaxyService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=PlanetResponse)
def ingest(
    request: IngestRequest,
    service: GalaxyService = Depends(get_galaxy_service),
) -> PlanetResponse:
    return service.ingest(request)
