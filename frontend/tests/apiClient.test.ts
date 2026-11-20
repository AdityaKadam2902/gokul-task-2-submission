import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient, ApiError } from '../src/services/apiClient';

describe('apiClient', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches health status successfully', async () => {
    const mockHealthResponse = {
      status: 'healthy',
      app: 'LabInsight',
      version: '0.1.0',
      timestamp: '2026-11-18T00:00:00Z',
    };

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealthResponse,
    } as Response);
    vi.stubGlobal('fetch', mockFetch);

    const result = await apiClient.getHealth();
    expect(result.status).toBe('healthy');
    expect(result.app).toBe('LabInsight');
    expect(result.version).toBe('0.1.0');
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/health', expect.any(Object));
  });

  it('fetches readiness status successfully', async () => {
    const mockReadinessResponse = {
      status: 'ready',
      app: 'LabInsight',
      version: '0.1.0',
      environment: 'development',
      phase: 'Phase 4A - TestWell Health API Integration',
      checks: {
        configuration: 'ok',
        persistence: 'ok',
      },
      timestamp: '2026-11-18T00:00:00Z',
    };

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockReadinessResponse,
    } as Response);
    vi.stubGlobal('fetch', mockFetch);

    const result = await apiClient.getReadiness();
    expect(result.status).toBe('ready');
    expect(result.checks.persistence).toBe('ok');
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/ready', expect.any(Object));
  });

  it('throws ApiError when response is not ok', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable',
    } as Response);
    vi.stubGlobal('fetch', mockFetch);

    await expect(apiClient.getHealth()).rejects.toThrow(ApiError);
  });
});
