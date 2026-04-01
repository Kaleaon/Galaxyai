from __future__ import annotations

from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class DomainCreateRequest(BaseModel):
    domain: str = Field(..., min_length=1)
    star_mass: float = 1.0
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class DomainResponse(BaseModel):
    domain: str
    system_id: str
    star_mass: float
    position: Tuple[float, float, float]
    planet_count: int


class IngestRequest(BaseModel):
    content: str = Field(..., min_length=1)
    domain: Optional[str] = None
    initial_confidence: float = Field(default=0.1, ge=0.0, le=1.0)
    contradicts: Optional[str] = None


class PlanetResponse(BaseModel):
    planet_id: str
    content: str
    confidence: float
    orbital_radius: float
    domain: Optional[str] = None


class FalsifyRequest(BaseModel):
    content: str = Field(..., min_length=1)
    domain: Optional[str] = None
    reason: str = ""


class FalsifyResponse(BaseModel):
    content: str
    domain: Optional[str] = None
    state: str


class QueryResponse(BaseModel):
    keyword: str
    domain: Optional[str] = None
    include_uncertain: bool = False
    results: List[PlanetResponse]


class Map3DSystemResponse(BaseModel):
    domain: str
    system_id: str
    position: Tuple[float, float, float]
    star_mass: float
    planet_count: int


class Map3DLaneResponse(BaseModel):
    lane_id: str
    from_system: str
    to_system: str
    lane_type: str
    stability: float
    distance_multiplier: float


class Map3DResponse(BaseModel):
    systems: List[Map3DSystemResponse]
    lanes: List[Map3DLaneResponse]
