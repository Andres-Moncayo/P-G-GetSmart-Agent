/**
 * Enhanced Pipeline Progress Page with detailed API call tracking.
 * 
 * Shows real-time progress of scraping and analysis pipeline with:
 * - API call status for each service (IGDB, RAWG, Steam, Tavily)
 * - Phase progress (scraping, analysis, synthesis, storage)
 * - Task completion status
 * - Performance metrics
 * - Real-time logs
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../services/api';

interface APIStatus {
  name: string;
  status: 'waiting' | 'running' | 'completed' | 'failed' | 'skipped';
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  data_items_found: number;
  error?: string;
  details?: any;
}

interface PhaseInfo {
  status: 'waiting' | 'running' | 'completed' | 'failed' | 'skipped';
  progress: number;
  started_at?: string;
  completed_at?: string;
  tasks: Array<{
    name: string;
    status: 'waiting' | 'running' | 'completed' | 'failed' | 'skipped';
    progress: number;
    error?: string;
  }>;
  api_calls: APIStatus[];
}

interface PipelineStatus {
  pipeline_id: string;
  phase: 'scraping' | 'analysis' | 'synthesis' | 'storage';
  status: 'waiting' | 'running' | 'completed' | 'failed' | 'skipped';
  is_complete: boolean;
  message: string;
  result?: any;
  seconds_elapsed: number;
  current_phase_progress: number;
  overall_progress: number;
  tasks_succeeded: number;
  tasks_failed: number;
  tasks_skipped: number;
  tasks_total: number;
  phases: Record<string, PhaseInfo>;
  api_calls: APIStatus[];
  current_task?: string;
  logs: Array<{
    timestamp: string;
    level: 'info' | 'success' | 'error' | 'warning';
    message: string;
  }>;
  scraping_durations: Record<string, number>;
  analysis_durations: Record<string, number>;
  total_records_processed: number;
}

function PipelineProgressPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const [pipelineData, setPipelineData] = useState<PipelineStatus | null>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch pipeline status
  const fetchPipelineStatus = async () => {
    if (!reportId) return;
    
    try {
      const response = await apiClient.getPipelineStatus(reportId);
      setPipelineData(response);
      setError(null);
    } catch (error: any) {
      console.error('Failed to fetch pipeline status:', error);
      if (error.response?.status === 404) {
        setError('Pipeline not found or may have been archived. Please check the report ID.');
      } else {
        setError('Failed to fetch pipeline status: ' + (error.message || 'Unknown error'));
      }
    } finally {
      setLoading(false);
    }
  };

  // Fetch logs
  const fetchLogs = async () => {
    if (!reportId) return;
    
    try {
      const response = await apiClient.getPipelineLogs(reportId);
      setLogs(response.logs || []);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  useEffect(() => {
    fetchPipelineStatus();
    fetchLogs();

    // Poll for updates every 2 seconds
    const interval = setInterval(() => {
      fetchPipelineStatus();
      fetchLogs();
    }, 2000);

    return () => clearInterval(interval);
  }, [reportId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'skipped': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'running': return '🔄';
      case 'failed': return '❌';
      case 'skipped': return '⏭️';
      default: return '⏳';
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${(seconds / 60).toFixed(1)}m`;
  };

  if (loading && !pipelineData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading pipeline status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow p-6 max-w-md w-full text-center">
          <div className="text-red-600 text-4xl mb-4">❌</div>
          <h2 className="text-xl font-semibold mb-2">Pipeline Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link to="/dashboard" className="text-blue-600 hover:text-blue-800 underline">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!pipelineData) {
    return <div className="min-h-screen bg-gray-50 p-8">No pipeline data found.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Pipeline Progress</h1>
            <Link 
              to="/dashboard" 
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Back to Dashboard
            </Link>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Pipeline ID: {pipelineData.pipeline_id}</h2>
              <div className="flex items-center space-x-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(pipelineData.status)}`}>
                  {getStatusIcon(pipelineData.status)} {pipelineData.status.toUpperCase()}
                </span>
                {pipelineData.is_complete && (
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    🎉 COMPLETED
                  </span>
                )}
              </div>
            </div>
            
            {/* Overall Progress */}
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Overall Progress</span>
                <span>{pipelineData.overall_progress.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${pipelineData.overall_progress}%` }}
                ></div>
              </div>
            </div>
            
            <p className="text-gray-600">{pipelineData.message}</p>
          </div>
        </div>

        {/* Phase Progress */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {(['scraping', 'analysis', 'synthesis', 'storage'] as const).map((phase) => {
            const phaseInfo = pipelineData.phases[phase];
            return (
              <div 
                key={phase} 
                className={`bg-white rounded-lg shadow p-4 border-2 ${
                  pipelineData.phase === phase ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold capitalize">{phase}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(phaseInfo?.status || 'waiting')}`}>
                    {phaseInfo?.status || 'waiting'}
                  </span>
                </div>
                
                {phaseInfo && (
                  <div>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{phaseInfo.progress.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          phaseInfo.status === 'completed' ? 'bg-green-500' : 
                          phaseInfo.status === 'running' ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                        style={{ width: `${phaseInfo.progress}%` }}
                      ></div>
                    </div>
                    
                    {/* Tasks in this phase */}
                    {phaseInfo.tasks.length > 0 && (
                      <div className="mt-3 space-y-1">
                        {phaseInfo.tasks.map((task, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs">
                            <span className="truncate">{task.name}</span>
                            <span className={getStatusColor(task.status)}>
                              {getStatusIcon(task.status)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* API Call Details */}
        {pipelineData.api_calls.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold mb-4">API Call Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {pipelineData.api_calls.map((api, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{api.name}</h4>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(api.status)}`}>
                      {getStatusIcon(api.status)} {api.status}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div>Items found: {api.data_items_found}</div>
                    {api.duration_seconds && (
                      <div>Duration: {formatDuration(api.duration_seconds)}</div>
                    )}
                    {api.error && (
                      <div className="text-red-600 text-xs mt-2">
                        Error: {api.error}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Task Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="font-semibold text-green-600 mb-2">Completed</h4>
            <p className="text-2xl font-bold">{pipelineData.tasks_succeeded}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="font-semibold text-red-600 mb-2">Failed</h4>
            <p className="text-2xl font-bold">{pipelineData.tasks_failed}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="font-semibold text-gray-600 mb-2">Skipped</h4>
            <p className="text-2xl font-bold">{pipelineData.tasks_skipped}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h4 className="font-semibold text-blue-600 mb-2">Total Tasks</h4>
            <p className="text-2xl font-bold">{pipelineData.tasks_total}</p>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Time Elapsed:</span>
                <span className="font-medium">{formatDuration(pipelineData.seconds_elapsed)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Records Processed:</span>
                <span className="font-medium">{pipelineData.total_records_processed}</span>
              </div>
              
              {Object.keys(pipelineData.scraping_durations).length > 0 && (
                <div>
                  <p className="font-medium mb-2">Scraping Durations:</p>
                  {Object.entries(pipelineData.scraping_durations).map(([key, duration]) => (
                    <div key={key} className="flex justify-between ml-4">
                      <span className="text-gray-600 capitalize">{key}:</span>
                      <span className="font-medium">{formatDuration(duration)}</span>
                    </div>
                  ))}
                </div>
              )}
              
              {Object.keys(pipelineData.analysis_durations).length > 0 && (
                <div>
                  <p className="font-medium mb-2">Analysis Durations:</p>
                  {Object.entries(pipelineData.analysis_durations).map(([key, duration]) => (
                    <div key={key} className="flex justify-between ml-4">
                      <span className="text-gray-600 capitalize">{key}:</span>
                      <span className="font-medium">{formatDuration(duration)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Real-time Logs */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Real-time Logs</h3>
              <button 
                onClick={fetchLogs}
                className="text-sm px-3 py-1 bg-blue-100 text-blue-600 rounded hover:bg-blue-200"
              >
                Refresh
              </button>
            </div>
            <div className="h-64 overflow-y-auto space-y-2 text-sm font-mono border rounded p-3 bg-gray-50">
              {logs.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No logs available</p>
              ) : (
                logs.slice(-50).reverse().map((log, idx) => (
                  <div key={idx} className="flex items-start space-x-2 border-b border-gray-200 pb-1">
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`text-xs px-1 py-0.5 rounded ${
                      log.level === 'error' ? 'bg-red-100 text-red-700' :
                      log.level === 'success' ? 'bg-green-100 text-green-700' :
                      log.level === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {log.level.toUpperCase()}
                    </span>
                    <span className="text-gray-700 break-all">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PipelineProgressPage;