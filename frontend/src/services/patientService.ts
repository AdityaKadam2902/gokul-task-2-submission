/**
 * Patient Service for interacting with /api/v1/patients REST APIs.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { apiClient } from './apiClient';
import {
  Patient,
  PatientListItem,
  PatientCreateInput,
  PatientUpdateInput,
} from '../types/patient';
import { PaginatedResponse, PaginationParams } from '../types/api';

export const patientService = {
  /**
   * Retrieve paginated patient list with optional search and sorting.
   */
  async listPatients(
    params: Partial<PaginationParams> = {}
  ): Promise<PaginatedResponse<PatientListItem>> {
    const query = new URLSearchParams();
    if (params.page) query.set('page', String(params.page));
    if (params.page_size) query.set('page_size', String(params.page_size));
    if (params.search?.trim()) query.set('search', params.search.trim());
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.sort_order) query.set('sort_order', params.sort_order);

    const queryString = query.toString();
    const endpoint = `/api/v1/patients${queryString ? `?${queryString}` : ''}`;
    return apiClient.get<PaginatedResponse<PatientListItem>>(endpoint);
  },

  /**
   * Get single patient record by ID including technical timestamps and latest analysis.
   */
  async getPatient(id: number): Promise<Patient> {
    return apiClient.get<Patient>(`/api/v1/patients/${id}`);
  },

  /**
   * Create a new patient record.
   * If allowDuplicate is true, includes query param and payload flag for duplicate insertion.
   */
  async createPatient(data: PatientCreateInput, allowDuplicate: boolean = false): Promise<Patient> {
    const payload = { ...data, allow_duplicate: allowDuplicate };
    const queryParam = allowDuplicate ? '?allow_duplicate=true' : '';
    return apiClient.post<Patient>(`/api/v1/patients${queryParam}`, payload);
  },

  /**
   * Partially update patient fields.
   */
  async updatePatient(
    id: number,
    data: PatientUpdateInput,
    allowDuplicate: boolean = false
  ): Promise<Patient> {
    const payload = { ...data, allow_duplicate: allowDuplicate };
    const queryParam = allowDuplicate ? '?allow_duplicate=true' : '';
    return apiClient.patch<Patient>(`/api/v1/patients/${id}${queryParam}`, payload);
  },

  /**
   * Delete a patient record, cascading to delete all associated analysis runs.
   */
  async deletePatient(id: number): Promise<void> {
    return apiClient.delete<void>(`/api/v1/patients/${id}`);
  },
};
