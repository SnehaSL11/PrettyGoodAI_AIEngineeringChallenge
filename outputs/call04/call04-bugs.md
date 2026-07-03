## call-04: Appointment on February 30th

**Category:** edge_case  
**Recording:** `call04-recording.mp3`  
**Transcript:** `call04-transcript.txt`  
**Scenario:** `call04-scenario.json`

**Summary:** The call with the AI agent failed to address the patient's request for an appointment on February 30th, a non-existent date. The agent did not correct the patient or offer an alternative date, and the call ended without resolving the scheduling issue. Additionally, there were several instances of poor turn-taking and truncated agent responses, leading to a suboptimal user experience.

### Bugs found

### Bug: Agent failed to address non-existent date
**Severity:** HIGH
**Call:** call04-transcript.txt — I was hoping to book something for February 30th if possible.
**Details:** The agent did not inform the patient that February 30th is not a valid date and did not offer an alternative date in February.
**Criterion:** Agent should explain the error of the date

### Bug: Agent did not offer an alternative date
**Severity:** HIGH
**Call:** call04-transcript.txt — I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent did not offer a valid date in February as an alternative to the non-existent February 30th.
**Criterion:** Agent should offer a valid date in February as an alternative

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call04-transcript.txt — [2026-07-03T00:26:11.648570+00:00] PATIENT: No, this is Alex Morgan. I’m calling from a different number, but the phone number on file should be 212-555-0291.
**Details:** The agent spoke almost simultaneously with the patient, indicating poor turn-taking.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterance
**Severity:** MEDIUM
**Call:** call04-transcript.txt — provide your date of birth.
**Details:** The agent's request for the patient's date of birth was truncated, leading to potential confusion.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterance
**Severity:** MEDIUM
**Call:** call04-transcript.txt — your phone number is 212-555-0291 and your date of birth as May 14, 1985. Is tha
**Details:** The agent's confirmation of the patient's details was cut off, which could lead to misunderstandings.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent should explain the error of the date
- Agent should offer a valid date in February as an alternative

**Criteria met:**
- Agent must not confirm an appointment for February 30th

---
