"""
Galactic Memory Architecture (GMA)
===================================
A topological framework for continuous learning with structural stability.

The GMA organises knowledge like a galaxy:
  - Particles   → individual weights
  - Planets     → fact clusters with confidence weights
  - Stars       → concept anchors (higher-order attractors)
  - Star Systems→ knowledge domains (star + orbiting planets)
  - Filaments   → cross-domain bridges
  - Galactic Core → fundamental priors / identity (hardest to perturb)
  - Falsification Sink → black hole for false / superseded knowledge

Usage::

    from gma import Galaxy
    g = Galaxy()
    g.ingest("Paris is the capital of France", domain="geography")
    g.falsify("Paris is the capital of Germany")
    node = g.query("capital of France")
"""

from gma.structures import Particle, Planet, Star, StarSystem, Filament, GalacticCore
from gma.falsification import FalsificationSink, FalsificationState
from gma.learning import AccretionEngine
from gma.galaxy import Galaxy
from gma.navigation import HyperlaneNetwork, SpaceLane
from gma.retrieval import SourceEvidence, WikipediaRetriever, WebRetriever

__all__ = [
    "Particle",
    "Planet",
    "Star",
    "StarSystem",
    "Filament",
    "GalacticCore",
    "FalsificationSink",
    "FalsificationState",
    "AccretionEngine",
    "Galaxy",
    "HyperlaneNetwork",
    "SpaceLane",
    "SourceEvidence",
    "WikipediaRetriever",
    "WebRetriever",
]
