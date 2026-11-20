# Engineering Standards

**Version:** 0.2 — Owner-approved implementation baseline

## Python/backend

- Python 3.12+ unless compatibility findings require another version.
- Type hints on public functions and service boundaries.
- Pydantic v2 schemas for every external/API boundary.
- SQLAlchemy 2.x typed declarative models.
- Keep routers thin; domain logic belongs in services.
- Provider adapters isolated behind interfaces.
- Use `Decimal` for numeric measurements.
- Explicit exceptions and typed error codes; no bare catch-all suppression.
- Structured logging with request/analysis ID; never log names, emails, DOB or full request bodies.
- One analysis-run state machine with transitions covered by unit tests.
- Pinned dependencies and lock file.

## Frontend

- TypeScript strict mode.
- API client layer separate from components.
- Shared API types aligned with backend Pydantic/OpenAPI contracts.
- Controlled forms and consistent validation.
- No unsafe HTML rendering of provider/model strings.
- Accessible labels, keyboard focus, confirmation dialogs and status text.
- Loading/error/empty states for every remote action.

## Naming and structure

- snake_case Python modules/functions/fields.
- PascalCase React components/types.
- UPPER_SNAKE_CASE constants.
- Clear separation among `api`, `schemas`, `models`, `services`, `providers`, `core` and tests.
- Avoid speculative abstraction and unnecessary generic frameworks.

## Error and logging policy

- User error message is understandable and does not leak stack traces.
- Provider error stored as bounded safe code/summary.
- Never log raw PII or full medical JSON payload.
- Use correlation IDs without embedding patient identifiers.
- Retry only transient errors; bounded attempts and backoff.

## Git and documentation

- Small focused commits per phase.
- No secrets, DB, raw fixture, source PDF, video or local logs in public repo.
- README setup tested from clean environment.
- Every architecture deviation enters `DECISION_LOG.md`.
- Project status reflects actual evidence, not intent.
- No phase marked complete without tests executed.

## AI-specific

- Version prompts and schemas.
- Pin model tag `llama3.2:3b`; record Ollama version.
- Use schema-constrained output where supported and verify Pydantic parsing.
- Treat model output as untrusted text.
- Model cannot invent source citations or numeric facts.
- Fallback explicitly labelled.
- Never store chain-of-thought.
