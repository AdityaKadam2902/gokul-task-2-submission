# Phase 0.3 Feasibility Review — Summary

## Reported working components
- TestWell `interpret_results`: HTTP 200, 786 ms, all three required biomarkers recognized in a neutral-data probe.
- Ollama 0.40.16 running locally.
- `llama3.2:3b` already present.
- Warm local inference around 2.2 s, JSON mode response around 1.56 s.

## Architecture consequences
- TestWell is a better primary external health-related API candidate than MedlinePlus Connect because it accepts values and returns provider-reported flags and educational explanations.
- MedlinePlus may remain a secondary educational resource only.
- `llama3.2:3b` is selected as the local wording-model candidate instead of the absent `phi4-mini`.
- TestWell returned fasting and adult-male qualifiers when optional context was omitted. The app must detect and display such qualifiers, not assume they fit the patient.
- The provider values still leave the machine; send only values and units, not identifiers.
- The exact unit profile still needs owner approval.

## Evidence qualification
All latency, HTTP and local model results are transcribed from the Antigravity Phase 0.3 report. They have not been independently re-run by this author. Vendor privacy claims remain vendor claims.
