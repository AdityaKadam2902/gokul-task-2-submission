/**
 * Analysis Service for triggering, retrieving, and polling analysis runs.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { apiClient } from './apiClient';
import { AnalysisDetailResponse, AnalysisSummary } from '../types/analysis';

export interface AnalysisStatusesResponse {
  external_status: string[];
  ai_status: string[];
  overall_status: string[];
}

export const analysisService = {
  /**
   * List all historical analysis runs for a given patient (newest first).
   */
  async listAnalyses(patientId: number): Promise<AnalysisDetailResponse[]> {
    return apiClient.get<AnalysisDetailResponse[]>(`/api/v1/patients/${patientId}/analyses`);
  },

  /**
   * Trigger or retry an analysis run for a patient.
   * Returns HTTP 202 Accepted with the scheduled run summary.
   */
  async triggerAnalysis(patientId: number): Promise<AnalysisSummary> {
    return apiClient.post<AnalysisSummary>(`/api/v1/patients/${patientId}/analyses`);
  },

  /**
   * Get specific analysis run detail including input snapshot, TestWell observations, and AI remarks.
   */
  async getAnalysis(patientId: number, analysisId: string): Promise<AnalysisDetailResponse> {
    return apiClient.get<AnalysisDetailResponse>(
      `/api/v1/patients/${patientId}/analyses/${analysisId}`
    );
  },

  /**
   * Retrieve canonical enum statuses from metadata discovery endpoint.
   */
  async getCanonicalStatuses(): Promise<AnalysisStatusesResponse> {
    return apiClient.get<AnalysisStatusesResponse>('/api/v1/meta/analysis-statuses');
  },
};
