/**
 * Patient Directory Data Table Component.
 * Responsive, accessible table with server-side pagination, search, status badges, and action triggers.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useState } from 'react';
import { PatientListItem } from '../../types/patient';
import { formatDateForDisplay } from '../../utils/date';
import { OverallStatusBadge } from '../common/StatusBadge';
import {
  Search,
  Plus,
  Eye,
  Pencil,
  Trash2,
  ChevronLeft,
  ChevronRight,
  UserX,
  X,
  RefreshCw,
} from 'lucide-react';

interface PatientTableProps {
  patients: PatientListItem[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  search: string;
  loading: boolean;
  onPageChange: (newPage: number) => void;
  onSearchChange: (query: string) => void;
  onRefresh: () => void;
  onAddPatient: () => void;
  onViewPatient: (id: number) => void;
  onEditPatient: (id: number) => void;
  onDeletePatient: (patient: PatientListItem) => void;
}

export const PatientTable: React.FC<PatientTableProps> = ({
  patients,
  total,
  page,
  pageSize,
  totalPages,
  search,
  loading,
  onPageChange,
  onSearchChange,
  onRefresh,
  onAddPatient,
  onViewPatient,
  onEditPatient,
  onDeletePatient,
}) => {
  const [searchInput, setSearchInput] = useState<string>(search);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchChange(searchInput);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    onSearchChange('');
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Table Toolbar */}
      <div className="p-4 sm:p-5 border-b border-slate-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <label htmlFor="patient-search" className="sr-only">
            Search patients by name or email
          </label>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              id="patient-search"
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search by name or email (press Enter)..."
              className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-200 text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-transparent transition"
            />
            {searchInput && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5 rounded"
                aria-label="Clear search"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </form>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5 self-end sm:self-auto">
          <button
            onClick={onRefresh}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium transition disabled:opacity-50"
            title="Refresh directory"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-teal-600' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          <button
            onClick={onAddPatient}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Patient Record</span>
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs sm:text-sm">
          <thead>
            <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 uppercase text-[11px] font-semibold tracking-wider">
              <th scope="col" className="py-3 px-4 w-16 text-center">ID</th>
              <th scope="col" className="py-3 px-4">Full Name</th>
              <th scope="col" className="py-3 px-4 whitespace-nowrap">Date of Birth</th>
              <th scope="col" className="py-3 px-4">Email</th>
              <th scope="col" className="py-3 px-4 text-right">
                Glucose <span className="normal-case text-slate-400 font-normal">(mg/dL)</span>
              </th>
              <th scope="col" className="py-3 px-4 text-right">
                Haemoglobin <span className="normal-case text-slate-400 font-normal">(g/dL)</span>
              </th>
              <th scope="col" className="py-3 px-4 text-right">
                Cholesterol <span className="normal-case text-slate-400 font-normal">(mg/dL)</span>
              </th>
              <th scope="col" className="py-3 px-4 text-center">Analysis Status</th>
              <th scope="col" className="py-3 px-4 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {loading ? (
              // Loading Skeleton Rows
              Array.from({ length: 4 }).map((_, idx) => (
                <tr key={`skeleton-${idx}`} className="animate-pulse">
                  <td className="py-3.5 px-4 text-center"><div className="h-4 w-6 bg-slate-200 rounded mx-auto" /></td>
                  <td className="py-3.5 px-4"><div className="h-4 w-32 bg-slate-200 rounded" /></td>
                  <td className="py-3.5 px-4"><div className="h-4 w-20 bg-slate-200 rounded" /></td>
                  <td className="py-3.5 px-4"><div className="h-4 w-40 bg-slate-200 rounded" /></td>
                  <td className="py-3.5 px-4 text-right"><div className="h-4 w-12 bg-slate-200 rounded ml-auto" /></td>
                  <td className="py-3.5 px-4 text-right"><div className="h-4 w-12 bg-slate-200 rounded ml-auto" /></td>
                  <td className="py-3.5 px-4 text-right"><div className="h-4 w-12 bg-slate-200 rounded ml-auto" /></td>
                  <td className="py-3.5 px-4 text-center"><div className="h-5 w-24 bg-slate-200 rounded-full mx-auto" /></td>
                  <td className="py-3.5 px-4 text-center"><div className="h-7 w-20 bg-slate-200 rounded mx-auto" /></td>
                </tr>
              ))
            ) : patients.length === 0 ? (
              // Empty State
              <tr>
                <td colSpan={9} className="py-12 px-4 text-center text-slate-500">
                  <div className="flex flex-col items-center justify-center max-w-sm mx-auto">
                    <div className="p-3 bg-slate-100 rounded-full text-slate-400 mb-3">
                      <UserX className="w-8 h-8" aria-hidden="true" />
                    </div>
                    <h3 className="font-semibold text-slate-800 text-base mb-1">
                      {search ? 'No matching patient records found' : 'No patient records saved'}
                    </h3>
                    <p className="text-xs text-slate-500 mb-4 text-center">
                      {search
                        ? `No results matching "${search}". Try searching by another name or clearing the search filter.`
                        : 'Get started by creating your first patient profile to analyze health biomarkers.'}
                    </p>
                    {search ? (
                      <button
                        onClick={handleClearSearch}
                        className="px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium"
                      >
                        Clear Search
                      </button>
                    ) : (
                      <button
                        onClick={onAddPatient}
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold shadow-xs"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Add First Patient</span>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              patients.map((patient) => (
                <tr
                  key={patient.id}
                  className="hover:bg-slate-50/70 transition-colors group"
                >
                  <td className="py-3 px-4 font-mono text-xs text-slate-500 text-center font-medium">
                    #{patient.id}
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-900 whitespace-nowrap">
                    {patient.full_name}
                  </td>
                  <td className="py-3 px-4 text-slate-600 whitespace-nowrap">
                    {formatDateForDisplay(patient.date_of_birth)}
                  </td>
                  <td className="py-3 px-4 text-slate-600 font-mono text-xs">
                    {patient.email}
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-slate-900">
                    {patient.glucose_value}
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-slate-900">
                    {patient.haemoglobin_value}
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-slate-900">
                    {patient.cholesterol_value}
                  </td>
                  <td className="py-3 px-4 text-center whitespace-nowrap">
                    <OverallStatusBadge status={patient.latest_analysis_status} />
                  </td>
                  <td className="py-3 px-4 text-center whitespace-nowrap">
                    <div className="inline-flex items-center gap-1">
                      <button
                        onClick={() => onViewPatient(patient.id)}
                        className="p-1.5 rounded text-slate-500 hover:text-teal-700 hover:bg-teal-50 transition"
                        title="View Detailed Observations & AI Remarks"
                        aria-label={`View record for ${patient.full_name}`}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onEditPatient(patient.id)}
                        className="p-1.5 rounded text-slate-500 hover:text-blue-700 hover:bg-blue-50 transition"
                        title="Edit Patient Details"
                        aria-label={`Edit record for ${patient.full_name}`}
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onDeletePatient(patient)}
                        className="p-1.5 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                        title="Delete Patient Record"
                        aria-label={`Delete record for ${patient.full_name}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
        <div>
          Showing{' '}
          <span className="font-semibold text-slate-700">
            {total === 0 ? 0 : (page - 1) * pageSize + 1}
          </span>{' '}
          to{' '}
          <span className="font-semibold text-slate-700">
            {Math.min(page * pageSize, total)}
          </span>{' '}
          of <span className="font-semibold text-slate-700">{total}</span> records
        </div>

        <div className="inline-flex items-center gap-1.5">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1 || loading}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
            aria-label="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Prev</span>
          </button>

          <span className="px-2 font-medium text-slate-700">
            Page {page} of {totalPages}
          </span>

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages || loading}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
            aria-label="Next page"
          >
            <span>Next</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
