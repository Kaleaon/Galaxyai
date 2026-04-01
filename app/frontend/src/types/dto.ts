export type FalsificationState =
  | 'stable'
  | 'contested'
  | 'accretion_disk'
  | 'beyond_event_horizon';

export interface PlanetDto {
  planet_id: string;
  content: string;
  confidence: number;
  orbital_radius: number;
  state: FalsificationState;
}

export interface RegisterDomainRequest {
  domain: string;
  star_mass?: number;
  position?: [number, number, number];
}

export interface DomainDto {
  domain: string;
  system_id: string;
  star_mass: number;
  position: [number, number, number];
  planet_count: number;
}

export interface IngestFactRequest {
  content: string;
  domain?: string;
  initial_confidence?: number;
  contradicts?: string;
}

export interface IngestFactResponse {
  planet: PlanetDto;
  contradiction_flagged: boolean;
}

export interface QueryRequest {
  keyword: string;
  domain?: string;
  include_uncertain?: boolean;
}

export interface QueryResponse {
  results: PlanetDto[];
}

export interface Map3DSystemDto {
  domain: string;
  system_id: string;
  position: [number, number, number];
  star_mass: number;
  planet_count: number;
}

export interface Map3DLaneDto {
  lane_id: string;
  from_system: string;
  to_system: string;
  lane_type: 'hyperlane' | 'wormhole';
  stability: number;
  distance_multiplier: number;
}

export interface Map3DResponse {
  systems: Map3DSystemDto[];
  lanes: Map3DLaneDto[];
}
