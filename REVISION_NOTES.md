# Revision Notes — Blueprint 0.2

## Why 0.2 exists

Version 0.1 used MedlinePlus Connect as the proposed primary external health API. That service retrieves general lab-test educational material by code; it does not evaluate the patient's entered numeric values. Antigravity's Phase 0.2 review correctly identified a material risk that this would not satisfy the task's external-health-API requirement.

Phase 0.3 reported a successful TestWell `interpret_results` smoke test for the three required analytes and a working local Ollama `llama3.2:3b` model. The provider's official documentation describes this endpoint as comparing submitted values against its physician-reviewed reference catalogue. Version 0.2 therefore proposes TestWell as the primary external health-related API, subject to owner approval and limitations documented in the package.

## Principal changes

1. Replace MedlinePlus Connect as primary provider with TestWell `interpret_results`.
2. Retain MedlinePlus only as an optional, secondary educational reference if needed.
3. Replace provisional `phi4-mini` with already installed `llama3.2:3b`, based on reported local feasibility evidence.
4. Require local LLM remarks to be generated only from normalized provider response facts and caveats.
5. Do not treat Pydantic structure validation or regex filtering as proof of clinical truth.
6. Explicitly detect provider range qualifiers and mark context-incompatible results as context-limited.
7. Treat units as an owner-approved assessment assumption; they are not present in the source PDF.
8. Split patient records from append-only analysis-run history.
9. Use non-blocking, in-process background analysis for this single-user local assessment, with explicit limits and stale-PENDING recovery.
10. Define consistent analysis status enums and PATCH behavior.
11. Add `RISK_REGISTER.md`, `AI_PROVIDER_RESEARCH.md` and `UI_SPECIFICATION.md`.
12. Keep exact employer-supplied data and the source PDF out of public Git; treat them as potentially identifiable health-related data.
13. Add explicit external-data acknowledgement before sending measurement values to TestWell.
14. Add a governance note for the `test_ollama.py` artifact recorded during the read-only feasibility spike.

## What 0.2 does not claim

- TestWell is not independently audited by this project.
- The provider's "not logged" statement is not independently verified.
- The provider's ranges do not substitute for the user's actual laboratory report.
- The application is not a medical device or diagnostic system.
- The local Llama model is not clinically validated.
- The reported timings are not production performance guarantees.
- The application has not been implemented or tested end-to-end.
