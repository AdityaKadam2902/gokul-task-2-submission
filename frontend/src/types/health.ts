/**
 * Health and Readiness API Types
 * Aligned with backend Pydantic schemas in app.schemas.health
 */

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  app: string;
  version: string;
  timestamp: string;
}

export interface ReadinessChecks {
  configuration: string;
  persistence: string;
}

export interface ReadinessResponse {
  status: 'ready' | 'not_ready';
  app: string;
  version: string;
  environment: string;
  phase: string;
  checks: ReadinessChecks;
  timestamp: string;
}

export interface SystemStatusState {
  health: HealthResponse | null;
  readiness: ReadinessResponse | null;
  loading: boolean;
  error: string | null;
  lastChecked: string | null;
}
