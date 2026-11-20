# Implementation Roadmap

**Version:** 0.2 — Owner-approved execution baseline  
**Rule:** one phase at a time. Phase 1 is authorized; each later phase requires explicit owner authorization.

## Phase 0.4 — Owner baseline approval
**Status: COMPLETE (18 November 2026).** Approved assumptions are recorded in `OPEN_DECISIONS.md`. No further broad review cycle is required before starting Phase 1. Concrete blockers discovered during implementation must be raised as focused findings.

## Phase 1 — Repository and development foundation
- Create/verify separate Task 2 repo; do not touch PracticeSignal.
- Python virtual environment and pinned dependencies.
- Frontend package and pinned dependencies.
- `backend/app`, `frontend/src`, `docs`, `tests`, local `data` structure.
- `.env.example`, `.gitignore`, formatter/linter/type config.
- Health endpoint only; no patient feature.
- README setup steps.
**Exit:** clean install/start/stop, formatting/lint baseline, no secrets or private references tracked.

## Phase 2 — Domain and persistence
- SQLAlchemy models: Patient, PatientAnalysis, optional IdempotencyRecord.
- SQLite engine configuration and FK/WAL.
- Alembic initial migration.
- Repository/service layer.
- Session/transaction tests.
- Cascade delete and restart persistence.
**Exit:** schema and DB tests pass; no provider or AI integration yet.

## Phase 3 — Validation and CRUD API
- Pydantic schemas.
- Strict date/email/numeric validation.
- Duplicate fingerprint and confirmation flow.
- CRUD endpoints.
- PATCH invalidation rules.
- Consistent API error envelope/status enums.
- Idempotency key or equivalent server-side replay protection, as specified in the approved owner decisions.
**Exit:** all backend API and validation tests pass with neutral fixtures. No external calls or Ollama yet.

## Phase 4A — TestWell integration and normalization
- Typed provider client.
- One combined three-marker POST.
- Timeouts and retry/backoff for 429/transient errors.
- Parse `found`, `flag`, `unitMismatch`, `range.qualifier`, `suggests`, `retest`, citations and links.
- Context mismatch handling.
- Outbound allowlist/privacy tests.
- Mocked contract tests + controlled live smoke test.
**Exit:** AT-10A and provider contract suite pass. Do not add LLM yet.

## Phase 4B — Local AI remarks
- Ollama adapter pinned to `llama3.2:3b`.
- Versioned prompt and Pydantic/JSON Schema response.
- Output schema and policy validation.
- No identity fields to prompt.
- Safe deterministic fallback.
- Retry and analysis history.
- Live local inference tests.
**Exit:** AT-10B, AT-10E and fallback tests pass. Fallback cannot be presented as AI.

## Phase 5 — Frontend
- Dashboard, patient list/detail, create/edit forms.
- Validation and duplicate dialog.
- Delete confirmation.
- Analysis status polling and history view.
- Provider flags/qualifiers/citations and AI remarks rendered separately.
- External data acknowledgement.
- Accessibility/responsive pass.
**Exit:** frontend tests and complete workflow with mocked services pass.

## Phase 6 — End-to-end acceptance and hardening
- Run all tests.
- Verify all ten employer records manually from local PDF.
- Seven rows after create sequence; email edit; delete different row; six final.
- Test real TestWell and local Ollama with neutral data first; then only exact employer sample values if owner approved external transmission.
- Inspect UI/API logs for data minimization.
- Run security checks and regression suite.
**Exit:** all required acceptance tests pass; video script reflects actual behaviour.

## Phase 7 — Release and submission
- README and screenshots using neutral data.
- Secret scan and Git history review.
- Confirm no PDF, exact raw fixtures, DB, `.env` or raw logs are committed.
- GitHub source uploaded.
- Record app demo and code walkthrough.
- Validate video link permissions.
- Candidate details table completed truthfully.
- One email with candidate information, repo link and video.
**Exit:** submission package verified and ready to send.

## Phase gates

- Do not pre-implement features from later phases.
- A phase may be reopened to fix defects.
- Antigravity must return a phase report and stop.
- Any architecture deviation requires an ADR and owner approval before code changes.
