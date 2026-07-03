## call-01: Weekend appointment request

**Category:** edge_case  
**Recording:** `call01-recording.mp3`  
**Transcript:** `call01-transcript.txt`  
**Scenario:** `call01-scenario.json`

**Summary:** The call had several issues related to turn-taking and the agent's failure to address the patient's request for a Sunday appointment. The agent did not inform the patient that the office is closed on weekends and failed to offer a weekday alternative. Additionally, there were multiple instances of poor turn-taking, where the agent spoke over the patient or repeated requests for information already provided.

### Bugs found

### Bug: Agent failed to inform about weekend closure
**Severity:** HIGH
**Call:** call01-transcript.txt — [2026-07-02T18:47:56.402570+00:00] PATIENT: Hi, this is Maya Patel. I’m calling to schedule an annual physical, just a routine checkup. I work weekdays, so I’d really prefer Sunday at 10 AM if that’s available.
**Details:** The agent did not inform the patient that the office is closed on weekends and did not offer a weekday alternative.
**Criterion:** Agent must NOT confirm an appointment on Sunday or any weekend

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call01-transcript.txt — [2026-07-02T18:48:12.884264+00:00] AGENT: Please provide your date of birth.
**Details:** The agent asked for the patient's date of birth immediately after the patient provided it, suggesting the agent did not wait for the patient to finish.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent repeated verification unnecessarily
**Severity:** MEDIUM
**Call:** call01-transcript.txt — [2026-07-02T18:48:31.360310+00:00] AGENT: Can you please spell your first and last name to make sure I have it correct? I have your date of birth as April 12th, 1989. Is that right?
**Details:** The agent repeated the verification of the date of birth after the patient had already confirmed it, indicating poor turn-taking.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterance cut off
**Severity:** MEDIUM
**Call:** call01-transcript.txt — [2026-07-02T18:48:53.282445+00:00] AGENT: your phone number is 866-284-5941 and your date of birth as April 12, 1989. Is t
**Details:** The agent's utterance appears to be cut off, leading to incomplete communication.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent must NOT confirm an appointment on Sunday or any weekend
- Agent should state or imply the office is closed weekends
- Agent should offer at least one valid weekday alternative

---
