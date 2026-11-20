# Risk Register

**Version:** 0.2 — Owner-approved implementation baseline

Scales: likelihood and impact are Low / Medium / High. Severity is a project judgement, not a quantified clinical risk score.

| ID | Risk | Likelihood | Impact | Severity | Mitigation | Residual |
|---|---|---|---|---|---|---|
| RK-01 | Employer may interpret "prediction" as requiring a predictive AI service | Medium | High | HIGH | Use health API that evaluates entered measurements; explain API + local AI roles precisely; avoid claiming diagnosis | Medium |
| RK-02 | Units missing from source fixtures | High | High | CRITICAL | Owner-approved visible unit profile; no silent inference | Medium |
| RK-03 | TestWell default ranges rely on fasting/male/adult assumptions | High | High | HIGH | Inspect qualifier; mark context incomplete; do not present as definitive | Medium |
| RK-04 | Third-party provider receives de-identified health values | Medium | High | HIGH | Explicit acknowledgement; no PII; provider claim not treated as guarantee; use assessment data only | Medium |
| RK-05 | Provider unavailable/rate-limited/changes schema | Medium | Medium | MEDIUM | Typed adapter, timeouts, response validation, clear failure and retry | Low/Medium |
| RK-06 | Local model hallucinates medical statement | Medium | High | HIGH | Narrow input; structured schema; validate IDs/codes; safety filter; fallback; adversarial tests | Medium |
| RK-07 | JSON-mode response not valid against required schema | Medium | Medium | MEDIUM | Use JSON Schema `format`; Pydantic validate; malformed output fallback | Low |
| RK-08 | Ollama model fails on low available RAM or cold start | Medium | Medium | MEDIUM | Use existing 3B model; timeouts; preflight check; benchmark on full app | Low/Medium |
| RK-09 | Background task lost when process exits | Medium | Medium | MEDIUM | In-process mechanism scoped to local demo; detect stale PENDING on startup; retry; disclose limitation | Medium |
| RK-10 | SQLite lock due long transaction | Medium | Medium | MEDIUM | Short transactions; network I/O outside transaction; WAL; one worker | Low |
| RK-11 | Double click/network retry creates duplicate patient | Medium | Medium | MEDIUM | UI lock; optional idempotency; duplicate confirmation is separate intentional path | Low |
| RK-12 | Exact employer entries published to public Git | Medium | High | HIGH | Keep PDF/entries local untracked; neutral public tests; secret/data scan | Low |
| RK-13 | Read-only feasibility phase created temporary script | Confirmed event | Medium | MEDIUM | Locate `test_ollama.py`, check status, remove only after owner review if unnecessary | Low |
| RK-14 | Provider/API claims are based on vendor material | High | Medium | HIGH | Label claims as provider statements; retain raw test evidence locally; do not claim independent audit | Medium |
| RK-15 | Demo video overclaims diagnosis or AI capabilities | Medium | High | HIGH | Script separates API flags, local LLM summary, assumptions and disclaimer | Low |
| RK-16 | License/attribution obligations for Llama model overlooked | Low/Medium | Medium | MEDIUM | Review Meta Llama 3.2 Community License; do not redistribute weights; include attribution where required | Low |
| RK-17 | Application is over-engineered beyond assignment | Medium | Medium | MEDIUM | Modular monolith; no cloud/microservices/queue; phase scope and change control | Low |

## Stop-ship risks

Before Phase 4A:
- O-02 unit assumptions must be approved.
- O-03 TestWell usage must be approved.
- O-04 external data acknowledgement must be approved.
- O-07 context-limited flag presentation must be approved.

Before public GitHub release:
- RK-12 must be checked against the full Git history and tracked-file set.
- Llama attribution and licence obligations must be checked.
