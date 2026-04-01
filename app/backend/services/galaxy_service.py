from __future__ import annotations

from typing import Optional

from gma.galaxy import Galaxy
from gma.structures import Planet, StarSystem

from app.backend.schemas import (
    DomainCreateRequest,
    DomainResponse,
    FalsifyRequest,
    FalsifyResponse,
    IngestRequest,
    Map3DResponse,
    PlanetResponse,
    QueryResponse,
)


class GalaxyService:
    """Thin translation layer between FastAPI schemas and gma.galaxy.Galaxy."""

    def __init__(self, galaxy: Optional[Galaxy] = None) -> None:
        self.galaxy = galaxy or Galaxy()

    def create_domain(self, request: DomainCreateRequest) -> DomainResponse:
        system = self.galaxy.register_domain(
            domain=request.domain,
            star_mass=request.star_mass,
            position=request.position,
        )
        return self._domain_response(request.domain, system)

    def ingest(self, request: IngestRequest) -> PlanetResponse:
        planet = self.galaxy.ingest(
            content=request.content,
            domain=request.domain,
            initial_confidence=request.initial_confidence,
            contradicts=request.contradicts,
        )
        return self._planet_response(planet, request.domain)

    def falsify(self, request: FalsifyRequest) -> FalsifyResponse:
        state = self.galaxy.falsify(
            content=request.content,
            domain=request.domain,
            reason=request.reason,
        )
        return FalsifyResponse(
            content=request.content,
            domain=request.domain,
            state=state.value,
        )

    def query(
        self,
        keyword: str,
        domain: Optional[str] = None,
        include_uncertain: bool = False,
    ) -> QueryResponse:
        planets = self.galaxy.query(
            keyword=keyword,
            domain=domain,
            include_uncertain=include_uncertain,
        )
        return QueryResponse(
            keyword=keyword,
            domain=domain,
            include_uncertain=include_uncertain,
            results=[self._planet_response(planet, domain) for planet in planets],
        )

    def map3d(self) -> Map3DResponse:
        return Map3DResponse.model_validate(self.galaxy.galaxy_map_3d())

    def _planet_response(self, planet: Planet, domain: Optional[str]) -> PlanetResponse:
        return PlanetResponse(
            planet_id=planet.planet_id,
            content=planet.content,
            confidence=planet.confidence,
            orbital_radius=planet.orbital_radius,
            domain=domain,
        )

    def _domain_response(self, domain: str, system: StarSystem) -> DomainResponse:
        return DomainResponse(
            domain=domain,
            system_id=system.system_id,
            star_mass=system.star.mass,
            position=system.position,
            planet_count=len(system.planets),
        )
