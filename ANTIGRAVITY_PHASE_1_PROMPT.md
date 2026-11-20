# ANTIGRAVITY — PHASE 1 IMPLEMENTATION PROMPT
## Repository and Development Foundation | Candidate 267

**Authorization:** The project owner has authorized Phase 1 only. Begin implementation now. Do not repeat a broad architecture review or request another approval for Phase 1.

The documents in `docs/` are the owner-approved v0.2 baseline. `reference/Task 2 - AI Growth Python Skills.pdf` is the employer's controlling requirement document and private local reference. Do not commit `reference/`.

## 1. Scope — Phase 1 only

Create the isolated Task 2 repository and a reproducible development foundation:

- Root structure with `backend/`, `frontend/`, `tests/`, `docs/`, and local `backend/data/` (data directory ignored by Git).
- Python backend project and virtual-environment instructions.
- FastAPI application entry point.
- `GET /api/v1/health` liveness endpoint.
- `GET /api/v1/ready` readiness endpoint with a clear implementation that does not pretend a database exists before Phase 2.
- React + TypeScript + Vite frontend shell with a minimal professional application frame and a real backend health/readiness connection.
- Pinned or bounded dependency versions and reproducible setup scripts.
- `.env.example`, `.gitignore`, formatter/linter/type-check/test configuration.
- Basic backend and frontend smoke tests.
- Root README with exact Windows PowerShell setup, run, test and stop commands.
- Ensure `reference/` is excluded from Git and not copied into public docs/tests.

## 2. Mandatory preflight

Before creating or changing files:

1. Confirm the current workspace is this extracted `Gokul_Task2_Health_Application` folder.
2. Confirm it is separate from PracticeSignal and the old `D:\Gokul-Task-2\Task-02` workspace.
3. Inspect current contents and preserve all supplied architecture documents and review records.
4. Search the old and new Task 2 workspace for `test_ollama.py`. Report exact path and inspect whether it contains only the neutral benchmark. Do not delete or move it. Ensure it is not accidentally included in the application repository.
5. Verify the original PDF remains in local `reference/` and is ignored by Git.
6. Check whether a Git repository already exists. Do not overwrite history or remote configuration. If the new folder is not a Git repository, initialize it only in this new folder and show the resulting status.

If the workspace is not the extracted package folder, stop and report the path mismatch rather than writing into PracticeSignal or the old project.

## 3. Technology baseline

- Python 3.11 or 3.12 (choose the installed compatible version and record it).
- FastAPI + Pydantic v2 + SQLAlchemy 2.x dependencies may be declared, but do not implement models or migrations in Phase 1.
- Uvicorn for local development; one worker.
- React + TypeScript + Vite.
- A small typed fetch client for backend health/readiness.

Do not add TestWell integration, Ollama calls, patient entities, CRUD endpoints, clinical rules or actual patient screens in Phase 1. Those belong to later phases.

## 4. Quality requirements

- Backend and frontend independently runnable.
- Environment-based configuration; never hardcode secrets.
- Minimal structured logs without patient data.
- Frontend handles backend-unavailable state cleanly.
- Small typed functions; no unnecessary abstractions or dependencies.
- No fake data, generic placeholders or generated-scaffolding clutter.
- Do not rewrite approved architecture documents. Record any unavoidable deviation in `docs/DECISION_LOG.md` with rationale.
- Do not claim a command passed unless it was executed.

## 5. Required validation

Run and report actual results for:
- Python version and dependency installation.
- Backend import/startup.
- Backend health and readiness endpoints.
- Backend tests.
- Python formatter/linter/type checks selected.
- Frontend dependency installation and production build.
- Frontend tests/typecheck/lint scripts.
- A smoke test proving frontend can reach backend health endpoint, where practical.
- Git status and tracked-file inventory confirming `reference/`, `.env`, DB files and local data are not tracked.

## 6. Phase 1 exit criteria

1. New project isolated from PracticeSignal and old workspace.
2. Backend and frontend start using documented commands.
3. Health/readiness endpoints behave as documented.
4. Frontend displays backend connectivity correctly.
5. Tests, build and quality checks have actual evidence.
6. No secrets or private reference data are tracked.
7. Windows setup instructions are reproducible.
8. No Phase 2+ functionality is implemented prematurely.

## 7. Completion report and stop

Update `PROJECT_STATUS.md` and report:
- Files created/modified.
- Exact dependency/runtime versions.
- Commands and actual results.
- Test/build/lint/type-check results.
- Git status and proof private `reference/` is untracked.
- `test_ollama.py` discovery result.
- Deviations and blockers.
- Phase 1 exit checklist and completion recommendation.

**Stop after Phase 1. Do not start Phase 2 automatically.**
