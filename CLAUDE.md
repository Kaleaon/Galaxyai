# CLAUDE.md — Galaxyai

## Project Overview

Galaxyai implements the **Galactic Memory Architecture (GMA)**, a topological framework for continuous learning with structural stability. Knowledge is modeled using a gravitational metaphor: facts orbit concept anchors, gain confidence through accretion, and are progressively falsified via a black-hole mechanism.

**Stage:** v0.1.0 — research prototype (pure Python, zero runtime dependencies).

## Repository Structure

```
gma/
  __init__.py          # Public API exports
  structures.py        # Core data model (Particle, Planet, Star, StarSystem, Filament, GalacticCore)
  galaxy.py            # Top-level Galaxy orchestrator (main entry point)
  learning.py          # AccretionEngine — continuous learning / fact integration
  falsification.py     # FalsificationSink — black-hole mechanism for false knowledge
tests/
  test_structures.py   # Unit tests for all data structures
  test_galaxy.py       # Integration tests for Galaxy orchestrator
  test_learning.py     # Tests for AccretionEngine
  test_falsification.py # Tests for FalsificationSink
DESIGN.md              # Architectural design document
ARCHITECTURE_EXPANSION_PLAN.md  # Production roadmap (4 phases)
pyproject.toml         # Build config, dependencies, pytest settings
```

## Tech Stack

- **Language:** Python 3.10+
- **Build:** setuptools + wheel (via pyproject.toml)
- **Testing:** pytest + pytest-cov
- **Runtime dependencies:** None (intentionally zero)
- **Dev dependencies:** pytest >= 8.0, pytest-cov

## Setup & Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov gma
```

## Architecture

### Data Model Hierarchy

```
Particle → Planet (fact) → StarSystem (domain) → Galaxy (top-level)
```

- **Particle** — Smallest unit (single weight parameter)
- **Planet** — A fact with confidence [0.0, 1.0]; orbital radius = 1/confidence
- **Star** — Concept anchor with gravitational mass
- **StarSystem** — A knowledge domain: one Star + orbiting Planets
- **Filament** — Cross-domain bridge linking two StarSystems
- **GalacticCore** — Immovable foundational priors (logical consistency, causal reasoning, non-contradiction)

### Key Subsystems

| Component | File | Purpose |
|-----------|------|---------|
| `Galaxy` | galaxy.py | Facade orchestrating all subsystems |
| `AccretionEngine` | learning.py | Routes new facts to domains, runs accretion cycles |
| `FalsificationSink` | falsification.py | Manages falsification lifecycle (STABLE → CONTESTED → ACCRETION_DISK → BEYOND_EVENT_HORIZON) |

### Important Constants (learning.py / falsification.py)

| Constant | Value | Meaning |
|----------|-------|---------|
| `DUST_INITIAL_CONFIDENCE` | 0.1 | New facts start with low confidence |
| `ACCRETION_CONFIDENCE_GAIN` | 0.1 | Confidence increase per accretion cycle |
| `STABLE_ORBIT_THRESHOLD` | 0.6 | Minimum confidence for stability |
| `CONTRADICTION_CONFIDENCE_PENALTY` | 0.2 | Confidence penalty on contradiction |
| `DEFAULT_EVENT_HORIZON_THRESHOLD` | 0.1 | Confidence floor before capture |
| `DEFAULT_CONFIDENCE_DECAY` | 0.15 | Decay per falsification challenge |

## Code Conventions

- **Type hints** on all function signatures (use `typing` module: `Optional`, `List`, `Dict`)
- **Docstrings** on all classes and public methods
- **PEP 8** naming: `snake_case` for functions/variables, `PascalCase` for classes
- **No external dependencies** at runtime — keep the core library pure Python
- **Forward references** use `TYPE_CHECKING` guard for circular imports
- Use `dataclass` or `__init__` with explicit attributes (no `**kwargs` dicts)
- Confidence values are always clamped to [0.0, 1.0]

## Testing Conventions

- Tests live in `tests/` mirroring source module names (`test_<module>.py`)
- One test class per source class/module
- Test names: `test_<behavior_being_tested>`
- Assert boundary conditions (confidence bounds, state transitions)
- All tests must pass before committing: `pytest`

## Key Patterns to Preserve

1. **Gravitational metaphor consistency** — orbital radius, mass, accretion, and event horizon concepts must remain coherent across the codebase
2. **State machine integrity** — FalsificationState transitions are ordered and irreversible (STABLE → CONTESTED → ACCRETION_DISK → BEYOND_EVENT_HORIZON)
3. **Galaxy as facade** — external consumers interact through `Galaxy`; internal subsystems should not be used directly
4. **Confidence-driven behavior** — confidence [0, 1] drives orbital radius, query ordering, and falsification state
5. **Zero runtime dependencies** — avoid adding external packages to the core library

## What's Not Yet Implemented

See `ARCHITECTURE_EXPANSION_PLAN.md` for the full roadmap. Key gaps:

- No persistence layer (everything is in-memory)
- No vector/semantic indexing (queries use substring matching)
- No event bus / async processing
- No REST/gRPC API
- No linting/formatting tooling (Black, flake8, mypy)
- No CI/CD pipeline
