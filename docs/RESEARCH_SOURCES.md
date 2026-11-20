# Research Sources and Evidence Register

**Reviewed:** 18 November 2026  
**Rule:** distinguish provider claims from independently executed checks.

## Employer source
- Original Task 2 PDF supplied in this conversation. It is the controlling requirements source and must remain local/untracked.

## TestWell provider documentation
- Developers: https://www.test-well.com/developers
- OpenAPI 3.1 specification: https://www.test-well.com/openapi.json
- Privacy policy: https://www.test-well.com/privacy
- Terms of Service: https://www.test-well.com/terms
- About: https://www.test-well.com/about
- Editorial policy: https://www.test-well.com/editorial-policy

Provider statements to treat as claims:
- public developer endpoint/no API key;
- 120 requests/minute/IP;
- physician-reviewed education content;
- no logging/storage of result values in the results-explainer endpoint;
- medical reviewer and reference review process.
The project has not independently audited provider infrastructure, storage, credentials, licence or clinical governance.

## TestWell Phase 0.3 smoke-test evidence
Antigravity reported a live neutral request to `POST /api/agent/interpret_results` with three invented markers, HTTP 200, 786 ms and 3/3 markers matched. Reported response included flags, reference qualifiers and citations. The report is an environment-generated result, not independently repeated here. Preserve the raw report locally; do not commit it if it includes workstation paths or user account details.

## Ollama
- Model page: https://ollama.com/library/llama3.2:3b
- Structured output guidance: https://ollama.com/blog/structured-outputs
- API reference: https://github.com/ollama/ollama/blob/main/docs/api.md
- Meta Llama materials/licence: https://www.llama.com/llama-downloads/

Phase 0.3 reported Ollama 0.40.16, `llama3.2:3b` installed and local inference successful. JSON mode was tested; JSON-Schema constrained output still needs app-specific verification.

## FastAPI and SQLAlchemy
- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- FastAPI async/concurrency: https://fastapi.tiangolo.com/async/
- SQLAlchemy SQLite dialect and foreign key behaviour: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html

## Evidence categories
- `EMPLOYER_SOURCE`: original PDF.
- `PROVIDER_PUBLISHED`: TestWell/Ollama vendor statements.
- `OFFICIAL_DOCS`: FastAPI/SQLAlchemy/Ollama/Meta documentation.
- `ENVIRONMENT_REPORT`: Antigravity's Phase 0.3 measurements.
- `PROJECT_DECISION`: proposed architecture decision awaiting owner approval.

## Explicit limitations
- No independent TestWell security audit.
- No clinical validation of provider output for Australian population/lab context.
- No verification that provider's no-logging statement matches production logs.
- No live TestWell request executed by this document authoring process.
- No repeat benchmark of Ollama on the candidate's physical machine.
