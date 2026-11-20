/**
 * Persistent Educational Disclaimer Banner.
 * Clearly articulates educational scope, conventional unit profile assumptions, and de-identification guarantees.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useState } from 'react';
import { AlertTriangle, ShieldCheck, ChevronDown, ChevronUp, Beaker } from 'lucide-react';

export const DisclaimerBanner: React.FC = () => {
  const [expanded, setExpanded] = useState<boolean>(false);

  return (
    <aside
      aria-label="Educational Disclaimer and Safety Notice"
      className="bg-amber-50/90 border-l-4 border-amber-500 p-4 rounded-r-lg text-amber-900 text-sm shadow-sm mb-6 transition"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <span className="font-semibold text-slate-900 block text-sm">
              Educational Healthcare Prototype &bull; Not a Diagnostic Medical Device
            </span>
            <p className="text-slate-700 text-xs mt-0.5 leading-relaxed">
              LabInsight synthesizes educational reference intervals from TestWell and generates plain-language
              observations via local Ollama (<code className="bg-amber-100/80 px-1 py-0.5 rounded text-amber-900 font-mono text-[11px]">llama3.2:3b</code>).
              Results do <span className="font-semibold underline">not</span> constitute a medical diagnosis, clinical evaluation, or treatment plan.
            </p>
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 text-xs font-medium text-amber-800 hover:text-amber-950 px-2 py-1 rounded bg-amber-100/60 hover:bg-amber-100 shrink-0 transition"
          aria-expanded={expanded}
          aria-controls="disclaimer-details"
        >
          <span>{expanded ? 'Less Details' : 'Unit Profile & Privacy'}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {expanded && (
        <div
          id="disclaimer-details"
          className="mt-3 pt-3 border-t border-amber-200/80 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-700"
        >
          <div className="flex items-start gap-2 bg-white/70 p-2.5 rounded border border-amber-200/60">
            <Beaker className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-900 block">Assessment Unit Profile Assumption</span>
              <p className="mt-0.5 text-slate-600">
                Conventional clinical units are assumed for this assessment: <strong>Glucose (mg/dL)</strong>,{' '}
                <strong>Haemoglobin (g/dL)</strong>, and <strong>Cholesterol (mg/dL)</strong>.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-2 bg-white/70 p-2.5 rounded border border-amber-200/60">
            <ShieldCheck className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-900 block">External Transmission & Privacy</span>
              <p className="mt-0.5 text-slate-600">
                Direct identifiers (name, email, DOB, record ID) are never sent to TestWell or Ollama. Only numerical measurements and unit codes are transmitted over HTTPS for educational reference interpretation. Excluding direct identifiers does not make lab measurements non-sensitive.
              </p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
