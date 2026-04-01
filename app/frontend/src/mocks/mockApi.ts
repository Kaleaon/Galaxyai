import type {
  DomainDto,
  IngestFactRequest,
  IngestFactResponse,
  Map3DResponse,
  PlanetDto,
  QueryRequest,
  QueryResponse,
  RegisterDomainRequest,
} from '../types/dto';

const wait = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));

const domains: DomainDto[] = [
  {
    domain: 'geography',
    system_id: 'sys-geo-1',
    star_mass: 2,
    position: [0, 0, 0],
    planet_count: 2,
  },
  {
    domain: 'astronomy',
    system_id: 'sys-astro-1',
    star_mass: 1.6,
    position: [8, 3, 2],
    planet_count: 1,
  },
];

const facts: PlanetDto[] = [
  {
    planet_id: 'p1',
    content: 'Paris is the capital of France',
    confidence: 0.89,
    orbital_radius: 1.12,
    state: 'stable',
  },
  {
    planet_id: 'p2',
    content: 'Paris is the capital of Germany',
    confidence: 0.18,
    orbital_radius: 5.55,
    state: 'accretion_disk',
  },
  {
    planet_id: 'p3',
    content: 'The Milky Way contains over 100 billion stars',
    confidence: 0.83,
    orbital_radius: 1.2,
    state: 'stable',
  },
];

export const mockApi = {
  async registerDomain(payload: RegisterDomainRequest): Promise<DomainDto> {
    await wait();
    const dto: DomainDto = {
      domain: payload.domain,
      system_id: `sys-${payload.domain}-${Date.now()}`,
      star_mass: payload.star_mass ?? 1,
      position: payload.position ?? [0, 0, 0],
      planet_count: 0,
    };
    domains.push(dto);
    return dto;
  },

  async ingestFact(payload: IngestFactRequest): Promise<IngestFactResponse> {
    await wait();
    const contradictionFlagged = Boolean(payload.contradicts);
    const newFact: PlanetDto = {
      planet_id: `p-${Date.now()}`,
      content: payload.content,
      confidence: payload.initial_confidence ?? 0.45,
      orbital_radius: 1 / (payload.initial_confidence ?? 0.45),
      state: 'stable',
    };
    facts.unshift(newFact);
    return { planet: newFact, contradiction_flagged: contradictionFlagged };
  },

  async queryFacts(payload: QueryRequest): Promise<QueryResponse> {
    await wait();
    const keyword = payload.keyword.toLowerCase();
    const results = facts.filter((fact) => fact.content.toLowerCase().includes(keyword));
    return { results };
  },

  async getMap3D(): Promise<Map3DResponse> {
    await wait();
    return {
      systems: domains.map((d) => ({
        domain: d.domain,
        system_id: d.system_id,
        position: d.position,
        star_mass: d.star_mass,
        planet_count: d.planet_count,
      })),
      lanes: [
        {
          lane_id: 'lane-1',
          from_system: domains[0]?.system_id ?? 'sys-geo-1',
          to_system: domains[1]?.system_id ?? 'sys-astro-1',
          lane_type: 'hyperlane',
          stability: 0.91,
          distance_multiplier: 1,
        },
      ],
    };
  },
};
