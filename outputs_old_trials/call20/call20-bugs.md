## call-20: Holiday appointment request

**Category:** edge_case  
**Recording:** `call20-recording.mp3`  
**Transcript:** `call20-transcript.txt`  
**Scenario:** `call20-scenario.json`

**Summary:** The call had several issues with the agent's performance, including repeated requests for information, truncated utterances, and failure to inform the patient about the clinic's closure on Thanksgiving Day. The agent did not suggest an alternative weekday appointment, nor did it confirm the patient's acceptance of a new appointment date. Additionally, there were multiple instances of poor turn-taking, where the agent's speech was cut off or overlapped with the patient's responses.

### Bugs found

### Bug: Agent failed to inform about Thanksgiving closure
**Severity:** HIGH
**Call:** call20-transcript.txt — [2026-07-02T20:43:48.777246+00:00] AGENT: I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent did not inform the patient that the clinic is closed on Thanksgiving Day, which was a critical piece of information for the patient's request.
**Criterion:** Agent must inform the patient about closure on Thanksgiving Day

### Bug: Agent did not suggest a weekday appointment
**Severity:** HIGH
**Call:** call20-transcript.txt — [2026-07-02T20:43:48.777246+00:00] AGENT: I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent failed to suggest the next available weekday afternoon appointment as an alternative to the unavailable Thanksgiving Day slot.
**Criterion:** Agent should suggest a weekday appointment as an alternative

### Bug: Agent did not confirm patient's acceptance of new appointment date
**Severity:** HIGH
**Call:** call20-transcript.txt — [2026-07-02T20:43:50.488288+00:00] PATIENT: Yes, please have them contact me.
**Details:** The agent did not confirm the patient's acceptance of a new appointment date, leaving the scheduling unresolved.
**Criterion:** Agent must confirm the patient's acceptance of a new appointment date

### Bug: Agent repeated request for date of birth
**Severity:** MEDIUM
**Call:** call20-transcript.txt — [2026-07-02T20:42:02.116220+00:00] AGENT: I need your data first to continue. Could you please tell me your data first?
**Details:** The agent redundantly asked for the patient's date of birth immediately after it was provided, indicating a failure to process the information correctly.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call20-transcript.txt — [2026-07-02T20:42:31.315203+00:00] AGENT: the moth name.
**Details:** The agent's utterance was cut off, suggesting it spoke over the patient or did not wait for the patient to finish.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterance was truncated
**Severity:** MEDIUM
**Call:** call20-transcript.txt — [2026-07-02T20:42:59.269235+00:00] AGENT: Thank you for clarifying. To help find your record, would you like to use the ph
**Details:** The agent's speech was cut off, indicating a technical issue or poor turn-taking.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent must inform the patient about closure on Thanksgiving Day
- Agent should suggest a weekday appointment as an alternative
- Agent must confirm the patient's acceptance of a new appointment date

---
