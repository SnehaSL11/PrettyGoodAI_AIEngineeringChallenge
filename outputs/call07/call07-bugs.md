## call-07: Appointment request on non-existent date

**Category:** edge_case  
**Recording:** `call07-recording.mp3`  
**Transcript:** `call07-transcript.txt`  
**Scenario:** `call07-scenario.json`

**Summary:** The call had several issues with the agent's handling of the appointment request. The agent failed to identify that February 29th is not possible in a non-leap year and did not offer an alternative date in March. Additionally, there were multiple instances of poor turn-taking and truncated utterances, which affected the flow of the conversation.

### Bugs found

### Bug: Agent failed to identify February 29th as unavailable
**Severity:** HIGH
**Call:** call07-transcript.txt — [2026-07-03T00:38:18.350447+00:00] PATIENT: I’d like to schedule a routine checkup for February 29th if that’s available.
**Details:** The agent did not inform the patient that February 29th is not possible in a non-leap year and did not offer an alternative date.
**Criterion:** Agent correctly identifies February 29th is not possible in a non-leap year

### Bug: Agent did not offer the next available date in March
**Severity:** HIGH
**Call:** call07-transcript.txt — [2026-07-03T00:38:18.350447+00:00] PATIENT: I’d like to schedule a routine checkup for February 29th if that’s available.
**Details:** The agent should have offered the next available date in March when February 29th was requested.
**Criterion:** Agent offers the next available date in March

### Bug: Agent repeated request for spelling of last name
**Severity:** MEDIUM
**Call:** call07-transcript.txt — [2026-07-03T00:36:59.518544+00:00] AGENT: Please spell your last name Johnson for me.
**Details:** The agent asked the patient to spell their last name multiple times unnecessarily, which could frustrate the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call07-transcript.txt — Duplicate patient replies (7ms apart) at 2026-07-03T00:37:25.682720+00:00
**Details:** The agent likely spoke over the patient, causing the patient to repeat their response.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterances
**Severity:** LOW
**Call:** call07-transcript.txt — Possible truncated agent utterance at 2026-07-03T00:36:22.082598+00:00
**Details:** The agent's utterances were cut off or incomplete, which could confuse the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent correctly identifies February 29th is not possible in a non-leap year
- Agent explains why February 29th is unavailable
- Agent offers the next available date in March

---
