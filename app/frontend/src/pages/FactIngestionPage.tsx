import { FormEvent, useState } from 'react';
import { apiClient } from '../api/client';
import { Badge } from '../components/Badge';
import type { IngestFactRequest, IngestFactResponse } from '../types/dto';

export function FactIngestionPage() {
  const [form, setForm] = useState<IngestFactRequest>({ content: '', domain: '', initial_confidence: 0.3, contradicts: '' });
  const [response, setResponse] = useState<IngestFactResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setError(null);
      const result = await apiClient.ingestFact({
        content: form.content,
        domain: form.domain || undefined,
        initial_confidence: form.initial_confidence,
        contradicts: form.contradicts || undefined,
      });
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingestion failed');
    }
  };

  return (
    <section className="panel">
      <h2>Fact Ingestion + Contradiction Flagging</h2>
      <form className="grid-form" onSubmit={submit}>
        <label>
          Fact
          <textarea required value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
        </label>
        <label>
          Domain
          <input value={form.domain} onChange={(e) => setForm({ ...form, domain: e.target.value })} />
        </label>
        <label>
          Initial Confidence (0-1)
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={form.initial_confidence ?? 0.3}
            onChange={(e) => setForm({ ...form, initial_confidence: Number(e.target.value) })}
          />
        </label>
        <label>
          Contradicts Existing Fact (optional)
          <input value={form.contradicts} onChange={(e) => setForm({ ...form, contradicts: e.target.value })} />
        </label>
        <button type="submit">Ingest</button>
      </form>
      {error && <p className="error">{error}</p>}
      {response && (
        <div className="card">
          <p>{response.planet.content}</p>
          <Badge tone={response.contradiction_flagged ? 'warn' : 'success'}>
            {response.contradiction_flagged ? 'Contradiction flagged' : 'No contradiction flagged'}
          </Badge>
        </div>
      )}
    </section>
  );
}
