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

