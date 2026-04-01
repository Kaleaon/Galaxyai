import { FormEvent, useState } from 'react';
import { apiClient } from '../api/client';
import type { DomainDto, RegisterDomainRequest } from '../types/dto';

export function DomainRegistrationPage() {
  const [form, setForm] = useState<RegisterDomainRequest>({ domain: '', star_mass: 1, position: [0, 0, 0] });
  const [registered, setRegistered] = useState<DomainDto | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setError(null);
      const created = await apiClient.registerDomain(form);
      setRegistered(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not register domain');
    }
  };

  return (
    <section className="panel">
      <h2>Domain Registration</h2>
      <form className="grid-form" onSubmit={submit}>
        <label>
          Domain Name
          <input required value={form.domain} onChange={(e) => setForm({ ...form, domain: e.target.value })} />
        </label>
        <label>
          Star Mass
          <input
            type="number"
            step="0.1"
            min="0"
            value={form.star_mass ?? 1}
            onChange={(e) => setForm({ ...form, star_mass: Number(e.target.value) })}
          />
        </label>
        <button type="submit">Register Domain</button>
      </form>
      {error && <p className="error">{error}</p>}
      {registered && <p className="success">Created {registered.domain} ({registered.system_id})</p>}
    </section>
  );
}
