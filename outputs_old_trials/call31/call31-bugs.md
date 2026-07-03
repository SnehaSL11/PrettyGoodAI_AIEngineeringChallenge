## call-31: Maya Patel July 10 booking

**Category:** scheduling  
**Recording:** `call31-recording.mp3`  
**Transcript:** `call31-transcript.txt`  
**Scenario:** `call31-scenario.json`

**Summary:** The call failed to meet the patient's goal of scheduling an appointment. The agent repeatedly asked for spelling of the patient's name despite receiving it multiple times, indicating a broken flow. The agent also failed to confirm the appointment and ended the call by transferring to support, which violates the success criteria. Additionally, there were multiple instances of voice overlap and truncated utterances, suggesting poor turn-taking and communication issues.

### Bugs found

### Bug: Agent failed to confirm appointment
**Severity:** HIGH
**Call:** call31-transcript.txt — [2026-07-02T22:19:42.049860+00:00] AGENT: I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent did not confirm the appointment and instead transferred the call to support, failing to meet the patient's goal of booking an appointment.
**Criterion:** Agent must confirm an appointment on Friday July 10, 2026

### Bug: Agent repeatedly asked for name spelling
**Severity:** MEDIUM
**Call:** call31-transcript.txt — [2026-07-02T22:10:44.975061+00:00] AGENT: Could you please spell your first and last name for me?
**Details:** The agent asked the patient to spell their name multiple times despite receiving the correct spelling, indicating a broken flow.
**Criterion:** Patient identity should be verified before booking

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call31-transcript.txt — [2026-07-02T22:10:15.916094+00:00] PATIENT: My date of birth is April 12, 1989.
**Details:** The agent's request for the date of birth was immediately followed by the patient's response, suggesting the agent did not wait for the patient to finish.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent utterances were truncated
**Severity:** MEDIUM
**Call:** call31-transcript.txt — [2026-07-02T22:11:19.712188+00:00] AGENT: Thank you. Now please fill in your last name, Patel, letter by letter.
**Details:** The agent's utterances were often cut off or incomplete, leading to confusion and repeated requests for information.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent must confirm an appointment on Friday July 10, 2026
- Agent should state or confirm a specific time (preferably 10:30 AM)
- Patient identity should be verified before booking
- Call should end with a clear booking confirmation, not a transfer to support

---
