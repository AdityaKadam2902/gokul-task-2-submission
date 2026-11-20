/**
 * Typed API Client for LabInsight Backend.
 * Centralized HTTP request handling, error envelope parsing, and network reliability.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { ErrorEnvelope, ErrorDetail } from '../types/api';
import { HealthResponse, ReadinessResponse } from '../types/health';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  status: number;
  code: string;
  details: ErrorDetail[];
  existingPatientId?: number | null;
  requestId?: string;

  constructor(
    message: string,
    status: number,
    code: string = 'API_ERROR',
    details: ErrorDetail[] = [],
    existingPatientId?: number | null,
    requestId?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
    this.existingPatientId = existingPatientId;
    this.requestId = requestId;
  }
}

export async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(options?.headers || {}),
      },
      ...options,
    });

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    if (!response.ok) {
      let errorBody: ErrorEnvelope | null = null;
      try {
        errorBody = (await response.json()) as ErrorEnvelope;
      } catch {
        // Response was not JSON
      }

      if (errorBody && errorBody.error) {
        throw new ApiError(
          errorBody.error.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorBody.error.code || 'API_ERROR',
          errorBody.error.details || [],
          errorBody.error.existing_patient_id,
          errorBody.error.request_id
        );
      }

      throw new ApiError(
        `HTTP ${response.status}: ${response.statusText}`,
        response.status
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    const message = error instanceof Error ? error.message : 'Unknown network error';
    throw new ApiError(`Network error connecting to backend: ${message}`, 0, 'NETWORK_ERROR');
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { method: 'GET', ...options }),

  post: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      ...options,
    }),

  patch: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, {
      method: 'PATCH',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      ...options,
    }),

  delete: <T = void>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { method: 'DELETE', ...options }),

  /**
   * Fetch liveness status from GET /api/v1/health
   */
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/api/v1/health');
  },

  /**
   * Fetch readiness status from GET /api/v1/ready
   */
  async getReadiness(): Promise<ReadinessResponse> {
    return request<ReadinessResponse>('/api/v1/ready');
  },
};
