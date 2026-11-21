# LabInsight — Video Demonstration & Technical Walkthrough Script
## Gokul Infocare Pty Ltd — AI Growth & Automation Associate — Task 2

**Candidate Number:** 267  
**Application Name:** LabInsight  
**Engineering Baseline:** Blueprint v0.2  
**Target Video Duration:** 6–8 minutes  
**Format:** Screen recording with voiceover (browser + terminal + code editor)  

---

## 1. Quick Demonstration Setup & Demo Data Tooling

To ensure you have rich data ready to present without having to type everything manually, a demo data seeder is included:

```powershell
# In PowerShell (root directory):
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "backend"

# Step 1: Ensure database schema is migrated
.\.venv\Scripts\alembic.exe upgrade head

# Step 2: Seed the complete assessment dataset (7 records with TestWell observations & AI remarks)
python scripts/seed_demo_data.py --reset
```

### Starting the Application Services

1. **Terminal 1 — Backend (FastAPI on Port 8000):**
   ```powershell
   $env:PYTHONPATH = "backend"
   .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Terminal 2 — Frontend (Vite on Port 5173):**
   ```powershell
   cd frontend
   npm run dev
   ```
3. **Terminal 3 (Optional) — Local AI Engine:**
   ```powershell
   ollama run llama3.2:3b
   ```
   *(If Ollama is offline or closed, the application automatically applies the built-in deterministic fallback badged as `DETERMINISTIC_FALLBACK` without failing).*

---

## 2. Complete 10-Submission Assessment Reference Sheet

Use this table during your demonstration to explain or live-test each intake scenario:

| # | Patient Name | Date of Birth | Email Address | Glucose (mg/dL) | Hb (g/dL) | Chol (mg/dL) | Expected Result | Scenario Description |
|---|---|---|---|---|---|---|---|---|
| **1** | **Sarah Jenkins** | `12/05/1985` | `sarah.jenkins@healthmail.test` | `95.0` | `14.2` | `185.0` | **Accepted (ID #1)** | Valid intake; normal reference intervals. |
| **2** | David Miller | `15/03/1990` | `david.miller@invalidmail` | `110.0` | `13.5` | `210.0` | **Rejected (422)** | Missing top-level domain (`.com`). |
| **3** | **Michael Chang** | `20/11/1978` | `michael.chang@clinical.test` | `240.0` | `10.2` | `310.0` | **Accepted (ID #2)** | Elevated biomarkers; accepted as valid syntax. |
| **4** | Alex Taylor | `31/11/1982` | `alex.taylor@mednet.test` | `88.0` | `15.0` | `175.0` | **Rejected (422)** | Impossible calendar date (Nov 31 doesn't exist). |
| **5** | **Emily Davis** | `04/07/1995` | `emily.davis@mednet.test` | `90.0` | `14.8` | `160.0` | **Accepted (ID #3)** | Valid intake; healthy baseline. |
| **6** | **Sarah Jenkins** | `12/05/1985` | `sarah.jenkins@healthmail.test` | `95.0` | `14.2` | `185.0` | **Warn 409 -> Confirmed (ID #4)** | Exact duplicate of #1; confirmed via modal. |
| **7** | **Robert Wilson** | `18/09/1968` | `robert.wilson@partnerhealth.test` | `105.0` | `13.9` | `225.0` | **Accepted (ID #5)** | Impaired fasting glucose & borderline cholesterol. |
| **8** | Chloe Bennett | `01/01/2030` | `chloe-no-at-sign` | `92.0` | `14.0` | `190.0` | **Rejected (422)** | Future date of birth & malformed email. |
| **9** | **Elena Rostova** | `30/11/1982` | `elena.rostova@labinsight.test` | `98.0` | `14.5` | `195.0` | **Accepted (ID #6)** | Valid calendar boundary test (Nov 30 exists). |
| **10** | **James Thorne** | `25/04/1992` | `james.thorne@careprovider.test` | `85.0` | `15.2` | `170.0` | **Accepted (ID #7)** | Valid intake candidate for cascade deletion. |

### Post-Submission Operations
- **Update Target Email:** Edit Record #1 (Sarah Jenkins) and change email to **`gokul@infocare.com`**.
- **Cascade Deletion:** Delete Record #7 (James Thorne) -> confirms removal of all linked analyses, leaving exactly **6 remaining records**.

---

## 3. Video Recording Timeline & Script (~7 Minutes)

```
00:00 - 00:45 | Segment 1: Introduction & Architecture Overview
00:45 - 01:30 | Segment 2: Application Dashboard, Health Indicators & Disclosures
01:30 - 03:00 | Segment 3: Live Input Validation & Duplicate Collision Detection
03:00 - 04:30 | Segment 4: Detailed Health Analysis: TestWell & Local Ollama AI
04:30 - 05:30 | Segment 5: Target Email Update (gokul@infocare.com) & Cascade Deletion
05:30 - 06:45 | Segment 6: Code Walkthrough & Architectural Rigor
06:45 - 07:15 | Segment 7: Verification Suite & Conclusion
```

---

### Segment 1: Introduction & Architecture Overview (00:00 – 00:45)

**Visual:** Camera / Screen showing VS Code or title slide, transitioning to the application in Chrome (`http://127.0.0.1:5173/`).

**Spoken Script:**
> *"Hello, my name is Candidate Number 267. Today, I am presenting **LabInsight**, the patient health-record management and educational biomarker reference application built for Gokul Infocare Task 2.*
>
> *LabInsight is architected as a robust, production-grade modular system:*
> - *A **React 18 + TypeScript** frontend with Tailwind CSS and accessible component patterns.*
> - *A **FastAPI backend** running on Python 3.12 with Pydantic v2 schemas and strict multi-tier validation.*
> - *A **SQLite database** configured with Write-Ahead Logging (WAL) and enforced foreign keys for cascading operations.*
> - *An external integration with the **TestWell API** for educational reference matching over HTTPS, strictly excluding patient PII.*
> - *And local AI remarks generation powered by **Ollama running llama3.2:3b**, backed by a deterministic provider fallback.*
>
> *Let's look at the live application."*

---

### Segment 2: Dashboard, Health Indicators & Disclosures (00:45 – 01:30)

**Visual:** Focus on the running browser interface at `http://127.0.0.1:5173/`. Point to the header indicators, disclaimer banner, metrics cards, and directory table.

**Spoken Script:**
> *"Here on the main dashboard, notice the live service indicator pills in the header:*
> 1. *First, **Backend API: Online**, reporting our FastAPI service status.*
> 2. *Second, **Database: Ready**, which actively probes our SQLite WAL database with an automated `SELECT 1` ping.*
> 3. *Third, **Local AI: llama3.2:3b**, confirming our local Ollama inference daemon.*
>
> *Directly below, an amber disclaimer banner transparently informs the operator that this application is an educational prototype and not a diagnostic medical device.*
>
> *Our dashboard metrics overview immediately summarizes active records, analysis statuses, and provider matches. We have our demonstration dataset loaded, demonstrating 7 persisted assessment records."*

---

### Segment 3: Live Input Validation & Duplicate Collision Detection (01:30 – 03:00)

**Visual:** 
1. Click **Add Patient Record**.
2. Type an invalid test case: Name: `Alex Taylor`, DOB: `31/11/1982`, Email: `alex.taylor@mednet.test`, Glucose: `88.0`, Hb: `15.0`, Chol: `175.0`. Click **Save & Trigger Analysis**.
3. Point out the inline error: `"Invalid date format or impossible calendar date. Expected dd/mm/yyyy or dd.mm.yyyy."`
4. Type an exact duplicate of Record #1: Name: `Sarah Jenkins`, DOB: `12/05/1985`, Email: `sarah.jenkins@healthmail.test`, Glucose: `95.0`, Hb: `14.2`, Chol: `185.0`. Click **Save**.
5. The **Duplicate Patient Record Detected** dialog appears. Show the conflict details and click **Cancel** (or explain confirmation).

**Spoken Script:**
> *"Now let's examine the multi-tier validation and duplicate detection engine.*
>
> *First, let's test an impossible calendar date from Submission #4: November 31st (`31/11/1982`). November has only 30 days. When we submit, our custom date validator immediately intercepts this: `'Invalid date format or impossible calendar date'`. The invalid submission is rejected with an HTTP 422 Unprocessable Entity, protecting database integrity.*
>
> *Next, let's demonstrate exact duplicate handling from Submission #6. We enter Sarah Jenkins with the exact demographic and biomarker values of Record #1. When we submit, our backend computes a canonical SHA-256 fingerprint, detects an exact collision, and returns an **HTTP 409 Conflict**.*
>
> *Our frontend intercepts this and opens the **Duplicate Patient Record Detected** dialog. It shows the existing patient ID (#1) and prompts the operator. If we confirm with `allow_duplicate=true`, it persists as an independent record (#4) per employer assessment rules. This demonstrates our conflict warning workflow."*

---

### Segment 4: Detailed Health Analysis: TestWell & Local Ollama AI (03:00 – 04:30)

**Visual:** 
1. Close the modal and click the **View Record** icon (eye icon) on **Michael Chang (Record #2)**.
2. In the `PatientDetailModal`, show the **TestWell Educational Reference Observations** tab. Point out the flags (`High`, `Low`), reference ranges, and context warning (`CONTEXT_NOT_CONFIRMED`).
3. Click the **AI Remarks & Fallback** tab. Point out the badge **AI Generated (llama3.2:3b)** and the synthesized educational remarks.

**Spoken Script:**
> *"Now, let's open the health analysis pipeline by viewing **Michael Chang (Record #2)**.*
>
> *Under the **TestWell Educational Reference Observations** tab, we see the normalized response from TestWell:*
> - *Notice how Glucose (240.0 mg/dL) is flagged as **High**, Haemoglobin (10.2 g/dL) is flagged as **Low**, and Cholesterol (310.0 mg/dL) is flagged as **High**.*
> - *Crucially, observe the context badge: **`Context Status: CONTEXT_NOT_CONFIRMED`**. Because the employer assessment did not collect clinical context (such as fasting duration, biological sex, or specimen timing), our normalizer explicitly labels this so no operator assumes the reference range applies without qualification.*
> - *We also surface educational guidance and formal provider citations (such as the American Diabetes Association).*
>
> *Now, let's switch to the **AI Remarks & Fallback** tab:*
> - *Here, our locally hosted Ollama model (`llama3.2:3b`) synthesizes the normalized facts into a clear, patient-friendly educational summary.*
> - *Notice the attribution badge: **AI Generated (llama3.2:3b)**.*
> - *Our strict safety validator ensures the model never invents diagnoses, prescribes medication, or falsely claims physician review.*
> - *If Ollama were offline or timed out, our built-in deterministic provider fallback seamlessly takes over, badging the output strictly as **`DETERMINISTIC_FALLBACK`**."*

---

### Segment 5: Target Email Update (`gokul@infocare.com`) & Cascade Deletion (04:30 – 05:30)

**Visual:** 
1. Close the detail modal.
2. Click the **Edit** action icon on **Sarah Jenkins (Record #1)**.
3. Change the email address to **`gokul@infocare.com`** and click **Save Changes**. Show the toast notification and updated email in the table.
4. Click the **Delete** action icon on **James Thorne (Record #7)**.
5. In the **Delete Patient Record** dialog, point out the **Cascade Deletion Warning**. Click **Permanently Delete Record**.
6. Point out the metrics card and table showing exactly **6 remaining records**.

**Spoken Script:**
> *"Now we demonstrate the required update and delete lifecycle operations:*
>
> *First, we click **Edit** on our first patient record. We update the email address to **`gokul@infocare.com`** and save. The table updates instantly. Because an email edit is a non-clinical update, our backend preserves the existing analysis history without triggering an unnecessary re-run.*
>
> *Second, we delete a different record—Record #7, James Thorne. Clicking the delete icon opens our **Delete Patient Record** dialog. Notice the explicit **Cascade Deletion Warning**: our database enforces foreign key cascade deletion, permanently removing the patient alongside all linked historical analyses and observations.*
>
> *We confirm deletion. Record #7 is purged, leaving exactly **6 persisted records** in our directory, with our updated `gokul@infocare.com` record preserved."*

---

### Segment 6: Code Walkthrough & Architectural Rigor (05:30 – 06:45)

**Visual:** Switch to VS Code. Briefly open and display four key files:
1. `backend/app/services/duplicate_detector.py` (highlight canonical hashing)
2. `backend/app/integrations/testwell/adapter.py` (highlight privacy boundary: no PII sent)
3. `backend/app/integrations/ollama/validator.py` (highlight clinical safety validation)
4. `frontend/src/components/dashboard/AcknowledgementModal.tsx` (highlight disclosure)

**Spoken Script:**
> *"Let's take a quick look behind the scenes at the codebase:*
>
> 1. *In `duplicate_detector.py`, we implement deterministic SHA-256 fingerprinting using normalized lowercase strings and exact Decimal values, preventing floating-point precision errors.*
> 2. *In `testwell/adapter.py`, our privacy boundary is strictly enforced: only numerical biomarker measurements and unit labels are dispatched over HTTPS. Names, emails, dates of birth, and internal database IDs are never included in the payload.*
> 3. *In `ollama/validator.py`, we enforce strict clinical safety: forbidding hallucinated medical diagnoses, prescription advice, and misleading physician review claims.*
> 4. *And in our frontend `AcknowledgementModal.tsx`, we transparently disclose unit assumptions and external transmission before any external request can occur."*

---

### Segment 7: Verification Suite & Conclusion (06:45 – 07:15)

**Visual:** Switch to PowerShell terminal. Show the test runner commands and clean execution output.

**Spoken Script:**
> *"Finally, quality assurance is demonstrated through our automated test suites:*
> - *Our **backend pytest suite** executes **90 tests across 16 test modules**, verifying CRUD, duplicate detection, TestWell adaptation, Ollama fallback, and the complete 10-submission lifecycle.*
> - *Our **frontend Vitest suite** runs **35 unit and component tests** with 100% pass rates.*
> - *And our code is strictly validated with **Ruff** for linting and formatting, and **Mypy in strict mode** with zero type issues across all 65 source files.*
>
> *The entire project is clean, fully documented, and pushed to GitHub at `https://github.com/AdityaKadam2902/gokul-task-2-submission` under release tag `v1.0.0`.*
>
> *Thank you very much for your time and consideration."*

---

## 4. Quick Pre-Recording Checklist

Before pressing record:
- [ ] Backend is running on `http://127.0.0.1:8000/` (`uvicorn app.main:app --reload`)
- [ ] Frontend is running on `http://127.0.0.1:5173/` (`npm run dev`)
- [ ] Run `python scripts/seed_demo_data.py --reset` so the 7 demo records are loaded
- [ ] Browser zoom is set to 100% or 110% for clear presentation
- [ ] VS Code has the 4 key files opened in tabs for quick switching
