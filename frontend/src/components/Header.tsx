/**
 * Application Header Component.
 * Displays LabInsight branding, educational disclosure subtitle, and live system status indicators.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React from 'react';
import { Activity, Database, Sparkles, RefreshCw, Server } from 'lucide-react';
import { HealthResponse, ReadinessResponse } from '../types/health';

interface HeaderProps {
  appName: string;
  version: string;
  health: HealthResponse | null;
  readiness: ReadinessResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  appName,
  version,
  health,
  readiness,
  loading,
  onRefresh,
}) => {
  const isApiHealthy = health?.status === 'healthy';
  const isDbReady = readiness?.status === 'ready' && readiness.checks.persistence === 'ok';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-3">
        {/* Branding & Subtitle */}
        <div className="flex items-center space-x-3">
          <div
            className="bg-teal-700 text-white p-2.5 rounded-lg shadow-sm flex items-center justify-center shrink-0"
            aria-hidden="true"
          >
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">{appName}</h1>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-200">
                v{version}
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Assessment Prototype &bull; Educational Clinical Reference Only &bull; Candidate 267
            </p>
          </div>
        </div>

        {/* Live System Connectivity & Readiness Indicators */}
        <div className="flex items-center space-x-2 sm:space-x-3 text-xs">
          {/* Backend API Indicator */}
          <div
            className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full border ${
              isApiHealthy
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-rose-50 text-rose-800 border-rose-200'
            }`}
            title={isApiHealthy ? 'FastAPI Backend Online' : 'FastAPI Backend Disconnected'}
          >
            <Server className={`w-3.5 h-3.5 ${isApiHealthy ? 'text-emerald-600' : 'text-rose-600'}`} />
            <span className="font-medium hidden sm:inline">Backend API:</span>
            <span className="font-semibold">{isApiHealthy ? 'Online' : 'Offline'}</span>
          </div>

          {/* Database Readiness Indicator */}
          <div
            className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full border ${
              isDbReady
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-amber-50 text-amber-800 border-amber-200'
            }`}
            title={isDbReady ? 'SQLite WAL Database Connected' : 'Database Disconnected'}
          >
            <Database className={`w-3.5 h-3.5 ${isDbReady ? 'text-emerald-600' : 'text-amber-600'}`} />
            <span className="font-medium hidden sm:inline">Database:</span>
            <span className="font-semibold">{isDbReady ? 'Ready' : 'Not Ready'}</span>
          </div>

          {/* Local Ollama Indicator */}
          <div
            className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200"
            title="Local Ollama daemon running llama3.2:3b with deterministic fallback"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span className="font-medium hidden sm:inline">Local AI:</span>
            <span className="font-semibold">llama3.2:3b</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition disabled:opacity-50"
            aria-label="Refresh system status"
            title="Refresh system status"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-teal-600' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
