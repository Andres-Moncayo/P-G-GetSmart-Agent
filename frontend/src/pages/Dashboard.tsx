import React, { useState, useEffect, useRef, useMemo } from 'react';
import { REPORTS, REPORT_PREVIEWS, GENRE_FILTERS, DEV_FILTERS, PLATFORM_FILTERS, DATE_FILTERS, REPORT_DATES } from '../data/gameData';
import type { Report, ReportPreview, GameCandidate } from '../types/game';
import { apiClient } from '../services/api';

function fmtDate(iso: string | undefined): string {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
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
              {fmtDate(REPORT_DATES[report.id])}
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

interface InPhaseSectionProps { reports: Report[]; onClickReport: (id: number) => void; }
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
          {fmtDate(REPORT_DATES[report.id])}
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
                  {c.igdb_id && (
                    <span className="text-[10px] text-disabled bg-elevated px-1.5 py-0.5 rounded font-mono">igdb: {c.igdb_id}</span>
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

// ─── PipelineModal ────────────────────────────────────────────────────────────

type PhaseState = 'idle' | 'running' | 'done';
const PHASES = ['Ingestion', 'Consolidation', 'Analysis', 'Synthesis', 'Packaging'];
const SKILLS = ['Design & Art', 'User Experience', 'Technology & Systems', 'Strategy & Market'];

interface PipelineModalProps { gameTitle: string; onClose: () => void; onComplete: () => void; }
function PipelineModal({ gameTitle, onClose, onComplete }: PipelineModalProps) {
  const [phases, setPhases]   = useState<PhaseState[]>(['running', 'idle', 'idle', 'idle', 'idle']);
  const [progress, setProgress] = useState(10);
  const [done, setDone]       = useState(false);
  const [skills, setSkills]   = useState<PhaseState[]>(['idle', 'idle', 'idle', 'idle']);

  useEffect(() => {
    const t0 = setTimeout(() => { setPhases(['done', 'running', 'idle', 'idle', 'idle']); setProgress(25); }, 900);
    const t1 = setTimeout(() => { setPhases(['done', 'done', 'running', 'idle', 'idle']); setProgress(45); }, 1800);
    const t2 = setTimeout(() => { setSkills(['running', 'running', 'running', 'running']); }, 2200);
    const t3 = setTimeout(() => { setPhases(['done', 'done', 'done', 'running', 'idle']); setProgress(75); setSkills(['done', 'done', 'done', 'done']); }, 3400);
    const t4 = setTimeout(() => { setPhases(['done', 'done', 'done', 'done', 'running']); setProgress(90); }, 4400);
    const t5 = setTimeout(() => { setPhases(['done', 'done', 'done', 'done', 'done']); setProgress(100); setDone(true); }, 5200);
    const t6 = setTimeout(() => { onComplete(); onClose(); }, 6400);
    return () => { [t0, t1, t2, t3, t4, t5, t6].forEach(clearTimeout); };
  }, []);

  const phaseIcon = (s: PhaseState) =>
    s === 'done'    ? <i className="fas fa-check text-success text-xs" /> :
    s === 'running' ? <div className="w-3 h-3 border-2 border-accent border-t-transparent rounded-full animate-spin" /> :
                      <span className="w-2 h-2 rounded-full bg-border block" />;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-sm mx-4 shadow-modal overflow-hidden">
        <div className="p-5 border-b border-border">
          <p className="text-xs text-accent font-medium uppercase tracking-wider mb-1">GetSmart Pipeline</p>
          <h3 className="text-base font-bold text-primary truncate">{gameTitle}</h3>
        </div>
        <div className="p-5 space-y-3">
          <div className="h-1.5 bg-elevated rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-accent to-secondary rounded-full progress-glow transition-all duration-700" style={{ width: `${progress}%` }} />
          </div>
          <div className="space-y-2">
            {PHASES.map((name, i) => (
              <div key={name} className="flex items-center gap-3">
                <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">{phaseIcon(phases[i])}</div>
                <span className={`text-sm ${phases[i] === 'done' ? 'text-primary' : phases[i] === 'running' ? 'text-accent' : 'text-disabled'}`}>{name}</span>
                {name === 'Analysis' && phases[i] === 'running' && (
                  <div className="ml-auto flex gap-1">
                    {skills.map((s, j) => (
                      <div key={j} title={SKILLS[j]} className={`w-1.5 h-1.5 rounded-full transition-colors ${s === 'done' ? 'bg-success' : s === 'running' ? 'bg-accent animate-pulse' : 'bg-border'}`} />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          {(phases[2] === 'running' || phases[2] === 'done') && (
            <div className="pt-2 border-t border-border grid grid-cols-2 gap-1.5">
              {SKILLS.map((name, i) => (
                <div key={name} className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-lg transition-all ${skills[i] === 'done' ? 'bg-success/10 text-success' : skills[i] === 'running' ? 'bg-accent/10 text-accent' : 'bg-elevated text-disabled'}`}>
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${skills[i] === 'done' ? 'bg-success' : skills[i] === 'running' ? 'bg-accent animate-pulse' : 'bg-disabled'}`} />
                  <span className="truncate">{name}</span>
                </div>
              ))}
            </div>
          )}
          {done && <p className="text-center text-sm font-semibold text-success pt-2">Report ready! Opening preview...</p>}
        </div>
      </div>
    </div>
  );
}

// ─── ReportPreviewModal ───────────────────────────────────────────────────────

interface ReportPreviewModalProps { report: Report; preview: ReportPreview; onClose: () => void; }
function ReportPreviewModal({ report, preview, onClose }: ReportPreviewModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [onClose]);

  const scoreColor = preview.overallScore >= 9 ? 'text-success' : preview.overallScore >= 7.5 ? 'text-warning' : 'text-danger';

  return (
    <div ref={overlayRef} className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}>
      <div className="bg-surface border border-border rounded-2xl w-full max-w-2xl shadow-modal max-h-[90vh] overflow-y-auto scrollbar-hide">
        <div className="relative h-44 bg-elevated overflow-hidden rounded-t-2xl">
          <img src={report.image} alt={report.title} className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/30 to-transparent" />
          <button onClick={onClose} className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white hover:bg-black/80 transition-colors">
            <i className="fas fa-times text-xs" />
          </button>
          <div className="absolute bottom-4 left-5 right-16">
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <p className="text-xs text-accent font-medium uppercase tracking-wider mb-0.5">{report.genre}</p>
                <h2 className="text-xl font-bold text-primary leading-tight">{report.title}</h2>
                <p className="text-xs text-muted">{report.developer} · {report.year}</p>
              </div>
              <div className="text-right">
                <p className={`text-3xl font-black ${scoreColor}`}>{preview.overallScore.toFixed(1)}</p>
                <p className="text-xs text-muted">{preview.tag}</p>
              </div>
            </div>
          </div>
        </div>
        <div className="p-5 space-y-5">
          <p className="text-sm text-primary-muted leading-relaxed">{preview.summary}</p>
          <div>
            <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Macro-Skill Analysis</p>
            <div className="grid grid-cols-2 gap-3">
              {preview.macroSkills.map((skill) => (
                <div key={skill.name} className={`rounded-xl p-3 bg-gradient-to-br ${skill.color} border border-border`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <i className={`fas ${skill.icon} text-xs ${skill.textColor}`} />
                      <p className="text-xs font-semibold text-primary">{skill.name}</p>
                    </div>
                    <span className={`text-sm font-black ${skill.textColor}`}>{skill.score.toFixed(1)}</span>
                  </div>
                  <p className="text-xs text-muted leading-snug mb-2 line-clamp-2">{skill.summary}</p>
                  <div className="space-y-1">
                    {skill.strengths.slice(0, 2).map((s) => (
                      <div key={s} className="flex items-start gap-1.5 text-xs text-primary-muted">
                        <i className="fas fa-plus text-success mt-0.5 flex-shrink-0 text-[9px]" />{s}
                      </div>
                    ))}
                    {skill.weaknesses.slice(0, 1).map((w) => (
                      <div key={w} className="flex items-start gap-1.5 text-xs text-primary-muted">
                        <i className="fas fa-minus text-danger mt-0.5 flex-shrink-0 text-[9px]" />{w}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Market Intelligence</p>
            <div className="grid grid-cols-4 gap-2">
              {Object.entries(preview.market).map(([key, val]) => (
                <div key={key} className="bg-elevated rounded-xl p-3 text-center">
                  <p className="text-sm font-bold text-primary leading-tight">{val}</p>
                  <p className="text-xs text-muted mt-0.5">{key}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="flex gap-2 pt-1 border-t border-border">
            <button className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-accent text-white text-xs font-semibold hover:bg-accent-dark transition-colors">
              <i className="fas fa-file-pdf" /> PDF
            </button>
            <button className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-elevated text-primary-muted text-xs font-semibold hover:bg-bg-hover hover:text-primary transition-colors border border-border">
              <i className="fas fa-code" /> JSON
            </button>
            <button className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-elevated text-primary-muted text-xs font-semibold hover:bg-bg-hover hover:text-primary transition-colors border border-border">
              <i className="fas fa-share-alt" /> Share
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

type SortKey = 'recent' | 'alpha' | 'year';

const platformIcon: Record<string, string> = {
  'PC': 'fab fa-windows',
  'PlayStation': 'fab fa-playstation',
  'Xbox': 'fab fa-xbox',
  'Switch': 'fas fa-gamepad',
};

export function Dashboard() {
  const [search, setSearch]               = useState('');
  const [sortKey, setSortKey]             = useState<SortKey>('recent');
  const [genreFilters, setGenreFilters]   = useState<string[]>([]);
  const [devFilters, setDevFilters]       = useState<string[]>([]);
  const [platformFilters, setPlatFilters] = useState<string[]>([]);
  const [dateFilter, setDateFilter]       = useState<number | null>(null);

  const [showDisamb, setShowDisamb]         = useState(false);
  const [showPipeline, setShowPipeline]     = useState(false);
  const [showPreview, setShowPreview]       = useState<number | null>(null);
  const [inputQuery, setInputQuery]         = useState('');
  const [pipelineTitle, setPipelineTitle]   = useState('');
  const [disambCandidates, setDisambCandidates] = useState<GameCandidate[]>([]);
  const [isGenerating, setIsGenerating]     = useState(false);

  function toggle<T>(arr: T[], val: T): T[] {
    return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];
  }

  // In-pipeline games — shown in dedicated section, also search-filtered
  const inPhaseReports = useMemo(() => {
    const processing = REPORTS.filter((r) => r.status === 'processing');
    if (!search.trim()) return processing;
    const q = search.toLowerCase();
    return processing.filter((r) => r.title.toLowerCase().includes(q) || r.developer.toLowerCase().includes(q));
  }, [search]);

  // Completed games — main grid
  const filteredReports = useMemo(() => {
    let list = REPORTS.filter((r) => r.status !== 'processing');

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((r) => r.title.toLowerCase().includes(q) || r.developer.toLowerCase().includes(q));
    }
    if (genreFilters.length)    list = list.filter((r) => genreFilters.includes(r.genre));
    if (devFilters.length)      list = list.filter((r) => devFilters.includes(r.developer));
    if (platformFilters.length) {
      list = list.filter((r) =>
        platformFilters.some((pf) => {
          const icon = platformIcon[pf];
          return icon && r.platforms.includes(icon);
        })
      );
    }
    if (dateFilter !== null) {
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - dateFilter);
      list = list.filter((r) => {
        const d = REPORT_DATES[r.id];
        return d && new Date(d) >= cutoff;
      });
    }

    if (sortKey === 'alpha')  list = [...list].sort((a, b) => a.title.localeCompare(b.title));
    else if (sortKey === 'year') list = [...list].sort((a, b) => b.year - a.year);
    else list = [...list].sort((a, b) => {
      const da = REPORT_DATES[a.id] ?? ''; const db = REPORT_DATES[b.id] ?? '';
      return db.localeCompare(da);
    });

    return list;
  }, [search, genreFilters, devFilters, platformFilters, dateFilter, sortKey]);

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

  function handleDisambiguationConfirm(game: GameCandidate) {
    setShowDisamb(false);
    setPipelineTitle(game.name);
    setShowPipeline(true);
  }

  const previewReport = showPreview !== null ? REPORTS.find((r) => r.id === showPreview) : null;
  const previewData   = showPreview !== null ? REPORT_PREVIEWS[showPreview] : null;

  const totalCompleted = REPORTS.filter((r) => r.status !== 'processing').length;

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
            {GENRE_FILTERS.map((f) => (
              <FilterCheckbox key={f.label} label={f.label} count={f.count}
                checked={genreFilters.includes(f.label)}
                onChange={() => setGenreFilters(toggle(genreFilters, f.label))} />
            ))}
          </div>

          <div>
            <p className="text-xs font-semibold text-primary mb-2">Developer</p>
            {DEV_FILTERS.map((f) => (
              <FilterCheckbox key={f.label} label={f.label} count={f.count}
                checked={devFilters.includes(f.label)}
                onChange={() => setDevFilters(toggle(devFilters, f.label))} />
            ))}
          </div>

          <div>
            <p className="text-xs font-semibold text-primary mb-2">Platform</p>
            {PLATFORM_FILTERS.map((f) => (
              <FilterCheckbox key={f.label} label={f.label} count={f.count}
                checked={platformFilters.includes(f.label)}
                onChange={() => setPlatFilters(toggle(platformFilters, f.label))} />
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
          <InPhaseSection reports={inPhaseReports} onClickReport={(id) => setShowPreview(id)} />

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

          {filteredReports.length === 0 ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-3">
              <i className="fas fa-search text-3xl text-disabled" />
              <p className="text-muted text-sm">No reports match your filters</p>
              <button onClick={() => { setSearch(''); setInputQuery(''); clearFilters(); }}
                className="text-xs text-accent hover:text-accent-light transition-colors">Clear all</button>
            </div>
          ) : (
            <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
              {filteredReports.map((r) => (
                <ReportCard key={r.id} report={r} onClick={() => setShowPreview(r.id)} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showDisamb && (
        <DisambiguationModal query={pipelineTitle} candidates={disambCandidates} onClose={() => setShowDisamb(false)} onConfirm={handleDisambiguationConfirm} />
      )}
      {showPipeline && (
        <PipelineModal gameTitle={pipelineTitle} onClose={() => setShowPipeline(false)} onComplete={() => {}} />
      )}
      {previewReport && previewData && (
        <ReportPreviewModal report={previewReport} preview={previewData} onClose={() => setShowPreview(null)} />
      )}
    </div>
  );
}
