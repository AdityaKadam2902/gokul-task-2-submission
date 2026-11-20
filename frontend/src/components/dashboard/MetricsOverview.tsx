/**
 * Operational Summary Metric Cards.
 * Presents real database counts for records and analysis states.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React from 'react';
import { Users, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { PatientSummaryMetrics } from '../../types/patient';

interface MetricsOverviewProps {
  metrics: PatientSummaryMetrics;
  loading: boolean;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ metrics, loading }) => {
  const cards = [
    {
      title: 'Total Patient Records',
      value: metrics.total,
      description: 'Persistent patient profiles in database',
      icon: Users,
      iconColor: 'text-slate-700',
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
    },
    {
      title: 'Analyses Completed',
      value: metrics.completed,
      description: 'Verified TestWell & AI remarks generated',
      icon: CheckCircle2,
      iconColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50/50',
      borderColor: 'border-emerald-200',
    },
    {
      title: 'Analyses In Progress',
      value: metrics.pending,
      description: 'Scheduled or undergoing local inference',
      icon: Clock,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50/50',
      borderColor: 'border-blue-200',
    },
    {
      title: 'Requires Attention / Fallback',
      value: metrics.attention,
      description: 'Degraded, fallback remarks, or provider error',
      icon: AlertTriangle,
      iconColor: 'text-amber-600',
      bgColor: 'bg-amber-50/50',
      borderColor: 'border-amber-200',
    },
  ];

  return (
    <section aria-labelledby="metrics-heading" className="mb-6">
      <h2 id="metrics-heading" className="sr-only">
        System Operational Metrics
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className={`p-4 rounded-xl border ${card.borderColor} ${card.bgColor} bg-white shadow-sm flex flex-col justify-between transition hover:shadow`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-600 tracking-wide uppercase">
                  {card.title}
                </span>
                <div className={`p-2 rounded-lg bg-white border border-slate-100 shadow-xs shrink-0 ${card.iconColor}`}>
                  <Icon className="w-4 h-4" aria-hidden="true" />
                </div>
              </div>

              <div className="mt-3">
                <div className="text-2xl font-bold text-slate-900 tracking-tight">
                  {loading ? (
                    <span className="inline-block w-8 h-6 bg-slate-200 animate-pulse rounded" />
                  ) : (
                    card.value
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5">{card.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
