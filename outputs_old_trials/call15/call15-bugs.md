## call-15: Nonexistent date appointment request

**Category:** edge_case  
**Recording:** `call15-recording.mp3`  
**Transcript:** `call15-transcript.txt`  
**Scenario:** `call15-scenario.json`

**Summary:** The call involved a patient mistakenly trying to schedule a dental appointment at an orthopedic clinic. The agent correctly identified the mismatch in services but did not address the nonexistent date issue as the patient ended the call after realizing the mistake. There was a minor overlap issue at the end of the call, but it did not affect the outcome.

### Bugs found

### Bug: Agent did not address nonexistent date
**Severity:** MEDIUM
**Call:** call15-transcript.txt — [2026-07-02T19:36:42.423391+00:00] PATIENT: Hi, this is Jamie Carter. I’d like to schedule a dental cleaning for February 30th, please.
**Details:** The agent did not recognize or correct the nonexistent date of February 30th, which was part of the patient's request.
**Criterion:** Agent recognizes and corrects the nonexistent date

### Bug: Agent spoke over patient
**Severity:** LOW
**Call:** call15-transcript.txt — [2026-07-02T19:37:25.661929+00:00] PATIENT: Thanks, I appreciate it. Have a good day.
**Details:** There was a tight turn gap suggesting simultaneous speech, but it did not impact the call flow.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent recognizes and corrects the nonexistent date
- Agent provides clear information about the correct calendar dates
- Agent successfully offers a valid appointment date

---
