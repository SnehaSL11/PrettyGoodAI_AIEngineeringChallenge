## call-17: Feeling Off Consultation Inquiry

**Category:** ambiguous_request  
**Recording:** `call17-recording.mp3`  
**Transcript:** `call17-transcript.txt`  
**Scenario:** `call17-scenario.json`

**Summary:** The call exhibited several issues with the agent's handling of the patient's request. The agent repeatedly asked for information that the patient had already provided, such as spelling the last name, and made errors in confirming the patient's name. The agent failed to ask for specific symptoms or provide advice based on the patient's vague symptoms, and instead redirected the patient to a support team without addressing the initial inquiry. Additionally, there were multiple instances of possible truncated utterances and turn-taking issues.

### Bugs found

### Bug: Agent repeatedly asked for spelling of last name
**Severity:** MEDIUM
**Call:** call17-transcript.txt — Could you please spell your last name, Morgan? / Please spell your last name for me.
**Details:** The agent asked the patient to spell their last name multiple times despite the patient already providing it clearly.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent confirmed incorrect name
**Severity:** HIGH
**Call:** call17-transcript.txt — To confirm, your full name is Alex Tan and your date of birth is July 15, 1985. Is that correct?
**Details:** The agent incorrectly confirmed the patient's name as 'Alex Tan' instead of 'Alex Morgan', despite the patient spelling it correctly.
**Criterion:** Agent should accurately confirm patient information

### Bug: Agent failed to ask for specific symptoms
**Severity:** HIGH
**Call:** call17-transcript.txt — I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent did not ask the patient for more specific symptoms or provide any advice based on the patient's vague symptoms.
**Criterion:** Agent asks for more specific symptoms or descriptions

### Bug: Agent did not provide advice based on symptoms
**Severity:** HIGH
**Call:** call17-transcript.txt — I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent did not provide any advice or guidance based on the patient's symptoms, failing to address the patient's concern.
**Criterion:** Agent provides potential advice based on generalized symptoms

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call17-transcript.txt — [2026-07-02T20:31:36.768915+00:00] AGENT then PATIENT — likely simultaneous speech.
**Details:** The agent spoke over the patient, leading to a poor user experience.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterances appeared truncated
**Severity:** MEDIUM
**Call:** call17-transcript.txt — here calling from the number we have on file. Am I speaking with Maya?
**Details:** The agent's utterance appeared truncated, which could confuse the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent asks for more specific symptoms or descriptions
- Agent provides potential advice based on generalized symptoms
- Agent suggests scheduling an appointment if symptoms persist or worsen

---
