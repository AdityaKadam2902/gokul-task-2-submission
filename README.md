# LabInsight — Patient Health Record & Biomarker Reference System
## Gokul Infocare Pty Ltd — AI Growth & Automation Associate — Task 2

**Candidate Number:** 267  
**Working Application Name:** LabInsight  
**Engineering Baseline:** Blueprint v0.2 — Phased Implementation Model  
**Implementation Status:** **Phase 7 Complete — Release & Submission Ready**  

---

## 1. Project Overview & Assessment Scope

**LabInsight** is a reliable, full-stack patient health-record management and educational biomarker reference application built for the Gokul Infocare Task 2 assessment.

The application allows health professionals and clinical administrators to:
1. **Manage Patient Profiles:** Create, read, update, and delete patient records containing identity fields (full name, date of birth, email) and three numerical blood biomarkers (Glucose, Haemoglobin, Total Cholesterol).
2. **Enforce Multi-Tier Validation:** Authoritatively validate demographic and clinical inputs across frontend and backend, rejecting malformed emails, impossible calendar dates (e.g., 31/02 or 31/11), future dates of birth, and negative or non-numeric biomarker values.
3. **Detect Exact Duplicates (HTTP 409):** Detect exact record collisions using canonical SHA-256 fingerprinting, issue explicit conflict warnings, and allow authorized duplicates upon user confirmation (`allow_duplicate=true`).
4. **Integrate External Health Interpretation (TestWell):** Transmit anonymous numerical biomarker values and unit profiles over HTTPS to the external TestWell reference catalog to retrieve qualitative flags, provider reference ranges, and educational citations.
5. **Generate Local AI Remarks (Ollama `llama3.2:3b`):** Synthesize normalized provider observations into plain-language educational summaries using a locally hosted Ollama model with structured JSON Schema output, strict clinical guardrails, and deterministic provider fallback.
6. **Support the Employer Assessment Sequence:** Successfully execute the 10 assessment submissions from the employer specification (3 rejected, 1 confirmed duplicate, 7 persisted), update a record's email to `gokul@infocare.com`, and delete a different record to leave exactly 6 records.

> [!IMPORTANT]
> **Educational Prototype Notice:** LabInsight is an educational assessment prototype, not a certified Medical Device Software (SaMD) or clinical diagnostic system. Results do not constitute a medical diagnosis, clinical evaluation, or treatment plan.

---

## 2. System Architecture & Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 + TypeScript UI                        │
│   (Vite, Tailwind CSS, Lucide Icons, Responsive Layout 375px–1280px)   │
└──────────────────┬───────────────────────────────────▲─────────────────┘
                   │ HTTP / JSON REST                  │ Polling / Toasts
                   ▼                                   │
┌────────────────────────────────────────────────────────────────────────┐
│                        Python FastAPI Backend                          │
│   (Pydantic v2 validation, Structured Error Envelopes, UUID Analysis)  │
└─────────┬──────────────────────┬───────────────────────────────┬───────┘
          │                      │                               │
          ▼                      ▼                               ▼
┌──────────────────┐  ┌─────────────────────────┐  ┌─────────────────────┐
│  SQLite Database │  │   External TestWell     │  │     Local Ollama    │
│  (WAL Mode, FKs, │  │   Reference API         │  │     llama3.2:3b     │
│  Alembic Schema) │  │   (Anonymous HTTPS)     │  │     (Local HTTP)    │
└──────────────────┘  └─────────────────────────┘  └─────────────────────┘
```

### Data Flow & Isolation Architecture
1. **Intake & Validation:** Incoming requests are validated against strict Pydantic schemas. Invalid calendar dates, leap-year anomalies, future dates of birth, and malformed emails are rejected with descriptive HTTP 422 envelopes.
2. **Duplicate Fingerprinting:** A SHA-256 hash is computed from normalized name, ISO date, lowercased email, and fixed 3-decimal biomarker values. If matched and `allow_duplicate` is false, an HTTP 409 Conflict is returned with existing record metadata.
3. **External Dissemination (TestWell):** After explicit user disclosure, **only** the numerical readings (`glucose_value`, `haemoglobin_value`, `cholesterol_value`) and unit profile (`ASSESSMENT_CONVENTIONAL_V1`) are sent to TestWell. Full names, email addresses, dates of birth, and internal database IDs are strictly excluded.
4. **Context Normalization:** Provider ranges are mapped to domain models. Because clinical context (fasting state, biological sex, specimen timing) is not collected, observations are conservatively flagged `CONTEXT_NOT_CONFIRMED`.
5. **Local AI Remarks:** The local Ollama daemon receives only the normalized findings and produces structured remarks. If Ollama is offline or safety validation trips, a deterministic provider fallback is applied and marked `DETERMINISTIC_FALLBACK`.

---

## 3. Technology Stack

- **Backend:** Python 3.12.6, FastAPI 0.115.14, Pydantic v2.14.3, Uvicorn 0.34.3.
- **Persistence:** SQLite 3 (WAL mode, foreign key enforcement, busy timeout 5000ms), SQLAlchemy 2.0.58, Alembic 1.14.1.
- **Frontend:** React 18.3.1, TypeScript 5.6.3, Vite 5.4.21, Tailwind CSS 3.4.17, Lucide React icons.
- **External Integration:** HTTPX 0.28.1 (async HTTP client with exponential backoff and connection pooling).
- **Local AI Engine:** Ollama daemon running `llama3.2:3b` with structured JSON Schema output.
- **Testing & Quality Assurance:** Pytest 8.4.2, Vitest 2.1.9, Playwright 1.65.2 (Chromium), Ruff 0.9.10, Mypy 1.14.1 (strict).

---

## 4. Quickstart & Setup Guide (Windows PowerShell)

### Prerequisites
- **Python:** 3.11 or 3.12 (verified on Python 3.12.6)
- **Node.js:** v20+ (verified on Node.js v24.20.0 with npm 11.19.0)
- **Git:** Installed on local machine
- **Ollama (Optional for local AI):** Ollama daemon with model `llama3.2:3b` pulled (`ollama run llama3.2:3b`)

### Step 1: Clone & Configure Environment
From the repository root (`D:\Gokul-Task-2\Gokul_Task2_Health_Application`):

```powershell
# Copy environment configuration template
Copy-Item .env.example .env

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies (core, dev, testing)
pip install -r backend/requirements-dev.txt

# Install frontend dependencies
cd frontend
npm ci
cd ..
```

### Step 2: Database Initialization & Migrations
Initialize the SQLite schema using Alembic:

```powershell
# Run database migrations to head
$env:PYTHONPATH = "backend"
.\.venv\Scripts\alembic.exe upgrade head
```

### Step 3: Run the Backend Service
In a PowerShell terminal:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now live at:
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Specification:** `http://127.0.0.1:8000/redoc`
- **Liveness Endpoint:** `http://127.0.0.1:8000/api/v1/health`
- **Readiness Probe:** `http://127.0.0.1:8000/api/v1/ready`

### Step 4: Run the Frontend Application
In a second PowerShell terminal:

```powershell
cd frontend
npm run dev
```
Open your browser to:
- **Application Dashboard:** `http://127.0.0.1:5173/`

---

## 5. REST API Specification

### Health & Operations
- `GET /api/v1/health`: Liveness probe reporting application status and version.
- `GET /api/v1/ready`: Readiness probe executing active database connectivity (`SELECT 1`).
- `GET /api/v1/meta/analysis-statuses`: Enumerates supported analysis statuses.

### Patient Record Management
- `POST /api/v1/patients`: Create a new patient record (validates input; checks duplicates; triggers analysis run).
- `GET /api/v1/patients`: List patient records (paginated with `page` and `limit`, optional `search` filter).
- `GET /api/v1/patients/{id}`: Retrieve a single patient profile with latest analysis state.
- `PATCH /api/v1/patients/{id}`: Partial update. Name/email updates preserve analysis; clinical updates (DOB, measurements) trigger a fresh immutable analysis run.
- `DELETE /api/v1/patients/{id}`: Delete patient record and cascade-purge linked analysis history.

### Health Analysis Pipeline
- `POST /api/v1/patients/{id}/analyses`: Trigger or retry health analysis execution (HTTP 202 Accepted). Reuses unstarted pending runs per Section 9 lifecycle rules.
- `GET /api/v1/patients/{id}/analyses`: List historical analysis runs for a patient.
- `GET /api/v1/patients/{id}/analyses/{analysis_id}`: Retrieve full details of an analysis run, including normalized provider observations, qualifiers, citations, and AI remarks.

---

## 6. Privacy, Ethics & Safety Boundaries

### 1. Direct Identifier Exclusion
Outbound requests to TestWell contain exclusively:
- `glucose_value` (number)
- `haemoglobin_value` (number)
- `cholesterol_value` (number)
- `unit_profile_code` (`ASSESSMENT_CONVENTIONAL_V1`)

Full names, email addresses, dates of birth, and internal database record IDs are **never** transmitted over the network or supplied to local LLM prompts.

### 2. Sensitivity Notice
Excluding direct identifiers does not render laboratory measurements non-sensitive. Data is transmitted securely over HTTPS solely for educational reference matching. Users are prompted with an explicit disclosure modal upon first submission.

### 3. Clinical Transparency & Attribution
- TestWell observations represent external reference intervals, not personal clinical evaluations.
- Local AI remarks synthesize provider observations into plain language; they never fabricate diagnoses, prescribe medications, or calculate disease probabilities.
- Provider reviewer metadata is not presented as individual verification.
- Output generated by Ollama is badged `AI Generated (llama3.2:3b)`. Deterministic fallback is strictly badged `DETERMINISTIC_FALLBACK` and is never falsely represented as AI-generated.

### 4. Conventional Unit Assumptions
The employer specification omitted units for biomarker readings. LabInsight explicitly assumes conventional clinical units:
- **Glucose:** `mg/dL`
- **Haemoglobin:** `g/dL`
- **Total Cholesterol:** `mg/dL`

These assumptions are surfaced across disclaimer banners, intake forms, and disclosure dialogs.

---

## 7. Verification & Quality Assurance Matrix

### Automated Test Execution Commands

```powershell
# 1. Backend Pytest Suite (90 tests across 16 test modules)
$env:PYTHONPATH = "backend"
.\.venv\Scripts\pytest.exe tests/backend/ -v

# 2. Python Static Analysis & Linting (Ruff)
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .

# 3. Python Strict Type Checking (Mypy)
.\.venv\Scripts\mypy.exe backend tests

# 4. Frontend Vitest Suite (35 tests across 5 test suites)
npm --prefix frontend test

# 5. Frontend TypeScript Typecheck
npm --prefix frontend run typecheck

# 6. Frontend Production Build
npm --prefix frontend run build

# 7. Playwright Browser End-to-End Suite (Google Chrome)
.\.venv\Scripts\python.exe scratch/run_browser_e2e.py
```

### Verified Test Summary
- **Backend Tests:** 90 / 90 passed (100% pass rate).
- **Frontend Tests:** 35 / 35 passed (100% pass rate).
- **Ruff Linter:** 0 errors across 65 source files.
- **Ruff Formatter:** 65 files verified formatted.
- **Mypy Strict:** 0 issues found in 65 source files.
- **Frontend Production Build:** Built in 3.50s (`dist/assets/index-CflvCWlD.js`: 232.6 kB, CSS: 29.9 kB).
- **Playwright Browser E2E:** 9 scenario groups executed against Google Chrome; 11 screenshots saved in `scratch/screenshots/`.
- **Secret Audit:** 0 secrets, tokens, or credentials found across tracked files.

---

## 8. Video Demonstration & Assessment Walkthrough

A complete, step-by-step video recording guide has been prepared at:  
👉 [`docs/VIDEO_DEMO_SCRIPT.md`](file:///d:/Gokul-Task-2/Gokul_Task2_Health_Application/docs/VIDEO_DEMO_SCRIPT.md)

### Assessment Sequence Summary
1. **Intake:** 10 submissions entered manually from the local employer assessment PDF.
2. **Rejections:** 3 invalid entries rejected with clear validation feedback (impossible calendar date 31.11, malformed email missing TLD, future year 2030).
3. **Duplicate Confirmation:** 1 exact duplicate flagged with HTTP 409 Conflict, then confirmed with `allow_duplicate=true`.
4. **Persisted Records:** Exactly 7 records saved in the database.
5. **Update Operation:** One record's email updated to `gokul@infocare.com` (count remains 7; analysis preserved).
6. **Cascade Delete:** A different record deleted with cascade confirmation (count becomes 6).
7. **Detailed Review:** Provider observations, clinical qualifiers (`CONTEXT_NOT_CONFIRMED`), citations, and local AI remarks reviewed in the patient detail drawer.

---

## 9. Repository Structure

```
.
├── backend/
│   ├── alembic/                 # Database migration scripts & env.py
│   ├── app/
│   │   ├── api/v1/              # FastAPI router & REST endpoints
│   │   ├── core/                # App configuration, logging & exceptions
│   │   ├── db/                  # SQLite connection engine & session factory
│   │   ├── integrations/
│   │   │   ├── ollama/          # Client, prompts, safety validator, fallback
│   │   │   └── testwell/        # Client, adapter, normalization & citations
│   │   ├── models/              # SQLAlchemy declarative models & enums
│   │   ├── schemas/             # Pydantic v2 domain & request/response schemas
│   │   └── services/            # Patient CRUD & analysis orchestration
│   ├── requirements.txt         # Core backend production dependencies
│   └── requirements-dev.txt     # Development, testing, and linting tools
├── frontend/
│   ├── src/
│   │   ├── components/          # React components (Header, Table, Modals)
│   │   ├── hooks/               # usePatients, useAnalysisPoll custom hooks
│   │   ├── services/            # Typed apiClient, patientService, analysisService
│   │   ├── types/               # TypeScript interfaces matching backend schemas
│   │   └── utils/               # Date parsing & client-side validation
│   ├── package.json             # Frontend dependencies & scripts
│   └── vite.config.ts           # Vite bundler & reverse proxy config
├── docs/                        # Complete architecture & design documentation
│   ├── ARCHITECTURE.md          # Full architectural blueprint
│   ├── API_SPECIFICATION.md     # OpenAPI contracts & error schemas
│   ├── DATABASE_DESIGN.md       # Entity-relationship design & migrations
│   ├── VALIDATION_SPECIFICATION.md # Multi-tier validation rules
│   ├── VIDEO_DEMO_SCRIPT.md     # Step-by-step video recording guide
│   └── ...
├── tests/
│   ├── backend/                 # 16 Pytest test modules (90 tests)
│   └── e2e/                     # Playwright browser integration tests
├── .env.example                 # Template environment variables
├── .gitignore                   # Excludes DBs, secrets, .venv, node_modules, PDF
└── README.md                    # This document
```

---

## 10. License & Candidate Information

- **Assessment Candidate:** Candidate Number 267
- **Target Organization:** Gokul Infocare Pty Ltd
- **Role:** AI Growth & Automation Associate — Task 2
- **License:** Proprietary Assessment Prototype — For Evaluation Purposes Only
