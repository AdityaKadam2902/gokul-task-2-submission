/**
 * Date parsing, formatting, and validation utilities.
 *
 * Gokul Infocare - AI Growth & Automation Associate - Task 2
 * Candidate Number: 267
 * Engineering Baseline: Blueprint v0.2
 */

/**
 * Format a calendar date string (YYYY-MM-DD or ISO) to display format DD/MM/YYYY.
 */
export function formatDateForDisplay(dateStr?: string | null): string {
  if (!dateStr) return '—';
  const clean = dateStr.trim();
  
  // If already DD/MM/YYYY
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(clean)) {
    return clean;
  }
  
  // If YYYY-MM-DD or full ISO
  const isoMatch = clean.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (isoMatch) {
    const [, year, month, day] = isoMatch;
    return `${day}/${month}/${year}`;
  }

  // Fallback parsing
  const d = new Date(clean);
  if (isNaN(d.getTime())) return dateStr;
  const day = String(d.getUTCDate()).padStart(2, '0');
  const month = String(d.getUTCMonth() + 1).padStart(2, '0');
  const year = d.getUTCFullYear();
  return `${day}/${month}/${year}`;
}

/**
 * Format a datetime ISO string for audit and execution timestamps.
 */
export function formatDateTime(isoStr?: string | null): string {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  if (isNaN(d.getTime())) return isoStr;
  
  return d.toLocaleString('en-AU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export interface DateValidationResult {
  isValid: boolean;
  errorMessage?: string;
  parsedDate?: Date;
  isoDate?: string;
}

/**
 * Validates a user-entered date string supporting DD/MM/YYYY, DD.MM.YYYY, and YYYY-MM-DD.
 * Strictly checks for impossible calendar dates and future dates.
 */
export function validateAndParseDate(input: string): DateValidationResult {
  const clean = input.trim();
  if (!clean) {
    return { isValid: false, errorMessage: 'Date of birth is required.' };
  }

  let day: number;
  let month: number;
  let year: number;

  // Pattern 1: DD/MM/YYYY or DD-MM-YYYY
  const slashMatch = clean.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/);
  // Pattern 2: DD.MM.YYYY (as used in employer PDF fixtures)
  const dotMatch = clean.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
  // Pattern 3: YYYY-MM-DD
  const isoMatch = clean.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);

  if (slashMatch) {
    day = parseInt(slashMatch[1], 10);
    month = parseInt(slashMatch[2], 10);
    year = parseInt(slashMatch[3], 10);
  } else if (dotMatch) {
    day = parseInt(dotMatch[1], 10);
    month = parseInt(dotMatch[2], 10);
    year = parseInt(dotMatch[3], 10);
  } else if (isoMatch) {
    year = parseInt(isoMatch[1], 10);
    month = parseInt(isoMatch[2], 10);
    day = parseInt(isoMatch[3], 10);
  } else {
    return {
      isValid: false,
      errorMessage: 'Invalid date format. Use dd/mm/yyyy or dd.mm.yyyy.',
    };
  }

  // Basic numeric range checks
  if (year < 1900 || year > 2100) {
    return { isValid: false, errorMessage: 'Year must be between 1900 and current year.' };
  }
  if (month < 1 || month > 12) {
    return { isValid: false, errorMessage: 'Month must be between 1 and 12.' };
  }
  if (day < 1 || day > 31) {
    return { isValid: false, errorMessage: 'Day must be between 1 and 31.' };
  }

  // Precise calendar days check (handles leap years, 30-day months, Feb 29)
  const daysInMonth = new Date(year, month, 0).getDate();
  if (day > daysInMonth) {
    return {
      isValid: false,
      errorMessage: `Impossible calendar date: ${month}/${year} has only ${daysInMonth} days.`,
    };
  }

  const parsed = new Date(Date.UTC(year, month - 1, day));
  const today = new Date();
  const todayUTC = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));

  if (parsed > todayUTC) {
    return {
      isValid: false,
      errorMessage: 'Date of birth cannot be in the future.',
    };
  }

  const formattedMonth = String(month).padStart(2, '0');
  const formattedDay = String(day).padStart(2, '0');
  const isoDate = `${year}-${formattedMonth}-${formattedDay}`;

  return {
    isValid: true,
    parsedDate: parsed,
    isoDate,
  };
}
