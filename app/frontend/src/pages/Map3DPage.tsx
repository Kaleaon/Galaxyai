import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Map3DPanel } from '../components/Map3DPanel';
import type { Map3DResponse } from '../types/dto';

export function Map3DPage() {
  const [data, setData] = useState<Map3DResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadMap = async () => {
    try {
      setLoading(true);
      setError(null);
      const mapPayload = await apiClient.getMap3D();
      setData(mapPayload);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load map');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadMap();
  }, []);

  return <Map3DPanel data={data} loading={loading} error={error} onRefresh={loadMap} />;
}
