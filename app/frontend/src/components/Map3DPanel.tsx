import type { Map3DResponse } from '../types/dto';

interface Map3DPanelProps {
  data: Map3DResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export function Map3DPanel({ data, loading, error, onRefresh }: Map3DPanelProps) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>3D Galaxy Map (GET /map3d)</h2>
        <button onClick={onRefresh} disabled={loading}>
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {!error && !data && <p>No map payload loaded yet.</p>}

      {data && (
        <div className="map-grid">
          <div>
            <h3>Systems</h3>
            <ul>
              {data.systems.map((system) => (
                <li key={system.system_id}>
                  <strong>{system.domain}</strong> @ [{system.position.join(', ')}], star mass {system.star_mass},
                  planets {system.planet_count}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3>Lanes</h3>
            <ul>
              {data.lanes.map((lane) => (
                <li key={lane.lane_id}>
                  {lane.lane_type}: {lane.from_system} → {lane.to_system} (stability {lane.stability})
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
