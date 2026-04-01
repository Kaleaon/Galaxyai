from __future__ import annotations

from fastapi import APIRouter, Depends

from app.backend.dependencies import get_galaxy_service
from app.backend.schemas import FalsifyRequest, FalsifyResponse
from app.backend.services.galaxy_service import GalaxyService

router = APIRouter(tags=["falsify"])


@router.post("/falsify", response_model=FalsifyResponse)
def falsify(
    request: FalsifyRequest,
    service: GalaxyService = Depends(get_galaxy_service),
) -> FalsifyResponse:
    return service.falsify(request)
