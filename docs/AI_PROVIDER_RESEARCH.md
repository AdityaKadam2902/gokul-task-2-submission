# AI and External Health API Provider Research

**Version:** 0.2 — researched 18 November 2026  
**Purpose:** choose an external health API and local wording model for the assessment. This is not a vendor security audit.

## 1. Employer requirement interpretation

The employer allows an external AI **or health-related API**, and asks to use values entered in the app to produce possible health-condition/risk remarks. A health-related API that accepts numeric lab values and returns flags/explanations is closer to this specification than a general educational content lookup. The local LLM supplies the AI-generated remark.

## 2. TestWell `interpret_results` — recommended conditionally

Official sources:
- [Developer portal](https://www.test-well.com/developers)
- [OpenAPI](https://www.test-well.com/openapi.json)
- [Privacy policy](https://www.test-well.com/privacy)
- [Terms](https://www.test-well.com/terms)
- [About TestWell](https://www.test-well.com/about)
- [Editorial/medical review policy](https://www.test-well.com/editorial-policy)

Published capabilities:
- Public read-only endpoint; no API key per documentation.
- `POST /api/agent/interpret_results`.
- Request accepts a `values` array with marker/value/optional unit, plus optional sex/age/pregnancy/postmenopausal context.
- Response includes `found`, `flag` (`low`, `normal`, `high`, `unknown`), range, unit mismatch indicator, educational `suggests`, retest text, citations and links.
- Published limit: 120 requests/minute/IP.
- Provider calls its interpretation educational and says the user's own report range takes precedence.

Phase 0.3 reported live test:
- HTTP 200 and 786 ms.
- 3/3 markers recognized (glucose, hemoglobin, total cholesterol).
- Reference data and citations returned.
- When optional context was omitted, observed glucose range qualifier was fasting and haemoglobin range qualifier was adult male.
- Abnormal neutral probe returned provider flags and educational suggestions.

Important limitations:
- This is a US lab reference catalogue, not an Australian laboratory reference service.
- Range applicability may require age/sex/fasting context not supplied by the employer.
- The provider's no-logging statement is self-published and not independently audited.
- Values are still transmitted to an external commercial server over HTTPS.
- The provider says it does not offer diagnosis or medical advice.
- TestWell was founded in 2025 according to its own About page; it is a relatively new provider. The project has not conducted a corporate, legal, security or clinical audit.
- Do not send real patient records.

Verdict: **Conditionally suitable for this coding assessment as an external health-related reference/interpreter API**, using de-identified numeric values only, with context caveats and no diagnostic claims. Owner approval is required.

## 3. NLM MedlinePlus Connect — secondary only

Official documentation: https://medlineplus.gov/medlineplus-connect/

It maps lab-test codes (e.g. LOINC) to educational information. It is useful for contextual articles and citations, but does not accept the patient's numeric results or calculate flags. It is not sufficient as the sole primary integration for this task.

## 4. Hosted generative LLMs — not selected

No hosted LLM is selected for the baseline. This avoids additional disclosure of health-related values and avoids relying on a provider whose terms may restrict health advice/clinical use. If a hosted LLM is later proposed, it needs a separate review of current terms, data processing, retention, region, user consent and intended-use restrictions. De-identification alone is not proof that provider use is permitted.

## 5. Local model: Ollama + Llama 3.2 3B

Official sources:
- [Ollama model page](https://ollama.com/library/llama3.2:3b)
- [Ollama structured output docs](https://ollama.com/blog/structured-outputs)
- [Meta Llama 3.2 license/model materials](https://www.llama.com/llama-downloads/)

Phase 0.3 reported:
- Ollama version 0.40.16.
- `llama3.2:3b` installed, approximately 2.02 GB quantized.
- CPU inference on Intel i5-1335U with 16 GB RAM.
- Warm generation approximately 2.221 seconds and 16.05 tokens/sec.
- JSON mode returned parseable JSON.

Limitations:
- Benchmarks reflect a short, neutral prompt; not the actual application prompt under concurrent frontend/backend load.
- JSON mode is not equivalent to JSON-Schema constrained output; test the latter in Phase 4B.
- The model is not clinically validated and must not interpret raw lab data independently.
- Meta Llama 3.2 uses a Community License, not a conventional OSI open-source license. Review the licence and attribution requirements; do not redistribute model weights.

Verdict: **Recommended local wording component**, conditional on Phase 4B schema, safety, latency and attribution tests.

## 6. Provider decision

Primary external health API: TestWell, conditional.
Secondary generic education links: sources returned by TestWell; optional MedlinePlus links where explicitly supplied by provider.
Local AI remark generator: Ollama `llama3.2:3b`.
Fallback: deterministic, visibly non-AI statement.
Hosted generative API: not selected.

## 7. Evidence classification

- Provider capabilities and privacy terms: provider-published statements.
- HTTP request and latency: verified during preliminary feasibility testing.
- Local model timings: verified during preliminary feasibility testing.
- Independent security/privacy audit: not performed.
- Clinical validation of returned ranges for Australian patients: not performed.
