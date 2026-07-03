## call-13: Holiday appointment request

**Category:** edge_case  
**Recording:** `call13-recording.mp3`  
**Transcript:** `call13-transcript.txt`  
**Scenario:** `call13-scenario.json`

**Summary:** The call failed to meet the success criteria as the agent did not inform the patient that the office is closed on New Year's Day, nor did it provide the next available appointment date. Additionally, there were several instances of poor turn-taking, with the agent's utterances being truncated and overlapping with the patient's speech.

### Bugs found

### Bug: Agent did not inform patient about office closure on New Year's Day
**Severity:** HIGH
**Call:** call13-transcript.txt — [turn 2026-07-02T19:33:44.392309+00:00] AGENT: I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent should have informed the patient that the office is closed on New Year's Day and provided the next available appointment date.
**Criterion:** Agent should explain the office is closed on public holidays

### Bug: Agent did not provide the next available appointment date
**Severity:** HIGH
**Call:** call13-transcript.txt — [turn 2026-07-02T19:33:44.392309+00:00] AGENT: I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent should have offered the next available weekday for an appointment after New Year's Day.
**Criterion:** Agent should provide the next available date for an appointment

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call13-transcript.txt — [turn 2026-07-02T19:32:29.765827+00:00] PATIENT: Alex Martinez. First name Alex, last name Martinez.
**Details:** The agent's request for confirmation of the patient's name overlapped with the patient's response, indicating poor turn-taking.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterance
**Severity:** MEDIUM
**Call:** call13-transcript.txt — [turn 2026-07-02T19:31:57.939750+00:00] AGENT: calling from the number we have on file. Am I speaking with Maya?
**Details:** The agent's utterance appears to be truncated, which could confuse the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterance
**Severity:** MEDIUM
**Call:** call13-transcript.txt — [turn 2026-07-02T19:32:05.999452+00:00] AGENT: your date of birth.
**Details:** The agent's utterance appears to be truncated, which could confuse the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterance
**Severity:** MEDIUM
**Call:** call13-transcript.txt — [turn 2026-07-02T19:32:49.694756+00:00] AGENT: you like me to use your phone number to look up your record? If so, please tell 
**Details:** The agent's utterance appears to be truncated, which could confuse the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent must not confirm an appointment on New Year's Day
- Agent should explain the office is closed on public holidays
- Agent should provide the next available date for an appointment

---
