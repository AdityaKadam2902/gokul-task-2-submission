/**
 * Patient Creation and Editing Form Modal.
 * Supports date parsing, decimal inputs, field-level validation, and retains entered data on error.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useState, useEffect } from 'react';
import { Patient, PatientFormData } from '../../types/patient';
import { formatDateForDisplay } from '../../utils/date';
import { validatePatientForm, FormErrors } from '../../utils/validation';
import { User, Calendar, Mail, Activity, X, AlertCircle, Check, Loader2 } from 'lucide-react';

interface PatientFormModalProps {
  isOpen: boolean;
  mode: 'create' | 'edit';
  patient?: Patient | null;
  loading: boolean;
  serverError: string | null;
  onClose: () => void;
  onSubmit: (formData: PatientFormData) => void;
}

export const PatientFormModal: React.FC<PatientFormModalProps> = ({
  isOpen,
  mode,
  patient,
  loading,
  serverError,
  onClose,
  onSubmit,
}) => {
  const [formData, setFormData] = useState<PatientFormData>({
    full_name: '',
    date_of_birth: '',
    email: '',
    glucose_value: '',
    haemoglobin_value: '',
    cholesterol_value: '',
  });

  const [fieldErrors, setFieldErrors] = useState<FormErrors>({});

  // Populate data when editing
  useEffect(() => {
    if (mode === 'edit' && patient) {
      setFormData({
        full_name: patient.full_name || '',
        date_of_birth: formatDateForDisplay(patient.date_of_birth),
        email: patient.email || '',
        glucose_value: String(patient.glucose_value ?? ''),
        haemoglobin_value: String(patient.haemoglobin_value ?? ''),
        cholesterol_value: String(patient.cholesterol_value ?? ''),
      });
      setFieldErrors({});
    } else if (mode === 'create') {
      setFormData({
        full_name: '',
        date_of_birth: '',
        email: '',
        glucose_value: '',
        haemoglobin_value: '',
        cholesterol_value: '',
      });
      setFieldErrors({});
    }
  }, [mode, patient, isOpen]);

  if (!isOpen) return null;

  const handleChange = (field: keyof PatientFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear field-level error on change
    if (fieldErrors[field]) {
      setFieldErrors((prev) => ({ ...prev, [field]: undefined }));
    }
    // If full_name is modified, also clear any combination error attached to email
    if (field === 'full_name' && fieldErrors.email?.includes('Gokul')) {
      setFieldErrors((prev) => ({ ...prev, email: undefined }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const { isValid, errors } = validatePatientForm(formData);
    if (!isValid) {
      setFieldErrors(errors);
      return;
    }
    onSubmit(formData);
  };

  const isEdit = mode === 'edit';

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="patient-form-title"
    >
      <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in fade-in-50 zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-teal-50 text-teal-700">
              <User className="w-5 h-5" aria-hidden="true" />
            </div>
            <div>
              <h3 id="patient-form-title" className="text-base font-bold text-slate-900">
                {isEdit ? `Edit Patient Record #${patient?.id}` : 'Create New Patient Record'}
              </h3>
              <p className="text-xs text-slate-500">
                {isEdit
                  ? 'Update patient demographic and laboratory measurements'
                  : 'Enter patient demographic and numerical biomarker readings'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg transition"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} noValidate className="p-5 space-y-4">
          {/* Server Error Alert */}
          {serverError && (
            <div
              className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-start gap-2"
              role="alert"
            >
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <span className="font-semibold block">Submission Error</span>
                <p className="mt-0.5">{serverError}</p>
              </div>
            </div>
          )}

          {/* Full Name */}
          <div>
            <label htmlFor="field-full-name" className="block text-xs font-semibold text-slate-700 mb-1">
              Full Name <span className="text-rose-500">*</span>
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="field-full-name"
                type="text"
                required
                disabled={loading}
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                placeholder="e.g. John Doe"
                className={`w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border ${
                  fieldErrors.full_name ? 'border-rose-400 focus:ring-rose-400' : 'border-slate-200 focus:ring-teal-600'
                } focus:outline-none focus:ring-2 focus:border-transparent transition`}
              />
            </div>
            {fieldErrors.full_name && (
              <p className="mt-1 text-[11px] text-rose-600 font-medium">{fieldErrors.full_name}</p>
            )}
          </div>

          {/* Date of Birth & Email Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {/* Date of Birth */}
            <div>
              <label htmlFor="field-dob" className="block text-xs font-semibold text-slate-700 mb-1">
                Date of Birth <span className="text-rose-500">*</span>{' '}
                <span className="text-slate-400 font-normal text-[11px]">(dd/mm/yyyy)</span>
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="field-dob"
                  type="text"
                  required
                  disabled={loading}
                  value={formData.date_of_birth}
                  onChange={(e) => handleChange('date_of_birth', e.target.value)}
                  placeholder="e.g. 15/06/1985"
                  className={`w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border ${
                    fieldErrors.date_of_birth ? 'border-rose-400 focus:ring-rose-400' : 'border-slate-200 focus:ring-teal-600'
                  } focus:outline-none focus:ring-2 focus:border-transparent transition`}
                />
              </div>
              {fieldErrors.date_of_birth && (
                <p className="mt-1 text-[11px] text-rose-600 font-medium">{fieldErrors.date_of_birth}</p>
              )}
            </div>

            {/* Email Address */}
            <div>
              <label htmlFor="field-email" className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="field-email"
                  type="email"
                  required
                  disabled={loading}
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  placeholder="e.g. user@example.com"
                  className={`w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border ${
                    fieldErrors.email ? 'border-rose-400 focus:ring-rose-400' : 'border-slate-200 focus:ring-teal-600'
                  } focus:outline-none focus:ring-2 focus:border-transparent transition`}
                />
              </div>
              {fieldErrors.email && (
                <p className="mt-1 text-[11px] text-rose-600 font-medium">{fieldErrors.email}</p>
              )}
            </div>
          </div>

          {/* Biomarkers Section */}
          <div className="pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-teal-600" />
                <span>Laboratory Biomarker Measurements</span>
              </span>
              <span className="text-[11px] text-slate-500 font-medium">Assumed Conventional Units</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Glucose */}
              <div>
                <label htmlFor="field-glucose" className="block text-xs font-medium text-slate-600 mb-1">
                  Glucose <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <input
                    id="field-glucose"
                    type="number"
                    step="any"
                    required
                    disabled={loading}
                    value={formData.glucose_value}
                    onChange={(e) => handleChange('glucose_value', e.target.value)}
                    placeholder="90.0"
                    className={`w-full pr-12 pl-3 py-2 text-xs sm:text-sm rounded-lg border ${
                      fieldErrors.glucose_value ? 'border-rose-400' : 'border-slate-200'
                    } focus:outline-none focus:ring-2 focus:ring-teal-600 transition`}
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-slate-400 font-mono">
                    mg/dL
                  </span>
                </div>
                {fieldErrors.glucose_value && (
                  <p className="mt-1 text-[10px] text-rose-600">{fieldErrors.glucose_value}</p>
                )}
              </div>

              {/* Haemoglobin */}
              <div>
                <label htmlFor="field-haemoglobin" className="block text-xs font-medium text-slate-600 mb-1">
                  Haemoglobin <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <input
                    id="field-haemoglobin"
                    type="number"
                    step="any"
                    required
                    disabled={loading}
                    value={formData.haemoglobin_value}
                    onChange={(e) => handleChange('haemoglobin_value', e.target.value)}
                    placeholder="14.0"
                    className={`w-full pr-10 pl-3 py-2 text-xs sm:text-sm rounded-lg border ${
                      fieldErrors.haemoglobin_value ? 'border-rose-400' : 'border-slate-200'
                    } focus:outline-none focus:ring-2 focus:ring-teal-600 transition`}
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-slate-400 font-mono">
                    g/dL
                  </span>
                </div>
                {fieldErrors.haemoglobin_value && (
                  <p className="mt-1 text-[10px] text-rose-600">{fieldErrors.haemoglobin_value}</p>
                )}
              </div>

              {/* Cholesterol */}
              <div>
                <label htmlFor="field-cholesterol" className="block text-xs font-medium text-slate-600 mb-1">
                  Cholesterol <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <input
                    id="field-cholesterol"
                    type="number"
                    step="any"
                    required
                    disabled={loading}
                    value={formData.cholesterol_value}
                    onChange={(e) => handleChange('cholesterol_value', e.target.value)}
                    placeholder="180.0"
                    className={`w-full pr-12 pl-3 py-2 text-xs sm:text-sm rounded-lg border ${
                      fieldErrors.cholesterol_value ? 'border-rose-400' : 'border-slate-200'
                    } focus:outline-none focus:ring-2 focus:ring-teal-600 transition`}
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-slate-400 font-mono">
                    mg/dL
                  </span>
                </div>
                {fieldErrors.cholesterol_value && (
                  <p className="mt-1 text-[10px] text-rose-600">{fieldErrors.cholesterol_value}</p>
                )}
              </div>
            </div>
          </div>

          {/* Dialog Action Buttons */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold shadow-xs transition disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>{isEdit ? 'Save Changes' : 'Save & Trigger Analysis'}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
