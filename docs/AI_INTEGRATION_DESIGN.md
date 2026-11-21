# External Health API and Local AI Integration Design

**Version:** 0.2 — Owner-approved implementation baseline

## 1. Employer requirement

The assignment asks the application to call an external AI or health-related API, use the patient's entered blood-test values to predict a possible health condition or disease risk, and display the result in the Remarks field.

The proposed implementation uses:
1. TestWell's external health-related `interpret_results` API to compare entered analytes with its physician-reviewed educational reference catalogue.
2. Local Ollama `llama3.2:3b` to generate a concise remarks summary from the normalized TestWell response and explicit caveats.

This is not a validated predictive model. The application must not claim to diagnose disease or calculate clinical risk probability. TestWell's returned high/low flags and explanatory copy are provider-reported educational signals. They are not a calibrated disease prediction. The employer may interpret “prediction” more narrowly; this remains a selection risk, so the demo must show exactly what the external health API did with the entered values and describe the boundary honestly.

## 2. Selected external API — conditional

Provider: TestWell  
Endpoint: `POST https://www.test-well.com/api/agent/interpret_results`  
Docs: <https://www.test-well.com/developers>  
OpenAPI: <https://www.test-well.com/openapi.json>

Provider documentation describes the endpoint as returning per-marker `low`, `normal`, `high` or `unknown` flags, physician-reviewed reference ranges, explanations, retest guidance, citations and links. Provider documentation states a limit of 120 requests/minute/IP and no authentication for its public read-only developer tools.

Initial feasibility verification reports:
- HTTP 200.
- 786 ms response.
- All three markers recognized.
- A response with reference ranges, flags and citations.
- A secondary neutral elevated-value probe returned high/low flags.

This is a reported smoke test, not independently reproduced by the architecture reviewer. The final app must re-run a controlled smoke test and have automated mocked contract tests.

## 3. Request minimization

Only send:
- `marker`
- numeric `value`
- `unit`

Do not send:
- full name
- email
- DOB
- internal patient ID
- record/analysis ID
- free-text remarks
- symptoms or history
- biological sex, age or pregnancy state, because the source task does not provide these

The provider privacy policy states that results-explainer values are not logged. This is a provider-published claim. The values still transit to an external server over HTTPS; they are not local-only. The user must acknowledge this data flow before first transmission.

## 4. Measurement unit policy

The employer PDF does not specify units. Proposed assessment profile for owner approval:
- Glucose: `mg/dL`.
- Haemoglobin: `g/dL`.
- Total cholesterol: `mg/dL`.

Do not describe these as employer-specified units. Display them as **assessment demo assumptions** in the form and analysis card. Keep a versioned `unit_profile_code` and copy the exact analyte/unit pairs into the analysis input snapshot.

If the owner does not approve this profile, do not call TestWell with guessed units. If the operator has an actual lab report, that report's units and reference interval take precedence.

## 5. Missing clinical context

Not supplied by assignment:
- fasting/random/post-meal status;
- biological sex;
- specimen collection date;
- age at specimen collection;
- pregnancy/postmenopausal status;
- lab-specific reference intervals;
- specimen type or assay method;
- total vs HDL/LDL cholesterol is not explicit.

Do not infer these from names or current date. In particular, DOB without specimen date cannot establish age at test.

The Phase 0.3 report found that when `sex` and `age` are omitted, TestWell returned:
- a fasting qualifier for glucose;
- an adult male qualifier for haemoglobin;
- adult age qualifier for total cholesterol.

The application must inspect the returned qualifier. When the response relies on an unprovided condition, set `context_status=CONTEXT_NOT_CONFIRMED` (or a more specific reason code) and show the qualifier. A provider `normal` flag does not become a definitive patient interpretation when its context is unknown.

## 6. Provider response normalization

For each result:
- Ensure the result maps to one requested marker.
- Require a boolean `found`.
- Accept only known flags `low`, `normal`, `high`, `unknown`.
- Validate that `unitMismatch` is boolean.
- Validate range object types if present.
- Preserve `range.text`, `range.unit`, and `range.qualifier`.
- Preserve provider `suggests`, `retest`, citations and links as provider-sourced fields.
- Reject unsafe URLs (only HTTPS and approved provider/source domains).
- Never invent a missing citation, reference interval or flag.
- If `found=false`, `flag=unknown`, or `unitMismatch=true`, do not treat it as normal.
- If a marker is missing, keep the other matched results and mark overall analysis `DEGRADED`.

The raw provider response should be retained in a bounded, sanitized analysis JSON field, not written to application logs.

## 7. Local LLM — Ollama

Selected model candidate: `llama3.2:3b`  
Local runtime reported by Phase 0.3: Ollama 0.40.16  
Model reported on machine: 2.02 GB quantized model.

Reported feasibility measurements:
- Cold wall time: 7.501 s.
- Warm wall time: 2.221 s.
- Warm token speed: 16.05 tokens/s.
- JSON mode test: 1.561 s.
- 16 GB physical RAM; approximately 4.52 GB available at test time.

These results are machine- and workload-specific. They are not performance guarantees. Phase 0.3 tested JSON mode (`format: "json"`), not a constrained JSON Schema request. Phase 4B must test JSON Schema structured output against the actual local runtime. Ollama documents a JSON Schema `format` option; see [Ollama structured outputs](https://ollama.com/blog/structured-outputs).

Model card: <https://ollama.com/library/llama3.2:3b>  
License: Meta Llama 3.2 Community License; review the terms and include appropriate attribution. Do not describe it as OSI-approved open source.

## 8. LLM responsibility boundary

The model receives only:
- normalized provider observations;
- provider-written explanatory text and citation IDs;
- measurement units;
- explicit context caveats;
- approved instruction template.

Treat all provider-returned text as untrusted data, not instructions. Delimit it as quoted reference content; never execute provider-supplied instructions, URLs or code. The model may refer only to observation IDs and citation IDs already present in the normalized input.

It does not receive patient identity or DOB.

The model may:
- create a concise plain-language summary of provider-returned information;
- state that context is missing;
- refer to provider source material by existing reference IDs.

The model must not:
- calculate its own thresholds;
- change `low`/`normal`/`high` flags;
- infer fasting status, sex, age at draw or symptoms;
- issue a diagnosis;
- assign disease probability or severity score;
- recommend medication or treatment;
- add tests, citations or medical claims not in the provider payload.

## 9. Structured output contract

Proposed Pydantic schema and matching TypeScript type:

```json
{
  "remark": "Short neutral summary based only on supplied provider observations.",
  "source_observation_ids": ["glucose-0"],
  "caveat_codes": ["FASTING_STATUS_UNKNOWN", "UNIT_ASSUMPTION"],
  "generation_label": "AI_GENERATED"
}
```

Validation:
- Exact required keys; forbid additional properties.
- `remark`: non-empty, maximum 500 characters.
- `source_observation_ids`: subset of IDs given to model.
- `caveat_codes`: enum only; no free-form caveats.
- `generation_label` must be a fixed enum.
- Provider citations are stored separately and never authored by the model.
- Reject invalid JSON, unknown observation IDs, unexpected diagnosis/treatment language, numeric values not present in source facts, or output outside size limits.
- Safety checks are layered; regex is only a rejection aid, not proof of safety.
- If semantics cannot be verified, discard model text and show fallback.

## 10. Safe fallback

If TestWell fails:
- `external_status=FAILED`.
- Do not invent clinical observations.
- If the local AI has no approved facts to summarize, do not ask it to fill in medical conclusions.
- Show: “External health reference could not be retrieved. No health interpretation is available.”

If TestWell succeeds but Ollama fails/schema validation fails:
- Preserve provider observations and citations.
- Set `ai_status=FALLBACK`.
- Set `overall_status=DEGRADED`.
- Display a deterministic, non-AI template clearly labelled “AI remarks unavailable — provider information shown”.
- Never label fallback text as AI-generated.

## 11. Required analysis acceptance tests

- AT-10A: at least one successful live TestWell invocation with all three matched markers.
- AT-10B: successful real local Llama inference producing a schema-valid remark from a controlled provider response.
- AT-10C: provider timeout/failure leads to honest no-interpretation state.
- AT-10D: Ollama timeout or invalid output leads to labelled deterministic fallback; no fabricated successful AI status.
- AT-10E: context qualifier mismatch is surfaced.
- AT-10F: no identifier appears in the serialized outbound provider payload or logs.

## 12. Medical disclaimer

Use a visible statement:
“Educational assessment prototype only. Provider ranges and explanations are informational and depend on the assumptions and context shown. This application does not diagnose, provide medical advice or replace the laboratory report or a qualified clinician.”

Do not label the app “clinically validated”, “diagnostic”, “predictive model” or “medical decision support”.
