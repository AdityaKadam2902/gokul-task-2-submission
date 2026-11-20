# Demo and Submission Plan

**Version:** 0.2 — Owner-approved implementation baseline

## 1. Pre-recording checklist

- App starts cleanly from documented commands.
- Database is reset to an empty assessment state.
- TestWell connectivity and local Ollama are checked with neutral values first.
- External disclosure acknowledgement is visible and accepted for assessment demonstration.
- Unit assumption banner is visible.
- Logs are visible only if redacted.
- Browser zoom/resolution makes all fields readable.
- No secrets are visible in editor, terminal or video.

## 2. Required assessment sequence

Use the local original employer PDF as the source. Do not change any row.

1. Attempt record #1: accepted.
2. Attempt record #2: rejected for malformed email; explain backend and inline validation.
3. Attempt record #3: accepted; clarify unusual numbers are not syntax errors.
4. Attempt record #4: rejected for impossible calendar date.
5. Attempt record #5: accepted.
6. Attempt record #6: exact duplicate warning; explicitly confirm and save.
7. Attempt record #7: accepted.
8. Attempt record #8: reject both malformed email and future DOB; show both errors.
9. Attempt record #9: accepted; explain that the date is valid.
10. Attempt record #10: accepted.

Expected persisted count: seven.

## 3. Read/edit/delete demonstration

- Show all seven records.
- Select one record and change its email to `gokul@infocare.com`.
- Show updated email; count remains seven.
- Select a different record and delete it with confirmation.
- Show remaining six records.

Do not delete the same record used for the update.

## 4. AI/API walkthrough

Show:
- Outbound TestWell request builder and explicit allowlisted fields.
- Evidence that name/email/DOB/internal IDs are excluded.
- TestWell response normalization and context qualifier logic.
- Displayed provider citations and range qualifier.
- Ollama local request to `llama3.2:3b`.
- Structured output schema and Pydantic validation.
- Failure handling/fallback state.
- Separate statuses for external API and local AI.
- Database analysis history record.

Explain that TestWell returns educational reference intervals and flags, not a personal physician evaluation or medical diagnosis; the local LLM summarizes provider reference observations and caveats without making clinical review claims.

## 5. Video storyline

1. Introduce application and architecture briefly.
2. Explain data assumptions and privacy boundary.
3. Demonstrate create and validation cases.
4. Show duplicate confirmation.
5. Show read/list.
6. Perform email edit.
7. Delete a different record and show final list.
8. Demonstrate actual TestWell and Llama success.
9. Walk through Python provider/client/analysis orchestration code.
10. Explain a forced failure and labelled fallback.
11. Close with repository and setup instructions.

Do not claim tests, API execution or AI output that did not actually occur.

## 6. GitHub package

- Public README uses neutral sample values only.
- No original employer PDF or exact fixture names/emails/DOBs.
- No local database, `.env`, API response dumps or sensitive recording.
- Include setup steps, architecture, tests and model attribution.
- Include Meta Llama 3.2 Community License notice where applicable and the required "Built with Llama" attribution if the Llama materials/license conditions apply to the distributed package. Do not redistribute model weights.

## 7. Submission email

One email to `jobs@gokulinfocare.com`, as requested, containing:
- candidate information requested on page 1;
- GitHub repository link;
- app demonstration video link.

Verify video access permissions before sending. Candidate details (education year/GPA, prior experience, notice period, computer/internet, start time) must be truthful and current. Do not invent availability.
