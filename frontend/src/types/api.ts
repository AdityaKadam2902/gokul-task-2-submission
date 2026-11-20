/**
 * Common API response envelopes, error structures, and pagination types.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

export type OverallStatus = 'PENDING' | 'COMPLETED' | 'DEGRADED' | 'FAILED' | 'NOT_RUN';
export type ExternalStatus = 'PENDING' | 'SUCCEEDED' | 'FAILED' | 'PARTIAL' | 'NO_MATCH';
export type AiStatus = 'NOT_RUN' | 'SUCCEEDED' | 'FALLBACK';
export type BiomarkerFlag = 'normal' | 'high' | 'low' | 'unknown';

export interface ErrorDetail {
  field?: string | null;
  code: string;
  message: string;
  existing_patient_id?: number | null;
}

export interface ErrorBody {
  code: string;
  message: string;
  details: ErrorDetail[];
  existing_patient_id?: number | null;
  request_id: string;
}

export interface ErrorEnvelope {
  error: ErrorBody;
}

export interface PaginationParams {
  page: number;
  page_size: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
