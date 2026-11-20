import { describe, it, expect, vi, beforeEach } from 'vitest';
import { patientService } from '../src/services/patientService';
import { apiClient } from '../src/services/apiClient';
import { Patient, PatientCreateInput, PatientListItem } from '../src/types/patient';
import { PaginatedResponse } from '../src/types/api';

describe('patientService', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('lists patients with pagination and search query', async () => {
    const mockResponse: PaginatedResponse<PatientListItem> = {
      items: [
        {
          id: 1,
          full_name: 'Jane Doe',
          date_of_birth: '1990-01-01',
          email: 'jane@example.com',
          glucose_value: '95.0',
          haemoglobin_value: '14.2',
          cholesterol_value: '180.0',
          unit_profile_code: 'CONVENTIONAL_US',
          created_at: '2026-11-18T00:00:00Z',
          updated_at: '2026-11-18T00:00:00Z',
          latest_analysis_status: 'COMPLETED',
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    };

    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue(mockResponse);

    const result = await patientService.listPatients({ page: 2, page_size: 20, search: 'Jane' });

    expect(getSpy).toHaveBeenCalledWith('/api/v1/patients?page=2&page_size=20&search=Jane');
    expect(result.items.length).toBe(1);
    expect(result.total).toBe(1);
  });

  it('gets a single patient by ID', async () => {
    const mockPatient: Patient = {
      id: 5,
      full_name: 'John Watson',
      date_of_birth: '1985-04-12',
      email: 'john@example.com',
      glucose_value: '102.0',
      haemoglobin_value: '15.0',
      cholesterol_value: '210.0',
      unit_profile_code: 'CONVENTIONAL_US',
      created_at: '2026-11-18T00:00:00Z',
      updated_at: '2026-11-18T00:00:00Z',
    };

    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue(mockPatient);

    const result = await patientService.getPatient(5);
    expect(getSpy).toHaveBeenCalledWith('/api/v1/patients/5');
    expect(result.full_name).toBe('John Watson');
  });

  it('creates a new patient with allow_duplicate=true flag when requested', async () => {
    const newPatient: PatientCreateInput = {
      full_name: 'Duplicate Patient',
      date_of_birth: '1980-01-01',
      email: 'dup@example.com',
      glucose_value: 100,
      haemoglobin_value: 14,
      cholesterol_value: 190,
    };

    const mockCreated: Patient = {
      id: 10,
      ...newPatient,
      unit_profile_code: 'CONVENTIONAL_US',
      created_at: '2026-11-18T00:00:00Z',
      updated_at: '2026-11-18T00:00:00Z',
    };

    const postSpy = vi.spyOn(apiClient, 'post').mockResolvedValue(mockCreated);

    const result = await patientService.createPatient(newPatient, true);

    expect(postSpy).toHaveBeenCalledWith('/api/v1/patients?allow_duplicate=true', {
      ...newPatient,
      allow_duplicate: true,
    });
    expect(result.id).toBe(10);
  });

  it('updates an existing patient email to gokul@infocare.com', async () => {
    const patchSpy = vi.spyOn(apiClient, 'patch').mockResolvedValue({
      id: 2,
      full_name: 'Gokul Candidate',
      date_of_birth: '1992-06-14',
      email: 'gokul@infocare.com',
      glucose_value: '95.0',
      haemoglobin_value: '14.5',
      cholesterol_value: '185.0',
      unit_profile_code: 'CONVENTIONAL_US',
      created_at: '2026-11-18T00:00:00Z',
      updated_at: '2026-11-18T10:00:00Z',
    });

    const result = await patientService.updatePatient(2, { email: 'gokul@infocare.com' });

    expect(patchSpy).toHaveBeenCalledWith('/api/v1/patients/2', {
      email: 'gokul@infocare.com',
      allow_duplicate: false,
    });
    expect(result.email).toBe('gokul@infocare.com');
  });

  it('deletes a patient by ID', async () => {
    const deleteSpy = vi.spyOn(apiClient, 'delete').mockResolvedValue(undefined);

    await patientService.deletePatient(3);

    expect(deleteSpy).toHaveBeenCalledWith('/api/v1/patients/3');
  });
});
