## call-12: Vague symptom discussion

**Category:** ambiguous_request  
**Recording:** `call12-recording.mp3`  
**Transcript:** `call12-transcript.txt`  
**Scenario:** `call12-scenario.json`

**Summary:** The call was primarily focused on verifying the patient's identity, with multiple redundant requests for spelling the last name, Morgan. The agent failed to address the patient's initial inquiry about symptoms and whether they required a doctor's visit or could be managed with over-the-counter medication. There were several instances of voice overlap and truncated agent utterances, indicating poor turn-taking and communication flow.

### Bugs found

### Bug: Agent failed to address patient's symptom inquiry
**Severity:** HIGH
**Call:** call12-transcript.txt — [2026-07-03T00:51:31.528794+00:00] PATIENT: Hi, I’m feeling a bit off and not sure how serious it is. Could you tell me if this is something that usually needs an in-person visit, or if it might be okay to try an over-the-counter medication first?
**Details:** The agent did not ask any clarifying questions about the symptoms or provide advice on whether the symptoms required a doctor's evaluation or could be managed with over-the-counter medication.
**Criterion:** Agent should ask clarifying questions about the symptoms

### Bug: Agent repeatedly asked for spelling of last name
**Severity:** MEDIUM
**Call:** call12-transcript.txt — [2026-07-03T00:52:37.571226+00:00] AGENT: And please spell your last name, Morgan.
**Details:** The agent repeatedly asked the patient to spell their last name, Morgan, despite the patient providing it multiple times. This led to a poor user experience.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call12-transcript.txt — Tight turn gap (567ms) at 2026-07-03T00:53:06.381121+00:00: AGENT then PATIENT — likely simultaneous speech.
**Details:** The agent likely spoke over the patient, causing confusion and repeated requests for information.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Truncated agent utterances
**Severity:** MEDIUM
**Call:** call12-transcript.txt — Possible truncated agent utterance at 2026-07-03T00:52:02.699763+00:00: 'Please provide your full name and date of birth.'
**Details:** Several agent utterances appeared truncated, which could lead to incomplete communication and misunderstanding.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent should ask clarifying questions about the symptoms
- Agent should determine if the symptoms require a doctor's evaluation
- Agent should provide general advice on whether to visit a doctor or use over-the-counter medication

---
