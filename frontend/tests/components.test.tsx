import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  OverallStatusBadge,
  BiomarkerFlagBadge,
  AiStatusBadge,
} from '../src/components/common/StatusBadge';
import { DisclaimerBanner } from '../src/components/DisclaimerBanner';
import { DuplicateModal } from '../src/components/patients/DuplicateModal';
import { PatientFormData } from '../src/types/patient';

describe('StatusBadge Components', () => {
  it('renders overall status badges correctly', () => {
    const { rerender } = render(<OverallStatusBadge status="COMPLETED" />);
    expect(screen.getByText('Completed')).toBeDefined();

    rerender(<OverallStatusBadge status="PENDING" />);
    expect(screen.getByText('Analyzing...')).toBeDefined();

    rerender(<OverallStatusBadge status="DEGRADED" />);
    expect(screen.getByText(/Degraded \/ Fallback/i)).toBeDefined();

    rerender(<OverallStatusBadge status="FAILED" />);
    expect(screen.getByText('Failed')).toBeDefined();

    rerender(<OverallStatusBadge status="NOT_RUN" />);
    expect(screen.getByText('Not Run')).toBeDefined();
  });

  it('renders biomarker flags correctly', () => {
    const { rerender } = render(<BiomarkerFlagBadge flag="NORMAL" />);
    expect(screen.getByText('Normal')).toBeDefined();

    rerender(<BiomarkerFlagBadge flag="HIGH" />);
    expect(screen.getByText(/Elevated/i)).toBeDefined();

    rerender(<BiomarkerFlagBadge flag="LOW" />);
    expect(screen.getByText('Low')).toBeDefined();
  });

  it('renders AI vs Template fallback badge correctly', () => {
    const { rerender } = render(
      <AiStatusBadge status="SUCCEEDED" generationLabel="AI_GENERATED" />
    );
    expect(screen.getByText(/AI Generated/i)).toBeDefined();

    rerender(
      <AiStatusBadge status="FALLBACK" generationLabel="DETERMINISTIC_FALLBACK" />
    );
    expect(screen.getByText(/Template Fallback/i)).toBeDefined();
  });
});

describe('DisclaimerBanner', () => {
  it('renders the educational notice and expands unit assumptions', () => {
    render(<DisclaimerBanner />);
    expect(screen.getByText(/Educational Healthcare Prototype/i)).toBeDefined();
    expect(screen.getByText(/Not a Diagnostic Medical Device/i)).toBeDefined();

    // Click toggle to reveal unit profile
    const toggleButton = screen.getByRole('button', { name: /Unit Profile & Privacy/i });
    fireEvent.click(toggleButton);

    expect(screen.getAllByText(/mg\/dL/i).length).toBeGreaterThan(0);
  });
});

describe('DuplicateModal', () => {
  const mockFormData: PatientFormData = {
    full_name: 'Existing Patient',
    date_of_birth: '15/05/1985',
    email: 'existing@example.com',
    glucose_value: '95.0',
    haemoglobin_value: '14.5',
    cholesterol_value: '185.0',
  };

  it('renders conflict details correctly', () => {
    render(
      <DuplicateModal
        isOpen={true}
        formData={mockFormData}
        existingPatientId={12}
        loading={false}
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    expect(screen.getByText(/Duplicate Patient Record Detected/i)).toBeDefined();
    expect(screen.getByText(/Matched Existing Record/i)).toBeDefined();
    expect(screen.getAllByText(/Existing Patient/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/existing@example.com/i)).toBeDefined();
  });

  it('triggers onConfirm when Confirm & Insert Duplicate Record is clicked', () => {
    const confirmSpy = vi.fn();
    render(
      <DuplicateModal
        isOpen={true}
        formData={mockFormData}
        existingPatientId={12}
        loading={false}
        onConfirm={confirmSpy}
        onCancel={vi.fn()}
      />
    );

    const confirmButton = screen.getByRole('button', { name: /Confirm & Insert Duplicate Record/i });
    fireEvent.click(confirmButton);
    expect(confirmSpy).toHaveBeenCalledTimes(1);
  });

  it('triggers onCancel when Cancel is clicked', () => {
    const cancelSpy = vi.fn();
    render(
      <DuplicateModal
        isOpen={true}
        formData={mockFormData}
        existingPatientId={12}
        loading={false}
        onConfirm={vi.fn()}
        onCancel={cancelSpy}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    fireEvent.click(cancelButton);
    expect(cancelSpy).toHaveBeenCalledTimes(1);
  });
});
