import { FormEvent, useState } from 'react';
import { apiClient } from '../api/client';
import { FactCard } from '../components/FactCard';
import type { PlanetDto } from '../types/dto';

export function QueryResultsPage() {
  const [keyword, setKeyword] = useState('Paris');
  const [results, setResults] = useState<PlanetDto[]>([]);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setError(null);
      const response = await apiClient.queryFacts({ keyword, include_uncertain: true });
      setResults(response.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed');
    }
  };

  return (
    <section className="panel">
      <h2>Query Results</h2>
      <form className="inline-form" onSubmit={submit}>
        <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="keyword" />
        <button type="submit">Search</button>
      </form>
      {error && <p className="error">{error}</p>}
      <div className="stack">
        {results.map((fact) => (
          <FactCard key={fact.planet_id} fact={fact} />
        ))}
      </div>
    </section>
  );
}
