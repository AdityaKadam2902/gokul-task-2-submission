/**
 * Custom Hook for tracking and polling long-running analysis runs.
 * Supports bounded exponential backoff, unmount cancellation, and terminal detection.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { AnalysisDetailResponse, AnalysisSummary } from '../types/analysis';
import { analysisService } from '../services/analysisService';

interface UseAnalysisPollOptions {
  patientId: number;
  initialAnalysis?: AnalysisSummary | AnalysisDetailResponse | null;
  onTerminal?: (completed: AnalysisDetailResponse) => void;
  autoStart?: boolean;
}

export function useAnalysisPoll({
  patientId,
  initialAnalysis,
  onTerminal,
  autoStart = true,
}: UseAnalysisPollOptions) {
  const [analysis, setAnalysis] = useState<AnalysisDetailResponse | null>(null);
  const [isPolling, setIsPolling] = useState<boolean>(false);
  const [pollError, setPollError] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);

  const timerRef = useRef<number | null>(null);
  const elapsedTimerRef = useRef<number | null>(null);
  const isMountedRef = useRef<boolean>(true);
  const pollIntervalRef = useRef<number>(2000); // Start at 2000ms

  const isTerminalStatus = (status?: string | null): boolean => {
    return status === 'COMPLETED' || status === 'DEGRADED' || status === 'FAILED';
  };

  const fetchDetail = useCallback(
    async (analysisId: string) => {
      try {
        const detail = await analysisService.getAnalysis(patientId, analysisId);
        if (!isMountedRef.current) return;

        setAnalysis(detail);
        setPollError(null);

        if (isTerminalStatus(detail.overall_status)) {
          // Terminal reached! Stop polling.
          setIsPolling(false);
          if (timerRef.current) clearTimeout(timerRef.current);
          if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
          if (onTerminal) onTerminal(detail);
        } else {
          // Continue polling with progressive backoff (max 5000ms)
          pollIntervalRef.current = Math.min(pollIntervalRef.current + 1000, 5000);
          timerRef.current = window.setTimeout(() => {
            if (isMountedRef.current) {
              fetchDetail(analysisId);
            }
          }, pollIntervalRef.current);
        }
      } catch (err) {
        if (!isMountedRef.current) return;
        const msg = err instanceof Error ? err.message : 'Error polling analysis status';
        setPollError(msg);
        // Continue retrying even on transient poll error up to backoff limit
        timerRef.current = window.setTimeout(() => {
          if (isMountedRef.current) {
            fetchDetail(analysisId);
          }
        }, 4000);
      }
    },
    [patientId, onTerminal]
  );

  const startPolling = useCallback(
    (analysisId: string) => {
      setIsPolling(true);
      setElapsedSeconds(0);
      pollIntervalRef.current = 2000;

      // Start elapsed timer
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
      elapsedTimerRef.current = window.setInterval(() => {
        if (isMountedRef.current) {
          setElapsedSeconds((prev) => prev + 1);
        }
      }, 1000);

      fetchDetail(analysisId);
    },
    [fetchDetail]
  );

  const stopPolling = useCallback(() => {
    setIsPolling(false);
    if (timerRef.current) clearTimeout(timerRef.current);
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
  }, []);

  useEffect(() => {
    isMountedRef.current = true;

    if (initialAnalysis) {
      if (isTerminalStatus(initialAnalysis.overall_status)) {
        // If already terminal, do a single detail fetch to populate all observation JSON
        analysisService
          .getAnalysis(patientId, initialAnalysis.id)
          .then((d) => {
            if (isMountedRef.current) setAnalysis(d);
          })
          .catch(() => {
            if (isMountedRef.current) setAnalysis(initialAnalysis as AnalysisDetailResponse);
          });
      } else if (autoStart && initialAnalysis.overall_status === 'PENDING') {
        startPolling(initialAnalysis.id);
      }
    }

    return () => {
      isMountedRef.current = false;
      if (timerRef.current) clearTimeout(timerRef.current);
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    };
  }, [initialAnalysis?.id, autoStart]);

  return {
    analysis,
    isPolling,
    isTerminal: isTerminalStatus(analysis?.overall_status),
    pollError,
    elapsedSeconds,
    startPolling,
    stopPolling,
    refreshDetail: (id: string) => fetchDetail(id),
  };
}
