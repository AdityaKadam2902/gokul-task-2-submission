# User Interface Specification

**Version:** 0.2 — Owner-approved implementation baseline  
**Working product name:** LabInsight (provisional)

## 1. Design principles

- Clean, calm, professional healthcare-administration style.
- Prioritize task completion over decorative analytics.
- No red/green clinical status colour without an explicit label and caveat; provider flags are not diagnoses.
- Use readable tables, labels and clear error messages.
- Responsive down to common mobile width.
- Meet basic WCAG 2.2 AA-minded contrast, keyboard and label practices (not a certification claim).

## 2. Global shell

Header:
- LabInsight name.
- Subtitle: "Assessment prototype — educational use only".
- API status indicator (last known status; no constant background polling).
- Ollama status indicator.
- DB ready indicator.

Persistent notice:
"Do not use with real patient records. Assessment demo assumes units shown below. Numeric lab values are sent to TestWell after acknowledgement; identity fields are not sent."

## 3. Dashboard (`/`)

- Summary cards: total saved records, pending analyses, completed/degraded analyses.
- Primary action: Add record.
- Patient table:
  - Full name
  - DOB (`dd/mm/yyyy`)
  - Email
  - Glucose + unit
  - Haemoglobin + unit
  - Cholesterol + unit
  - Latest remarks/status
  - View/Edit/Delete actions
- Search by name/email and sort by creation time.
- Empty state with clear add-record action.
- Table columns remain usable on small screens through horizontal scrolling or responsive card layout.

## 4. Create/edit form

Fields:
- Full name.
- DOB, helper: `dd/mm/yyyy` (the employer fixtures use dot separators; both supported).
- Email.
- Glucose value and visible unit label.
- Haemoglobin value and visible unit label.
- Cholesterol value and visible unit label.

Validation:
- Inline per-field error.
- Summary error region for server validation.
- Do not clear valid user input when a different field fails.
- Submission button disabled while request is in flight.

## 5. Unit-profile and external-data acknowledgement

Before first TestWell transmission, show an acknowledgement modal/banner:
- Unit values are assessment assumptions, not specified in employer PDF.
- Numeric values and unit labels are sent to TestWell.
- Name, email, DOB and internal IDs are not sent.
- TestWell output is educational; provider says not diagnosis.
- Do not use real patient records.
- Buttons: "I understand — continue" and "Cancel".

If declined, save valid patient record with analysis `NOT_RUN`; provide an explicit retry after acknowledgement.

## 6. Duplicate confirmation

On 409:
- Show the possible duplicate match using internal record ID and selected safe details.
- Explain that the task includes an exact duplicate entry.
- Buttons: Cancel; Confirm and save second entry.
- Confirmation does not bypass field validation.
- Avoid displaying unnecessary sensitive information in logs.

## 7. Patient detail (`/patients/:id`)

Sections:
- Required record fields.
- Latest analysis status.
- Provider observations: flag, range, qualifier, context state, educational explanation and citations.
- Local AI-generated remarks as a separate card with model label.
- Caveats and unit assumption visible.
- Analysis history table with timestamp, provider/model and status.
- Actions: edit, retry analysis, delete.

Do not merge the provider response with the AI-written summary in a way that hides provenance.

## 8. Status vocabulary and badges

- `PENDING`: analysis running.
- `COMPLETED`: provider normalized + AI response passed validation.
- `DEGRADED`: provider information available but one part limited/fallback.
- `FAILED`: no usable analysis.
- `NOT_RUN`: not requested/declined.
- AI label: `AI Generated` only for actual validated Ollama response.
- Fallback label: `Template fallback — not AI-generated`.

Avoid using a badge alone; include accessible textual status.

## 9. Delete confirmation

Explicitly state that deleting the record also deletes its analysis history in this local assessment app. Require a second action to confirm.

## 10. Loading and failure states

- Patient save: immediate created response with pending indicator.
- Analysis: poll with bounded interval, stop after terminal state.
- TestWell failure: show reference service unavailable; no fabricated flags.
- Ollama failure: show provider observations with clearly labelled non-AI fallback.
- No match/unit mismatch/context missing: show the exact limitation.
- Empty list, slow network and retry states are designed explicitly.

## 11. Accessibility

- Every form control has a persistent label.
- Errors are text and programmatically associated with field.
- Dialogs trap/return focus correctly.
- Keyboard navigation for table actions.
- Do not rely on colour alone.
- Respect reduced-motion setting.
- Use meaningful button labels.
