# Galaxyai

A.I. network design inspired by galaxy structures.

**Galaxyai** implements the **Galactic Memory Architecture (GMA)** — a topological framework for continuous learning with structural stability.

Knowledge is organised like a galaxy:
- **Particles** → individual weights
- **Planets** → fact clusters (confidence-weighted)
- **Stars** → concept anchors (higher-order attractors)
- **Star Systems** → knowledge domains
- **Filaments** → cross-domain bridges
- **Galactic Core** → fundamental priors / identity
- **Falsification Sink** → black hole for false or superseded knowledge

See [DESIGN.md](DESIGN.md) for the full architecture specification.
See [ARCHITECTURE_EXPANSION_PLAN.md](ARCHITECTURE_EXPANSION_PLAN.md) for a pragmatic roadmap from prototype to production architecture.

## Quick Start

```python
from gma import Galaxy

g = Galaxy()
g.register_domain("geography", star_mass=2.0)

# Ingest a fact
g.ingest("Paris is the capital of France", domain="geography")

# Query
results = g.query("capital of France")
print(results[0].content)   # Paris is the capital of France

# Falsify incorrect knowledge
g.ingest("Paris is the capital of Germany", domain="geography")
g.falsify("Paris is the capital of Germany", domain="geography")
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```



## New Capabilities (v0.2 scaffolding)

- **External retrieval ingestion**
  - `Galaxy.ingest_from_wikipedia(topic, domain=...)`
  - `Galaxy.ingest_from_url(url, domain=...)`
- **Evidence-aware ingest path** via `SourceEvidence`.
- **Hyperlanes and wormholes** for long-distance domain traversal.
- **3D galaxy map payload** via `Galaxy.galaxy_map_3d()` for rendering in Three.js/Plotly.

### Example: Hyperlanes + Wormholes

```python
from gma import Galaxy

g = Galaxy()
g.register_domain("geography", position=(0.0, 0.0, 0.0))
g.register_domain("astronomy", position=(10.0, 2.0, 1.0))
g.register_domain("biology", position=(20.0, -2.0, 0.0))

g.add_hyperlane("geography", "astronomy")
g.add_wormhole("geography", "biology", distance_multiplier=0.05)

print(g.shortest_domain_path("geography", "biology"))
print(g.galaxy_map_3d())
```
