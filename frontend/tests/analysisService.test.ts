import { describe, it, expect, vi, beforeEach } from 'vitest';
import { analysisService } from '../src/services/analysisService';
import { apiClient } from '../src/services/apiClient';
import { AnalysisDetailResponse, AnalysisSummary } from '../src/types/analysis';

describe('analysisService', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('triggers analysis for a patient', async () => {
    const mockAnalysis: AnalysisSummary = {
      id: 'analysis-uuid-1',
      patient_id: 42,
      run_number: 1,
      overall_status: 'PENDING',
      external_status: 'PENDING',
      ai_status: 'NOT_RUN',
      external_provider: 'TestWell',
      created_at: '2026-11-18T10:00:00Z',
    };

    const postSpy = vi.spyOn(apiClient, 'post').mockResolvedValue(mockAnalysis);

    const result = await analysisService.triggerAnalysis(42);

    expect(postSpy).toHaveBeenCalledWith('/api/v1/patients/42/analyses');
    expect(result.patient_id).toBe(42);
    expect(result.overall_status).toBe('PENDING');
  });

  it('retrieves detailed analysis with TestWell and AI remarks', async () => {
    const mockDetail: AnalysisDetailResponse = {
      id: 'analysis-uuid-1',
      patient_id: 42,
      run_number: 1,
      overall_status: 'COMPLETED',
      external_status: 'SUCCEEDED',
      ai_status: 'SUCCEEDED',
      external_provider: 'TestWell',
      ai_model: 'llama3.2:3b',
      created_at: '2026-11-18T10:00:00Z',
      input_snapshot_json: {},
      external_result_json: {
        provider: 'TestWell Health Analytics',
        endpoint: '/api/v1/lookup',
        retrieved_at: '2026-11-18T10:00:00Z',
        summary: { total: 3, matched: 3 },
        global_caveats: [],
        observations: [
          {
            analyte: 'glucose',
            query_marker: 'glucose',
            flag: 'normal',
            value: 95.0,
            unit: 'mg/dL',
            found: true,
            context_status: 'CONFIRMED',
            citations: [],
          },
        ],
      },
      ai_result_json: {
        summary: 'Metabolic markers are within standard clinical reference ranges.',
        generation_label: 'AI_GENERATED',
        analyte_remarks: [],
        source_observation_ids: [],
        caveat_codes: [],
      },
    };

    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue(mockDetail);

    const result = await analysisService.getAnalysis(42, 'analysis-uuid-1');

    expect(getSpy).toHaveBeenCalledWith('/api/v1/patients/42/analyses/analysis-uuid-1');
    expect(result.overall_status).toBe('COMPLETED');
    expect(result.external_result_json?.observations.length).toBe(1);
    expect(result.ai_model).toBe('llama3.2:3b');
  });

  it('lists historical analyses for a patient', async () => {
    const mockList: AnalysisSummary[] = [
      {
        id: 'analysis-uuid-2',
        patient_id: 42,
        run_number: 2,
        overall_status: 'COMPLETED',
        external_status: 'SUCCEEDED',
        ai_status: 'SUCCEEDED',
        external_provider: 'TestWell',
        created_at: '2026-11-18T10:10:00Z',
      },
      {
        id: 'analysis-uuid-1',
        patient_id: 42,
        run_number: 1,
        overall_status: 'DEGRADED',
        external_status: 'SUCCEEDED',
        ai_status: 'FALLBACK',
        external_provider: 'TestWell',
        created_at: '2026-11-18T10:00:00Z',
      },
    ];

    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue(mockList);

    const result = await analysisService.listAnalyses(42);

    expect(getSpy).toHaveBeenCalledWith('/api/v1/patients/42/analyses');
    expect(result.length).toBe(2);
  });
});
