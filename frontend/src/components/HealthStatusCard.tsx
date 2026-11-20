import React from 'react';
import {
  CheckCircle2,
  XCircle,
  RefreshCw,
  Server,
  Layers,
  Settings,
  Database,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { HealthResponse, ReadinessResponse } from '../types/health';

interface HealthStatusCardProps {
  health: HealthResponse | null;
  readiness: ReadinessResponse | null;
  loading: boolean;
  error: string | null;
  lastChecked: string | null;
  onRefresh: () => void;
}

export const HealthStatusCard: React.FC<HealthStatusCardProps> = ({
  health,
  readiness,
  loading,
  error,
  lastChecked,
  onRefresh,
}) => {
  const isHealthy = health?.status === 'healthy';
  const isReady = readiness?.status === 'ready';
  const isConnected = isHealthy && !error;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div
            className={`p-2.5 rounded-lg ${
              isConnected
                ? 'bg-emerald-50 text-emerald-600'
                : 'bg-rose-50 text-rose-600'
            }`}
          >
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Backend System Connectivity</h2>
            <p className="text-xs text-slate-500">
              Live communication with FastAPI service endpoints
            </p>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          aria-label="Refresh backend connection status"
          className="inline-flex items-center px-3.5 py-1.5 border border-slate-300 shadow-sm text-xs font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin text-blue-600' : 'text-slate-500'}`}
          />
          {loading ? 'Checking...' : 'Refresh Status'}
        </button>
      </div>

      <div className="p-6">
        {/* Main Status Pill */}
        <div className="mb-6 flex items-center justify-between p-4 rounded-lg bg-slate-50 border border-slate-200">
          <div className="flex items-center space-x-3">
            {isConnected ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-500 flex-shrink-0" />
            ) : (
              <XCircle className="w-6 h-6 text-rose-500 flex-shrink-0" />
            )}
            <div>
              <div className="text-sm font-semibold text-slate-900">
                {isConnected
                  ? 'FastAPI Backend Connected & Healthy'
                  : 'Backend Service Unavailable'}
              </div>
              <div className="text-xs text-slate-500 mt-0.5">
                {isConnected
                  ? `Response received from ${health?.app || 'LabInsight'} (v${health?.version || '0.1.0'})`
                  : 'Unable to reach backend API endpoints. Check backend process.'}
              </div>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
              isConnected
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-rose-100 text-rose-800'
            }`}
          >
            {isConnected ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>

        {/* Error Alert if Offline */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
            <div className="flex items-start">
              <AlertCircle className="w-4 h-4 text-rose-600 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block mb-1">Connection Failure:</span>
                <p className="font-mono text-[11px] mb-2">{error}</p>
                <p className="text-rose-700">
                  Ensure the FastAPI backend is running via PowerShell:
                  <code className="bg-rose-100 px-1.5 py-0.5 rounded ml-1 text-slate-800">
                    .venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
                  </code>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Grid of Verified Probes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Liveness Probe */}
          <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 flex items-center">
                <Layers className="w-3.5 h-3.5 mr-1.5 text-blue-500" />
                Liveness Probe (GET /api/v1/health)
              </span>
              <span
                className={`text-[11px] font-semibold px-2 py-0.5 rounded ${
                  isHealthy
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-slate-200 text-slate-700'
                }`}
              >
                {health?.status || 'UNKNOWN'}
              </span>
            </div>
            <div className="text-xs text-slate-600 space-y-1">
              <div>
                <span className="text-slate-400">Endpoint:</span>{' '}
                <code className="font-mono text-[11px] text-slate-700">/api/v1/health</code>
              </div>
              <div>
                <span className="text-slate-400">App Name:</span>{' '}
                <span className="font-medium text-slate-800">{health?.app || '—'}</span>
              </div>
              <div>
                <span className="text-slate-400">Version:</span>{' '}
                <span className="font-medium text-slate-800">{health?.version || '—'}</span>
              </div>
            </div>
          </div>

          {/* Readiness Probe */}
          <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 flex items-center">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-indigo-500" />
                Readiness Probe (GET /api/v1/ready)
              </span>
              <span
                className={`text-[11px] font-semibold px-2 py-0.5 rounded ${
                  isReady
                    ? 'bg-indigo-100 text-indigo-800'
                    : 'bg-slate-200 text-slate-700'
                }`}
              >
                {readiness?.status || 'UNKNOWN'}
              </span>
            </div>
            <div className="text-xs text-slate-600 space-y-1">
              <div>
                <span className="text-slate-400">Environment:</span>{' '}
                <span className="font-medium text-slate-800 capitalize">
                  {readiness?.environment || '—'}
                </span>
              </div>
              <div>
                <span className="text-slate-400">Phase Baseline:</span>{' '}
                <span className="font-medium text-slate-800">{readiness?.phase || '—'}</span>
              </div>
              <div>
                <span className="text-slate-400">Configuration:</span>{' '}
                <span className="font-medium text-emerald-600">
                  {readiness?.checks.configuration || '—'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Readiness Architectural Details */}
        <div className="mt-4 p-4 rounded-lg border border-slate-200 bg-slate-50/50">
          <div className="text-xs font-semibold text-slate-700 mb-2 flex items-center">
            <Settings className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            Phase 1 Architectural Boundary Verification
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-600">
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-amber-500 flex-shrink-0" />
              <div>
                <span className="text-slate-500">Persistence Status:</span>{' '}
                <span className="font-mono text-[11px] bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded border border-amber-200">
                  {readiness?.checks.persistence || 'pending_phase_2_initialization'}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-slate-400 flex-shrink-0" />
              <div>
                <span className="text-slate-500">Last Verified:</span>{' '}
                <span className="font-medium text-slate-800">
                  {lastChecked ? new Date(lastChecked).toLocaleTimeString() : 'Not yet'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
