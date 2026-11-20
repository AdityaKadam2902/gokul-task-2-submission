# Requirements Traceability Matrix

**Version:** 0.2  
**Primary source:** employer Task 2 PDF, retained locally and excluded from public Git.

| ID | Employer requirement | Design location | Planned implementation phase | Acceptance evidence |
|---|---|---|---|---|
| R-01 | Python backend | Architecture, API specification | 1–3 | FastAPI starts; OpenAPI docs available |
| R-02 | Any suitable frontend | UI specification | 5 | Browser UI works |
| R-03 | Full name field | Project spec, database | 2, 5 | Create/read/edit display |
| R-04 | DOB field | Validation, database | 2, 3, 5 | Strict date parsing and display |
| R-05 | Email field | Validation, database | 2, 3, 5 | Syntax validation and update |
| R-06 | Glucose field | Database, AI integration | 2–5 | Value persisted and sent with unit |
| R-07 | Haemoglobin field | Database, AI integration | 2–5 | Value persisted and sent with unit |
| R-08 | Cholesterol field | Database, AI integration | 2–5 | Value persisted and sent with unit |
| R-09 | AI-generated remarks | AI integration | 4B, 5 | Real local LLM output labelled as AI |
| R-10 | Create | API specification | 3 | POST and UI create tests |
| R-11 | Read/list/detail | API specification | 3, 5 | GET tests and UI list/detail |
| R-12 | Update | API specification | 3, 5 | PATCH test and UI email edit |
| R-13 | Delete | API specification | 3, 5 | DELETE test and UI confirmation |
| R-14 | Clean, simple interface | UI specification | 5 | Usability checklist and screenshots |
| R-15 | Valid email | Validation | 3 | Positive/negative email tests |
| R-16 | DOB not in future | Validation | 3 | Runtime-date test |
| R-17 | dd/mm/yyyy | Validation | 3, 5 | Slash accepted; dot fixture format accepted |
| R-18 | Numeric blood values | Validation | 3 | Decimal, non-numeric, NaN, infinity, negative tests |
| R-19 | Persistent storage | Database design | 2 | Restart persistence test |
| R-20 | External AI or health API call using entered values | AI/provider design | 4A | Live TestWell request; evidence excludes identifiers |
| R-21 | Prediction/possible risk and remarks | AI integration | 4A, 4B, 5 | Provider educational flags plus qualified AI-generated remarks; no diagnosis claim |
| R-22 | Do not modify ten supplied records | Validation/demo plan | 6 | Exact manual-entry checklist against local PDF |
| R-23 | List all created records | Demo plan | 6 | Seven records displayed after valid/duplicate-confirmed entries |
| R-24 | Edit one email to specified address | Demo plan | 6 | Updated record visible |
| R-25 | Delete one record and show final list | Demo plan | 6 | Six remaining records visible |
| R-26 | Explain invalid entries in video | Demo plan | 7 | Video covers each validation message |
| R-27 | Walk through API and AI code | Demo plan | 7 | Code walkthrough covers adapters and safety boundary |
| R-28 | Upload GitHub without secrets | Security/release plan | 7 | Secret scan and clean repository |
| R-29 | Submit candidate details, GitHub and video in one email | Demo plan | 7 | Single final email checklist |

## Fixture outcome trace

The exact values are retained only in the employer PDF. Public documentation uses row numbers and outcome categories only.

| Test # | Expected outcome | Reason category |
|---:|---|---|
| 1 | Accept | Valid input |
| 2 | Reject | Invalid email syntax |
| 3 | Accept | Valid input; unusual numbers are not syntax errors |
| 4 | Reject | Impossible calendar date |
| 5 | Accept | Valid input |
| 6 | Warn, then accept if confirmed | Exact duplicate of #1 |
| 7 | Accept | Valid input |
| 8 | Reject | Invalid email and future DOB |
| 9 | Accept | Valid calendar date and email |
| 10 | Accept | Valid input |

## Required record-count proof

- Six non-duplicate valid entries.
- One explicitly confirmed duplicate.
- Three invalid entries rejected.
- Seven persisted after the creation sequence.
- Seven after one email update.
- Six after deleting a different record.

This matrix intentionally does not reproduce the employer's names, email addresses, DOBs or raw health values in public Git documentation.
