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
