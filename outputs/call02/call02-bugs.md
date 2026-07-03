## call-02: Feeling off consultation request

**Category:** ambiguous_request  
**Recording:** `call02-recording.mp3`  
**Transcript:** `call02-transcript.txt`  
**Scenario:** `call02-scenario.json`

**Summary:** The call had several issues with the agent's handling of patient information and turn-taking. The agent repeatedly asked for the patient's date of birth and name spelling, despite the patient providing this information multiple times. The agent also misrecorded the patient's name and did not address the patient's initial request for medical advice, failing to suggest an appointment or provide any guidance on the symptoms described.

### Bugs found

### Bug: Agent did not address patient's request for medical advice
**Severity:** HIGH
**Call:** call02-transcript.txt — [2026-07-03T00:19:47.546383+00:00] PATIENT: Hi, this is Taylor Morgan. I’ve been feeling generally unwell and really tired, just kind of off, and I’m not sure if I should schedule a check-up or do something at home first. Could you let me know what you’d recommend?
**Details:** The agent failed to ask clarifying questions about the patient's symptoms or suggest an appointment, which was the patient's main concern.
**Criterion:** Agent should ask clarifying questions about symptoms

### Bug: Agent repeatedly asked for information already provided
**Severity:** MEDIUM
**Call:** call02-transcript.txt — [2026-07-03T00:20:15.610419+00:00] AGENT: full date of birth.
**Details:** The agent asked for the patient's date of birth multiple times despite the patient providing it clearly.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent misrecorded patient's name
**Severity:** HIGH
**Call:** call02-transcript.txt — [2026-07-03T00:21:55.174618+00:00] AGENT: for spelling that out. I have your name as Paylor Morrison and your date of birth as March 15th 1985. Is that correct?
**Details:** The agent incorrectly recorded the patient's name as 'Paylor Morrison' despite the patient spelling it out multiple times.
**Criterion:** Agent should not dismiss the symptoms without advice

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call02-transcript.txt — Tight turn gap (1ms) at 2026-07-03T00:20:15.611045+00:00: AGENT then PATIENT — likely simultaneous speech.
**Details:** The agent did not wait for the patient to finish speaking before responding, leading to overlapping speech.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent should ask clarifying questions about symptoms
- Agent should suggest an appointment for a physical evaluation
- Agent should not dismiss the symptoms without advice

---
