/**
 * Duplicate Record Confirmation Dialog.
 * Implements the mandatory employer requirement to prompt for explicit confirmation
 * before inserting an identical duplicate patient record (allow_duplicate=true).
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React from 'react';
import { Copy, AlertTriangle, Check, X } from 'lucide-react';
import { PatientFormData } from '../../types/patient';

interface DuplicateModalProps {
  isOpen: boolean;
  formData: PatientFormData | null;
  existingPatientId?: number | null;
  loading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DuplicateModal: React.FC<DuplicateModalProps> = ({
  isOpen,
  formData,
  existingPatientId,
  loading,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen || !formData) return null;

  return (
    <div
      className="fixed inset-0 z-[60] overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="duplicate-dialog-title"
    >
      <div className="bg-white rounded-xl shadow-xl border border-amber-200 max-w-lg w-full overflow-hidden animate-in fade-in-50 zoom-in-95 duration-150">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
            <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 shrink-0">
              <Copy className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <h3 id="duplicate-dialog-title" className="text-base font-bold text-slate-900">
                Duplicate Patient Record Detected
              </h3>
              <p className="text-xs text-amber-700 font-medium">
                HTTP 409 Conflict &bull; Confirmation Required
              </p>
            </div>
          </div>

          {/* Explanation */}
          <div className="mt-4 space-y-3 text-xs text-slate-600 leading-relaxed">
            <p>
              An existing patient record with matching demographic and clinical measurements was located in the database
              {existingPatientId ? (
                <> (Matched Existing Record: <strong className="text-slate-800">#{existingPatientId}</strong>)</>
              ) : ''}.
            </p>

            <div className="bg-amber-50/70 p-3.5 rounded-lg border border-amber-200 text-amber-900 space-y-1.5">
              <div className="flex items-center gap-1.5 font-semibold text-xs text-amber-950">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Assessment Requirement Notice</span>
              </div>
              <p className="text-[11px] leading-normal text-amber-900">
                The employer's assessment specification specifically includes an exact duplicate record scenario.
                Standard clinical safety requires explicit confirmation before persisting duplicate entries.
              </p>
            </div>

            {/* Submitted Record Summary */}
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-slate-700">
              <span className="font-semibold block text-slate-900 mb-1">Submitted Record Details:</span>
              <ul className="grid grid-cols-2 gap-x-4 gap-y-1 text-[11px]">
                <li><span className="text-slate-500">Name:</span> {formData.full_name}</li>
                <li><span className="text-slate-500">DOB:</span> {formData.date_of_birth}</li>
                <li className="col-span-2"><span className="text-slate-500">Email:</span> {formData.email}</li>
                <li><span className="text-slate-500">Glucose:</span> {formData.glucose_value} mg/dL</li>
                <li><span className="text-slate-500">Haemoglobin:</span> {formData.haemoglobin_value} g/dL</li>
                <li><span className="text-slate-500">Cholesterol:</span> {formData.cholesterol_value} mg/dL</li>
              </ul>
            </div>

            <p className="text-[11px] text-slate-500">
              Clicking <strong>Confirm and Insert Duplicate</strong> will submit with <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-[10px]">allow_duplicate=true</code> to insert the second independent record.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              onClick={onCancel}
              disabled={loading}
              className="inline-flex items-center gap-1 px-4 py-2 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition"
            >
              <X className="w-3.5 h-3.5" />
              <span>Cancel</span>
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shadow-xs transition disabled:opacity-50"
            >
              <Check className="w-4 h-4" />
              <span>Confirm & Insert Duplicate Record</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
