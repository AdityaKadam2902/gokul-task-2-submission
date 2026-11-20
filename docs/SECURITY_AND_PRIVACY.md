# Security and Privacy Specification

**Version:** 0.2 — Owner-approved implementation baseline

## 1. Data classification

The employer's PDF contains names, email addresses, DOBs and blood-test values. The employer does not state that they are synthetic. Treat the records as **potentially identifiable health-related assessment data**. Do not assert that they are synthetic.

## 2. Local-only records and repository boundary

Keep the following local and untracked:
- Original employer Task 2 PDF.
- Any exact transcription/CSV of employer entries.
- Local SQLite database and backups.
- Local videos/screenshots containing employer fixture records, unless the employer explicitly expects and authorizes their sharing.
- TestWell/Ollama request/response captures containing real assessment values.

Public repository may contain:
- neutral synthetic examples;
- redacted logs;
- schema examples with invented values;
- generic tests for email/date/duplicate/CRUD behaviour;
- screenshots using neutral sample records.

## 3. External TestWell data transfer

The selected API is a third-party service. The app sends only:
- analyte labels;
- numeric values;
- explicitly selected units.

Never send name, email, DOB, patient ID, analysis ID or other identifiers. Do not pass the entire Pydantic patient object to the HTTP client; construct the outbound body using an explicit allowlisted serializer.

Require a one-time acknowledgement in the UI:
“Lab values and units will be sent over HTTPS to TestWell for educational reference interpretation. Patient name, email, date of birth and internal record identifiers are not sent. Do not use this prototype with real patient records.”

TestWell's privacy policy states that results-explainer values are not logged. This is a provider claim; the project does not independently verify its logs, infrastructure, retention controls or security. Do not state “no data leaves the machine”.

## 4. Local LLM boundary

- Ollama endpoint must bind to loopback (`127.0.0.1`) for local use.
- Do not expose Ollama port on LAN/public interfaces.
- Do not use a hosted model as a fallback.
- Never send identity fields to Ollama unnecessarily; use a numeric/provider payload only.
- Do not log full prompts or model output by default; store only the validated final remark and provenance needed for demo.
- Keep prompt and model versions in analysis metadata.

## 5. Secrets and configuration

- `.env` and `.env.local` ignored by Git.
- `.env.example` contains placeholders only.
- No hardcoded credentials.
- TestWell public endpoint does not require an API key according to its current documentation; do not invent one.
- If future provider authentication is added, use environment variables and never commit secrets.

## 6. API and browser security

- Bind local API to localhost for assessment.
- CORS allow only the Vite local origin(s) used in development.
- Limit request body size and field lengths.
- Use Pydantic validation and parameterized ORM operations.
- Escape user-controlled text in frontend rendering; do not use raw HTML for AI remarks.
- Restrict rendered citation URLs to HTTPS. Use safe external link attributes.
- Do not expose stack traces or provider raw exception text to UI.
- Add request IDs to internal errors.
- Do not log raw blood values unless needed for local debug and explicitly redacted; prefer analysis IDs and status.

## 7. Deletion and persistence

Patient deletion cascades to analysis history for this single-user demo. Explain permanent deletion. Local DB file is not committed to Git. SQLite WAL/SHM files also ignored.

## 8. Security verification before submission

- Inspect `.gitignore`.
- Run secret scanning.
- Search Git history for credentials, not only current files.
- Verify `.env`, `.db`, raw fixtures, raw reports and recordings are not tracked.
- Verify app/API logs contain no names, emails, DOB or outbound raw payload.
- Verify TestWell request builder sends only allowlisted fields.
- Verify Ollama binds only to loopback.
- Confirm public repository examples are neutral and invented.

This prototype does not claim HIPAA compliance, Australian Privacy Act compliance, clinical governance approval or medical-device compliance.
