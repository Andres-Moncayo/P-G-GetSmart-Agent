import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { DATE_FILTERS } from '../data/gameData';
import type { Report, GameCandidate, ApiReport, ApiReportListResponse } from '../types/game';
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

// ─── PipelineModal ────────────────────────────────────────────────────────────

type PhaseState = 'idle' | 'running' | 'done';
type SubtaskState = 'waiting' | 'running' | 'paused' | 'blocked' | 'completed' | 'failed';

const PHASE_CONFIG = [
  { 
    name: 'Scraping', 
    icon: 'fa-search', 
    substeps: ['Buscando en bases de datos', 'Obteniendo datos del juego', 'Recopilando reseñas'],
    color: 'from-blue-500 to-cyan-500'
  },
  { 
    name: 'Análisis IA', 
    icon: 'fa-brain', 
    substeps: ['Tech Systems', 'Strategy & Market', 'Optimization', 'Spec Detection'],
    color: 'from-purple-500 to-pink-500'
  },
  { 
    name: 'Síntesis', 
    icon: 'fa-layer-group', 
    substeps: ['Procesando resultados', 'Creando insights', 'Construyendo correlaciones'],
    color: 'from-orange-500 to-red-500'
  },
  { 
    name: 'Guardar en BD', 
    icon: 'fa-database', 
    substeps: ['Validando datos', 'Almacenando resultados', 'Actualizando índices'],
    color: 'from-green-500 to-emerald-500'
  }
];

interface PipelineStatus {
  status: 'queued' | 'processing' | 'completed' | 'failed';
  message: string;
  details?: any;
  current_task?: string;
  phase?: string;
  phase_progress?: number;
  overall_progress?: number;
  tasks_succeeded?: number;
  tasks_failed?: number;
  tasks_total?: number;
  phases?: Record<string, {
    status: string;
    progress: number;
    tasks: Array<{
      name: string;
      status: string;
      progress: number;
      error?: string;
    }>;
  }>;
}

interface PipelineModalProps { gameTitle: string; reportId: string; onClose: () => void; onComplete: (reportId: string, dbReportId?: string) => void; }
function PipelineModal({ gameTitle, reportId, onClose, onComplete }: PipelineModalProps) {
  const [currentPhase, setCurrentPhase] = useState(0);
  const [progress, setProgress] = useState(5);
  const [done, setDone] = useState(false);
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [detailedStatus, setDetailedStatus] = useState<any>(null);
  const [currentSubstep, setCurrentSubstep] = useState(0);
  
  // Map backend pipeline status to frontend phases
  const getPhaseFromStatus = (statusInfo: PipelineStatus) => {
    const phase = statusInfo.phase?.toLowerCase() || '';

    if (phase === 'scraping') return 0;
    if (phase === 'analysis') return 1;
    if (phase === 'synthesis') return 2;
    if (phase === 'storage') return 3;

    const message = statusInfo.message.toLowerCase();
    if (message.includes('scraping') || message.includes('phase 1')) return 0;
    if (message.includes('analysis') || message.includes('phase 2')) return 1;
    if (message.includes('synthesis') || message.includes('phase 3')) return 2;
    if (message.includes('saving') || message.includes('phase 4') || message.includes('database')) return 3;

    return currentPhase;
  };

  const getProgressFromStatus = (statusInfo: PipelineStatus) => {
    if (statusInfo.overall_progress !== undefined && statusInfo.overall_progress !== null) {
      return statusInfo.overall_progress;
    }

    const phase = getPhaseFromStatus(statusInfo);
    const baseProgress = phase * 25;
    const phaseProgress = statusInfo.phase_progress || 0;
    return Math.min(100, baseProgress + (phaseProgress / 100) * 25);
  };

  // Poll for pipeline status
  useEffect(() => {
    if (!reportId) return;

    const pollInterval = setInterval(async () => {
      try {
        const statusData = await apiClient.getPipelineStatus(reportId);
        setStatus(statusData);
        
        // Also get detailed logs if available
        try {
          const detailedData = await apiClient.getPipelineLogs(reportId);
          setDetailedStatus(detailedData);
        } catch (e) {
          // Detailed logs might not be available yet
        }
        
if (statusData.status === 'completed' || statusData.status === 'done') {
          setProgress(100);
          setDone(true);
          setCurrentPhase(4);
          setTimeout(() => {
            onComplete(reportId, statusData.db_report_id);
            onClose();
          }, 2000);
          clearInterval(pollInterval);
        } else if (statusData.status === 'failed') {
          clearInterval(pollInterval);
        } else {
          const newPhase = getPhaseFromStatus(statusData);
          setCurrentPhase(newPhase);
          setProgress(getProgressFromStatus(statusData));
          
          // Update substep based on current task
          if (statusData.current_task) {
            const phaseSubsteps = PHASE_CONFIG[newPhase].substeps;
            const substepIndex = phaseSubsteps.findIndex(step => 
              step.toLowerCase().includes(statusData.current_task.toLowerCase()) ||
              statusData.current_task.toLowerCase().includes(step.toLowerCase())
            );
            if (substepIndex !== -1) {
              setCurrentSubstep(substepIndex);
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
        clearInterval(pollInterval);
      }
    }, 1500);

    return () => clearInterval(pollInterval);
  }, [reportId, onComplete, onClose]);

  const phaseIcon = (index: number, currentPhase: number, done: boolean) => {
    if (done) return <i className="fas fa-check text-success text-xs" />;
    if (index === currentPhase) return <div className="w-3 h-3 border-2 border-accent border-t-transparent rounded-full animate-spin" />;
    if (index < currentPhase) return <i className="fas fa-check text-success text-xs" />;
    return <span className="w-2 h-2 rounded-full bg-border block" />;
  };

  const getPhaseState = (index: number): PhaseState => {
    if (done) return 'done';
    if (index === currentPhase) return 'running';
    if (index < currentPhase) return 'done';
    return 'idle';
  };

const getSubstepState = (phaseIndex: number, substepIndex: number, substepName: string): SubtaskState => {
    // Get real status from backend if available
    const phaseKey = ['scraping', 'analysis', 'synthesis', 'storage'][phaseIndex];
    const phaseData = status?.phases?.[phaseKey];
    
    if (phaseData?.tasks) {
      const task = phaseData.tasks.find((t: any) => t.name === substepName);
      if (task) {
        // Map backend status to frontend states
        const backendStatus = task.status;
        if (backendStatus === 'COMPLETED' || backendStatus === 'completed') return 'completed';
        if (backendStatus === 'RUNNING' || backendStatus === 'running') return 'running';
        if (backendStatus === 'PAUSED' || backendStatus === 'paused') return 'paused';
        if (backendStatus === 'BLOCKED' || backendStatus === 'blocked') return 'blocked';
        if (backendStatus === 'FAILED' || backendStatus === 'failed') return 'failed';
        if (backendStatus === 'WAITING' || backendStatus === 'waiting') return 'waiting';
        return backendStatus as SubtaskState;
      }
    }
    
    // Only use fallback if no backend data available
    if (done && phaseIndex < currentPhase) return 'completed';
    if (done && phaseIndex === currentPhase) return 'completed';
    if (phaseIndex < currentPhase) return 'completed';
    if (phaseIndex === currentPhase) {
      // Don't just assume completion based on index
      const state = getPhaseState(phaseIndex);
      return state === 'running' ? 'waiting' : 'waiting';
    }
    return 'waiting';
  };

  const getSubstepProgress = (phaseIndex: number, substepIndex: number, substepName: string): number => {
    // Get real progress from backend if available
    const phaseKey = ['scraping', 'analysis', 'synthesis', 'storage'][phaseIndex];
    const phaseData = status?.phases?.[phaseKey];
    
    if (phaseData?.tasks) {
      const task = phaseData.tasks.find((t: any) => t.name === substepName);
      if (task) {
        return task.progress || 0;
      }
    }
    
    // Fallback to估算
    const state = getSubstepState(phaseIndex, substepIndex, substepName);
    return state === 'completed' ? 100 : state === 'running' ? 50 : 0;
  };

  const getCurrentStatusMessage = () => {
    if (done) return '✅ ¡Reporte completado con éxito!';
    if (status?.status === 'failed') return '❌ Error en el análisis. Por favor inténtalo de nuevo.';
    if (status?.current_task) return status.current_task;
    if (detailedStatus?.logs?.length > 0) return detailedStatus.logs[detailedStatus.logs.length - 1].message;
    
    const phaseMessages = [
      '🔍 Buscando en bases de datos de juegos...',
      '🧠 Analizando con IA para obtener insights...',
      '🔄 Sintetizando resultados y correlaciones...',
      '💾 Guardando en la base de datos...'
    ];
    return phaseMessages[currentPhase] || 'Procesando...';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-lg mx-4 shadow-modal overflow-hidden">
        <div className="p-5 border-b border-border">
          <p className="text-xs text-accent font-medium uppercase tracking-wider mb-1">GetSmart Pipeline</p>
          <h3 className="text-base font-bold text-primary truncate">{gameTitle}</h3>
          <p className="text-xs text-muted mt-2 font-medium">{getCurrentStatusMessage()}</p>
        </div>
        <div className="p-5 space-y-4 max-h-[70vh] overflow-y-auto scrollbar-hide">
          {/* Progreso general */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted">Progreso Total</span>
              <span className="text-xs font-bold text-accent">{progress}%</span>
            </div>
            <div className="h-2 bg-elevated rounded-full overflow-hidden">
              <div 
                className={`h-full bg-gradient-to-r ${PHASE_CONFIG[Math.floor(currentPhase)]?.color || 'from-accent to-secondary'} rounded-full transition-all duration-700`} 
                style={{ width: `${progress}%` }} 
              />
            </div>
          </div>

          {/* Estadísticas si están disponibles */}
          {status && (status.tasks_total || status.tasks_succeeded || status.tasks_failed) && (
            <div className="flex gap-4 text-xs">
              <div className="flex items-center gap-1">
                <i className="fas fa-check-circle text-success text-[10px]" />
                <span className="text-muted">Completadas: {status.tasks_succeeded || 0}</span>
              </div>
              <div className="flex items-center gap-1">
                <i className="fas fa-times-circle text-danger text-[10px]" />
                <span className="text-muted">Fallidas: {status.tasks_failed || 0}</span>
              </div>
              <div className="flex items-center gap-1">
                <i className="fas fa-list text-accent text-[10px]" />
                <span className="text-muted">Total: {status.tasks_total || 0}</span>
              </div>
            </div>
          )}

          {/* Fases con subtareas */}
          <div className="space-y-3">
            {PHASE_CONFIG.map((phase, i) => {
              const state = getPhaseState(i);
              return (
                <div key={phase.name} className={`rounded-lg border p-3 transition-all ${
                  state === 'running' ? 'border-accent bg-accent/5' : 
                  state === 'done' ? 'border-success/20 bg-success/5' : 'border-border bg-elevated/30'
                }`}>
                  {/* Cabecera de fase */}
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
                      {phaseIcon(i, currentPhase, done)}
                    </div>
                    <i className={`fas ${phase.icon} text-xs ${
                      state === 'done' ? 'text-success' : 
                      state === 'running' ? 'text-accent' : 'text-disabled'
                    }`} />
                    <span className={`text-sm font-semibold ${
                      state === 'done' ? 'text-primary' : 
                      state === 'running' ? 'text-accent' : 'text-disabled'
                    }`}>{phase.name}</span>
                    {state === 'running' && (
                      <div className="ml-auto">
                        <div className={`w-1.5 h-1.5 rounded-full bg-accent animate-pulse`} />
                      </div>
                    )}
                  </div>

{/* Subtareas de la fase */}
                  <div className="ml-8 space-y-1.5">
                    {phase.substeps.map((substep, j) => {
                      const substepState = getSubstepState(i, j, substep);
                      const substepProgress = getSubstepProgress(i, j, substep);
                      
                      const getStatusColor = (state: SubtaskState) => {
                        switch (state) {
                          case 'running': return 'bg-amber-500';
                          case 'paused': return 'bg-yellow-500';
                          case 'blocked': return 'bg-red-700';
                          case 'failed': return 'bg-red-500';
                          case 'completed': return 'bg-success';
                          default: return 'bg-border';
                        }
                      };
                      
                      const getStatusIcon = (state: SubtaskState) => {
                        switch (state) {
                          case 'running': return 'fa-spinner fa-spin';
                          case 'paused': return 'fa-pause';
                          case 'blocked': return 'fa-lock';
                          case 'failed': return 'fa-times';
                          case 'completed': return 'fa-check';
                          default: return '';
                        }
                      };
                      
                      const getStatusIconColor = (state: SubtaskState) => {
                        switch (state) {
                          case 'running': return 'text-amber-500';
                          case 'paused': return 'text-yellow-500';
                          case 'blocked': return 'text-red-700';
                          case 'failed': return 'text-red-500';
                          case 'completed': return 'text-success';
                          default: return 'text-transparent';
                        }
                      };
                      
                      const getTextColor = (state: SubtaskState) => {
                        switch (state) {
                          case 'running': return 'text-amber-500 font-medium';
                          case 'paused': return 'text-yellow-500';
                          case 'blocked': return 'text-red-700 font-medium';
                          case 'failed': return 'text-red-500 font-medium';
                          case 'completed': return 'text-muted line-through';
                          default: return 'text-disabled';
                        }
                      };

                      return (
                        <div key={j} className="flex items-center gap-2 whitespace-nowrap">
                          {/* Status indicator */}
                          <div className={`w-1.5 h-1.5 rounded-full transition-all flex-shrink-0 ${
                            substepState === 'running' ? 'bg-amber-500 animate-pulse' :
                            getStatusColor(substepState)
                          }`} />
                          
                          {/* Status icon */}
                          <i className={`fas ${
                            getStatusIcon(substepState)
                          } text-[8px] ${
                            getStatusIconColor(substepState)
                          }`} />
                          
                          {/* Substep name */}
                          <span className={`text-xs transition-colors flex-1 min-w-0 ${
                            getTextColor(substepState)
                          }`}>
                            {substep}
                          </span>
                          
                          {/* Progress percentage */}
                          <span className={`text-xs font-medium ${
                            substepState === 'running' ? 'text-amber-500' : 
                            substepState === 'completed' ? 'text-success' : 'text-muted'
                          }`}>
                            {substepProgress > 0 && `${substepProgress.toFixed(0)}%`}
                          </span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Mini progreso de fase */}
                  {state === 'running' && (
                    <div className="mt-2">
                      <div className="h-0.5 bg-elevated rounded-full overflow-hidden">
                        <div className={`h-full bg-gradient-to-r ${phase.color} rounded-full animate-pulse`} style={{ width: '75%' }} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Logs detallados si están disponibles */}
          {detailedStatus?.logs?.length > 0 && (
            <div className="bg-elevated/50 rounded-lg p-3">
              <p className="text-xs font-semibold text-muted mb-2">Actividad reciente:</p>
              <div className="space-y-1 max-h-20 overflow-y-auto scrollbar-hide">
                {detailedStatus.logs.slice(-5).reverse().map((log: any, i: number) => (
                  <div key={i} className="text-xs text-muted flex items-start gap-2">
                    <div className="w-1 h-1 rounded-full bg-accent mt-1.5 flex-shrink-0" />
                    <span>{log.message || log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Estado final */}
          {done && (
            <div className="text-center py-3 border-t border-border">
              <i className="fas fa-check-circle text-success text-2xl mb-2" />
              <p className="text-sm font-semibold text-success">¡Reporte listo para revisar!</p>
            </div>
          )}
          {status?.status === 'failed' && (
            <div className="text-center py-3 border-t border-border">
              <i className="fas fa-exclamation-triangle text-danger text-2xl mb-2" />
              <p className="text-sm font-semibold text-danger">El análisis falló. Por favor intenta nuevamente.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── ReportPreviewModal removed — data now comes from the real API ────────────

// ─── Dashboard ────────────────────────────────────────────────────────────────

// ─── Dashboard ────────────────────────────────────────────────────────────────

type SortKey = 'recent' | 'alpha' | 'year';

export function Dashboard() {
  const [search, setSearch]               = useState('');
  const [sortKey, setSortKey]             = useState<SortKey>('recent');
  const [genreFilters, setGenreFilters]   = useState<string[]>([]);
  const [devFilters, setDevFilters]       = useState<string[]>([]);
  const [platformFilters, setPlatFilters] = useState<string[]>([]);
  const [dateFilter, setDateFilter]       = useState<number | null>(null);

  const [showDisamb, setShowDisamb]           = useState(false);
  const [showPipeline, setShowPipeline]       = useState(false);
  const [inputQuery, setInputQuery]           = useState('');
  const [pipelineTitle, setPipelineTitle]     = useState('');
  const [pipelineReportId, setPipelineReportId] = useState<string | null>(null);
  const [disambCandidates, setDisambCandidates] = useState<GameCandidate[]>([]);
  const [reports, setReports]                 = useState<Report[]>([]);
  const [facets, setFacets]                   = useState<ApiReportListResponse['facets'] | null>(null);
  const [isLoadingReports, setIsLoadingReports] = useState(false);
  const [isGenerating, setIsGenerating]       = useState(false);
  const navigate = useNavigate();

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
    setPipelineTitle(game.name);
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
                <ReportCard key={r.id} report={r} onClick={() => {}} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showDisamb && (
        <DisambiguationModal query={pipelineTitle} candidates={disambCandidates} onClose={() => setShowDisamb(false)} onConfirm={handleDisambiguationConfirm} />
      )}
      {showPipeline && pipelineReportId && (
        <PipelineModal 
          gameTitle={pipelineTitle}
          reportId={pipelineReportId}
          onClose={() => { setShowPipeline(false); setPipelineReportId(null); }}
          onComplete={(reportId, dbReportId) => {
            if (dbReportId) {
              navigate(`/pipeline/${reportId}?db_report_id=${dbReportId}`);
            } else {
              navigate(`/pipeline/${reportId}`);
            }
          }}
        />
      )}
    </div>
  );
}
