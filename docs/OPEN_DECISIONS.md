# Owner Decisions and Implementation Assumptions

**Baseline:** Engineering Blueprint v0.2  
**Decision date:** 18 November 2026  
**Authority:** Project owner instructed the team to stop further review cycles and begin development.  
**Status:** Decisions below are approved for this assessment prototype, with the stated limitations. They are not claims of clinical validity.

| ID | Decision | Owner-approved implementation direction | Boundary / evidence still required |
|---|---|---|---|
| O-01 | Application name | Use `LabInsight` as the working name. | Branding can change later without affecting architecture. |
| O-02 | Measurement units | Use glucose `mg/dL`, haemoglobin `g/dL`, total cholesterol `mg/dL` as an explicit assessment assumption for the supplied numeric dataset. | The employer PDF does not state units. Display this assumption prominently; never describe it as source-confirmed. Do not infer that these are the actual laboratory units. |
| O-03 | Primary external health API | Implement TestWell `POST /api/agent/interpret_results` as the primary external health-related API. | Phase 4A must verify current OpenAPI contract, live connectivity, all marker matches, error cases and provider caveats. Use only the assessment prototype and de-identified numeric values. |
| O-04 | External data acknowledgement | Require a clear one-time user acknowledgement before sending measurements to TestWell. | Explain that numerical measurements and selected units leave the device; no name, email, DOB, record ID or other direct identifier is sent. Provide a decline path (`NOT_RUN`). |
| O-05 | Local AI model | Use the already installed Ollama model `llama3.2:3b`. | Phase 4B must test actual application JSON-Schema output, prompt safety, latency and failure handling. Do not download another model without approval. Observe Meta Llama Community License and attribution requirements. |
| O-06 | AI role | Local LLM only converts normalized, provider-returned educational facts and caveats into concise remarks. | It must not inspect raw measurements to invent thresholds, alter provider flags, diagnose, prescribe, invent citations or add unsupported claims. |
| O-07 | Context-dependent flags | Preserve provider flags and range qualifiers, but mark them context-limited when the required context is absent. | Do not send or infer sex, age-at-specimen, fasting status, pregnancy or other missing context. Do not present a provider default as individually established. |
| O-08 | Analysis execution | Use FastAPI in-process `BackgroundTasks` with one Uvicorn worker for this local assessment app. | Commit patient and pending analysis first; perform network/model I/O outside DB transactions; persist terminal result. Document that this is not a durable production job queue. |
| O-09 | Create idempotency | Implement an `Idempotency-Key` for create requests if it fits the Phase 3 contract; at minimum lock the form while submitting and prevent accidental replay. | Same key must return the original created resource; duplicate-confirmation flow must remain possible. |
| O-10 | Delete semantics | Deleting a patient cascades to its analysis history. | No public API to independently delete analysis history. Confirm delete in UI. |
| O-11 | Original employer PDF | Keep the PDF under local `reference/`; exclude it from Git. | Use exact values only for the required local demonstration; neutral fixtures in public tests/docs. |
| O-12 | `test_ollama.py` governance deviation | During Phase 1 preflight, locate any such file under the old and new Task 2 workspaces and inspect its location/content. | Do not automatically delete, move or commit it. If outside the new project, leave it alone. It is not a reason to delay project scaffolding unless it conflicts with the new workspace. |
| O-13 | TestWell trust boundary | Accept TestWell conditionally for this educational assessment prototype. | This project has not independently audited the provider, its infrastructure, medical review or privacy claims. No real patient data. Display educational-only disclaimer and source/caveat details. |

## Implementation authorization

The project owner has authorized **Phase 1 only**: repository and development foundation. This approval does not authorize implementing database entities, patient CRUD, external API integration, model prompts or the frontend workflows before their designated phases.

Phase 1 can proceed using the decisions above. Any blocker that affects the foundation must be reported precisely; do not restart a broad architecture review. Further provider/AI acceptance checks belong to Phases 4A and 4B.
