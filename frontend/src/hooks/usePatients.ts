/**
 * Custom Hook for patient directory data management, pagination, and summary metrics.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { useState, useEffect, useCallback } from 'react';
import { PatientListItem, PatientSummaryMetrics } from '../types/patient';
import { patientService } from '../services/patientService';

export function usePatients() {
  const [patients, setPatients] = useState<PatientListItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [metrics, setMetrics] = useState<PatientSummaryMetrics>({
    total: 0,
    completed: 0,
    pending: 0,
    attention: 0,
  });

  const fetchPatients = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await patientService.listPatients({
        page,
        page_size: pageSize,
        search: search.trim() || undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      });
      setPatients(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages || 1);

      // Compute operational metrics across all items
      // When search is empty, fetch all records (up to 100 for local prototype) to compute exact metrics
      if (!search.trim()) {
        try {
          const allRes = await patientService.listPatients({ page: 1, page_size: 100 });
          let completed = 0;
          let pending = 0;
          let attention = 0;
          for (const item of allRes.items) {
            const st = item.latest_analysis_status;
            if (st === 'COMPLETED') completed++;
            else if (st === 'PENDING') pending++;
            else if (st === 'DEGRADED' || st === 'FAILED') attention++;
          }
          setMetrics({
            total: allRes.total,
            completed,
            pending,
            attention,
          });
        } catch {
          // If secondary metric fetch fails, default total
          setMetrics((prev) => ({ ...prev, total: response.total }));
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load patient records';
      setError(msg);
      setPatients([]);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  const handleSearch = useCallback((newSearch: string) => {
    setSearch(newSearch);
    setPage(1); // Reset to page 1 on new search
  }, []);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return {
    patients,
    total,
    page,
    pageSize,
    totalPages,
    search,
    loading,
    error,
    metrics,
    setPage: handlePageChange,
    setPageSize,
    handleSearch,
    refresh: fetchPatients,
  };
}
