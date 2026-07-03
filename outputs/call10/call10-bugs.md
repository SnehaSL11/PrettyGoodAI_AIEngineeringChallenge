## call-10: Holiday appointment request

**Category:** edge_case  
**Recording:** `call10-recording.mp3`  
**Transcript:** `call10-transcript.txt`  
**Scenario:** `call10-scenario.json`

**Summary:** The call exhibited several issues, including the agent's failure to inform the patient about the clinic's closure on July 4th and not offering an alternative appointment date. Additionally, there were multiple instances of poor turn-taking, with the agent speaking over the patient and repeating requests for information already provided.

### Bugs found

### Bug: Agent failed to inform about holiday closure
**Severity:** HIGH
**Call:** call10-transcript.txt — [2026-07-03T00:47:23.489323+00:00] PATIENT: I’m hoping to schedule an appointment for July 4th if you have availability. If not, I can take the closest date you have.
**Details:** The agent did not inform the patient that the clinic is closed on July 4th, nor did it offer an alternative date.
**Criterion:** Agent informs the patient about the holiday closure

### Bug: Agent did not offer another appointment date
**Severity:** HIGH
**Call:** call10-transcript.txt — [2026-07-03T00:47:23.489323+00:00] PATIENT: I’m hoping to schedule an appointment for July 4th if you have availability. If not, I can take the closest date you have.
**Details:** The agent failed to offer another appointment date after the holiday, leaving the patient without a resolution.
**Criterion:** Agent offers another appointment date after the holiday

### Bug: Agent repeated request for date of birth
**Severity:** MEDIUM
**Call:** call10-transcript.txt — [2026-07-03T00:46:27.194108+00:00] AGENT: Thanks, Alex. What is your date of birth?
**Details:** The agent asked for the patient's date of birth again immediately after it was provided, indicating a failure to process the information correctly.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent repeated request for name spelling
**Severity:** MEDIUM
**Call:** call10-transcript.txt — [2026-07-03T00:47:04.947532+00:00] AGENT: Could you please spell your first and last name for me?
**Details:** The agent asked the patient to spell their name again immediately after it was already spelled out, suggesting a failure in processing or memory.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent spoke over patient
**Severity:** LOW
**Call:** call10-transcript.txt — [2026-07-03T00:46:36.824138+00:00] PATIENT then AGENT — likely simultaneous speech.
**Details:** The agent spoke over the patient, indicating poor turn-taking and potentially causing confusion.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent does not schedule an appointment on the public holiday
- Agent informs the patient about the holiday closure
- Agent offers another appointment date after the holiday

---
