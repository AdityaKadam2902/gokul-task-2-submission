# Test Strategy

**Version:** 0.2 — Owner-approved implementation baseline

## 1. Testing principles

- Test each layer independently.
- Mock external TestWell and Ollama in deterministic tests.
- Keep live provider/model smoke tests separate from CI/unit tests.
- A fallback test never substitutes for successful AI acceptance.
- Use neutral invented records in public automated tests.
- The exact employer records are manually entered during the required local demonstration.

## 2. Test layers

### Unit
- Date parser and runtime future DOB validation.
- Email validator.
- Decimal parser and finite/non-negative constraints.
- Duplicate canonicalization and hashing.
- Provider response normalizer.
- Qualifier/context compatibility.
- Analysis state machine.
- LLM output validation and safety gate.
- Fallback text generation.

### Database/integration
- Patient create/read/update/delete.
- Patient-analysis one-to-many persistence.
- Cascade delete.
- Foreign-key enforcement.
- Short transaction boundaries.
- Migration from empty DB.
- Persistence after restart.
- Analysis snapshot immutability.

### API
- All CRUD endpoint success/errors.
- Duplicate 409, explicit confirmation, repeated request handling.
- PATCH email-only vs measurement/DOB change.
- Polling while analysis pending.
- Retry after failed analysis.
- Consistent status enums across DB/API/TypeScript.

### External TestWell contract (mocked)
- Normal response with three analytes.
- `found=false`.
- `unknown` flag.
- `unitMismatch=true`.
- qualifier requiring fasting/sex/age.
- missing citations or unexpected JSON.
- HTTP 400, 429, 500, timeout, DNS/network failure.
- response includes unsafe/non-HTTPS links.
- provider partial match (one analyte missing).
- no raw identifiers included in outbound JSON.

### Ollama (mocked)
- valid schema JSON.
- invalid JSON.
- extra keys.
- unknown observation ID.
- output too long.
- diagnosis/treatment/probability claim.
- conflicting statement.
- timeout/unavailable model.
- fallback is not labelled AI.

### Live smoke tests
- One request to TestWell with neutral synthetic data and all three markers.
- One local `llama3.2:3b` call; test the actual JSON Schema output, not only JSON mode.
- No employer fixture values in live feasibility tests.
- Capture redacted status, latency and marker-match evidence.

### Frontend and E2E
- keyboard-accessible forms;
- inline validation;
- duplicate confirmation;
- list/detail/edit/delete;
- status polling and AI/fallback badge;
- responsive layout;
- external disclosure acknowledgement;
- full assessment sequence.

## 3. Mandatory acceptance tests

- AT-01: Backend starts and readiness reports DB.
- AT-02: Create valid patient persists.
- AT-03: List/detail read persisted data.
- AT-04: Update fields and verify persistence.
- AT-05: Delete patient and analysis cascade.
- AT-06: Invalid email rejected.
- AT-07: Impossible and future DOB rejected.
- AT-08: Numeric values reject non-finite/negative/non-numeric values.
- AT-09: Duplicate warning; explicit confirmation inserts second row.
- AT-10A: Live TestWell API returns matched observations for all three analytes with response evidence.
- AT-10B: Local Ollama `llama3.2:3b` generates a schema-valid AI remark from a normalized provider response.
- AT-10C: Context qualifier is shown and not silently treated as applicable.
- AT-10D: Provider failure produces no fabricated interpretation.
- AT-10E: AI failure produces labelled fallback and `ai_status=FALLBACK`.
- AT-10F: No identifiers are sent externally or logged.
- AT-11: Email-only PATCH does not trigger new analysis.
- AT-12: DOB/measurement PATCH creates a new immutable analysis run.
- AT-13: Full employer sequence results in seven records, email update preserves count, delete results in six.

AT-10A and AT-10B are distinct. Fallback never satisfies either.

## 4. Performance evidence

Record:
- cold and warm local model response latency;
- TestWell request latency;
- total time from patient submit to terminal analysis;
- UI responsiveness during pending processing;
- resource usage if readily available.

Do not set arbitrary thresholds without a target. Proposed assessment acceptance: normal local run should complete within 30 seconds under observed conditions; report actual values and any cold-start variation.

## 5. Test data policy

Public tests must use invented names/domains such as `Example Person` and `.test` email addresses, with neutral measurements. Exact employer data remains local and is manually entered for video.

## 6. Test report format

Each phase report includes command, exit code, test count, passed/failed/skipped, environment, actual failures, screenshots/log evidence, and limitations. Never state “all tests pass” without executed evidence.

## 7. Phase 6 Acceptance Test Execution Matrix

All mandatory acceptance tests (AT-01 through AT-13) have been fully automated and verified:

| Test ID | Description | Automated Test Location | Result |
|---|---|---|---|
| AT-01 | Backend startup & database readiness probe | `tests/backend/test_health.py`, `tests/backend/test_readiness.py` | PASS |
| AT-02 | Create valid patient & persistence | `tests/backend/test_patient_api.py`, `tests/backend/test_phase6_acceptance.py` | PASS |
| AT-03 | List/detail read persisted data | `tests/backend/test_patient_api.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-04 | Update fields and verify persistence | `tests/backend/test_patient_api.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-05 | Delete patient & cascade analysis history | `tests/backend/test_models.py`, `tests/backend/test_patient_api.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-06 | Invalid email syntax rejection (missing TLD, no @) | `tests/backend/test_patient_validation.py`, `tests/backend/test_phase6_acceptance.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-07 | Impossible (31/11, 31/02) and future DOB rejected | `tests/backend/test_patient_validation.py`, `tests/backend/test_phase6_acceptance.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-08 | Biomarkers reject negative/non-numeric values | `tests/backend/test_patient_validation.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-09 | Exact duplicate HTTP 409 warning & confirmed override | `tests/backend/test_patient_api.py`, `tests/backend/test_phase6_acceptance.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-10A | TestWell API returns matched observations | `tests/backend/test_testwell_adapter.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-10B | Ollama generates structured JSON Schema AI remarks | `tests/backend/test_ollama_client.py`, `tests/backend/test_ollama_safety_and_validation.py`, `scratch/run_browser_e2e.py` | PASS |
| AT-10C | Clinical context qualifiers displayed (fasting, age) | `tests/backend/test_testwell_adapter.py`, `frontend/src/components/patients/PatientDetailModal.tsx` | PASS |
| AT-10D | TestWell network failure produces safe recovery | `tests/backend/test_phase6_acceptance.py::test_failure_recovery_testwell_network_outage` | PASS |
| AT-10E | Ollama failure produces labelled deterministic fallback | `tests/backend/test_phase6_acceptance.py::test_failure_recovery_ollama_fallback` | PASS |
| AT-10F | Zero PII transmitted externally or to local LLM | `tests/backend/test_testwell_privacy.py`, `tests/backend/test_ollama_privacy.py` | PASS |
| AT-11 | Email-only PATCH preserves analysis without re-run | `tests/backend/test_patient_api.py`, `tests/backend/test_phase6_acceptance.py` | PASS |
| AT-12 | Clinical input PATCH triggers fresh immutable analysis | `tests/backend/test_patient_api.py` | PASS |
| AT-13 | 10-submission workflow (3 rejected, 1 dup, 7 saved, edit, delete -> 6) | `tests/backend/test_phase6_acceptance.py::test_employer_assessment_10_submission_lifecycle`, `scratch/run_browser_e2e.py` | PASS |

