/**
 * Destructive Delete Patient Confirmation Dialog.
 * Explicitly warns that deleting a patient cascades and removes all historical analysis runs.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React from 'react';
import { Trash2, AlertTriangle, Loader2 } from 'lucide-react';
import { PatientListItem, Patient } from '../../types/patient';

interface DeletePatientModalProps {
  isOpen: boolean;
  patient: PatientListItem | Patient | null;
  loading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeletePatientModal: React.FC<DeletePatientModalProps> = ({
  isOpen,
  patient,
  loading,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen || !patient) return null;

  return (
    <div
      className="fixed inset-0 z-[60] overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-dialog-title"
    >
      <div className="bg-white rounded-xl shadow-xl border border-rose-200 max-w-md w-full overflow-hidden animate-in fade-in-50 zoom-in-95 duration-150">
        <div className="p-6">
          <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
            <div className="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-600 shrink-0">
              <Trash2 className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <h3 id="delete-dialog-title" className="text-base font-bold text-slate-900">
                Delete Patient Record
              </h3>
              <p className="text-xs text-rose-600 font-medium">
                Irreversible Destructive Action
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-3 text-xs text-slate-600 leading-relaxed">
            <p>
              Are you sure you want to permanently delete the patient record for{' '}
              <strong className="text-slate-900">{patient.full_name}</strong> (Record #{patient.id})?
            </p>

            <div className="bg-rose-50/80 p-3 rounded-lg border border-rose-200 text-rose-900 space-y-1">
              <div className="flex items-center gap-1.5 font-semibold text-xs text-rose-950">
                <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>Cascade Deletion Warning</span>
              </div>
              <p className="text-[11px] leading-normal text-rose-900">
                Deleting this patient will permanently purge all associated data, including all historical analysis runs,
                TestWell observations, and generated AI remarks. This action cannot be undone.
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              onClick={onCancel}
              disabled={loading}
              className="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-xs transition disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Deleting...</span>
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  <span>Permanently Delete</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
