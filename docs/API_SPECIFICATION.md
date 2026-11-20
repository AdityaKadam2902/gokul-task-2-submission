# REST API Specification

**Version:** 0.2 — Owner-approved implementation baseline  
**Prefix:** `/api/v1`  
**Content type:** `application/json`

## 1. Common rules

- Pydantic request/response schemas are the contract authority.
- All timestamps are ISO 8601 UTC.
- DOB in API JSON is `YYYY-MM-DD`; UI entry accepts `dd/mm/yyyy` and fixture dot form; UI display uses `dd/mm/yyyy`.
- Decimal values are serialized as JSON numbers with documented precision.
- All error responses use the common envelope below.
- Patient create/update endpoints return before long-running analysis completes.
- No patient identifier is included in external-provider payload.

## 2. Error envelope

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "details": [
      {"field": "email", "code": "INVALID_EMAIL", "message": "Enter a valid email address."}
    ],
    "request_id": "uuid"
  }
}
```

## 3. Endpoints

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | `/health` | Process liveness | 200 |
| GET | `/ready` | DB and local config readiness (not necessarily live provider reachability) | 200/503 |
| GET | `/patients` | Paginated patient list | 200 |
| POST | `/patients` | Validate and create patient; schedule analysis | 201 |
| GET | `/patients/{patient_id}` | Patient detail + latest analysis | 200 |
| PATCH | `/patients/{patient_id}` | Update; maybe create new analysis run | 200 |
| DELETE | `/patients/{patient_id}` | Delete patient and history | 204 |
| GET | `/patients/{patient_id}/analyses` | Analysis history | 200 |
| GET | `/patients/{patient_id}/analyses/{analysis_id}` | Analysis run detail | 200 |
| POST | `/patients/{patient_id}/analyses` | Retry analysis using current stored values | 202 |
| GET | `/meta/analysis-statuses` | Canonical enum values for frontend | 200 |

## 4. Create patient

`POST /api/v1/patients`

Request:
```json
{
  "full_name": "Alex Example",
  "date_of_birth": "1990-04-28",
  "email": "alex@example.test",
  "glucose_value": 90.0,
  "haemoglobin_value": 14.0,
  "cholesterol_value": 180.0,
  "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
  "allow_duplicate": false
}
```

Headers:
- `Content-Type: application/json`
- `Idempotency-Key: <client-generated UUID>` (required for create if idempotency table is approved)

`allow_duplicate` is a control field, not stored in `patients`.

Responses:
- `201 Created`: patient and `PENDING` analysis-run resource created; body includes `patient` and `latest_analysis`.
- `409 Conflict`: exact duplicate found and `allow_duplicate=false`; response includes duplicate record ID and a confirmation message, but no row is created.
- `422 Unprocessable Entity`: validation failures.
- `503 Service Unavailable`: database unavailable; no patient row created.

Frontend polls patient detail or analysis detail until status is terminal. Do not keep the create request open while contacting TestWell or Ollama.

## 5. Read

`GET /api/v1/patients?page=1&page_size=20&search=...`

Return stable ordering by `created_at DESC, id DESC`, total count and items. Do not return the complete analysis payload in the list; include latest analysis status, short remark and updated timestamp.

`GET /api/v1/patients/{id}` returns all employer-required fields and the latest analysis summary.

`GET /api/v1/patients/{id}/analyses` returns newest-first history with provider/model/version provenance.

## 6. Update patient

`PATCH /api/v1/patients/{id}` accepts only fields being updated plus optional `allow_duplicate`.

Rules:
- Validate the resulting whole record, not only individual patch values.
- Duplicate check compares the proposed normalized record against other patients, excluding the current ID.
- If an exact duplicate is detected and not confirmed, return 409.
- Name/email-only update does not trigger analysis.
- DOB or any measurement change creates a new analysis row with an immutable numeric/unit snapshot and `PENDING`.
- Old analysis rows are retained.
- Patient update commits even if subsequent analysis fails.
- Return 200 with current record and latest analysis status.

## 7. Delete patient

`DELETE /api/v1/patients/{id}`:
- Require UI confirmation.
- Delete patient row and cascade its analysis history.
- Return 204.
- Unknown ID returns 404.

## 8. Retry analysis

`POST /api/v1/patients/{id}/analyses`:
- Creates a new analysis row from current persisted values.
- Does not overwrite a previous run.
- Returns 202 Accepted with analysis ID and `PENDING`.
- Do not run two concurrent analyses for the same patient snapshot unless a prior run is terminal.

## 9. Analysis response schema

The final response should include:

```json
{
  "id": "analysis-uuid",
  "patient_id": 12,
  "overall_status": "COMPLETED",
  "external_status": "SUCCEEDED",
  "ai_status": "SUCCEEDED",
  "provider": "testwell",
  "model": "llama3.2:3b",
  "remarks_text": "Educational summary generated from the external result and listed caveats.",
  "provider_observations": [
    {
      "analyte": "glucose",
      "value": 90.0,
      "unit": "mg/dL",
      "provider_flag": "normal",
      "range_text": "70–99 mg/dL",
      "range_qualifier": "age 18+, fasting",
      "context_status": "CONTEXT_NOT_CONFIRMED",
      "citations": [{"label": "Example source", "url": "https://example.org"}]
    }
  ],
  "caveat_codes": ["FASTING_STATUS_UNKNOWN", "UNIT_ASSUMPTION"],
  "created_at": "2026-11-18T07:00:00Z",
  "completed_at": "2026-11-18T07:00:03Z"
}
```

Illustrative structure only; example names and values are invented. Do not use these sample ranges as medical recommendations.

## 10. Status definitions

All status enums must exactly match database and frontend definitions. See `DATABASE_DESIGN.md`.

## 11. External API contract

TestWell request:
`POST https://www.test-well.com/api/agent/interpret_results`

Example body (invented test values):
```json
{
  "values": [
    {"marker": "glucose", "value": 90.0, "unit": "mg/dL"},
    {"marker": "hemoglobin", "value": 14.0, "unit": "g/dL"},
    {"marker": "total cholesterol", "value": 180.0, "unit": "mg/dL"}
  ]
}
```

Do not send `sex`, `age`, `pregnancy` or `postmenopausal`; the assignment does not provide them. Do not infer them. The response must be checked for `found`, `flag`, `unitMismatch`, `range.qualifier`, `suggests`, `retest`, citations and provider disclaimer.

If a returned qualifier requires missing context, preserve the provider flag but mark it context-limited. Do not display it as an unqualified patient-specific result.

## 12. HTTP status handling

- 400: invalid provider request/schema.
- 404: unknown route/record as relevant.
- 409: duplicate confirmation required or conflicting in-flight action.
- 422: application validation.
- 429: provider rate limit; store safe error and allow retry with backoff.
- 500: internal failure; do not expose stack traces.
- 502: invalid/unexpected upstream response.
- 503: provider/database/model dependency unavailable where endpoint readiness requires it.
- 504: upstream timeout, recorded on analysis run; the patient record remains.
