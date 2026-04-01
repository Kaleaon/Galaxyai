"""
gma.falsification
=================
The Falsification Sink — the "black hole" at the centre of the GMA galaxy.

False, harmful, or superseded knowledge is not deleted; it is gravitationally
captured.  Facts move through four states:

    STABLE → CONTESTED → ACCRETION_DISK → BEYOND_EVENT_HORIZON

Once a fact crosses the event horizon its gravitational influence drops to
zero — it can no longer affect inference — but it is still stored for
auditability (analogous to Hawking radiation preserving information).
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gma.structures import Planet


# ---------------------------------------------------------------------------
# FalsificationState
# ---------------------------------------------------------------------------

class FalsificationState(enum.Enum):
    """Lifecycle states for a fact moving through the falsification process."""

    STABLE = "stable"
    """The fact is well-supported and not currently under challenge."""

    CONTESTED = "contested"
    """New evidence contradicts this fact; verification is in progress."""

    ACCRETION_DISK = "accretion_disk"
    """The fact is losing confidence and orbiting closer to the sink.
    It can still be referenced but is flagged with epistemic uncertainty.
    """

    BEYOND_EVENT_HORIZON = "beyond_event_horizon"
    """The fact has crossed the event horizon.  Its gravitational influence
    is zero; it will not appear in normal inference outputs.
    """


# ---------------------------------------------------------------------------
# CapturedFact  (audit record)
# ---------------------------------------------------------------------------

@dataclass
class CapturedFact:
    """Audit record for a fact that has been captured by the falsification sink.

    Attributes:
        planet: The original Planet (fact cluster).
        reason: Why this fact was falsified.
        captured_at: Unix timestamp of event-horizon crossing.
        state: Current state in the falsification lifecycle.
    """

    planet: Planet
    reason: str = ""
    captured_at: float = field(default_factory=time.time)
    state: FalsificationState = FalsificationState.ACCRETION_DISK


# ---------------------------------------------------------------------------
# FalsificationSink
# ---------------------------------------------------------------------------

class FalsificationSink:
    """The central black hole of the GMA galaxy.

    Manages the lifecycle of facts that are being (or have been) falsified.

    Key properties:
      - Facts are *never deleted* — information is preserved for auditability.
      - Facts lose influence *progressively* as their orbital radius grows.
      - Below ``event_horizon_threshold`` a fact's influence drops to zero.
      - The gradient between truth and falsity *steepens* as the model matures
        (modelled here by ``maturity_factor``).

    Attributes:
        event_horizon_threshold: Confidence below which a fact crosses the
            event horizon.  Default 0.1.
        maturity_factor: Multiplier applied to confidence decay each step.
            Higher values → faster learning, stronger gradient.
        _accretion_disk: Facts currently in the accretion disk.
        _captured: Facts that have crossed the event horizon.
    """

    DEFAULT_EVENT_HORIZON_THRESHOLD: float = 0.1
    DEFAULT_CONFIDENCE_DECAY: float = 0.15

    def __init__(
        self,
        event_horizon_threshold: float = DEFAULT_EVENT_HORIZON_THRESHOLD,
        maturity_factor: float = 1.0,
    ) -> None:
        if not 0.0 < event_horizon_threshold < 1.0:
            raise ValueError(
                f"event_horizon_threshold must be in (0, 1), "
                f"got {event_horizon_threshold}"
            )
        self.event_horizon_threshold = event_horizon_threshold
        self.maturity_factor = maturity_factor

        self._accretion_disk: Dict[str, CapturedFact] = {}
        self._captured: Dict[str, CapturedFact] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def challenge(self, planet: Planet, reason: str = "") -> FalsificationState:
        """Begin the falsification process for *planet*.

        If the planet is already in the accretion disk, apply another round
        of confidence decay.

        Returns:
            The new FalsificationState of the planet.
        """
        if planet.planet_id in self._captured:
            return FalsificationState.BEYOND_EVENT_HORIZON

        if planet.planet_id in self._accretion_disk:
            # Planet is already contested — apply additional decay.
            record = self._accretion_disk[planet.planet_id]
            record.reason = reason or record.reason
            return self._apply_decay(record)

        # First challenge — move to CONTESTED then immediately into the disk.
        record = CapturedFact(
            planet=planet,
            reason=reason,
            state=FalsificationState.CONTESTED,
        )
        self._accretion_disk[planet.planet_id] = record
        return self._apply_decay(record)

    def get_state(self, planet_id: str) -> FalsificationState:
        """Return the current falsification state of a planet."""
        if planet_id in self._captured:
            return FalsificationState.BEYOND_EVENT_HORIZON
        if planet_id in self._accretion_disk:
            return self._accretion_disk[planet_id].state
        return FalsificationState.STABLE

    def is_beyond_event_horizon(self, planet_id: str) -> bool:
        """Return True if this planet can no longer influence inference."""
        return planet_id in self._captured

    def accretion_disk_contents(self) -> List[CapturedFact]:
        """Return all facts currently in the accretion disk (uncertain)."""
        return list(self._accretion_disk.values())

    def captured_contents(self) -> List[CapturedFact]:
        """Return all facts that have crossed the event horizon (audit log)."""
        return list(self._captured.values())

    def set_maturity_factor(self, factor: float) -> None:
        """Adjust how aggressively the sink decays challenged facts.

        As the model matures, this factor can be increased to steepen the
        gradient between truth and falsity.
        """
        if factor <= 0:
            raise ValueError(f"maturity_factor must be > 0, got {factor}")
        self.maturity_factor = factor

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_decay(self, record: CapturedFact) -> FalsificationState:
        """Apply one round of confidence decay and update the record state."""
        planet = record.planet
        decay = self.DEFAULT_CONFIDENCE_DECAY * self.maturity_factor
        new_confidence = max(0.0, planet.confidence - decay)
        planet.update_confidence(new_confidence)

        if new_confidence <= self.event_horizon_threshold:
            # Cross the event horizon.
            record.state = FalsificationState.BEYOND_EVENT_HORIZON
            record.captured_at = time.time()
            self._captured[planet.planet_id] = record
            del self._accretion_disk[planet.planet_id]
        else:
            record.state = FalsificationState.ACCRETION_DISK

        return record.state

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FalsificationSink("
            f"accretion_disk={len(self._accretion_disk)}, "
            f"captured={len(self._captured)}, "
            f"maturity={self.maturity_factor:.2f})"
        )
