# Database Design

**Version:** 0.2 — Owner-approved implementation baseline  
**Database:** SQLite  
**ORM:** SQLAlchemy 2.x  
**Migrations:** Alembic

## 1. Design principles

- Separate current patient/contact data from immutable analysis-run history.
- Do not enforce unique email or unique patient identity; the employer requires a confirmed duplicate row.
- Preserve exact submitted measurement precision using `Decimal`.
- Do not store dates of birth as timestamps.
- Do not store patient identifiers in provider request snapshots.
- Enable SQLite foreign keys on every connection.
- Keep transactions short; no network/model call inside a transaction.

## 2. Table: `patients`

| Column | Type | Rules |
|---|---|---|
| `id` | Integer PK | Auto increment |
| `full_name` | String(120) | Required, trimmed |
| `date_of_birth` | Date | Required, actual date |
| `email` | String(254) | Required, validated syntax; not unique |
| `glucose_value` | Numeric(10,3) | Required, finite, >= 0 |
| `haemoglobin_value` | Numeric(10,3) | Required, finite, >= 0 |
| `cholesterol_value` | Numeric(10,3) | Required, finite, >= 0 |
| `unit_profile_code` | String(40) | Required; approved profile ID, not inferred |
| `created_at` | UTC DateTime | Required |
| `updated_at` | UTC DateTime | Required |

The exact measurement-unit fields are resolved by the selected `unit_profile_code`. Versioned profiles live in application configuration and are copied into each analysis input snapshot. This prevents historical analysis from changing if the default profile changes later.

## 3. Table: `patient_analyses`

One row represents one analysis attempt. New analysis runs are inserted on creation, retry, or clinically relevant input update. Prior runs are not overwritten.

| Column | Type | Rules |
|---|---|---|
| `id` | UUID/String PK | Unique analysis ID |
| `patient_id` | FK -> patients.id | Required, `ON DELETE CASCADE` |
| `run_number` | Integer | Sequential per patient |
| `input_snapshot_json` | JSON text | Only numeric values, analyte names, unit profile/version; no name/email/DOB |
| `external_provider` | String(60) | e.g. `testwell` |
| `external_api_version` | String(40) | Captured when known |
| `external_status` | Enum string | `PENDING`, `SUCCEEDED`, `NO_MATCH`, `FAILED`, `NOT_RUN` |
| `external_result_json` | JSON text nullable | Sanitized provider result; validate before storing |
| `ai_provider` | String(40) nullable | `ollama` |
| `ai_model` | String(80) nullable | `llama3.2:3b` |
| `ai_status` | Enum string | `PENDING`, `SUCCEEDED`, `FALLBACK`, `FAILED`, `NOT_RUN` |
| `ai_result_json` | JSON text nullable | Validated local model output only |
| `remarks_text` | Text nullable | Final remarks, clearly status-labelled |
| `overall_status` | Enum string | `PENDING`, `COMPLETED`, `DEGRADED`, `FAILED`, `NOT_RUN` |
| `ruleset_version` | String(40) nullable | `provider-normalizer-vN`; no disease-threshold rule set |
| `prompt_version` | String(40) nullable | AI instruction template version |
| `error_code` | String(80) nullable | Safe machine-readable code |
| `error_summary` | String(300) nullable | Redacted, user-safe summary |
| `created_at` | UTC DateTime | Required |
| `started_at` | UTC DateTime nullable | When worker starts |
| `completed_at` | UTC DateTime nullable | On terminal state |
| `retry_of_id` | FK nullable | Previous analysis row, if retry |

Unique constraint: (`patient_id`, `run_number`). Indexes: (`patient_id`, `created_at`), (`overall_status`, `created_at`).

## 4. Optional idempotency table

`idempotency_records` is recommended if implemented in Phase 3:
- `idempotency_key` string primary key.
- `resource_id` patient ID.
- `response_status` integer.
- `created_at` timestamp.

Only successful create actions store a key. A replay with the same key returns the original resource. A confirmed duplicate submission uses the same key if no row was committed on the first 409 response. If implementation complexity is disproportionate, form submit locking plus a server-side request token may be proposed as an ADR before code.

## 5. Status vocabulary

Keep identical enums in SQLAlchemy, Pydantic and TypeScript.

`external_status`:
- `PENDING`
- `SUCCEEDED`
- `NO_MATCH`
- `FAILED`
- `NOT_RUN`

`ai_status`:
- `PENDING`
- `SUCCEEDED`
- `FALLBACK`
- `FAILED`
- `NOT_RUN`

`overall_status`:
- `PENDING`
- `COMPLETED`
- `DEGRADED`
- `FAILED`
- `NOT_RUN`

Meaning:
- `COMPLETED`: TestWell response normalized and local LLM remark passed validation.
- `DEGRADED`: a usable external response exists but the AI generator used deterministic fallback, or one non-critical analyte could not be matched.
- `FAILED`: no usable analysis result was produced.
- `NOT_RUN`: operator declined external transmission or no run has been requested.
- `PENDING`: analysis queued/in progress.

A fallback must never be represented as `ai_status=SUCCEEDED`.

## 6. Relationships and delete behaviour

- `Patient` has many `PatientAnalysis` rows.
- Deleting a patient cascades to its analysis history.
- Do not hard-delete an analysis run independently through the public API.
- Patient detail returns the latest analysis summary; a history endpoint returns all runs.

## 7. SQLite setup requirements

- `PRAGMA foreign_keys=ON` on every connection.
- `PRAGMA journal_mode=WAL` after verifying the environment supports it.
- Bounded busy timeout, proposed 5000 ms.
- `check_same_thread=False` where required by the selected SQLAlchemy SQLite driver setup.
- One Uvicorn worker for the local assessment application.
- Database file under `backend/data/` and ignored by Git.
- Never hold a write transaction open while waiting for TestWell or Ollama.

SQLAlchemy's SQLite docs explicitly note that foreign key enforcement requires the `PRAGMA foreign_keys=ON` setting on connections. See [SQLAlchemy SQLite dialect](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html).

## 8. Migration policy

- Use Alembic from the first schema version.
- Never edit an already-applied migration to change schema history.
- Test upgrade from empty database and migration rollback where supported.
- Keep test databases isolated under temporary paths.
