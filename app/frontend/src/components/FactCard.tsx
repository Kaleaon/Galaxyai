import type { PlanetDto } from '../types/dto';
import { Badge } from './Badge';

function confidenceTone(confidence: number) {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.4) return 'info';
  return 'warn';
}

function stateTone(state: PlanetDto['state']) {
  if (state === 'stable') return 'success';
  if (state === 'accretion_disk' || state === 'contested') return 'warn';
  return 'danger';
}

export function FactCard({ fact }: { fact: PlanetDto }) {
  return (
    <article className="card">
      <p className="fact-text">{fact.content}</p>
      <div className="fact-meta">
        <Badge tone={confidenceTone(fact.confidence)}>
          confidence: {(fact.confidence * 100).toFixed(0)}%
        </Badge>
        <Badge tone={stateTone(fact.state)}>state: {fact.state}</Badge>
      </div>
    </article>
  );
}
