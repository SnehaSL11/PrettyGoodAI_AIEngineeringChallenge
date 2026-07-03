## call-29: Past date appointment request

**Category:** edge_case  
**Recording:** `call29-recording.mp3`  
**Transcript:** `call29-transcript.txt`  
**Scenario:** `call29-scenario.json`

**Summary:** The call failed to meet the scenario's success criteria. The agent did not address the patient's request to schedule an appointment on June 25, 2026, nor did it inform the patient that the date is in the past. Instead, the agent repeatedly asked for verification details and eventually transferred the call without resolving the appointment request. There were multiple instances of poor turn-taking, with the agent speaking over the patient or having truncated utterances.

### Bugs found

### Bug: Agent failed to address past date appointment request
**Severity:** HIGH
**Call:** call29-transcript.txt — [2026-07-02T22:21:46.604535+00:00] PATIENT: Hi, I’d like to schedule a routine checkup for June 25, 2026 at 2:00 PM.
**Details:** The agent did not inform the patient that June 25, 2026, is in the past, nor did it offer the next available appointment date.
**Criterion:** Agent must state or imply that June 25, 2026 is in the past or has already passed

### Bug: Agent did not offer a future appointment date
**Severity:** HIGH
**Call:** call29-transcript.txt — [2026-07-02T22:21:46.604535+00:00] PATIENT: Hi, I’d like to schedule a routine checkup for June 25, 2026 at 2:00 PM.
**Details:** The agent failed to offer or state at least one next available future appointment date after the patient requested a past date.
**Criterion:** Agent should offer or state at least one next available future appointment date

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call29-transcript.txt — [2026-07-02T22:22:56.673372+00:00] PATIENT: Yes, that’s correct.
**Details:** The agent spoke over the patient, leading to a tight turn gap and potential miscommunication.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterance was truncated
**Severity:** MEDIUM
**Call:** call29-transcript.txt — [2026-07-02T22:23:15.388074+00:00] AGENT: proceed further right now but I can make sure our clinic support team follows up
**Details:** The agent's utterance was cut off, leading to incomplete communication.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent must state or imply that June 25, 2026 is in the past or has already passed
- Agent must NOT confirm an appointment on June 25, 2026
- Agent should offer or state at least one next available future appointment date

---
