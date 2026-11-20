# Architecture Decision Log

**Version:** 0.2 — Owner-approved implementation baseline

| ID | Decision | Status | Reason / consequence |
|---|---|---|---|
| ADR-001 | Use a modular monolith | PROPOSED | Small assessment; avoids distributed infrastructure |
| ADR-002 | FastAPI + Pydantic v2 | PROPOSED | Clear Python REST contract and validation |
| ADR-003 | React + TypeScript + Vite | PROPOSED | Suitable responsive UI and typed API client |
| ADR-004 | SQLite + SQLAlchemy + Alembic | PROPOSED | Local persistent store; simple reproducible demo |
| ADR-005 | Separate `patients` and `patient_analyses` | PROPOSED | Preserve analysis history and provenance |
| ADR-006 | TestWell `interpret_results` primary external health API | CONDITIONAL | Phase 0.3 reported three-marker successful smoke test; educational only |
| ADR-007 | MedlinePlus Connect is not the primary value interpreter | ACCEPTED FOR 0.2 | It retrieves generic content by code, not patient numeric results |
| ADR-008 | Local Ollama `llama3.2:3b` for remarks | CONDITIONAL | Already installed and benchmarked on target machine |
| ADR-009 | No hosted generative LLM | PROPOSED | Minimize health data disclosure and avoid provider-use restrictions |
| ADR-010 | Use only provider facts; no local disease thresholds | PROPOSED | Avoid unsupported clinical algorithm |
| ADR-011 | Units are an owner-approved explicit assumption | OPEN | Source PDF does not state units |
| ADR-012 | Do not infer age-at-draw, sex or fasting state | ACCEPTED FOR 0.2 | Source task omits specimen date and context |
| ADR-013 | Surface TestWell range qualifiers and context mismatch | PROPOSED | API defaults can be context-specific |
| ADR-014 | In-process FastAPI background task for this demo | PROPOSED | Returns immediately; suitable modest workload; not durable |
| ADR-015 | Short DB transactions; external calls outside transactions | ACCEPTED FOR 0.2 | Prevent lock contention and long-held writes |
| ADR-016 | Create and retain immutable analysis-run history | PROPOSED | Retries and changes do not overwrite provenance |
| ADR-017 | Allow duplicate after explicit confirmation | REQUIRED | Employer's test fixture includes exact duplicate |
| ADR-018 | Keep exact employer fixtures local/untracked | REQUIRED | Employer does not classify records as synthetic |
| ADR-019 | Require external data-flow acknowledgement | PROPOSED | Values are transmitted to a third-party service |
| ADR-020 | Use consistent analysis status enums | PROPOSED | Avoid DB/API/frontend mismatch |
| ADR-021 | Pin local model identifier; document Llama license | PROPOSED | Reproducibility and attribution |
| ADR-022 | No model-generated citations or independent clinical thresholds | PROPOSED | Prevent fabricated provenance/unsupported medical statements |

## Change control

Each accepted architecture change must identify the old decision, new decision, evidence, impacted documents, migration/API implications and owner approval date.
