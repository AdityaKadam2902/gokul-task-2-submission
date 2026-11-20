# Validation Specification

**Version:** 0.2 — Owner-approved implementation baseline

## 1. General principles

- Backend validation is authoritative; frontend validation improves usability.
- Return all independent field errors in one response where practical.
- Do not silently mutate input to make invalid fixtures pass.
- Trim leading/trailing whitespace in text.
- Numeric validity is not clinical normality.
- Employer test rows are local assessment fixtures. Do not publish raw entries in public docs/tests.

## 2. Full name

- Required, trimmed, 1–120 characters.
- Reject whitespace-only.
- Do not infer sex, ethnicity, health or identity from a name.

## 3. Email

- Required.
- Syntax validation using a standards-aware validator such as Pydantic `EmailStr`.
- Trim whitespace; canonical storage may lowercase for comparison.
- Do not perform DNS deliverability checks or send email.
- Invalid examples in employer PDF must be rejected according to their actual syntax.

## 4. Date of birth

- Required date-only value.
- Accept strict `dd/mm/yyyy` plus `dd.mm.yyyy` for the employer's supplied dot-formatted fixtures.
- Parse day/month/year explicitly.
- Reject impossible calendar dates.
- Reject a date later than runtime current date.
- Never hardcode the current date in implementation logic.
- Store ISO `date`; API emits `YYYY-MM-DD`; UI shows `dd/mm/yyyy`.
- Do not accept ambiguous month/day US format.
- Date of birth is not used to infer age at specimen collection because the specimen date is missing.

## 5. Measurements

- Required finite numeric decimal.
- Reject booleans, strings that do not parse as a number, NaN, positive/negative infinity and negative values.
- Accept zero only if owner decides zero is technically allowed; it is non-negative but may be clinically implausible. Do not reject on clinical grounds in input validation.
- Keep decimal precision; do not silently round original input.
- Apply a documented unit profile, not a value-based unit guess.
- Use a configurable display label for units and include that profile in the analysis snapshot.

## 6. Exact fixture outcome categories

The source PDF remains local. Public documentation records only test numbers and categories.

| Test | Expected outcome | Explanation |
|---:|---|---|
| 1 | Accept | Valid syntax and past DOB |
| 2 | Reject | Malformed email |
| 3 | Accept | Unusual measurements are not syntax errors |
| 4 | Reject | Impossible calendar date |
| 5 | Accept | Valid input |
| 6 | Warn then accept if confirmed | Exact duplicate of test 1 |
| 7 | Accept | Valid input |
| 8 | Reject | Malformed email and future DOB |
| 9 | Accept | Valid calendar date; do not reject |
| 10 | Accept | Valid input |

## 7. Duplicate fingerprint

Exact duplicate detection occurs after field validation and before create/update:
- normalize name (trim + casefold);
- normalize DOB to ISO date;
- normalize email to lowercase trimmed form;
- normalize Decimal values without float conversion;
- include unit profile code.

Use a deterministic canonical representation and hash (e.g. SHA-256). A hash is a comparison key, not a substitute for comparing canonical values if a collision-safe check is desired.

On Create:
- `allow_duplicate=false`: return 409 and do not insert.
- confirmed repeat with `allow_duplicate=true`: insert distinct record.

On Update:
- compare against other records, excluding current patient ID.
- same confirmation workflow applies.
- `allow_duplicate` only bypasses duplicate warning, never other validation.

## 8. Assessment workflow counts

- Six non-duplicate valid rows.
- One explicitly confirmed duplicate.
- Three rejected.
- Seven persisted records after creation.
- Seven after email update.
- Six after deleting a different record.

## 9. Update validation and analysis invalidation

- Validate resultant complete record on PATCH.
- Name/email-only patch does not create a new analysis.
- DOB or measurement change creates a fresh analysis run.
- Keep old run and input snapshot.
- Never overwrite a prior analysis with the new result.

## 10. Clinical/provider response is not input validation

A numeric measurement can be valid input even if the provider returns `high`, `low`, `unknown`, or context-incompatible. Do not reject a record based on a TestWell flag.

If provider response reports `unitMismatch`, do not reinterpret the measurement; mark it context-limited or unavailable.

## 11. Test cases

Public automated tests use neutral synthetic values. The exact employer dataset is entered manually from the local PDF during the recording.

Test categories:
- valid email, malformed email and edge email syntax;
- dot and slash DOB formats;
- leap dates, invalid dates and runtime future date;
- numeric integer/decimal, blank, text, boolean, NaN, infinity and negative values;
- duplicate detection create and patch;
- explicit duplicate confirmation;
- measurement update re-analysis;
- name/email-only patch without re-analysis;
- all count invariants.
