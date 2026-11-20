/**
 * Roadmap and Phase Board Component.
 * Collapsible section illustrating Blueprint v0.2 governance and phase gates.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useState } from 'react';
import { Layers, CheckCircle2, ChevronDown, ChevronUp, Lock } from 'lucide-react';

export const RoadmapCard: React.FC = () => {
  const [collapsed, setCollapsed] = useState<boolean>(true);

  const phases = [
    { id: 'Phase 1', name: 'Repository & Foundation', status: 'COMPLETE', desc: 'FastAPI foundation, health/readiness endpoints, React shell' },
    { id: 'Phase 2', name: 'Domain & Persistence', status: 'COMPLETE', desc: 'SQLite WAL, Alembic, Patient & Analysis models' },
    { id: 'Phase 3', name: 'Validation & CRUD REST API', status: 'COMPLETE', desc: 'Decimal precision, duplicate detection, full REST CRUD' },
    { id: 'Phase 4A', name: 'TestWell Health API', status: 'COMPLETE', desc: 'External reference range & observation normalization' },
    { id: 'Phase 4B', name: 'Local Ollama AI', status: 'COMPLETE', desc: 'llama3.2:3b remarks generation with deterministic fallback' },
    { id: 'Phase 5', name: 'Professional Frontend', status: 'ACTIVE', desc: 'Clinical intake, observations viewer, disclosure workflows' },
    { id: 'Phase 6', name: 'E2E Testing & QA', status: 'GATED', desc: 'Full-system integration verification & hardening' },
    { id: 'Phase 7', name: 'Release & Submission', status: 'GATED', desc: 'Repository sanitization, demo & employer packaging' },
  ];

  return (
    <section
      aria-labelledby="roadmap-heading"
      className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mt-6 transition"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <Layers className="w-5 h-5 text-teal-700" />
          <div>
            <h3 id="roadmap-heading" className="text-sm font-bold text-slate-900">
              Engineering Implementation Roadmap & Phase Board
            </h3>
            <p className="text-xs text-slate-500">
              Blueprint v0.2 &bull; Phased Authorization Model &bull; Phase 5 Active
            </p>
          </div>
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="inline-flex items-center gap-1 text-xs text-slate-600 hover:text-slate-900 font-medium px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition"
          aria-expanded={!collapsed}
        >
          <span>{collapsed ? 'View Phase Gates' : 'Collapse'}</span>
          {collapsed ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
      </div>

      {!collapsed && (
        <div className="mt-4 pt-4 border-t border-slate-100">
          <p className="text-xs text-slate-600 mb-4 leading-relaxed">
            Implementation strictly progresses through independently verified phases. Each phase gate requires verifiable automated test evidence before the next phase is unlocked.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {phases.map((phase) => {
              const isComplete = phase.status === 'COMPLETE';
              const isActive = phase.status === 'ACTIVE';

              return (
                <div
                  key={phase.id}
                  className={`p-3 rounded-lg border text-xs flex flex-col justify-between ${
                    isActive
                      ? 'bg-teal-50/60 border-teal-300 ring-1 ring-teal-400'
                      : isComplete
                      ? 'bg-slate-50/70 border-slate-200'
                      : 'bg-slate-50/30 border-slate-200 opacity-60'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-slate-900">{phase.id}</span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${
                          isActive
                            ? 'bg-teal-700 text-white'
                            : isComplete
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-slate-200 text-slate-600'
                        }`}
                      >
                        {phase.status}
                      </span>
                    </div>
                    <div className="font-semibold text-slate-800 text-[11px] mb-1">{phase.name}</div>
                    <p className="text-[10px] text-slate-500 leading-tight">{phase.desc}</p>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-end">
                    {isComplete ? (
                      <span className="text-[10px] text-emerald-700 flex items-center gap-1 font-medium">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Verified</span>
                      </span>
                    ) : isActive ? (
                      <span className="text-[10px] text-teal-800 font-bold flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-teal-600 animate-ping" />
                        <span>In Development</span>
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-400 flex items-center gap-1">
                        <Lock className="w-3 h-3" />
                        <span>Gated</span>
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
};
