"""Navigation primitives for long-distance graph traversal in the GMA galaxy."""

from __future__ import annotations

import heapq
import math
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SpaceLane:
    """A long-distance connection between two star systems.

    Attributes:
        system_a_id: Origin star system id.
        system_b_id: Destination star system id.
        stability: Reliability in [0, 1]; lower stability means higher travel cost.
        distance_multiplier: Scalar applied to geometric distance.
            Wormholes can use values close to 0.
        lane_type: "hyperlane" or "wormhole".
    """

    system_a_id: str
    system_b_id: str
    stability: float = 0.9
    distance_multiplier: float = 1.0
    lane_type: str = "hyperlane"
    lane_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def traversal_cost(self, distance: float) -> float:
        """Compute weighted travel cost for this lane."""
        safe_stability = max(self.stability, 0.05)
        return (distance * self.distance_multiplier) / safe_stability


class HyperlaneNetwork:
    """Graph helper that models hyperlanes and wormholes between systems."""

    def __init__(self) -> None:
        self._lanes: Dict[Tuple[str, str], SpaceLane] = {}

    @staticmethod
    def _key(a: str, b: str) -> Tuple[str, str]:
        return tuple(sorted((a, b)))

    def add_hyperlane(self, system_a_id: str, system_b_id: str, stability: float = 0.9) -> SpaceLane:
        lane = SpaceLane(
            system_a_id=system_a_id,
            system_b_id=system_b_id,
            stability=stability,
            distance_multiplier=1.0,
            lane_type="hyperlane",
        )
        self._lanes[self._key(system_a_id, system_b_id)] = lane
        return lane

    def add_wormhole(
        self,
        system_a_id: str,
        system_b_id: str,
        stability: float = 0.75,
        distance_multiplier: float = 0.1,
    ) -> SpaceLane:
        lane = SpaceLane(
            system_a_id=system_a_id,
            system_b_id=system_b_id,
            stability=stability,
            distance_multiplier=distance_multiplier,
            lane_type="wormhole",
        )
        self._lanes[self._key(system_a_id, system_b_id)] = lane
        return lane

    def lanes(self) -> List[SpaceLane]:
        return list(self._lanes.values())

    def shortest_path(
        self,
        source_system_id: str,
        target_system_id: str,
        positions: Dict[str, Tuple[float, float, float]],
    ) -> List[str]:
        """Return cheapest route using Dijkstra with geometric+lane costs."""
        if source_system_id == target_system_id:
            return [source_system_id]

        adjacency: Dict[str, List[Tuple[str, SpaceLane]]] = {}
        for lane in self._lanes.values():
            adjacency.setdefault(lane.system_a_id, []).append((lane.system_b_id, lane))
            adjacency.setdefault(lane.system_b_id, []).append((lane.system_a_id, lane))

        dist: Dict[str, float] = {source_system_id: 0.0}
        prev: Dict[str, Optional[str]] = {source_system_id: None}
        heap: List[Tuple[float, str]] = [(0.0, source_system_id)]

        while heap:
            current_cost, node = heapq.heappop(heap)
            if node == target_system_id:
                break
            if current_cost > dist.get(node, float("inf")):
                continue

            for neighbor, lane in adjacency.get(node, []):
                step_cost = lane.traversal_cost(_distance(positions[node], positions[neighbor]))
                new_cost = current_cost + step_cost
                if new_cost < dist.get(neighbor, float("inf")):
                    dist[neighbor] = new_cost
                    prev[neighbor] = node
                    heapq.heappush(heap, (new_cost, neighbor))

        if target_system_id not in prev:
            return []

        path: List[str] = []
        cursor: Optional[str] = target_system_id
        while cursor is not None:
            path.append(cursor)
            cursor = prev.get(cursor)
        return list(reversed(path))


def _distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
