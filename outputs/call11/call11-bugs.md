## call-11: Rescheduling for a holiday

**Category:** reschedule  
**Recording:** `call11-recording.mp3`  
**Transcript:** `call11-transcript.txt`  
**Scenario:** `call11-scenario.json`

**Summary:** The call failed to meet the patient's goal of rescheduling an appointment. The agent did not inform the patient about the holiday closure or provide a weekday alternative. Additionally, there were several issues with voice overlap and truncated utterances, leading to a poor user experience.

### Bugs found

### Bug: Agent did not inform about holiday closure
**Severity:** HIGH
**Call:** call11-transcript.txt — [2026-07-03T00:48:45.190099+00:00] PATIENT: Hi, this is Stephanie Miller. I’d like to reschedule my existing appointment to July 4th at 2 PM, please.
**Details:** The agent failed to inform the patient that the clinic is closed on July 4th, a holiday, and did not provide a weekday alternative.
**Criterion:** Agent should inform the patient about the holiday closure

### Bug: Agent did not provide a weekday alternative
**Severity:** HIGH
**Call:** call11-transcript.txt — [2026-07-03T00:48:45.190099+00:00] PATIENT: Hi, this is Stephanie Miller. I’d like to reschedule my existing appointment to July 4th at 2 PM, please.
**Details:** The agent did not offer the next available weekday appointment after informing the patient about the holiday closure.
**Criterion:** Agent should provide a weekday alternative

### Bug: Agent repeated request for phone number
**Severity:** MEDIUM
**Call:** call11-transcript.txt — [2026-07-03T00:50:03.687214+00:00] AGENT: Please tell me the phone number you have on file with us.
**Details:** The agent asked for the phone number again immediately after the patient had already provided it, indicating a failure to process the information.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterances were truncated
**Severity:** MEDIUM
**Call:** call11-transcript.txt — [2026-07-03T00:49:15.922185+00:00] AGENT: Thank you for clarifying, please provide your date of birth.
**Details:** The agent's utterance appears to be truncated, potentially leading to confusion.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterances were truncated
**Severity:** MEDIUM
**Call:** call11-transcript.txt — [2026-07-03T00:50:34.905086+00:00] AGENT: you to a representative. Please wait.
**Details:** The agent's utterance appears to be truncated, potentially leading to confusion.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent should inform the patient about the holiday closure
- Agent should not confirm an appointment on the holiday
- Agent should provide a weekday alternative

---
