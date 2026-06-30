export type ReportStatus = 'completed' | 'processing' | 'queued' | 'pending' | 'failed';

export interface Report {
  id: string;
  title: string;
  developer: string;
  year: number;
  genre: string;
  status: ReportStatus;
  platforms: string[];      // FontAwesome class strings for display
  platformNames: string[];  // raw platform names for filtering
  time: string;
  createdAt: string;        // ISO date string
  image: string;
  progress?: number;
  confidenceScore?: number | null;
  tags?: string[];
  allGenres?: string[];
  macroSkillScores?: Record<string, number | null>;
  executiveSummaryData?: Record<string, any>;
  structuredSkills?: MacroSkillStructured[];
}

// ─── API Response Types ───────────────────────────────────────────────────────

export interface ApiGame {
  id: string;
  name: string;
  developer: string | null;
  release_year: number | null;
  primary_genre: string | null;
  primary_platform: string | null;
  all_genres: string[];
  all_platforms: string[];
  cover_url: string | null;
  slug: string | null;
}

export interface ApiReport {
  id: string;
  status: 'completed' | 'processing' | 'pending' | 'failed';
  game: ApiGame;
  created_at: string;
  updated_at: string;
  confidence_score: number | null;
  tags: string[];
  current_phase: string | null;
  pipeline_progress: number;
  executive_summary?: Record<string, any> | null;
  thematic_analysis?: Record<string, any> | null;
  confidence_analysis?: Record<string, any> | null;
}

export interface ApiReportListResponse {
  items: ApiReport[];
  pagination: { page: number; page_size: number; total: number; total_pages: number };
  facets: {
    genre: { value: string; count: number }[];
    platform: { value: string; count: number }[];
    developer: { value: string; count: number }[];
    status: { value: string; count: number }[];
  };
}

export interface MacroSkillStructured {
  skill_key: string;
  skill_label: string;
  score: number | null;
  confidence_raw: number | null;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  key_findings: string[];
  risks: string[];
  opportunities: string[];
  evidence_count: number;
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
