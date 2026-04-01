import { mockApi } from '../mocks/mockApi';
import type {
  DomainDto,
  IngestFactRequest,
  IngestFactResponse,
  Map3DResponse,
  QueryRequest,
  QueryResponse,
  RegisterDomainRequest,
} from '../types/dto';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const MOCK_MODE = import.meta.env.VITE_API_MOCK_MODE === 'true';

async function jsonRequest<T>(path: string, method: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text || response.statusText}`);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  async registerDomain(payload: RegisterDomainRequest): Promise<DomainDto> {
    if (MOCK_MODE) return mockApi.registerDomain(payload);
    return jsonRequest<DomainDto>('/domains/register', 'POST', payload);
  },

  async ingestFact(payload: IngestFactRequest): Promise<IngestFactResponse> {
    if (MOCK_MODE) return mockApi.ingestFact(payload);
    return jsonRequest<IngestFactResponse>('/facts/ingest', 'POST', payload);
  },

  async queryFacts(payload: QueryRequest): Promise<QueryResponse> {
    if (MOCK_MODE) return mockApi.queryFacts(payload);
    return jsonRequest<QueryResponse>('/query', 'POST', payload);
  },

  async getMap3D(): Promise<Map3DResponse> {
    if (MOCK_MODE) return mockApi.getMap3D();
    return jsonRequest<Map3DResponse>('/map3d', 'GET');
  },
};

export { MOCK_MODE };
