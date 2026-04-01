from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.backend.dependencies import get_galaxy_service
from app.backend.schemas import QueryResponse
from app.backend.services.galaxy_service import GalaxyService

router = APIRouter(tags=["query"])


@router.get("/query", response_model=QueryResponse)
def query(
    keyword: str = Query(..., min_length=1),
    domain: Optional[str] = None,
    include_uncertain: bool = False,
    service: GalaxyService = Depends(get_galaxy_service),
) -> QueryResponse:
    return service.query(keyword=keyword, domain=domain, include_uncertain=include_uncertain)
