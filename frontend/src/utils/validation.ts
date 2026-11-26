/**
 * Patient form validation utilities.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

import { PatientFormData } from '../types/patient';
import { validateAndParseDate } from './date';

export interface FormErrors {
  full_name?: string;
  date_of_birth?: string;
  email?: string;
  glucose_value?: string;
  haemoglobin_value?: string;
  cholesterol_value?: string;
  general?: string;
}

export function validateFullName(name: string): string | null {
  const trimmed = name.trim();
  if (!trimmed) {
    return 'Full name is required.';
  }
  if (trimmed.length > 120) {
    return 'Full name cannot exceed 120 characters.';
  }
  return null;
}

export function validateEmail(email: string): string | null {
  const trimmed = email.trim();
  if (!trimmed) {
    return 'Email address is required.';
  }
  if (trimmed.length > 254) {
    return 'Email address cannot exceed 254 characters.';
  }
  // Standard email format regex adhering to HTML5 / backend RFC checks
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;
  if (!emailRegex.test(trimmed)) {
    return 'Invalid email address format (e.g. user@example.com).';
  }
  return null;
}

export function validateGokulGmailCombination(fullName: string, email: string): string | null {
  const trimmedName = fullName.trim();
  const trimmedEmail = email.trim();
  if (trimmedName.toLowerCase() === 'gokul' && trimmedEmail.toLowerCase().includes('gmail')) {
    return "The name 'Gokul' cannot be used with an email address containing 'gmail'.";
  }
  return null;
}

export function validateBiomarker(val: string, label: string): string | null {
  const trimmed = val.trim();
  if (!trimmed) {
    return `${label} measurement is required.`;
  }
  const num = Number(trimmed);
  if (isNaN(num) || !isFinite(num)) {
    return `${label} must be a valid numeric measurement.`;
  }
  if (num < 0) {
    return `${label} cannot be negative.`;
  }
  return null;
}

export function validatePatientForm(data: PatientFormData): { isValid: boolean; errors: FormErrors } {
  const errors: FormErrors = {};

  const nameError = validateFullName(data.full_name);
  if (nameError) errors.full_name = nameError;

  const dateRes = validateAndParseDate(data.date_of_birth);
  if (!dateRes.isValid) {
    errors.date_of_birth = dateRes.errorMessage;
  }

  const emailError = validateEmail(data.email);
  if (emailError) {
    errors.email = emailError;
  } else {
    const comboError = validateGokulGmailCombination(data.full_name, data.email);
    if (comboError) {
      errors.email = comboError;
    }
  }

  const glucoseError = validateBiomarker(data.glucose_value, 'Glucose');
  if (glucoseError) errors.glucose_value = glucoseError;

  const haemoglobinError = validateBiomarker(data.haemoglobin_value, 'Haemoglobin');
  if (haemoglobinError) errors.haemoglobin_value = haemoglobinError;

  const cholesterolError = validateBiomarker(data.cholesterol_value, 'Cholesterol');
  if (cholesterolError) errors.cholesterol_value = cholesterolError;

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}
