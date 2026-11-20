/**
 * Analysis domain models, TestWell observations, and Ollama remarks payload.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { AiStatus, ExternalStatus, OverallStatus, BiomarkerFlag } from './api';

export interface ProviderCitation {
  label: string;
  url?: string | null;
}

export interface NormalizedObservation {
  analyte: string;
  query_marker: string;
  matched_marker?: string | null;
  value: number;
  unit: string;
  found: boolean;
  flag: BiomarkerFlag;
  range_text?: string | null;
  range_min?: number | null;
  range_max?: number | null;
  range_unit?: string | null;
  range_qualifier?: string | null;
  unit_mismatch?: boolean;
  context_status: string; // 'CONFIRMED' | 'CONTEXT_NOT_CONFIRMED'
  suggests?: string | null;
  retest?: string | null;
  citations: ProviderCitation[];
  links?: Record<string, string | null>;
  warnings?: string[];
}

export interface NormalizedProviderResult {
  provider: string;
  endpoint: string;
  api_version?: string | null;
  catalog_review_date?: string | null;
  reviewer?: string | null;
  observations: NormalizedObservation[];
  summary: {
    total: number;
    matched: number;
    high?: number;
    low?: number;
    normal?: number;
    unknown?: number;
  };
  global_caveats: string[];
  retrieved_at: string;
  latency_ms?: number | null;
}

export interface AnalyteRemark {
  analyte: string;
  observation_id: string;
  provider_flag: string;
  summary: string;
}

export interface AiRemarksPayload {
  summary: string;
  analyte_remarks: AnalyteRemark[];
  source_observation_ids: string[];
  caveat_codes: string[];
  generation_label: 'AI_GENERATED' | 'DETERMINISTIC_FALLBACK';
}

export interface AnalysisSummary {
  id: string;
  patient_id: number;
  run_number: number;
  overall_status: OverallStatus;
  external_status: ExternalStatus;
  ai_status: AiStatus;
  external_provider: string;
  ai_model?: string | null;
  remarks_text?: string | null;
  error_code?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface AnalysisDetailResponse extends AnalysisSummary {
  input_snapshot_json: Record<string, any>;
  external_result_json?: NormalizedProviderResult | null;
  ai_result_json?: AiRemarksPayload | Record<string, any> | null;
  error_summary?: string | null;
  retry_of_id?: string | null;
}
