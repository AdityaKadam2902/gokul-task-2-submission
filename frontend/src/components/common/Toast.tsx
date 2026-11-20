/**
 * Toast Notification Component for user actions and operational status.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  return (
    <div
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full px-4 pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ toast: ToastMessage; onDismiss: (id: string) => void }> = ({
  toast,
  onDismiss,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id);
    }, 5000);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const bgStyle =
    toast.type === 'success'
      ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
      : toast.type === 'error'
      ? 'bg-rose-50 border-rose-300 text-rose-900'
      : 'bg-blue-50 border-blue-300 text-blue-900';

  const Icon =
    toast.type === 'success' ? CheckCircle2 : toast.type === 'error' ? AlertCircle : Info;

  const iconColor =
    toast.type === 'success'
      ? 'text-emerald-600'
      : toast.type === 'error'
      ? 'text-rose-600'
      : 'text-blue-600';

  return (
    <div
      className={`pointer-events-auto flex items-start p-3.5 rounded-lg border shadow-md transition-all ${bgStyle}`}
      role="alert"
    >
      <Icon className={`w-5 h-5 mr-3 shrink-0 mt-0.5 ${iconColor}`} aria-hidden="true" />
      <div className="flex-1 text-sm">
        <h4 className="font-semibold">{toast.title}</h4>
        {toast.message && <p className="mt-0.5 text-xs opacity-90">{toast.message}</p>}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="ml-3 text-slate-400 hover:text-slate-600 rounded p-1 transition"
        aria-label="Dismiss notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
