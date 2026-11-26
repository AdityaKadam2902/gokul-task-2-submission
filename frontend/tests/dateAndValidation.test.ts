import { describe, it, expect } from 'vitest';
import {
  validateAndParseDate,
  formatDateForDisplay,
  formatDateTime,
} from '../src/utils/date';
import {
  validateFullName,
  validateEmail,
  validateBiomarker,
  validatePatientForm,
  validateGokulGmailCombination,
} from '../src/utils/validation';

describe('Date Utilities', () => {
  it('parses YYYY-MM-DD format correctly', () => {
    const res = validateAndParseDate('1990-05-15');
    expect(res.isValid).toBe(true);
    expect(res.isoDate).toBe('1990-05-15');
  });

  it('parses DD/MM/YYYY format correctly', () => {
    const res = validateAndParseDate('15/05/1990');
    expect(res.isValid).toBe(true);
    expect(res.isoDate).toBe('1990-05-15');
  });

  it('parses DD.MM.YYYY format correctly', () => {
    const res = validateAndParseDate('15.05.1990');
    expect(res.isValid).toBe(true);
    expect(res.isoDate).toBe('1990-05-15');
  });

  it('rejects impossible dates like February 30th or 31st', () => {
    expect(validateAndParseDate('30/02/2020').isValid).toBe(false);
    expect(validateAndParseDate('31/02/2024').isValid).toBe(false);
    expect(validateAndParseDate('31/04/2021').isValid).toBe(false);
  });

  it('handles leap years correctly', () => {
    // 2020 and 2024 are leap years
    expect(validateAndParseDate('29/02/2020').isValid).toBe(true);
    expect(validateAndParseDate('29/02/2024').isValid).toBe(true);
    // 2021 is not a leap year
    expect(validateAndParseDate('29/02/2021').isValid).toBe(false);
    expect(validateAndParseDate('2021-02-29').isValid).toBe(false);
  });

  it('rejects future dates', () => {
    const futureDate = '2099-01-01';
    expect(validateAndParseDate(futureDate).isValid).toBe(false);
    expect(validateAndParseDate(futureDate).errorMessage).toContain('future');
  });

  it('formats dates consistently', () => {
    expect(formatDateForDisplay('1985-10-24')).toBe('24/10/1985');
    expect(formatDateForDisplay('24/10/1985')).toBe('24/10/1985');
    expect(formatDateForDisplay(null)).toBe('—');
  });

  it('formats ISO timestamps for audit displays', () => {
    const timestamp = '2026-11-18T10:00:00Z';
    const formatted = formatDateTime(timestamp);
    expect(formatted).not.toBe('—');
    expect(formatted).toContain('2026');
  });
});

describe('Validation Utilities', () => {
  describe('validateFullName', () => {
    it('accepts valid full names', () => {
      expect(validateFullName('Jane Doe')).toBeNull();
      expect(validateFullName("Sarah O'Connor-Smith")).toBeNull();
    });

    it('rejects empty or whitespace-only names', () => {
      expect(validateFullName('')).not.toBeNull();
      expect(validateFullName('   ')).not.toBeNull();
    });

    it('rejects overly long names exceeding 120 chars', () => {
      const longName = 'A'.repeat(125);
      expect(validateFullName(longName)).not.toBeNull();
    });
  });

  describe('validateEmail', () => {
    it('accepts valid emails', () => {
      expect(validateEmail('gokul@infocare.com')).toBeNull();
      expect(validateEmail('user.name+tag@domain.co.uk')).toBeNull();
    });

    it('rejects invalid emails', () => {
      expect(validateEmail('')).not.toBeNull();
      expect(validateEmail('notanemail')).not.toBeNull();
      expect(validateEmail('missing@tld')).not.toBeNull();
      expect(validateEmail('@missinguser.com')).not.toBeNull();
    });
  });

  describe('validateBiomarker', () => {
    it('accepts valid non-negative numbers', () => {
      expect(validateBiomarker('95.5', 'Glucose')).toBeNull();
      expect(validateBiomarker('140.2', 'Cholesterol')).toBeNull();
      expect(validateBiomarker('0', 'Haemoglobin')).toBeNull();
    });

    it('rejects negative numbers and invalid strings', () => {
      expect(validateBiomarker('-5', 'Glucose')).not.toBeNull();
      expect(validateBiomarker('abc', 'Glucose')).not.toBeNull();
      expect(validateBiomarker('', 'Glucose')).not.toBeNull();
    });
  });

  describe('validatePatientForm', () => {
    it('passes for a valid complete form', () => {
      const result = validatePatientForm({
        full_name: 'Gokul Candidate',
        date_of_birth: '1992-06-14',
        email: 'gokul@infocare.com',
        glucose_value: '95.0',
        haemoglobin_value: '14.5',
        cholesterol_value: '185.0',
      });
      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('returns specific field errors for invalid inputs', () => {
      const result = validatePatientForm({
        full_name: '',
        date_of_birth: '31/02/2021', // impossible date
        email: 'bad-email',
        glucose_value: '-10',
        haemoglobin_value: 'not-a-number',
        cholesterol_value: '200',
      });
      expect(result.isValid).toBe(false);
      expect(result.errors.full_name).toBeDefined();
      expect(result.errors.date_of_birth).toBeDefined();
      expect(result.errors.email).toBeDefined();
      expect(result.errors.glucose_value).toBeDefined();
      expect(result.errors.haemoglobin_value).toBeDefined();
      expect(result.errors.cholesterol_value).toBeUndefined();
    });

    it('rejects Gokul + Gmail combination and attaches error to email field', () => {
      const result = validatePatientForm({
        full_name: 'Gokul',
        date_of_birth: '1990-05-15',
        email: 'test.user@gmail.com',
        glucose_value: '95.0',
        haemoglobin_value: '14.5',
        cholesterol_value: '185.0',
      });
      expect(result.isValid).toBe(false);
      expect(result.errors.email).toBe(
        "The name 'Gokul' cannot be used with an email address containing 'gmail'."
      );
      expect(result.errors.full_name).toBeUndefined();
    });

    it('accepts Gokul with non-Gmail address in validatePatientForm', () => {
      const result = validatePatientForm({
        full_name: 'Gokul',
        date_of_birth: '1990-05-15',
        email: 'user@yahoo.com',
        glucose_value: '95.0',
        haemoglobin_value: '14.5',
        cholesterol_value: '185.0',
      });
      expect(result.isValid).toBe(true);
      expect(result.errors.email).toBeUndefined();
    });

    it('accepts Gokul Kadam with Gmail address in validatePatientForm', () => {
      const result = validatePatientForm({
        full_name: 'Gokul Kadam',
        date_of_birth: '1990-05-15',
        email: 'user@gmail.com',
        glucose_value: '95.0',
        haemoglobin_value: '14.5',
        cholesterol_value: '185.0',
      });
      expect(result.isValid).toBe(true);
      expect(result.errors.email).toBeUndefined();
    });
  });

  describe('validateGokulGmailCombination', () => {
    it('rejects exact match Gokul + gmail.com address', () => {
      const error = validateGokulGmailCombination('Gokul', 'user@gmail.com');
      expect(error).toBe("The name 'Gokul' cannot be used with an email address containing 'gmail'.");
    });

    it('rejects uppercase GOKUL + uppercase Gmail address', () => {
      const error = validateGokulGmailCombination('GOKUL', 'USER@GMAIL.COM');
      expect(error).toBe("The name 'Gokul' cannot be used with an email address containing 'gmail'.");
    });

    it('rejects mixed-case variations', () => {
      expect(validateGokulGmailCombination('gokul', 'user@Gmail.com')).toBe(
        "The name 'Gokul' cannot be used with an email address containing 'gmail'."
      );
      expect(validateGokulGmailCombination('GoKuL', 'user@gMaIl.com')).toBe(
        "The name 'Gokul' cannot be used with an email address containing 'gmail'."
      );
    });

    it('handles leading and trailing whitespace properly', () => {
      const error = validateGokulGmailCombination('   Gokul   ', '  user@gmail.com  ');
      expect(error).toBe("The name 'Gokul' cannot be used with an email address containing 'gmail'.");
    });

    it('accepts Gokul with a non-Gmail address', () => {
      expect(validateGokulGmailCombination('Gokul', 'user@yahoo.com')).toBeNull();
      expect(validateGokulGmailCombination('Gokul', 'gokul@infocare.com')).toBeNull();
      expect(validateGokulGmailCombination('Gokul', 'user@outlook.com')).toBeNull();
    });

    it('accepts another name with a Gmail address', () => {
      expect(validateGokulGmailCombination('Rahul', 'user@gmail.com')).toBeNull();
      expect(validateGokulGmailCombination('Aditya', 'user@gmail.com')).toBeNull();
    });

    it('accepts names containing Gokul as substring (e.g., Gokul Kadam)', () => {
      expect(validateGokulGmailCombination('Gokul Kadam', 'user@gmail.com')).toBeNull();
      expect(validateGokulGmailCombination('Kadam Gokul', 'user@gmail.com')).toBeNull();
      expect(validateGokulGmailCombination('Gokulraj', 'user@gmail.com')).toBeNull();
    });
  });
});
