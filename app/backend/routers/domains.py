from __future__ import annotations

from fastapi import APIRouter, Depends

from app.backend.dependencies import get_galaxy_service
from app.backend.schemas import DomainCreateRequest, DomainResponse
from app.backend.services.galaxy_service import GalaxyService

router = APIRouter(tags=["domains"])


@router.post("/domains", response_model=DomainResponse)
def create_domain(
    request: DomainCreateRequest,
    service: GalaxyService = Depends(get_galaxy_service),
) -> DomainResponse:
    return service.create_domain(request)
