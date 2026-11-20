/**
 * Comprehensive Patient Detail Drawer/Modal.
 * Displays patient demographics, live analysis progress, TestWell observations with context qualifiers,
 * local Ollama AI remarks / safe fallback, and complete historical audit lineage.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useState, useEffect } from 'react';
import { Patient } from '../../types/patient';
import { AnalysisDetailResponse } from '../../types/analysis';
import { formatDateForDisplay, formatDateTime } from '../../utils/date';
import { OverallStatusBadge, AiStatusBadge, BiomarkerFlagBadge } from '../common/StatusBadge';
import { useAnalysisPoll } from '../../hooks/useAnalysisPoll';
import { analysisService } from '../../services/analysisService';
import {
  User,
  Activity,
  Sparkles,
  History,
  ExternalLink,
  AlertTriangle,
  Clock,
  RefreshCw,
  X,
  Pencil,
  Trash2,
  ShieldAlert,
  Calendar,
  Mail,
  FileText,
} from 'lucide-react';

interface PatientDetailModalProps {
  isOpen: boolean;
  patient: Patient | null;
  onClose: () => void;
  onEdit: (patientId: number) => void;
  onDelete: (patient: Patient) => void;
  onPatientUpdated?: () => void;
}

export const PatientDetailModal: React.FC<PatientDetailModalProps> = ({
  isOpen,
  patient,
  onClose,
  onEdit,
  onDelete,
  onPatientUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'observations' | 'ai' | 'history'>('observations');
  const [historyRuns, setHistoryRuns] = useState<AnalysisDetailResponse[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);
  const [selectedRun, setSelectedRun] = useState<AnalysisDetailResponse | null>(null);
  const [triggeringRun, setTriggeringRun] = useState<boolean>(false);

  // Use the long-running analysis poll hook
  const {
    analysis: liveAnalysis,
    isPolling,
    elapsedSeconds,
    startPolling,
  } = useAnalysisPoll({
    patientId: patient?.id ?? 0,
    initialAnalysis: patient?.latest_analysis || null,
    onTerminal: (completed) => {
      setSelectedRun(completed);
      loadHistory();
      if (onPatientUpdated) onPatientUpdated();
    },
    autoStart: true,
  });

  const loadHistory = async () => {
    if (!patient) return;
    setLoadingHistory(true);
    try {
      const runs = await analysisService.listAnalyses(patient.id);
      setHistoryRuns(runs);
    } catch {
      // History fetch error
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (isOpen && patient) {
      loadHistory();
      setActiveTab('observations');
    }
  }, [isOpen, patient?.id]);

  if (!isOpen || !patient) return null;

  // Active display analysis is selectedRun or liveAnalysis
  const displayAnalysis = selectedRun || liveAnalysis;
  const isLiveRun = !selectedRun || selectedRun.id === liveAnalysis?.id;

  const handleTriggerRetry = async () => {
    if (!patient || triggeringRun || isPolling) return;
    setTriggeringRun(true);
    try {
      const scheduled = await analysisService.triggerAnalysis(patient.id);
      startPolling(scheduled.id);
      setSelectedRun(null); // Return to live view
      await loadHistory();
      if (onPatientUpdated) onPatientUpdated();
    } catch (err) {
      // Error handling
    } finally {
      setTriggeringRun(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="patient-detail-title"
    >
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in-50 zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-teal-700 text-white shadow-xs shrink-0">
              <User className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 id="patient-detail-title" className="text-lg font-bold text-slate-900 tracking-tight">
                  {patient.full_name}
                </h3>
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-200/70 text-slate-700 font-semibold">
                  #{patient.id}
                </span>
              </div>
              <p className="text-xs text-slate-500 flex flex-wrap items-center gap-x-3 gap-y-1 mt-0.5">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  DOB: {formatDateForDisplay(patient.date_of_birth)}
                </span>
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5" />
                  {patient.email}
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onEdit(patient.id)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium transition"
            >
              <Pencil className="w-3.5 h-3.5 text-slate-500" />
              <span>Edit</span>
            </button>
            <button
              onClick={() => onDelete(patient)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-rose-200 bg-rose-50/50 hover:bg-rose-50 text-rose-700 text-xs font-medium transition"
            >
              <Trash2 className="w-3.5 h-3.5 text-rose-600" />
              <span>Delete</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition ml-1"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Biomarker Summary Bar */}
        <div className="px-5 py-3 bg-slate-100/60 border-b border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex flex-wrap items-center gap-6">
            <div>
              <span className="text-slate-500 font-medium block text-[11px]">Glucose (Conventional)</span>
              <span className="font-bold text-slate-900 text-sm">{patient.glucose_value} mg/dL</span>
            </div>
            <div className="w-px h-6 bg-slate-200 hidden sm:block" />
            <div>
              <span className="text-slate-500 font-medium block text-[11px]">Haemoglobin (Conventional)</span>
              <span className="font-bold text-slate-900 text-sm">{patient.haemoglobin_value} g/dL</span>
            </div>
            <div className="w-px h-6 bg-slate-200 hidden sm:block" />
            <div>
              <span className="text-slate-500 font-medium block text-[11px]">Cholesterol (Conventional)</span>
              <span className="font-bold text-slate-900 text-sm">{patient.cholesterol_value} mg/dL</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-500">Unit Profile:</span>
            <code className="text-[11px] font-mono bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-700">
              {patient.unit_profile_code}
            </code>
          </div>
        </div>

        {/* Polling / Pending Live Banner */}
        {isPolling && (
          <div className="bg-blue-50 border-b border-blue-200 px-5 py-3 flex items-center justify-between text-xs text-blue-900 animate-pulse">
            <div className="flex items-center gap-2.5">
              <Clock className="w-4 h-4 text-blue-600 animate-spin shrink-0" />
              <div>
                <span className="font-semibold">Local AI Inference In Progress</span>
                <p className="text-[11px] text-blue-700">
                  Synthesizing TestWell reference data with local Ollama (<code className="font-mono">llama3.2:3b</code>).
                  Cold inference may take 10–35s on workstation CPU.
                </p>
              </div>
            </div>
            <span className="font-mono font-semibold text-blue-800 bg-blue-100/70 px-2 py-0.5 rounded">
              {elapsedSeconds}s elapsed
            </span>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200 px-5 bg-white text-xs font-semibold">
          <button
            onClick={() => setActiveTab('observations')}
            className={`py-3 px-4 border-b-2 inline-flex items-center gap-2 transition ${
              activeTab === 'observations'
                ? 'border-teal-700 text-teal-800'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>TestWell Observations</span>
          </button>

          <button
            onClick={() => setActiveTab('ai')}
            className={`py-3 px-4 border-b-2 inline-flex items-center gap-2 transition ${
              activeTab === 'ai'
                ? 'border-indigo-600 text-indigo-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>AI Remarks & Fallback</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`py-3 px-4 border-b-2 inline-flex items-center gap-2 transition ${
              activeTab === 'history'
                ? 'border-teal-700 text-teal-800'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Analysis History ({historyRuns.length})</span>
          </button>

          {/* Trigger Retry Button on tab line */}
          <div className="ml-auto flex items-center py-2">
            <button
              onClick={handleTriggerRetry}
              disabled={isPolling || triggeringRun}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 text-xs font-semibold transition disabled:opacity-40"
              title="Schedule a new analysis run for this patient"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${triggeringRun ? 'animate-spin' : ''}`} />
              <span>Rerun Analysis</span>
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {/* Historical Run Banner if inspecting past run */}
          {!isLiveRun && selectedRun && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 text-xs flex items-center justify-between">
              <span>
                Viewing historical analysis <strong>Run #{selectedRun.run_number}</strong> (Recorded:{' '}
                {formatDateTime(selectedRun.completed_at || selectedRun.created_at)})
              </span>
              <button
                onClick={() => setSelectedRun(null)}
                className="underline font-semibold hover:text-amber-950"
              >
                Return to Latest Run
              </button>
            </div>
          )}

          {/* Current Status Header Card */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
                Analysis Run #{displayAnalysis?.run_number ?? 1} Lineage
              </span>
              <div className="flex items-center gap-2.5 mt-1">
                <OverallStatusBadge status={displayAnalysis?.overall_status} size="md" />
                <AiStatusBadge
                  status={displayAnalysis?.ai_status}
                  generationLabel={
                    displayAnalysis?.ai_result_json?.generation_label ||
                    (displayAnalysis?.ai_status === 'SUCCEEDED' ? 'AI_GENERATED' : undefined)
                  }
                  size="md"
                />
              </div>
            </div>

            <div className="text-right text-xs text-slate-500">
              <span className="block">
                Executed: <strong>{displayAnalysis?.external_provider || 'TestWell'}</strong> &bull;{' '}
                <strong>{displayAnalysis?.ai_model || 'llama3.2:3b'}</strong>
              </span>
              <span className="block text-[11px] text-slate-400 mt-0.5">
                Completed: {formatDateTime(displayAnalysis?.completed_at)}
              </span>
            </div>
          </div>

          {/* TAB 1: TestWell Observations */}
          {activeTab === 'observations' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">
                    TestWell Educational Reference Observations
                  </h4>
                  <p className="text-xs text-slate-500">
                    External educational reference intervals matched to patient numerical measurements
                  </p>
                </div>
              </div>

              {!displayAnalysis?.external_result_json?.observations ||
              displayAnalysis.external_result_json.observations.length === 0 ? (
                <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-slate-500 text-xs">
                  <Activity className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="font-semibold text-slate-700">Observations Not Yet Available</p>
                  <p className="mt-1">
                    {displayAnalysis?.overall_status === 'PENDING'
                      ? 'Analysis is currently executing in background. Observations will appear once provider response returns.'
                      : 'No provider observations recorded for this run.'}
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {displayAnalysis.external_result_json.observations.map((obs) => {
                    const isContextUnconfirmed = obs.context_status !== 'CONFIRMED';
                    return (
                      <div
                        key={obs.analyte}
                        className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs space-y-3"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-900 text-sm capitalize">
                              {obs.matched_marker || obs.analyte}
                            </span>
                            <BiomarkerFlagBadge flag={obs.flag} />
                          </div>

                          <span className="font-mono font-bold text-slate-900 text-sm">
                            {obs.value} {obs.unit}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                          <div>
                            <span className="text-slate-500 block text-[11px]">Provider Reference Range</span>
                            <span className="font-semibold text-slate-800">
                              {obs.range_text || 'None specified'}
                            </span>
                            {obs.range_qualifier && (
                              <span className="text-slate-500 block text-[11px] mt-0.5">
                                Qualifier: <em>{obs.range_qualifier}</em>
                              </span>
                            )}
                          </div>

                          {obs.suggests && (
                            <div>
                              <span className="text-slate-500 block text-[11px]">Educational Guidance</span>
                              <p className="text-slate-700 mt-0.5">{obs.suggests}</p>
                            </div>
                          )}
                        </div>

                        {/* Clinical Context Limitation Warning */}
                        {isContextUnconfirmed && (
                          <div className="p-2.5 rounded-lg bg-amber-50/80 border border-amber-200 text-amber-900 text-xs flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                            <div>
                              <span className="font-semibold block">Context Limitation Warning</span>
                              <p className="text-[11px] text-amber-800">
                                Patient demographic / physiological context ({obs.range_qualifier || 'fasting/sex'})
                                was not clinically confirmed for this patient. Reference range comparison is context-limited.
                              </p>
                            </div>
                          </div>
                        )}

                        {/* Provider Citations */}
                        {obs.citations && obs.citations.length > 0 && (
                          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-[11px]">
                            <span className="text-slate-500 font-medium">Verified Citations:</span>
                            {obs.citations.map((cite, i) =>
                              cite.url ? (
                                <a
                                  key={i}
                                  href={cite.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-teal-700 hover:text-teal-900 underline font-medium"
                                >
                                  <span>{cite.label}</span>
                                  <ExternalLink className="w-3 h-3" />
                                </a>
                              ) : (
                                <span key={i} className="text-slate-700 font-medium">
                                  {cite.label}
                                </span>
                              )
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: AI Remarks & Fallback */}
          {activeTab === 'ai' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">
                    Local AI Remarks Generation
                  </h4>
                  <p className="text-xs text-slate-500">
                    Natural-language clinical reference remarks synthesized by local Ollama llama3.2:3b
                  </p>
                </div>

                <AiStatusBadge
                  status={displayAnalysis?.ai_status}
                  generationLabel={displayAnalysis?.ai_result_json?.generation_label}
                />
              </div>

              {!displayAnalysis?.remarks_text ? (
                <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-slate-500 text-xs">
                  <Sparkles className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="font-semibold text-slate-700">AI Remarks Not Generated</p>
                  <p className="mt-1">
                    {displayAnalysis?.overall_status === 'PENDING'
                      ? 'Local Ollama model is currently generating structured remarks.'
                      : 'No AI remarks recorded for this run.'}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Formatted Remarks Card */}
                  <div className="p-5 rounded-xl border border-slate-200 bg-white shadow-xs space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        {displayAnalysis.ai_status === 'SUCCEEDED' ? (
                          <Sparkles className="w-4 h-4 text-indigo-600" />
                        ) : (
                          <FileText className="w-4 h-4 text-slate-600" />
                        )}
                        <span className="font-bold text-slate-900 text-xs">
                          {displayAnalysis.ai_status === 'SUCCEEDED'
                            ? `Ollama Synthesized Remarks (${displayAnalysis.ai_model || 'llama3.2:3b'})`
                            : 'Deterministic Fallback Remarks (Local AI Unavailable)'}
                        </span>
                      </div>
                      <span className="font-mono text-[10px] text-slate-400 uppercase">
                        label: {displayAnalysis.ai_result_json?.generation_label || 'AI_GENERATED'}
                      </span>
                    </div>

                    <pre className="font-sans text-xs sm:text-sm text-slate-800 whitespace-pre-wrap leading-relaxed bg-slate-50/70 p-4 rounded-lg border border-slate-100">
                      {displayAnalysis.remarks_text}
                    </pre>

                    {/* Prominent Clinical Caveats */}
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
                      <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5 text-slate-600" />
                        <span>Preserved Clinical Caveat Codes</span>
                      </span>
                      <ul className="list-disc pl-5 text-[11px] text-slate-600 space-y-0.5">
                        <li>
                          <code>UNIT_ASSUMPTION</code>: Conventional clinical units assumed for this assessment.
                        </li>
                        <li>
                          <code>FASTING_STATUS_NOT_CONFIRMED</code>: Patient fasting state not clinically recorded.
                        </li>
                        <li>
                          <code>DEMOGRAPHIC_CONTEXT_NOT_CONFIRMED</code>: Biological sex/age baseline not clinically confirmed.
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Analysis History */}
          {activeTab === 'history' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">
                    Patient Analysis Historical Audit Lineage
                  </h4>
                  <p className="text-xs text-slate-500">
                    Immutable history of all executed interpretation runs for this patient
                  </p>
                </div>
                <button
                  onClick={loadHistory}
                  disabled={loadingHistory}
                  className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium"
                  title="Reload audit history"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingHistory ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {historyRuns.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">No historical runs recorded.</p>
              ) : (
                <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-white">
                  {historyRuns.map((run) => (
                    <div
                      key={run.id}
                      className={`p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/80 transition ${
                        selectedRun?.id === run.id ? 'bg-teal-50/40 border-l-4 border-l-teal-600' : ''
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900 text-xs">Run #{run.run_number}</span>
                          <OverallStatusBadge status={run.overall_status} />
                          <AiStatusBadge
                            status={run.ai_status}
                            generationLabel={run.ai_result_json?.generation_label}
                          />
                        </div>
                        <p className="text-[11px] text-slate-500">
                          Executed: {formatDateTime(run.completed_at || run.created_at)} &bull; Provider:{' '}
                          {run.external_provider} &bull; Model: {run.ai_model || 'llama3.2:3b'}
                          {run.retry_of_id && (
                            <span className="ml-1 text-slate-400">
                              (Retry of: <code className="font-mono text-[10px]">{run.retry_of_id.slice(0, 8)}</code>)
                            </span>
                          )}
                        </p>
                      </div>

                      <button
                        onClick={() => setSelectedRun(run)}
                        className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-medium self-start sm:self-auto"
                      >
                        {selectedRun?.id === run.id ? 'Viewing' : 'Inspect Run'}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Record ID: #{patient.id} &bull; Created: {formatDateForDisplay(patient.created_at)}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold text-xs transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
