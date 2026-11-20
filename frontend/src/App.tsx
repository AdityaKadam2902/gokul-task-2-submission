/**
 * LabInsight Professional Healthcare Application Root.
 * Complete integration with FastAPI backend, SQLite, TestWell, and local Ollama llama3.2:3b.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { MetricsOverview } from './components/dashboard/MetricsOverview';
import { PatientTable } from './components/dashboard/PatientTable';
import { AcknowledgementModal } from './components/dashboard/AcknowledgementModal';
import { PatientFormModal } from './components/patients/PatientFormModal';
import { DuplicateModal } from './components/patients/DuplicateModal';
import { DeletePatientModal } from './components/patients/DeletePatientModal';
import { PatientDetailModal } from './components/patients/PatientDetailModal';
import { RoadmapCard } from './components/roadmap/RoadmapCard';
import { ToastContainer, ToastMessage, ToastType } from './components/common/Toast';

import { usePatients } from './hooks/usePatients';
import { apiClient, ApiError } from './services/apiClient';
import { patientService } from './services/patientService';
import { analysisService } from './services/analysisService';

import { Patient, PatientListItem, PatientFormData } from './types/patient';
import { HealthResponse, ReadinessResponse } from './types/health';
import { validateAndParseDate } from './utils/date';

export const App: React.FC = () => {
  // System Health and Readiness State
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [systemLoading, setSystemLoading] = useState<boolean>(true);

  // Patient Directory State via Custom Hook
  const {
    patients,
    total,
    page,
    pageSize,
    totalPages,
    search,
    loading: patientsLoading,
    metrics,
    setPage,
    handleSearch,
    refresh: refreshPatients,
  } = usePatients();

  // Modals & Dialogs State
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);
  const [formSubmitting, setFormSubmitting] = useState<boolean>(false);
  const [formServerError, setFormServerError] = useState<string | null>(null);

  // Unit Acknowledgment State (shown on first create)
  const [isAckOpen, setIsAckOpen] = useState<boolean>(false);
  const [hasAcknowledgedUnits, setHasAcknowledgedUnits] = useState<boolean>(false);
  const [pendingCreateData, setPendingCreateData] = useState<PatientFormData | null>(null);

  // Duplicate Confirmation Dialog State (409)
  const [isDuplicateOpen, setIsDuplicateOpen] = useState<boolean>(false);
  const [duplicateFormData, setDuplicateFormData] = useState<PatientFormData | null>(null);
  const [duplicateExistingId, setDuplicateExistingId] = useState<number | null>(null);
  const [duplicateSubmitting, setDuplicateSubmitting] = useState<boolean>(false);

  // Delete Confirmation State
  const [isDeleteOpen, setIsDeleteOpen] = useState<boolean>(false);
  const [deletingPatient, setDeletingPatient] = useState<PatientListItem | Patient | null>(null);
  const [deleteSubmitting, setDeleteSubmitting] = useState<boolean>(false);

  // Patient Detail View Drawer/Modal State
  const [isDetailOpen, setIsDetailOpen] = useState<boolean>(false);
  const [detailPatient, setDetailPatient] = useState<Patient | null>(null);

  // Toast Notifications State
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback((title: string, message?: string, type: ToastType = 'success') => {
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setToasts((prev) => [...prev, { id, title, message, type }]);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Fetch System Health Status
  const fetchSystemStatus = useCallback(async () => {
    setSystemLoading(true);
    try {
      const [h, r] = await Promise.all([apiClient.getHealth(), apiClient.getReadiness()]);
      setHealth(h);
      setReadiness(r);
    } catch {
      setHealth(null);
      setReadiness(null);
    } finally {
      setSystemLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSystemStatus();
  }, [fetchSystemStatus]);

  // --- Handlers: Create Patient ---
  const handleOpenCreate = () => {
    setEditingPatient(null);
    setFormMode('create');
    setFormServerError(null);
    setIsFormOpen(true);
  };

  const executePatientCreation = async (formData: PatientFormData, allowDuplicate: boolean = false) => {
    setFormSubmitting(true);
    setFormServerError(null);

    const dateResult = validateAndParseDate(formData.date_of_birth);
    if (!dateResult.isValid || !dateResult.isoDate) {
      setFormServerError(dateResult.errorMessage || 'Invalid date of birth format.');
      setFormSubmitting(false);
      return;
    }

    try {
      const payload = {
        full_name: formData.full_name.trim(),
        date_of_birth: dateResult.isoDate,
        email: formData.email.trim().toLowerCase(),
        glucose_value: Number(formData.glucose_value),
        haemoglobin_value: Number(formData.haemoglobin_value),
        cholesterol_value: Number(formData.cholesterol_value),
        allow_duplicate: allowDuplicate,
      };

      const created = await patientService.createPatient(payload, allowDuplicate);

      // Trigger initial analysis run via documented API
      try {
        await analysisService.triggerAnalysis(created.id);
      } catch (triggerErr) {
        addToast(
          'Patient Saved, Analysis Queued',
          'Record created; analysis will start when services are available.',
          'info'
        );
      }

      setIsFormOpen(false);
      setIsDuplicateOpen(false);
      setDuplicateFormData(null);
      addToast(
        allowDuplicate ? 'Duplicate Record Confirmed & Saved' : 'Patient Record Created',
        `Record #${created.id} (${created.full_name}) saved successfully.`
      );

      // Refresh directory and open detail view
      await refreshPatients();
      const fresh = await patientService.getPatient(created.id);
      setDetailPatient(fresh);
      setIsDetailOpen(true);
    } catch (err) {
      if (err instanceof ApiError) {
        if (
          err.status === 409 &&
          (err.code === 'DUPLICATE_RECORD' || err.code === 'DUPLICATE_PATIENT_RECORD')
        ) {
          // Open duplicate confirmation dialog (Section 5)
          setDuplicateFormData(formData);
          setDuplicateExistingId(err.existingPatientId || null);
          setIsDuplicateOpen(true);
          return;
        }
        setFormServerError(err.message);
      } else {
        setFormServerError('An unexpected network error occurred while saving.');
      }
    } finally {
      setFormSubmitting(false);
      setDuplicateSubmitting(false);
    }
  };

  const handleFormSubmit = (formData: PatientFormData) => {
    if (formMode === 'create') {
      if (!hasAcknowledgedUnits) {
        // Intercept first creation with Unit Profile & De-identification Disclosure
        setPendingCreateData(formData);
        setIsAckOpen(true);
        return;
      }
      executePatientCreation(formData, false);
    } else if (formMode === 'edit' && editingPatient) {
      executePatientUpdate(editingPatient.id, formData);
    }
  };

  const handleConfirmAcknowledgement = () => {
    setHasAcknowledgedUnits(true);
    setIsAckOpen(false);
    if (pendingCreateData) {
      executePatientCreation(pendingCreateData, false);
      setPendingCreateData(null);
    }
  };

  // --- Handlers: Duplicate Confirmation ---
  const handleConfirmDuplicate = () => {
    if (!duplicateFormData) return;
    setDuplicateSubmitting(true);
    executePatientCreation(duplicateFormData, true);
  };

  // --- Handlers: Edit Patient ---
  const handleOpenEdit = async (patientId: number) => {
    setFormServerError(null);
    setFormMode('edit');
    try {
      const p = await patientService.getPatient(patientId);
      setEditingPatient(p);
      setIsFormOpen(true);
    } catch (err) {
      addToast('Error', 'Failed to retrieve patient details for editing.', 'error');
    }
  };

  const executePatientUpdate = async (patientId: number, formData: PatientFormData) => {
    setFormSubmitting(true);
    setFormServerError(null);

    const dateResult = validateAndParseDate(formData.date_of_birth);
    if (!dateResult.isValid || !dateResult.isoDate) {
      setFormServerError(dateResult.errorMessage || 'Invalid date of birth format.');
      setFormSubmitting(false);
      return;
    }

    try {
      const payload = {
        full_name: formData.full_name.trim(),
        date_of_birth: dateResult.isoDate,
        email: formData.email.trim().toLowerCase(),
        glucose_value: Number(formData.glucose_value),
        haemoglobin_value: Number(formData.haemoglobin_value),
        cholesterol_value: Number(formData.cholesterol_value),
      };

      const updated = await patientService.updatePatient(patientId, payload);
      setIsFormOpen(false);
      setEditingPatient(null);
      addToast(
        'Patient Record Updated',
        `Updated details for ${updated.full_name} (${updated.email}).`
      );

      await refreshPatients();
      if (isDetailOpen && detailPatient?.id === patientId) {
        setDetailPatient(updated);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setFormServerError(err.message);
      } else {
        setFormServerError('Failed to save updates.');
      }
    } finally {
      setFormSubmitting(false);
    }
  };

  // --- Handlers: Delete Patient ---
  const handleOpenDelete = (patient: PatientListItem | Patient) => {
    setDeletingPatient(patient);
    setIsDeleteOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingPatient) return;
    setDeleteSubmitting(true);
    try {
      await patientService.deletePatient(deletingPatient.id);
      setIsDeleteOpen(false);
      if (isDetailOpen && detailPatient?.id === deletingPatient.id) {
        setIsDetailOpen(false);
        setDetailPatient(null);
      }
      addToast(
        'Patient Record Deleted',
        `Record #${deletingPatient.id} and its associated analysis history were removed.`
      );
      setDeletingPatient(null);
      await refreshPatients();
    } catch (err) {
      addToast('Deletion Failed', 'Unable to delete patient record.', 'error');
    } finally {
      setDeleteSubmitting(false);
    }
  };

  // --- Handlers: View Patient Details ---
  const handleViewPatient = async (patientId: number) => {
    try {
      const p = await patientService.getPatient(patientId);
      setDetailPatient(p);
      setIsDetailOpen(true);
    } catch (err) {
      addToast('Error', 'Failed to load patient detail view.', 'error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-800 antialiased selection:bg-teal-100 selection:text-teal-900">
      {/* Toast Notification Region */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      {/* Global Application Header */}
      <Header
        appName="LabInsight"
        version="0.1.0"
        health={health}
        readiness={readiness}
        loading={systemLoading}
        onRefresh={fetchSystemStatus}
      />

      {/* Main Responsive Content Shell */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Persistent Educational Notice Banner */}
        <DisclaimerBanner />

        {/* Operational Metrics Overview Cards */}
        <MetricsOverview metrics={metrics} loading={patientsLoading} />

        {/* Patient Records Directory Table */}
        <PatientTable
          patients={patients}
          total={total}
          page={page}
          pageSize={pageSize}
          totalPages={totalPages}
          search={search}
          loading={patientsLoading}
          onPageChange={setPage}
          onSearchChange={handleSearch}
          onRefresh={refreshPatients}
          onAddPatient={handleOpenCreate}
          onViewPatient={handleViewPatient}
          onEditPatient={handleOpenEdit}
          onDeletePatient={handleOpenDelete}
        />

        {/* Phase Board & Implementation Roadmap (Collapsible) */}
        <RoadmapCard />
      </main>

      {/* Educational Acknowledgement Modal */}
      <AcknowledgementModal
        isOpen={isAckOpen}
        onConfirm={handleConfirmAcknowledgement}
        onCancel={() => {
          setIsAckOpen(false);
          setPendingCreateData(null);
        }}
      />

      {/* Create / Edit Patient Form Modal */}
      <PatientFormModal
        isOpen={isFormOpen}
        mode={formMode}
        patient={editingPatient}
        loading={formSubmitting}
        serverError={formServerError}
        onClose={() => {
          setIsFormOpen(false);
          setEditingPatient(null);
        }}
        onSubmit={handleFormSubmit}
      />

      {/* Mandatory Duplicate Confirmation Dialog */}
      <DuplicateModal
        isOpen={isDuplicateOpen}
        formData={duplicateFormData}
        existingPatientId={duplicateExistingId}
        loading={duplicateSubmitting}
        onConfirm={handleConfirmDuplicate}
        onCancel={() => {
          setIsDuplicateOpen(false);
          setDuplicateFormData(null);
        }}
      />

      {/* Destructive Delete Confirmation Dialog */}
      <DeletePatientModal
        isOpen={isDeleteOpen}
        patient={deletingPatient}
        loading={deleteSubmitting}
        onConfirm={handleConfirmDelete}
        onCancel={() => {
          setIsDeleteOpen(false);
          setDeletingPatient(null);
        }}
      />

      {/* Patient Detail Drawer / Modal with TestWell Observations and AI Remarks */}
      <PatientDetailModal
        isOpen={isDetailOpen}
        patient={detailPatient}
        onClose={() => {
          setIsDetailOpen(false);
          setDetailPatient(null);
        }}
        onEdit={(id) => {
          setIsDetailOpen(false);
          handleOpenEdit(id);
        }}
        onDelete={(p) => {
          setIsDetailOpen(false);
          handleOpenDelete(p);
        }}
        onPatientUpdated={refreshPatients}
      />
    </div>
  );
};

export default App;
