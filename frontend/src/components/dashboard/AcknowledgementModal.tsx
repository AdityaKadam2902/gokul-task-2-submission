/**
 * Unit Profile & External Data Acknowledgement Modal.
 * Transparently discloses unit assumptions and de-identification boundaries before external transmission.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React from 'react';
import { ShieldAlert, Check, Beaker, Lock } from 'lucide-react';

interface AcknowledgementModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const AcknowledgementModal: React.FC<AcknowledgementModalProps> = ({
  isOpen,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[60] overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="ack-modal-title"
    >
      <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in fade-in-50 zoom-in-95 duration-150">
        <div className="p-6">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
            <div className="p-2.5 rounded-lg bg-teal-50 border border-teal-200 text-teal-700 shrink-0">
              <ShieldAlert className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <h3 id="ack-modal-title" className="text-base font-bold text-slate-900">
                Educational Assessment Disclosure
              </h3>
              <p className="text-xs text-slate-500">
                Data Transmission & Unit Assumption Acknowledgement
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-3.5 text-xs text-slate-600 leading-relaxed">
            <p>
              Before dispatching biomarkers for external interpretation, please confirm your understanding of the
              following engineering boundaries:
            </p>

            <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 space-y-2.5">
              <div className="flex items-start gap-2">
                <Beaker className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                <p>
                  <strong>Assessment Unit Assumptions:</strong> The employer's assignment PDF omitted clinical units.
                  This prototype explicitly assumes conventional units: <strong>Glucose (mg/dL)</strong>,{' '}
                  <strong>Haemoglobin (g/dL)</strong>, and <strong>Cholesterol (mg/dL)</strong>.
                </p>
              </div>

              <div className="flex items-start gap-2">
                <Lock className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <p>
                  <strong>Direct Identifier Exclusion:</strong> Direct patient identifiers (full name, email address, date of birth,
                  and internal database IDs) are <strong>never</strong> transmitted. Only the three numerical blood measurements and unit
                  labels are sent to the external TestWell service over HTTPS for educational reference interpretation.
                </p>
              </div>

              <div className="flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <p className="text-[11px] text-amber-900 leading-normal">
                  <strong>Sensitivity Notice:</strong> Excluding direct identifiers does not make laboratory measurements non-sensitive.
                  This application is an educational prototype, not a diagnostic medical device or a replacement for professional medical advice.
                </p>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 italic">
              Notice: TestWell returns educational reference intervals and observations; local Ollama summarizes those observations. Results do not constitute a medical diagnosis or personal clinical review.
            </p>
          </div>

          <div className="mt-6 flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              onClick={onCancel}
              className="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 font-medium text-xs transition"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-800 text-white font-medium text-xs shadow-xs transition"
            >
              <Check className="w-4 h-4" />
              <span>I Understand — Continue</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
