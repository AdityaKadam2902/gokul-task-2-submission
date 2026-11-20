/**
 * Patient domain models, list items, and form inputs.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { OverallStatus } from './api';
import { AnalysisSummary } from './analysis';

export interface Patient {
  id: number;
  full_name: string;
  date_of_birth: string; // ISO date 'YYYY-MM-DD'
  email: string;
  glucose_value: number | string;
  haemoglobin_value: number | string;
  cholesterol_value: number | string;
  unit_profile_code: string;
  created_at: string;
  updated_at: string;
  latest_analysis?: AnalysisSummary | null;
  current_analysis?: AnalysisSummary | null;
}

export interface PatientListItem {
  id: number;
  full_name: string;
  date_of_birth: string;
  email: string;
  glucose_value: number | string;
  haemoglobin_value: number | string;
  cholesterol_value: number | string;
  unit_profile_code: string;
  created_at: string;
  updated_at: string;
  latest_analysis_status?: OverallStatus | null;
  latest_remarks?: string | null;
}

export interface PatientCreateInput {
  full_name: string;
  date_of_birth: string; // Accepts 'YYYY-MM-DD', 'DD/MM/YYYY', or 'DD.MM.YYYY'
  email: string;
  glucose_value: number | string;
  haemoglobin_value: number | string;
  cholesterol_value: number | string;
  unit_profile_code?: string;
  allow_duplicate?: boolean;
}

export interface PatientUpdateInput {
  full_name?: string;
  date_of_birth?: string;
  email?: string;
  glucose_value?: number | string;
  haemoglobin_value?: number | string;
  cholesterol_value?: number | string;
  unit_profile_code?: string;
  allow_duplicate?: boolean;
}

export interface PatientFormData {
  full_name: string;
  date_of_birth: string;
  email: string;
  glucose_value: string;
  haemoglobin_value: string;
  cholesterol_value: string;
}

export interface PatientSummaryMetrics {
  total: number;
  completed: number;
  pending: number;
  attention: number; // DEGRADED or FAILED
}
