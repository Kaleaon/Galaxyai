from __future__ import annotations

from fastapi import APIRouter, Depends

from app.backend.dependencies import get_galaxy_service
from app.backend.schemas import Map3DResponse
from app.backend.services.galaxy_service import GalaxyService

router = APIRouter(tags=["map3d"])


@router.get("/map3d", response_model=Map3DResponse)
def map3d(
    service: GalaxyService = Depends(get_galaxy_service),
) -> Map3DResponse:
    return service.map3d()
