export type ReportStatus = 'completed' | 'processing' | 'queued';

export interface Report {
  id: number;
  title: string;
  developer: string;
  year: number;
  genre: string;
  status: ReportStatus;
  platforms: string[];
  time: string;
  image: string;
  progress?: number;
}

export interface MacroSkill {
  name: string;
  icon: string;
  score: number;
  color: string;
  textColor: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
}

export interface ReportPreview {
  overallScore: number;
  tag: string;
  summary: string;
  macroSkills: MacroSkill[];
  market: Record<string, string>;
}

export interface GameCandidateSource {
  provider: 'igdb' | 'rawg' | 'steam' | 'stub';
  external_id: string;
  confidence: number;
}

export interface GameCandidate {
  id: string;
  name: string;
  slug: string | null;
  release_year: number | null;
  release_date: string | null;
  developer: string | null;
  publisher: string | null;
  platforms: string[];
  genres: string[];
  cover_url: string | null;
  summary: string | null;
  igdb_id: string | null;
  rawg_id: string | null;
  steam_app_id: string | null;
  sources: GameCandidateSource[];
}

export interface GameSearchResponse {
  query: string;
  total: number;
  candidates: GameCandidate[];
  sources_queried: string[];
  latency_ms: number;
}

export interface GameConfirmResponse {
  confirmed_game: GameCandidate;
  can_run_pipeline: boolean;
  pipeline_token: string;
}