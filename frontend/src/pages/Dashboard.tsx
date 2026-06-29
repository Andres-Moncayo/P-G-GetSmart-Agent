import React, { useState, useEffect, useRef, useMemo } from 'react';
import { DATE_FILTERS } from '../data/gameData';
import type { Report, GameCandidate, ApiReport, ApiReportListResponse, MacroSkillStructured } from '../types/game';
import { apiClient } from '../services/api';

function fmtDate(iso: string | undefined): string {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ─── API → Legacy adapter ─────────────────────────────────────────────────────

const PLATFORM_ICON: Record<string, string> = {
  'PC': 'fab fa-windows',
  'PlayStation 4': 'fab fa-playstation',
  'PlayStation 5': 'fab fa-playstation',
  'PlayStation 3': 'fab fa-playstation',
  'Xbox One': 'fab fa-xbox',
  'Xbox Series X': 'fab fa-xbox',
  'Xbox Series S': 'fab fa-xbox',
  'Xbox 360': 'fab fa-xbox',
  'Nintendo Switch': 'fas fa-gamepad',
  'macOS': 'fab fa-apple',
  'iOS': 'fab fa-apple',
  'Android': 'fab fa-android',
};

const PHASE_NUM: Record<string, number> = {
  ingestion: 1, consolidation: 2, analysis: 3, synthesis: 4,
};

function apiReportToLegacy(r: ApiReport): Report {
  const platforms = (r.game.all_platforms ?? []).map(p => PLATFORM_ICON[p] ?? 'fas fa-gamepad');
  const phaseNum = r.current_phase ? (PHASE_NUM[r.current_phase.toLowerCase()] ?? 1) : 1;
  const isActive = r.status === 'processing' || r.status === 'pending';
  return {
    id: r.id,
    title: r.game.name,
    developer: r.game.developer ?? 'Unknown',
    year: r.game.release_year ?? 0,
    genre: r.game.primary_genre ?? 'Unknown',
    status: isActive ? 'processing' : r.status === 'failed' ? 'failed' : 'completed',
    platforms: [...new Set(platforms)],
    platformNames: r.game.all_platforms ?? [],
    time: isActive ? `Phase ${phaseNum}/4` : '',
    createdAt: r.created_at,
    image: r.game.cover_url ?? `https://picsum.photos/seed/${r.id}/400/225`,
    progress: r.pipeline_progress,
    confidenceScore: r.confidence_score,
    tags: r.tags ?? [],
    allGenres: r.game.all_genres ?? [],
    macroSkillScores: (r.thematic_analysis?.skill_scores as Record<string, number | null>) ?? {},
    executiveSummaryData: r.executive_summary ?? {},
    structuredSkills: (r.thematic_analysis?.structured_skills as MacroSkillStructured[] | undefined) ?? [],
  };
}

// ─── FilterCheckbox ───────────────────────────────────────────────────────────

interface FilterCheckboxProps { label: string; count?: number; checked: boolean; onChange: () => void; }
function FilterCheckbox({ label, count, checked, onChange }: FilterCheckboxProps) {
  return (
    <label className="flex items-center gap-2.5 py-1 cursor-pointer group">
      <div className="relative flex-shrink-0">
        <input type="checkbox" checked={checked} onChange={onChange} className="sr-only" />
        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all duration-150 ${checked ? 'bg-accent border-accent' : 'bg-[#222222] border-[#3A3A3A] group-hover:border-[#525252]'}`}>
          {checked && <i className="fas fa-check text-white text-[8px]" />}
        </div>
      </div>
      <span className={`text-sm flex-1 transition-colors ${checked ? 'text-primary' : 'text-muted group-hover:text-primary-muted'}`}>{label}</span>
      {count !== undefined && <span className="text-xs text-disabled">{count}</span>}
    </label>
  );
}

// ─── DateRadio ────────────────────────────────────────────────────────────────

interface DateRadioProps { label: string; selected: boolean; onChange: () => void; }
function DateRadio({ label, selected, onChange }: DateRadioProps) {
  return (
    <label className="flex items-center gap-2.5 py-1 cursor-pointer group">
      <div className="relative flex-shrink-0">
        <input type="radio" checked={selected} onChange={onChange} className="sr-only" />
        <div className={`w-4 h-4 rounded-full border flex items-center justify-center transition-all duration-150 ${selected ? 'bg-accent border-accent' : 'bg-[#222222] border-[#3A3A3A] group-hover:border-[#525252]'}`}>
          {selected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
        </div>
      </div>
      <span className={`text-sm flex-1 transition-colors ${selected ? 'text-primary' : 'text-muted group-hover:text-primary-muted'}`}>{label}</span>
    </label>
  );
}

// ─── InPhaseCard ──────────────────────────────────────────────────────────────

const PHASE_NAMES = ['Ingestion', 'Consolidation', 'Analysis', 'Synthesis'];

interface InPhaseCardProps { report: Report; onClick: () => void; }
function InPhaseCard({ report, onClick }: InPhaseCardProps) {
  const m = report.time.match(/Phase (\d+)\/(\d+)/);
  const current = m ? parseInt(m[1]) : 1;
  const total   = m ? parseInt(m[2]) : 4;
  const phaseName = PHASE_NAMES[current - 1] ?? 'Processing';

  return (
    <div
      onClick={onClick}
      className="glow-border bg-surface rounded-xl overflow-hidden cursor-pointer hover:-translate-y-0.5 transition-all duration-200 flex"
    >
      {/* Thumbnail */}
      <div className="w-28 flex-shrink-0 relative">
        <img
          src={report.image}
          alt={report.title}
          className="w-full h-full object-cover"
          onError={(e) => { (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${report.id}/200/130`; }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent to-surface/90" />
      </div>

      {/* Info */}
      <div className="flex-1 p-3 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-primary truncate leading-tight">{report.title}</p>
            <p className="text-xs text-muted truncate">{report.developer}</p>
            <p className="text-xs text-disabled flex items-center gap-1 mt-0.5">
              <i className="fas fa-calendar-alt text-[9px]" />
              {fmtDate(report.createdAt)}
            </p>
          </div>
          <span className="flex-shrink-0 text-xs font-semibold text-warning bg-warning/10 border border-warning/20 px-2 py-0.5 rounded-full">
            Phase {current}/{total}
          </span>
        </div>

        {/* Phase steps */}
        <div className="flex gap-1 mb-1.5">
          {Array.from({ length: total }).map((_, i) => (
            <div key={i} className="flex-1 relative h-1.5 rounded-full overflow-hidden bg-elevated">
              {i < current - 1 && <div className="absolute inset-0 bg-warning rounded-full" />}
              {i === current - 1 && (
                <div className="absolute inset-0 bg-warning/40 rounded-full">
                  <div className="h-full w-2/3 bg-warning rounded-full animate-pulse" />
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <span className="text-xs text-warning">{phaseName}</span>
          <span className="text-xs text-disabled">{report.progress ?? 0}%</span>
        </div>

        {/* Progress bar */}
        <div className="h-0.5 bg-elevated rounded-full mt-1.5 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-warning to-amber-300 rounded-full transition-all duration-700"
            style={{ width: `${report.progress ?? 0}%` }}
          />
        </div>
      </div>
    </div>
  );
}

// ─── InPhaseSection ───────────────────────────────────────────────────────────

interface InPhaseSectionProps { reports: Report[]; onClickReport: (id: string) => void; }
function InPhaseSection({ reports, onClickReport }: InPhaseSectionProps) {
  if (reports.length === 0) return null;
  return (
    <div className="mb-5 pb-5 border-b border-border flex-shrink-0">
      <div className="flex items-center gap-2 mb-3">
        <span className="w-2 h-2 rounded-full bg-warning dot-pulse flex-shrink-0" />
        <span className="text-xs font-semibold text-muted uppercase tracking-wider">In Pipeline</span>
        <span className="ml-1 text-xs bg-warning/10 text-warning border border-warning/20 px-2 py-0.5 rounded-full">
          {reports.length} active
        </span>
      </div>
      <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {reports.map((r) => (
          <InPhaseCard key={r.id} report={r} onClick={() => onClickReport(r.id)} />
        ))}
      </div>
    </div>
  );
}

// ─── ReportCard ──────────────────────────────────────────────────────────────

interface ReportCardProps { report: Report; onClick: () => void; }
function ReportCard({ report, onClick }: ReportCardProps) {
  return (
    <div
      onClick={onClick}
      className="glow-border bg-surface rounded-xl overflow-hidden cursor-pointer group flex flex-col transition-all duration-300 hover:-translate-y-1"
    >
      <div className="card-zoom relative aspect-video bg-elevated">
        <img
          src={report.image}
          alt={report.title}
          className="w-full h-full object-cover"
          loading="lazy"
          onError={(e) => { (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${report.id}/400/225`; }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
        <span className="absolute bottom-2 left-2 text-xs font-medium bg-black/60 text-primary-muted px-2 py-0.5 rounded-full backdrop-blur-sm">
          {report.genre}
        </span>
        <div className="absolute top-2 right-2 flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-sm text-success">
          <span className="w-1.5 h-1.5 rounded-full bg-success" />
          Done
        </div>
      </div>
      <div className="p-3 flex flex-col gap-1 flex-1">
        <p className="text-sm font-semibold text-primary leading-snug line-clamp-1">{report.title}</p>
        <p className="text-xs text-muted">{report.developer} · {report.year}</p>
        <p className="text-xs text-disabled flex items-center gap-1 mt-0.5">
          <i className="fas fa-calendar-alt text-[9px]" />
          {fmtDate(report.createdAt)}
        </p>
        <div className="flex gap-1.5 mt-auto pt-2">
          {report.platforms.slice(0, 4).map((icon) => (
            <i key={icon} className={`${icon} text-xs text-disabled`} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── ReportPreviewModal ───────────────────────────────────────────────────────

const SKILL_CONFIG = [
  { key: 'Design & Art',         icon: 'fa-palette',    color: 'from-purple-500/15 to-violet-600/10', textColor: 'text-purple-400' },
  { key: 'User Experience',      icon: 'fa-user-circle',color: 'from-sky-500/15 to-cyan-600/10',      textColor: 'text-sky-400'    },
  { key: 'Technology Systems',   icon: 'fa-microchip',  color: 'from-emerald-500/15 to-green-600/10', textColor: 'text-emerald-400'},
  { key: 'Strategy Market',      icon: 'fa-chart-line', color: 'from-amber-500/15 to-orange-600/10',  textColor: 'text-amber-400'  },
];

// Normalize the loose skill keys coming from the orchestrator enrichment
function resolveSkillScore(scores: Record<string, number | null>, configKey: string): number | null {
  const variants: string[] = [
    configKey,
    configKey.toLowerCase(),
    configKey.toLowerCase().replace(/\s+/g, '_'),
    configKey.toLowerCase().replace(/\s+/g, '-'),
    configKey.replace(/ /g, ''),
  ];
  for (const v of variants) {
    if (scores[v] != null) return scores[v];
  }
  // partial match
  const lower = configKey.toLowerCase();
  for (const [k, v] of Object.entries(scores)) {
    if (k.toLowerCase().includes(lower.split(' ')[0])) return v;
  }
  return null;
}

interface ReportPreviewModalProps {
  report: Report;
  onClose: () => void;
}

function ReportPreviewModal({ report, onClose }: ReportPreviewModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [onClose]);

  const rawScore     = report.confidenceScore;
  const overallScore = rawScore != null ? rawScore * 10 : null;
  const tag          = (report.tags ?? [])[0] ?? (report.status === 'completed' ? 'Completed' : '—');
  const scores       = report.macroSkillScores ?? {};
  const scoreColor   = overallScore == null ? 'text-muted' : overallScore >= 9 ? 'text-success' : overallScore >= 7.5 ? 'text-warning' : 'text-error';

  // Index structured skills by label for quick lookup
  const structuredByLabel = Object.fromEntries(
    (report.structuredSkills ?? []).map(s => [s.skill_label, s])
  );

  const market: Record<string, string> = {
    Genre:      report.genre,
    Platforms:  report.platformNames.length ? String(report.platformNames.length) : '—',
    Year:       report.year ? String(report.year) : '—',
    Status:     report.status === 'completed' ? 'Done' : report.status,
  };

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div className="bg-surface border border-border rounded-2xl w-full max-w-2xl shadow-modal max-h-[90vh] overflow-y-auto scrollbar-hide">

        {/* ── Cover header ── */}
        <div className="relative h-44 bg-elevated overflow-hidden rounded-t-2xl">
          <img
            src={report.image}
            alt={report.title}
            className="w-full h-full object-cover"
            onError={e => { (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${report.id}/600/300`; }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/30 to-transparent" />
          <button
            onClick={onClose}
            className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white hover:bg-black/80 transition-colors"
          >
            <i className="fas fa-times text-xs" />
          </button>
          <div className="absolute bottom-4 left-5 right-5">
            <div className="flex items-end gap-3">
              <div className="flex-1 min-w-0">
                <p className="text-xs text-accent font-medium uppercase tracking-wider mb-0.5">{report.genre}</p>
                <h2 className="text-xl font-bold text-primary leading-tight truncate">{report.title}</h2>
                <p className="text-xs text-muted">{report.developer} · {report.year || '—'}</p>
              </div>
              {overallScore != null && (
                <div className="text-right flex-shrink-0">
                  <p className={`text-3xl font-black ${scoreColor}`}>{overallScore.toFixed(1)}</p>
                  <p className="text-xs text-muted truncate max-w-[100px]">{tag}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Body ── */}
        <div className="p-5 space-y-5">

          {/* Macro-Skill Analysis */}
          <div>
            <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Macro-Skill Analysis</p>
            <div className="grid grid-cols-2 gap-3">
              {SKILL_CONFIG.map((skill) => {
                const structured = structuredByLabel[skill.key];
                const scoreRaw = structured?.confidence_raw ?? resolveSkillScore(scores, skill.key);
                const scoreDisplay = structured?.score ?? (scoreRaw != null ? scoreRaw * 10 : null);
                const barWidth = scoreRaw != null ? scoreRaw * 100 : (scoreDisplay != null ? scoreDisplay * 10 : null);
                const summary = structured?.summary ?? '';
                const strengths = structured?.strengths ?? [];
                const weaknesses = structured?.weaknesses ?? [];
                const hasDetail = summary || strengths.length > 0 || weaknesses.length > 0;

                return (
                  <div key={skill.key} className={`rounded-xl p-3 bg-gradient-to-br ${skill.color} border border-border flex flex-col gap-2`}>
                    {/* Header row */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 min-w-0">
                        <i className={`fas ${skill.icon} text-xs ${skill.textColor} flex-shrink-0`} />
                        <p className="text-xs font-semibold text-primary truncate">{skill.key}</p>
                      </div>
                      <span className={`text-sm font-black ${skill.textColor} flex-shrink-0 ml-1`}>
                        {scoreDisplay != null ? scoreDisplay.toFixed(1) : '—'}
                      </span>
                    </div>

                    {/* Score bar */}
                    {barWidth != null ? (
                      <div className="h-1 bg-black/20 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${skill.textColor.replace('text-', 'bg-')}`} style={{ width: `${barWidth}%` }} />
                      </div>
                    ) : null}

                    {/* LLM-generated detail */}
                    {hasDetail ? (
                      <div className="space-y-1.5 mt-0.5">
                        {summary && (
                          <p className="text-[10px] text-muted leading-snug line-clamp-2">{summary}</p>
                        )}
                        {strengths.slice(0, 2).map((s, i) => (
                          <p key={i} className="text-[10px] text-success/80 flex gap-1 leading-snug">
                            <span className="flex-shrink-0">+</span><span className="line-clamp-1">{s}</span>
                          </p>
                        ))}
                        {weaknesses.slice(0, 1).map((w, i) => (
                          <p key={i} className="text-[10px] text-error/70 flex gap-1 leading-snug">
                            <span className="flex-shrink-0">−</span><span className="line-clamp-1">{w}</span>
                          </p>
                        ))}
                      </div>
                    ) : (
                      !barWidth && <p className="text-[10px] text-muted/60 italic">No data yet</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Tags */}
          {(report.tags ?? []).length > 0 && (
            <div>
              <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">Tags</p>
              <div className="flex flex-wrap gap-1.5">
                {(report.tags ?? []).map(t => (
                  <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-accent/10 text-accent border border-accent/20">{t}</span>
                ))}
              </div>
            </div>
          )}

          {/* Market Intelligence */}
          <div>
            <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Market Intelligence</p>
            <div className="grid grid-cols-4 gap-2">
              {Object.entries(market).map(([key, val]) => (
                <div key={key} className="bg-elevated rounded-xl p-3 text-center">
                  <p className="text-sm font-bold text-primary leading-tight truncate">{val}</p>
                  <p className="text-xs text-muted mt-0.5">{key}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-1 border-t border-border">
            <button className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-accent text-white text-xs font-semibold hover:bg-accent-dark transition-colors">
              <i className="fas fa-file-alt" /> Full Report
            </button>
            <button className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-elevated text-primary-muted text-xs font-semibold hover:text-primary transition-colors border border-border">
              <i className="fas fa-download" /> Export
            </button>
            <button
              onClick={onClose}
              className="flex items-center justify-center gap-1.5 py-2 px-4 rounded-lg bg-elevated text-muted text-xs hover:text-primary transition-colors border border-border"
            >
              Close
            </button>
          </div>

          {/* Date */}
          <p className="text-xs text-disabled flex items-center gap-1.5 -mt-2">
            <i className="fas fa-calendar-alt text-[9px]" />
            Generated {fmtDate(report.createdAt)}
          </p>
        </div>

      </div>
    </div>
  );
}

// ─── PipelineModal ───────────────────────────────────────────────────────────

const PIPELINE_PHASES = [
  { key: 'scraping',  label: 'Scraping'   },
  { key: 'analysis',  label: 'Analysis'   },
  { key: 'synthesis', label: 'Synthesis'  },
  { key: 'storage',   label: 'Storage'    },
];

interface PipelineModalProps {
  reportId: string;
  gameName: string;
  onClose: () => void;
  onComplete: () => void;
}

function PipelineModal({ reportId, gameName, onClose, onComplete }: PipelineModalProps) {
  const [pipelineData, setPipelineData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const doneRef = useRef(false);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      while (!cancelled) {
        try {
          const data = await apiClient.getPipelineStatus(reportId);
          if (cancelled) return;
          setPipelineData(data);
          if (data.is_complete && !doneRef.current) {
            doneRef.current = true;
            onComplete();
            return;
          }
          if (data.status === 'failed' && !doneRef.current) {
            setErrorMsg(data.message || 'Pipeline failed');
            return;
          }
        } catch {
          // keep retrying silently
        }
        if (!cancelled) await new Promise<void>(r => setTimeout(r, 3000));
      }
    }

    poll();
    return () => { cancelled = true; };
  }, [reportId, onComplete]);

  const overall   = pipelineData?.overall_progress ?? 0;
  const phases    = pipelineData?.phases ?? {};
  const currentMsg = pipelineData?.message ?? 'Starting pipeline…';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-md mx-4 shadow-modal">
        {/* Header */}
        <div className="p-5 border-b border-border flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs text-warning font-medium uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-warning dot-pulse inline-block" />
              Pipeline Running
            </p>
            <h3 className="text-base font-bold text-primary truncate">{gameName}</h3>
            <p className="text-xs text-muted mt-0.5 truncate">{currentMsg}</p>
          </div>
          <button
            onClick={onClose}
            title="Minimize — pipeline continues in background"
            className="text-muted hover:text-primary flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg hover:bg-elevated transition-colors"
          >
            <i className="fas fa-minus text-xs" />
          </button>
        </div>

        {/* Overall progress bar */}
        <div className="px-5 pt-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-muted">Overall Progress</span>
            <span className="text-xs font-semibold text-primary">{overall}%</span>
          </div>
          <div className="h-2 bg-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-warning to-amber-300 rounded-full transition-all duration-700"
              style={{ width: `${overall}%` }}
            />
          </div>
        </div>

        {/* Phase list */}
        <div className="p-5 space-y-4">
          {PIPELINE_PHASES.map(({ key, label }, idx) => {
            const ph = phases[key] ?? {};
            const st = ph.status ?? 'waiting';
            const pr = ph.progress ?? 0;
            const isRunning  = st === 'running';
            const isDonePhase = st === 'completed';
            const isFailed   = st === 'failed';
            const isSkipped  = st === 'skipped';

            return (
              <div key={key} className="flex items-center gap-3">
                {/* Status icon */}
                <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs ${
                  isDonePhase ? 'bg-success/15 text-success' :
                  isFailed    ? 'bg-error/15 text-error'    :
                  isSkipped   ? 'bg-elevated text-muted'    :
                  isRunning   ? 'bg-warning/15 text-warning' :
                                'bg-elevated text-disabled'
                }`}>
                  {isDonePhase ? <i className="fas fa-check" /> :
                   isFailed    ? <i className="fas fa-times" /> :
                   isSkipped   ? <i className="fas fa-forward text-[10px]" /> :
                   isRunning   ? <div className="w-3.5 h-3.5 border-2 border-warning/30 border-t-warning rounded-full animate-spin" /> :
                                 <span className="font-bold text-[10px]">{idx + 1}</span>}
                </div>

                {/* Label + progress */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-xs font-medium ${
                      isDonePhase ? 'text-success' :
                      isFailed    ? 'text-error'   :
                      isRunning   ? 'text-warning'  :
                                    'text-disabled'
                    }`}>{label}</span>
                    <span className="text-xs text-muted">
                      {isDonePhase ? 'Done'   :
                       isFailed    ? 'Failed' :
                       isSkipped   ? 'Skipped':
                       isRunning   ? `${pr}%` : ''}
                    </span>
                  </div>
                  {isRunning && (
                    <div className="h-1 bg-elevated rounded-full overflow-hidden">
                      <div
                        className="h-full bg-warning rounded-full transition-all duration-500"
                        style={{ width: `${pr}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-5 pb-5">
          {errorMsg ? (
            <>
              <div className="bg-error/10 border border-error/20 rounded-lg p-3 mb-3">
                <p className="text-xs text-error">{errorMsg}</p>
              </div>
              <button onClick={onClose} className="w-full py-2 rounded-lg border border-border text-sm text-muted hover:text-primary transition-colors">
                Close
              </button>
            </>
          ) : (
            <p className="text-xs text-disabled text-center">
              <i className="fas fa-info-circle mr-1 text-muted" />
              You can minimize this — the pipeline continues in the background
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── DisambiguationModal ─────────────────────────────────────────────────────

interface DisambiguationModalProps {
  query: string;
  candidates: GameCandidate[];
  onClose: () => void;
  onConfirm: (game: GameCandidate) => void;
}

function DisambiguationModal({ query, candidates, onClose, onConfirm }: DisambiguationModalProps) {
  const [selectedId, setSelectedId] = useState<string | null>(
    candidates.length > 0 ? candidates[0].id : null
  );

  const selectedGame = candidates.find((c) => c.id === selectedId) ?? null;

  function handleConfirm() {
    if (selectedGame) onConfirm(selectedGame);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-surface border border-border rounded-2xl w-full max-w-md mx-4 shadow-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-5 border-b border-border">
          <p className="text-xs text-accent font-medium uppercase tracking-wider mb-1">Disambiguation</p>
          <h3 className="text-lg font-bold text-primary">"{query}"</h3>
          <p className="text-xs text-muted mt-0.5">
            {candidates.length === 0
              ? 'No games found — try a different search term'
              : `${candidates.length} match${candidates.length !== 1 ? 'es' : ''} found — select the correct game`}
          </p>
        </div>

        {/* Candidates list */}
        <div className="p-4 space-y-2 max-h-80 overflow-y-auto scrollbar-hide">
          {candidates.length === 0 && (
            <div className="text-center py-6">
              <i className="fas fa-search text-disabled text-2xl mb-2" />
              <p className="text-sm text-muted">No games found for "{query}"</p>
              <p className="text-xs text-disabled mt-1">Try a different search term</p>
            </div>
          )}

          {candidates.map((c) => (
            <label
              key={c.id}
              className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                selectedId === c.id ? 'border-accent bg-accent/8' : 'border-border hover:border-border-hover'
              }`}
            >
              {/* Cover thumbnail */}
              <div className="w-14 h-14 rounded-lg overflow-hidden flex-shrink-0 bg-elevated">
                {c.cover_url ? (
                  <img src={c.cover_url} alt={c.name} className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <i className="fas fa-gamepad text-disabled text-lg" />
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-primary leading-tight truncate">{c.name}</p>
                <p className="text-xs text-muted mt-0.5">
                  {[c.developer, c.release_year, c.genres[0]].filter(Boolean).join(' · ')}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  {c.rawg_id && (
                    <span className="text-[10px] text-disabled bg-elevated px-1.5 py-0.5 rounded font-mono">rawg: {c.rawg_id}</span>
                  )}
                  {c.platforms.length > 0 && (
                    <span className="text-[10px] text-disabled truncate">{c.platforms.slice(0, 2).join(', ')}</span>
                  )}
                </div>
              </div>

              {/* Radio */}
              <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-all ${
                selectedId === c.id ? 'border-accent bg-accent' : 'border-border bg-transparent'
              }`}>
                {selectedId === c.id && <div className="w-2 h-2 rounded-full bg-white" />}
              </div>
              <input type="radio" name="candidate" value={c.id} checked={selectedId === c.id} onChange={() => setSelectedId(c.id)} className="sr-only" />
            </label>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <div className="flex gap-2">
            <button onClick={onClose} className="flex-1 py-2 rounded-lg border border-border text-sm text-muted hover:text-primary hover:border-border-hover transition-colors">
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={!selectedGame}
              className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-colors ${
                selectedGame
                  ? 'bg-accent text-white hover:bg-accent-dark shadow-lg shadow-accent/25'
                  : 'bg-elevated text-disabled cursor-not-allowed'
              }`}
            >
              Run Pipeline
            </button>
          </div>
          <p className="text-xs text-muted text-center mt-2">
            Can't find it?{' '}
            <button onClick={onClose} className="text-accent hover:text-accent-light transition-colors">Search with different terms</button>
          </p>
        </div>
      </div>
    </div>
  );
}


type SortKey = 'recent' | 'alpha' | 'year';

export function Dashboard() {
  const [search, setSearch]               = useState('');
  const [sortKey, setSortKey]             = useState<SortKey>('recent');
  const [genreFilters, setGenreFilters]   = useState<string[]>([]);
  const [devFilters, setDevFilters]       = useState<string[]>([]);
  const [platformFilters, setPlatFilters] = useState<string[]>([]);
  const [dateFilter, setDateFilter]       = useState<number | null>(null);

  const [showDisamb, setShowDisamb]           = useState(false);
  const [inputQuery, setInputQuery]           = useState('');
  const [pipelineTitle, setPipelineTitle]     = useState('');
  const [disambCandidates, setDisambCandidates] = useState<GameCandidate[]>([]);
  const [reports, setReports]                 = useState<Report[]>([]);
  const [facets, setFacets]                   = useState<ApiReportListResponse['facets'] | null>(null);
  const [isLoadingReports, setIsLoadingReports] = useState(false);
  const [isGenerating, setIsGenerating]       = useState(false);
  const [showPipeline, setShowPipeline]         = useState(false);
  const [pipelineReportId, setPipelineReportId] = useState<string | null>(null);
  const [previewReport, setPreviewReport]       = useState<Report | null>(null);

  async function loadReports() {
    setIsLoadingReports(true);
    try {
      const data = await apiClient.getReports({ page: 1, page_size: 200 });
      setReports(data.items.map(apiReportToLegacy));
      setFacets(data.facets);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setIsLoadingReports(false);
    }
  }

  useEffect(() => { loadReports(); }, []);

  function toggle<T>(arr: T[], val: T): T[] {
    return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];
  }

  const inPhaseReports = useMemo(() => {
    const processing = reports.filter((r) => r.status === 'processing');
    if (!search.trim()) return processing;
    const q = search.toLowerCase();
    return processing.filter((r) => r.title.toLowerCase().includes(q) || r.developer.toLowerCase().includes(q));
  }, [search, reports]);

  const filteredReports = useMemo(() => {
    let list = reports.filter((r) => r.status !== 'processing');

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((r) => r.title.toLowerCase().includes(q) || r.developer.toLowerCase().includes(q));
    }
    if (genreFilters.length)    list = list.filter((r) => genreFilters.includes(r.genre));
    if (devFilters.length)      list = list.filter((r) => devFilters.includes(r.developer));
    if (platformFilters.length) {
      list = list.filter((r) =>
        platformFilters.some((pf) => r.platformNames.some((n) => n === pf))
      );
    }
    if (dateFilter !== null) {
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - dateFilter);
      list = list.filter((r) => r.createdAt && new Date(r.createdAt) >= cutoff);
    }

    if (sortKey === 'alpha')       list = [...list].sort((a, b) => a.title.localeCompare(b.title));
    else if (sortKey === 'year')   list = [...list].sort((a, b) => b.year - a.year);
    else list = [...list].sort((a, b) => (b.createdAt ?? '').localeCompare(a.createdAt ?? ''));

    return list;
  }, [search, genreFilters, devFilters, platformFilters, dateFilter, sortKey, reports]);

  const hasFilters = genreFilters.length + devFilters.length + platformFilters.length > 0 || dateFilter !== null;

  function clearFilters() {
    setGenreFilters([]); setDevFilters([]); setPlatFilters([]); setDateFilter(null);
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const query = inputQuery.trim();
    if (!query) return;
    setIsGenerating(true);
    try {
      const res = await apiClient.searchGames(query, 10);
      setDisambCandidates(res.candidates);
    } catch {
      setDisambCandidates([]);
    } finally {
      setIsGenerating(false);
      setPipelineTitle(query);
      setShowDisamb(true);
    }
  }

  async function handleDisambiguationConfirm(game: GameCandidate) {
    setShowDisamb(false);
    setIsGenerating(true);
    try {
      const response = await apiClient.startPipeline(game.id);
      setPipelineReportId(response.report_id);
      setShowPipeline(true);
    } catch (error) {
      console.error('Failed to start pipeline:', error);
      alert('Error starting pipeline. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  }

  function handlePipelineComplete() {
    setShowPipeline(false);
    setPipelineReportId(null);
    loadReports();
  }

  const totalCompleted = reports.filter((r) => r.status !== 'processing').length;

  return (
    <div className="flex flex-col h-full">
      {/* Search hero */}
      <div className="px-6 pt-5 pb-4 border-b border-border flex-shrink-0">
        <div className="flex items-center gap-4 max-w-4xl">
          <div className="flex-1 relative">
            <form onSubmit={handleSearch}>
              <i className="fas fa-search absolute left-3.5 top-1/2 -translate-y-1/2 text-muted text-sm pointer-events-none" />
              <input
                type="text"
                placeholder="Search reports or analyze a new game…"
                value={inputQuery}
                onChange={(e) => { setInputQuery(e.target.value); setSearch(e.target.value); }}
                className="w-full bg-elevated border border-border rounded-xl py-2.5 pl-10 pr-44 text-sm text-primary placeholder-muted focus:outline-none focus:border-accent transition-colors"
                autoComplete="off"
              />
              <button
                type="submit"
                disabled={isGenerating || !inputQuery.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-accent hover:bg-accent-dark disabled:bg-elevated disabled:text-disabled disabled:cursor-not-allowed text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
              >
                {isGenerating
                  ? <><div className="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />Searching…</>
                  : 'Generate New Report'
                }
              </button>
            </form>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-xs text-muted">Sort:</span>
            {(['recent', 'alpha', 'year'] as SortKey[]).map((key) => (
              <button key={key} onClick={() => setSortKey(key)}
                className={`text-xs px-2.5 py-1.5 rounded-lg transition-colors ${sortKey === key ? 'bg-accent text-white' : 'bg-elevated border border-border text-muted hover:text-primary'}`}>
                {key === 'recent' ? 'Recent' : key === 'alpha' ? 'A–Z' : 'Year'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 min-h-0">
        {/* Sidebar */}
        <aside className="w-52 flex-shrink-0 border-r border-border overflow-y-auto scrollbar-hide py-4 px-3 space-y-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted uppercase tracking-wider">Filters</span>
            {hasFilters && (
              <button onClick={clearFilters} className="text-xs text-accent hover:text-accent-light transition-colors">Clear</button>
            )}
          </div>

          <div>
            <p className="text-xs font-semibold text-primary mb-2">Genre</p>
            {(facets?.genre ?? []).map((f) => (
              <FilterCheckbox key={f.value} label={f.value} count={f.count}
                checked={genreFilters.includes(f.value)}
                onChange={() => setGenreFilters(toggle(genreFilters, f.value))} />
            ))}
          </div>

          <div>
            <p className="text-xs font-semibold text-primary mb-2">Developer</p>
            {(facets?.developer ?? []).map((f) => (
              <FilterCheckbox key={f.value} label={f.value} count={f.count}
                checked={devFilters.includes(f.value)}
                onChange={() => setDevFilters(toggle(devFilters, f.value))} />
            ))}
          </div>

          <div>
            <p className="text-xs font-semibold text-primary mb-2">Platform</p>
            {(facets?.platform ?? []).map((f) => (
              <FilterCheckbox key={f.value} label={f.value} count={f.count}
                checked={platformFilters.includes(f.value)}
                onChange={() => setPlatFilters(toggle(platformFilters, f.value))} />
            ))}
          </div>

          <div>
            <p className="text-xs font-semibold text-primary mb-2">Date Created</p>
            {DATE_FILTERS.map((f) => (
              <DateRadio key={f.label} label={f.label}
                selected={dateFilter === f.days}
                onChange={() => setDateFilter(dateFilter === f.days ? null : f.days)} />
            ))}
          </div>
        </aside>

        {/* Grid */}
        <div className="flex-1 overflow-y-auto scrollbar-hide px-5 py-4 flex flex-col min-h-0">
          {/* In Pipeline section */}
          <InPhaseSection reports={inPhaseReports} onClickReport={() => {}} />

          {/* Completed header */}
          <div className="flex items-center justify-between mb-4 flex-shrink-0">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-success flex-shrink-0" />
              <p className="text-xs font-semibold text-muted uppercase tracking-wider">Completed Reports</p>
            </div>
            <p className="text-xs text-muted">
              <span className="text-primary font-semibold">{filteredReports.length}</span> of {totalCompleted}
            </p>
          </div>

          {isLoadingReports ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-3">
              <div className="w-6 h-6 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
              <p className="text-muted text-sm">Loading reports…</p>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-3">
              <i className="fas fa-search text-3xl text-disabled" />
              <p className="text-muted text-sm">No reports match your filters</p>
              <button onClick={() => { setSearch(''); setInputQuery(''); clearFilters(); }}
                className="text-xs text-accent hover:text-accent-light transition-colors">Clear all</button>
            </div>
          ) : (
            <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
              {filteredReports.map((r) => (
                <ReportCard key={r.id} report={r} onClick={() => setPreviewReport(r)} />
              ))}
            </div>
          )}
        </div>
      </div>

      {previewReport && (
        <ReportPreviewModal report={previewReport} onClose={() => setPreviewReport(null)} />
      )}

      {showDisamb && (
        <DisambiguationModal query={pipelineTitle} candidates={disambCandidates} onClose={() => setShowDisamb(false)} onConfirm={handleDisambiguationConfirm} />
      )}

      {showPipeline && pipelineReportId && (
        <PipelineModal
          reportId={pipelineReportId}
          gameName={pipelineTitle}
          onClose={() => setShowPipeline(false)}
          onComplete={handlePipelineComplete}
        />
      )}
    </div>
  );
}
