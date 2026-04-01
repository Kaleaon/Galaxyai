"""Repository interfaces for GMA persistence adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from gma.falsification import CapturedFact, FalsificationState
from gma.structures import Filament, GalacticCore, StarSystem


class StructureRepository(Protocol):
    """Persistence operations for core GMA structures."""

    def save_star_system(self, system: StarSystem, metadata: Optional[dict] = None) -> None:
        ...

    def get_star_system(self, system_id: str) -> Optional[StarSystem]:
        ...

    def save_filament(self, filament: Filament, metadata: Optional[dict] = None) -> None:
        ...

    def get_filament(self, filament_id: str) -> Optional[Filament]:
        ...

    def save_galactic_core(self, core: GalacticCore, metadata: Optional[dict] = None) -> None:
        ...

    def load_galactic_core(self) -> GalacticCore:
        ...


class FalsificationRepository(Protocol):
    """Persistence operations for falsification records and transitions."""

    def save_captured_fact(self, captured_fact: CapturedFact, metadata: Optional[dict] = None) -> None:
        ...

    def record_transition(
        self,
        planet_id: str,
        from_state: FalsificationState,
        to_state: FalsificationState,
        reason: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        ...


@dataclass(frozen=True)
class PersistenceAdapter:
    """Pair of repositories exposed by a configured persistence backend."""

    structures: StructureRepository
    falsification: FalsificationRepository
