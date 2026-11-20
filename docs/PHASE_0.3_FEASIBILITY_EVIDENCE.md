# Phase 0.3 Feasibility Evidence

**Evidence source:** Antigravity report pasted by project owner  
**Report date:** 18 November 2026  
**Status:** Environment results reported; not independently reproduced by blueprint author

## 1. Environment stated by report

- Windows 11 Pro, 64-bit.
- Intel Core i5-1335U, 10 physical cores / 12 logical processors.
- Intel Iris Xe integrated graphics.
- 16 GB physical RAM; 4.52 GB available at test time.
- Ollama 0.40.16.
- `llama3.2:3b` present, reported 2.02 GB.
- Ollama HTTP service on 127.0.0.1:11434.

No hardware inventory or machine-identifying detail beyond what is needed for runtime planning should be copied into public marketing materials.

## 2. TestWell result as reported

Request:
`POST https://www.test-well.com/api/agent/interpret_results`

Payload used invented neutral data only, with:
- glucose 90.0 mg/dL;
- hemoglobin 14.0 g/dL;
- total cholesterol 180.0 mg/dL.

Reported:
- TLS connection succeeded.
- HTTP 200.
- 786 ms latency.
- 3/3 analytes matched.
- Three reference intervals, flags, citations and links returned.
- A second neutral abnormal-value probe returned high/low flags and educational `suggests` text.

Important context result:
- Glucose qualifier returned as fasting.
- Haemoglobin qualifier returned as adult male.
- Sex/age/fasting were not supplied.
Therefore these flags must be context-limited in the app.

## 3. Local Ollama result as reported

Neutral prompt: one sentence explaining why an app validates input before saving.

- Cold request: 7.501 s.
- Warm request: 2.221 s.
- Warm generation: 16.05 tokens/second.
- JSON mode: 1.561 s; parseable response.
- No reported memory errors.

JSON mode was used. Full JSON Schema constrained output has not yet been tested with the application's eventual schema.

## 4. Governance note

The activity log also recorded `Created test_ollama.py` during a phase explicitly restricted to read-only. Its exact path is not present in the report. The project owner must locate and inspect the file before deciding whether to retain or remove it. It must not silently enter the implementation repository.

## 5. What this evidence does not prove

- No proof that the TestWell API is independently audited.
- No proof that returned ranges are appropriate for Australian clinical practice or a specific laboratory.
- No proof that the provider never stores/processes submitted values; only the provider's current privacy statement is available.
- No proof that `llama3.2:3b` will remain at the measured latency under full application load.
- No proof of clinical safety or model reliability.
- No proof of end-to-end application functionality.
