# Repository Hygiene and Public Release Rules

**Version:** 0.2 — Owner-approved implementation baseline

## Never commit
- `.env`, `.env.*` except approved `.env.example`.
- SQLite DB, WAL/SHM, backups and test databases.
- `reference/` (original employer PDF).
- `private/`, `assessment-fixtures.local.*`.
- exact assessment names, emails, DOBs or numeric row data copied from employer PDF.
- raw TestWell responses if they contain the employer measurements.
- local Ollama logs, prompt dumps, local cache.
- screen recordings or screenshots showing private assessment entries.
- `test_ollama.py` until owner confirms purpose/path; normally keep temporary spike files outside repository.
- downloaded model weights.

## Suggested .gitignore patterns
```gitignore
.env
.env.*
!.env.example
*.db
*.sqlite
*.sqlite3
*.db-wal
*.db-shm
backend/data/
reference/
private/
assessment-fixtures.local.*
*.log
logs/
ollama-cache/
recordings/
screenshots/private/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
node_modules/
dist/
coverage/
```

Review this list against actual project structure before using it. Do not ignore public documentation or tests indiscriminately.

## Before first public push
1. Run `git status --short`.
2. Run a full tracked-file inventory.
3. Search files for common secret patterns.
4. Inspect `git log --all` and staged changes for secrets/private data.
5. Confirm source PDF, DB, fixture transcript, logs and video are not tracked.
6. Scan screenshots manually.
7. Verify README test data is neutral.
8. Confirm license and attribution notice for Llama.
