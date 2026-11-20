# LabInsight — Video Demonstration & Technical Walkthrough Script
## Gokul Infocare Pty Ltd — AI Growth & Automation Associate — Task 2

**Candidate Number:** 267  
**Application Name:** LabInsight  
**Engineering Baseline:** Blueprint v0.2  
**Target Video Duration:** 6–8 minutes  
**Format:** Screen recording with voiceover (split-screen / terminal + browser + editor)

---

### Pre-Recording Setup Checklist (Before Pressing Record)

1. **Clean Database Setup:**
   Ensure you start with a clean database for the recording:
   ```powershell
   # In PowerShell:
   Remove-Item -Path "backend/data/labinsight_demo.db" -ErrorAction SilentlyContinue
   $env:DATABASE_URL = "sqlite:///./backend/data/labinsight_demo.db"
   $env:PYTHONPATH = "backend"
   .\.venv\Scripts\alembic.exe upgrade head
   ```
2. **Start Backend Server:**
   ```powershell
   # Terminal 1:
   $env:DATABASE_URL = "sqlite:///./backend/data/labinsight_demo.db"
   $env:PYTHONPATH = "backend"
   .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
   ```
3. **Start Frontend Server:**
   ```powershell
   # Terminal 2:
   cd frontend
   npm run dev
   ```
4. **Local AI Engine:**
   Confirm Ollama is running in the background (`http://127.0.0.1:11434`) with model `llama3.2:3b`.
5. **Open Applications:**
   - Chrome browser at `http://127.0.0.1:5173/` (set 100% or 110% zoom for crisp readability).
   - VS Code open to the project root with key files bookmarked.
   - Employer assessment document `Task 2 - AI Growth Python Skills.pdf` open side-by-side or on a second screen for manual fixture entry. *(Keep this PDF off camera or focused strictly on your browser/code window to preserve privacy).*

---

### Step-by-Step Walkthrough Timeline (Total: ~7 minutes)

```
00:00 - 00:45 | 1. Introduction & Architecture Overview
00:45 - 01:15 | 2. Application Startup & Live Connectivity Indicators
01:15 - 01:45 | 3. Intake Disclosure & Conventional Unit Assumptions
01:45 - 04:15 | 4. The 10 Assessment Submissions Walkthrough
04:15 - 05:00 | 5. Target Email Update (gokul@infocare.com) & Cascade Deletion
05:00 - 06:15 | 6. Detailed Health Analysis: TestWell & Local Ollama Remarks
06:15 - 07:15 | 7. Code Walkthrough & Architectural Rigor
07:15 - 07:45 | 8. Conclusion & Submission Sign-Off
```

---

### Segment 1: Introduction & Architecture Overview (00:00 – 00:45)

**Visual:** Browser showing the LabInsight dashboard (`http://127.0.0.1:5173/`).

**Spoken Script:**
> *"Hello, my name is Candidate Number 267. Today, I am demonstrating **LabInsight**, my complete, production-grade submission for the Gokul Infocare Task 2 Health Application assessment.*
>
> *LabInsight is a full-stack health record management and biomarker reference interpretation system. It features a modern React 18 and TypeScript frontend with Tailwind CSS, a high-performance Python FastAPI backend, a persistent SQLite database running in WAL mode with Alembic migrations, and an external integration pipeline that connects to the TestWell reference catalog and synthesizes structured educational summaries using a locally running Ollama `llama3.2:3b` model.*
>
> *The application is designed specifically as an educational clinical reference prototype. It strictly adheres to healthcare privacy boundaries, ensures whole-record data integrity, and handles hostile or malformed inputs gracefully."*

---

### Segment 2: Application Startup & Live Connectivity Indicators (00:45 – 01:15)

**Visual:** Mouse cursor hovers over the header pills in the top-right corner.

**Spoken Script:**
> *"Looking at the dashboard header, we immediately see three real-time operational status pills:*
> 1. *First, **Backend API: Online**, confirming our FastAPI REST service is responding with healthy liveness probes.*
> 2. *Second, **Database: Ready**, which actively probes our SQLite WAL database with an automated `SELECT 1` ping.*
> 3. *Third, **Local AI: llama3.2:3b**, which detects our local Ollama inference daemon.*
>
> *Directly below, an amber disclaimer banner clearly reminds the user that this application is an educational prototype and not a diagnostic medical device. It also provides an expandable drawer detailing our assumed conventional unit profile and privacy guarantees."*

---

### Segment 3: Intake Disclosure & Conventional Unit Assumptions (01:15 – 01:45)

**Visual:** Click the **Add Patient Record** button. The modal opens; fill in Test #1 fields and click **Save & Trigger Analysis**. The `Educational Assessment Disclosure` modal pops up.

**Spoken Script:**
> *"When creating our first patient profile, the application presents an explicit **Educational Assessment Disclosure** modal before any external data transfer occurs.*
>
> *Here, we communicate two vital boundaries:*
> 1. *First, the **Assessment Unit Assumptions**: because the employer PDF specified numerical measurements without units, this prototype explicitly assumes conventional units: Glucose in mg/dL, Haemoglobin in g/dL, and Cholesterol in mg/dL.*
> 2. *Second, our **Direct Identifier Exclusion Boundary**: we inform the user that their direct identifiers—name, email, date of birth, and database ID—are strictly excluded and never transmitted over the network. Only the numerical measurements and unit labels are dispatched over HTTPS to TestWell for reference interval matching. Furthermore, we transparently disclose that excluding direct identifiers does not make lab data non-sensitive.*
>
> *We click **I Understand — Continue** to accept and save the record."*

---

### Segment 4: The 10 Assessment Submissions Walkthrough (01:45 – 04:15)

**Visual:** Systematically enter all 10 entries from the local employer assessment PDF (`reference/Task 2 - AI Growth Python Skills.pdf`, Pages 2–3).

**Spoken Script:**
> *"Now, we will execute the exact ten assessment submissions specified in the employer assignment document:*
>
> - ***Submission #1:** Valid intake. We enter the first patient's details from the PDF. The record is accepted immediately, persisted as Record #1, and an initial analysis run is queued.*
>
> - ***Submission #2:** Malformed email test. Notice that the email in the PDF is missing a top-level domain (`@email` without `.com`). When we attempt to submit, both our frontend and backend validation intercept this immediately, displaying a clear inline error: `'Invalid email address format (e.g. user@example.com)'`. The invalid record is rejected and not saved to the database.*
>
> - ***Submission #3:** Valid intake with atypical biomarker readings. High or low laboratory measurements reflect physiological states, not syntax errors. The application validates the numerical syntax and saves the record cleanly as Record #2.*
>
> - ***Submission #4:** Impossible calendar date test. The PDF specifies November 31st (`31.11`). November has only 30 days. Our date parser strictly rejects this impossible date with `'Impossible calendar date'` before any database write occurs.*
>
> - ***Submission #5:** Valid intake. We enter the fifth record. It validates and persists cleanly as Record #3.*
>
> - ***Submission #6:** Exact duplicate submission. This entry is an exact duplicate of Submission #1. When we submit, our duplicate detection engine flags a SHA-256 fingerprint collision and returns an **HTTP 409 Conflict**. The frontend intercepts this and displays our **Duplicate Patient Record Detected** dialog, showing that Record #1 already exists with identical demographic and biomarker values. Per employer requirements, we click **Confirm & Insert Duplicate Record** (`allow_duplicate=true`) to explicitly confirm insertion. The duplicate is successfully persisted as an independent record with ID #4.*
>
> - ***Submission #7:** Valid intake. Accepted and persisted cleanly as Record #5.*
>
> - ***Submission #8:** Malformed email and future date of birth test. The PDF provides a future year (`2030`) and a malformed email. The form and backend validate both constraints, rejecting the future date and invalid email format. The record is rejected.*
>
> - ***Submission #9:** Valid date boundary test. This record uses November 30th (`30.11`). Because November 30 exists on the calendar, our parser correctly accepts it, persisting Record #6.*
>
> - ***Submission #10:** Final valid intake. Accepted and persisted as Record #7.*
>
> *Looking at our operational metrics card and table footer, we have exactly **7 persisted records** in the database after the 10 intake attempts (3 rejected, 1 confirmed duplicate, 7 persisted)."*

---

### Segment 5: Target Email Update (`gokul@infocare.com`) & Cascade Deletion (04:15 – 05:00)

**Visual:** 
1. Click the **Edit** action icon on the first patient record (`#1`). Change the email address to `gokul@infocare.com` and click **Save Changes**.
2. Click the **Delete** action icon on a **different** record (e.g., `#2`). Show the warning modal and click **Permanently Delete**.

**Spoken Script:**
> *"Next, we demonstrate the required update and deletion operations:*
>
> *First, we click **Edit** on our first patient record. We update the email address to **`gokul@infocare.com`** and click Save Changes. The table updates instantly. Because an email change is a non-clinical update, our backend preserves the existing analysis history without triggering an unnecessary re-run. Our record count remains exactly seven.*
>
> *Second, we delete a **different** patient record—Record #2. Clicking the delete icon opens our **Delete Patient Record** dialog. Notice the explicit **Cascade Deletion Warning**, informing the user that deleting this patient permanently purges all historical analysis runs, TestWell observations, and AI remarks. We confirm deletion.*
>
> *Record #2 is permanently removed. Our patient directory now displays exactly **6 remaining records**, with our updated `gokul@infocare.com` record preserved."*

---

### Segment 6: Detailed Health Analysis: TestWell & Local Ollama Remarks (05:00 – 06:15)

**Visual:** Click the **View record** icon on any remaining patient to open `PatientDetailModal`.

**Spoken Script:**
> *"Now let's examine the heart of our health interpretation pipeline by opening the patient details drawer:*
>
> *At the top, we see the patient's identity summary, demographic information, and biomarker readings.*
>
> *Under the **TestWell Educational Reference Observations** tab, we see the normalized observations returned by TestWell:*
> - *Each analyte—Glucose, Haemoglobin, and Cholesterol—is displayed with its numerical value, conventional unit, and qualitative flag (`Normal`, `High`, or `Low`).*
> - *Crucially, notice the **Clinical Context Warning** on each card: `'Context Status: CONTEXT_NOT_CONFIRMED'`. Because the intake assessment did not collect fasting state, biological sex, or specimen timing, our normalizer conservatively flags this so no clinician or user assumes the range applies without qualification.*
> - *We also surface educational guidance and official provider citations (such as the American Diabetes Association).*
>
> *Next, we click the **AI Remarks & Fallback** tab:*
> - *Here, our local Ollama model (`llama3.2:3b`) synthesizes the normalized facts into clear, plain-language educational remarks.*
> - *Notice the prominent badge: **AI Generated (llama3.2:3b)**.*
> - *Our strict safety validator enforces that the remarks never fabricate diagnoses, prescribe treatments, or falsely claim that a physician personally reviewed this individual patient's results.*
> - *Furthermore, if Ollama were offline or timed out, our built-in deterministic fallback activates seamlessly, marking the output strictly as **DETERMINISTIC_FALLBACK**."*

---

### Segment 7: Code Walkthrough & Architectural Rigor (06:15 – 07:15)

**Visual:** Switch to VS Code. Briefly open and highlight 4 specific files:
1. `backend/app/services/duplicate_detector.py`
2. `backend/app/integrations/testwell/adapter.py`
3. `backend/app/integrations/ollama/validator.py`
4. `frontend/src/utils/validation.ts`

**Spoken Script:**
> *"To conclude, let's look at the underlying architecture in our codebase:*
>
> 1. *In `duplicate_detector.py`, we implement canonical identity hashing using SHA-256 over normalized patient names, ISO dates, emails, and fixed 3-decimal biomarker representations. This guarantees deterministic duplicate detection.*
> 2. *In `testwell/adapter.py`, our outbound request builder strictly filters fields: only numeric biomarkers and the unit profile are sent over HTTPS. No names, emails, dates of birth, or database IDs ever reach the network layer.*
> 3. *In `ollama/validator.py`, we enforce strict clinical guardrails using Pydantic JSON Schema validation and regex phrase filters that immediately reject diagnostic claims, medication prescriptions, or physician-review falsehoods.*
> 4. *In `validation.ts` on the frontend, our date parser validates leap years and calendar bounds (`DD/MM/YYYY`, `DD.MM.YYYY`, `YYYY-MM-DD`), while our form retaining mechanism prevents data loss during conflict warnings."*

---

### Segment 8: Conclusion & Submission Sign-Off (07:15 – 07:45)

**Visual:** Switch back to the clean LabInsight dashboard with 6 records visible.

**Spoken Script:**
> *"In summary, LabInsight fulfills every requirement of Gokul Infocare Task 2:*
> - *Complete, robust validation of all demographic and blood-test fields.*
> - *Reliable SQLite WAL persistence with Alembic migrations and cascade deletion.*
> - *Duplicate detection with explicit confirmation override.*
> - *Full 10-submission assessment verification resulting in 7 persisted records, followed by the target email update to `gokul@infocare.com` and deletion of a different record to leave exactly 6 records.*
> - *Live external API integration with TestWell and local Ollama `llama3.2:3b` AI remarks with deterministic fallback and strict clinical safety guardrails.*
> - *125 automated tests across backend and frontend, with 100% clean static analysis.*
>
> *Thank you for your time and consideration. This concludes the demonstration for Candidate 267."*

---

### Candidate Video Recording Guidelines (Reminders for Candidate 267)

1. **Resolution & Audio:** Record in 1080p (1920x1080) at 30 or 60 fps. Use a clear microphone with minimal background noise.
2. **Data Privacy:** Keep the employer PDF off-camera. Do not type passwords or display personal file paths on your machine.
3. **Pacing:** Speak at a steady, professional pace. If you make a minor verbal slip, pause for 2 seconds and re-read the sentence smoothly—you do not need to restart the entire recording.
4. **Local Database Isolation:** Always run the recording against `labinsight_demo.db` so your main development databases (`labinsight.db`, `labinsight_e2e.db`) remain untouched.
5. **No Submission Email:** After completing your video, save the recording locally. Await the final submission email review before transmitting any files.
