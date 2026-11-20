# Project Specification

**Version:** 0.2 — Draft for owner approval  
**Source of truth:** Employer's original Task 2 PDF (local, untracked reference)

## 1. Objective

Build a local web application using Python as the backend to manage contact/patient records containing the required identity and blood-test fields, perform CRUD operations, validate input, persist records, call an external health-related API using the entered measurements, and display AI-generated remarks.

The implementation must be explainable by the candidate during a technical interview. It must be modest in scope and reliable, not an overbuilt hospital system.

## 2. Employer-mandated fields

- Full Name
- Date of Birth
- Email Address
- Glucose
- Haemoglobin
- Cholesterol
- Remarks generated from AI

The UI must display the assigned fields. The database may include technical metadata required for provenance, processing status and history.

## 3. Functional requirements

### FR-01 — Create

Create a record from the required fields. Backend validation is authoritative. A valid record must persist even if an external service or local model subsequently fails; analysis failure must not erase the record.

### FR-02 — Read

Display all records and view a single record. Show the latest analysis state and remarks. Provide access to past analysis runs for traceability.

### FR-03 — Update

Update editable patient fields. An email-only or name-only change does not trigger another health analysis. A change to DOB or any measurement creates a new analysis run against a new immutable input snapshot. Previous runs are retained.

### FR-04 — Delete

Delete a selected record after explicit confirmation. For this assessment application, deleting a patient cascades to its analysis history. The confirmation UI must clearly state that deletion is permanent.

### FR-05 — Input validation

- Required non-empty name.
- Valid email syntax.
- DOB in `dd/mm/yyyy`; also accept `dd.mm.yyyy` because that is how the supplied fixtures are written.
- Reject impossible calendar dates and future DOBs using runtime date.
- Measurements must be finite numeric decimals and not negative.
- Numeric validity is distinct from a provider's clinical flag. Do not reject a valid numeric measurement because it is unusual.

### FR-06 — Duplicate handling

An exact normalized duplicate must produce a warning/confirmation workflow, not silent rejection. The user must explicitly confirm the second insert for the supplied duplicate fixture. No database unique constraint may prevent this required case.

### FR-07 — Persistence

Use SQLite with SQLAlchemy and Alembic. Enable SQLite foreign keys on every connection, use short transactions and keep database files out of Git.

### FR-08 — External health API

Call TestWell's public `POST /api/agent/interpret_results` endpoint with all three numeric measurements in one request, plus an explicitly approved measurement unit profile. Do not send name, email, DOB, internal patient ID or any other identifier. The API is an external health-related API, not a clinically validated predictor for this app.

### FR-09 — AI-generated remarks

Use local Ollama `llama3.2:3b` to generate a short, structured remark from the already-normalized TestWell result and explicit missing-context caveats. The model must not decide reference ranges, diagnose, invent probabilities, add treatments or fabricate citations. The application must preserve the exact provider output and source links separately from the AI paraphrase.

### FR-10 — Honest analysis states

The UI distinguishes pending, completed, degraded, failed and not-run analysis. A deterministic fallback must never be labelled AI-generated.

### FR-11 — External disclosure acknowledgement

Before the first external analysis in a local session, show and record an acknowledgement explaining that analyte values and units will be sent over HTTPS to TestWell, and that names, email addresses, DOB and internal IDs are not included. The user can decline; in that case the patient record remains saved with analysis `NOT_RUN` and can be retried after acknowledgement.

### FR-12 — Assessment sequence

Use the exact employer fixture values manually from the local PDF:
1. Attempt all ten entries unmodified.
2. Reject the invalid cases with clear errors.
3. Warn and request confirmation for the exact duplicate.
4. Show seven persisted records.
5. Change one saved email to `gokul@infocare.com`.
6. Delete a different record.
7. Show the remaining six records.

## 4. Analysis interpretation contract

The application is not permitted to silently choose or infer:
- Units from values alone.
- Fasting/random/post-meal context.
- Biological sex.
- Age at specimen collection.
- Whether cholesterol means total, HDL, LDL or another fraction.
- Lab-specific reference intervals.

The proposed assessment demo profile is:
- Glucose: mg/dL.
- Haemoglobin: g/dL.
- Total cholesterol: mg/dL.

This is a **proposed explicit assumption**, not a fact from the PDF. It must be visibly labelled and approved by the project owner before Phase 4A. The UI must allow the operator to see the profile. If this assumption is not approved, no provider classification may be treated as applicable.

TestWell may return qualifiers such as "fasting" or "male, age 18+". A returned flag must be labelled `PROVIDER_REPORTED_CONTEXT_LIMITED` whenever a required qualifier is not supplied by the assessment. Do not convert such a flag into a definitive patient-specific condition.

## 5. Non-functional requirements

- Maintainable modular monolith.
- Clear Pydantic contracts and generated OpenAPI docs.
- Reliable error handling and short database transactions.
- No credentials committed to Git.
- No exact assessment data committed to public Git.
- No health values sent to hosted LLMs.
- Accessible labels, keyboard-operable controls and clear validation.
- Local reproducible setup.
- Unit and integration tests do not require live network or Ollama.
- A separate live smoke test proves external and local AI integrations.

## 6. Out of scope

- Diagnosis, treatment, prescription or emergency triage.
- Clinical decision support or validated disease-probability scores.
- Medical-device certification or claims of regulatory compliance.
- Real clinic integration or real patient records.
- Authentication, multi-tenancy or production cloud deployment.
- Automated scraping, outreach or unrelated business features.
- Training/fine-tuning a model on the ten assessment records.
