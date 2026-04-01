# Galaxyai Mobile + Cloud Blueprint

This blueprint turns the current GMA library into a phone-runnable app with cloud-assisted continuous learning.

## 1. Runtime split

- **On-device (Android / Pixel):**
  - Quantized inference model (NNAPI / GPU delegate)
  - Local domain cache (SQLite)
  - 3D galaxy map renderer (e.g. Three.js in WebView)
  - Sync client for ingest/query events
- **Cloud backend:**
  - Website/Wikipedia retrievers
  - Evidence scoring + contradiction detection
  - Durable GMA state + vector retrieval
  - Federated/fleet-learning coordinator

## 2. NPU/TPU training path

- Device contributes training deltas (privacy-preserving if desired).
- Cloud aggregates updates into graph/topology weights.
- Updated confidence/orbit parameters are synced back to devices.
- If device supports fast accelerators, run optional local adaptation tasks during charging + Wi-Fi.

## 3. Hyperlane and wormhole semantics

- `hyperlane`: standard cross-domain bridge for medium-range reasoning transfer.
- `wormhole`: shortcut edge with low effective distance for very distant but strongly linked domains.
- Route planning uses weighted shortest-path over 3D domain coordinates.

## 4. 3D map representation

`Galaxy.galaxy_map_3d()` returns serializable nodes/edges for any renderer.

- nodes: domain, system id, 3D position, star mass, planet count
- edges: lane id, source, destination, lane type, stability, distance multiplier

## 5. Suggested stack

- Android app: Kotlin + WorkManager + Room + TensorFlow Lite
- Backend API: Python FastAPI
- Stores: Postgres + pgvector (or similar)
- Observability: OpenTelemetry + Prometheus
